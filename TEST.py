import os
import psutil
import numpy
import math
from string import Template

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




def newtonraphson(H_0, E, A, G_0, G_x, L, alpha, delta_T):
    # Konstanter
    a = E*A*(G_x*L)**2/24
    b = - H_0+E*A*(G_0*L)**2/(24*H_0**2) + E*A*alpha*delta_T

    # Itererer
    i = 0
    H_x = H_0
    res = a - H_x**2 * (H_x + b)
    while res > 100:
        K_T = 3*H_x**2 + 2*H_x*b
        delta_H_x = res/K_T
        H_x += delta_H_x
        res = a - H_x**2 * (H_x+b)
        i += 1

    return(H_x, i)





if __name__ == "__main__":

    H_x, i = newtonraphson(H_0=2480, E=56000, A=242.54, G_0=6.43/1000, G_x=6.43/1000,
                           L=30000, alpha=2.3*10**(-5), delta_T=-45)
    print("H_x = {:.3g} kN\nAntall iterasjoner: {}".format(H_x/1000, i))







