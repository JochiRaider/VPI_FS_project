import json

def run(**args):
  basic_config =json.dumps([{"module" : "dir_lister"},{"module" : "enviro"},{"module" : "sleep24h"},{"module" : "stage_2"}])
  return basic_config
