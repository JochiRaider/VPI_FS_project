import json

def run(**args):
  basic_config =json.dumps([{"module" : "dir_lister"},{"module" : "enviro"}])
  return basic_config
