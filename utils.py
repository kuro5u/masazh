import os
import sys
import time
import threading
from colorama import Fore

class BackgroundTasks(threading.Thread):
    def run(self, *args, **kwargs):
        loading_message()

def handle_sigint(signum, frame):
    print("\nExiting..")
    os._exit(0)

def loading_message():
    ticks = 4
    for i in range(ticks):
        sys.stdout.write(f'\r{Fore.GREEN}Mashazing{Fore.RESET} your audio' + ' .' * (i % ticks))
        sys.stdout.flush()
        time.sleep(1)

def clear_message():
    sys.stdout.write('\r' + ' ' * 30 + '\r')
    sys.stdout.flush()
