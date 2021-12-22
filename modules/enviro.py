import os

def run(**args):
    print('[*] In enviroment module.')
    print(os.environ)
    return os.environ
    
