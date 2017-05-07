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
    x = 3
    y = 3
    z = 3
    R = numpy.zeros((x,y,z))
    for a in range(x):
        for b in range(y):
            for c in range(z):
                R[a][b][c] = 1

    print(R)
    R[:, 1, :] = 0
    print("\n\n\n\n")
    print(R)

    k = numpy.sum(R, axis=0)
    K = numpy.sum(k, axis=0)


    print(k)
    print("\n\n\n\n")
    R[:][:][2] = 0
    print(R)






