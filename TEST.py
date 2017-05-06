import os
import psutil
import numpy as np

"""Funksjoner for testing av applikasjon"""

def memory_info():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss/10**6

def print_memory_info():
    print()
    print("************************")
    print("Minnebruk: {} MB".format(memory_info()))
    print("************************")
    print()



if __name__ == "__main__":
    a = np.zeros((15,9,4))
    b = np.zeros((15,9))
    c = np.zeros((15))

    c[2] = 2
    b[2][3] = 3
    a[2][3][4] = 4