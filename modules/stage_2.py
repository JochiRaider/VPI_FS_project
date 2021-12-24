import json

def run(**args):
  basic_config =json.dumps([{"module" : "sleep24h"}])
  return basic_config
