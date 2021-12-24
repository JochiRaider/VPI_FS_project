import json

def run(**args):
  print('[$] Enter stage 1')
  basic_config =json.dumps([{"module" : "dir_lister"},{"module" : "enviro"},{"module" : "sleep"},{"module" : "qrw_stage_2"}])
  return basic_config
