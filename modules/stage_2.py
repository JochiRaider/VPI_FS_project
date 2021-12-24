import json

def run(**args):
  print('[$] Enter Stage 2')
  basic_config =json.dumps([{"module" : "sleep24h"}])
  return basic_config
