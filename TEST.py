"""Funksjoner for testing av applikasjon"""

import os
import psutil
import math
import mast
import matplotlib.pyplot as plt



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

    def P(q, l, f):
        return q * l**2 / (8 * f)

    def s(l, f):
        return l * (1 + (8/3)*(f/l)**2)

    def ds(alpha, dT, l, dP, E, A):
        return alpha*dT*l + dP*l/(E*A)

    def dN(E, A, ds, l):
        return E * A * ds / l

    # Fiberoptisk kabel
    q = 2.65
    l = 60
    f = 1.0
    alpha = 3.94 * 10 ** (-5)
    dT = -35
    dP = 0
    A = 268.9
    E = 12000

    P = P(q, l, f)
    s = s(l, f)
    ds = ds(alpha, dT, l, dP, E, A)
    dN = dN(E, A, ds, l)


    print(P)
    print(s)
    print(ds)
    print(dN)






