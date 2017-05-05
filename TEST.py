import os
import psutil
import numpy

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
    a = []
    b = [2]
    c = []
    c.extend(a)
    c.extend(a)
    c.extend(b)
    c.extend(a)
    c.extend(b)

    print(c)