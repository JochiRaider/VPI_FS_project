import time
import random

def run(**args):
   upper = 5*60
   lower = 4*60
   time.sleep(random.randint(lower, upper))
