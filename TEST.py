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
    a = [2, 4, 1]
    b = numpy.array(a)
    c = numpy.array([0, 0, 0])
    d = numpy.count_nonzero(b)
    e = numpy.count_nonzero(c)
    print(d)
    print(e)