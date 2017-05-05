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
    a = "hei"
    b = "nei"

    F = [[] for i in range(7)]

    y[0].append(a)
    y[0].append(b)
    y[1].append(a)

    print(y)