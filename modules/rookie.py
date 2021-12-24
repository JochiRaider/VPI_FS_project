import json

def run(**args):
  basic_config =json.dumps([{"module" : "dir_lister"},{"module" : "enviro"},{"module" : "sleep24h"}])
  return basic_config
