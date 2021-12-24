
import os

def run(**args):
    print('[*] In dir_lister module.')
    files = os.listdir('.')
    return str(files)
