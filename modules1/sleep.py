
import time
import random

def run(**args):
   upper = 15
   lower = 10
   sleep_time = random.randint(lower, upper)
   print('[!] Sleep:', sleep_time)
   time.sleep(sleep_time)
   return sleep_time
