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

    F = []

    a = numpy.ones((2,2))

    F.extend([a])

    print(F)

    F[0] = -F[0]

    print(F)
    print()
    print(a)







