import os
import psutil
import numpy
from math import *
from string import Template
import matplotlib.pyplot as plt

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




def newtonraphson(H_guess, H_0, E, A, G_0, G_x, L, alpha, delta_T):
    # Konstanter
    a = E*A*G_x**2*L**2/24
    b = - H_0 + E*A*G_0**2*L**2/(24*H_0**2) + E*A*alpha*delta_T

    # Itererer
    i = 0
    H_list = []
    H_x = H_guess
    res = a - H_x**3 - b*H_x**2
    while abs(res)>10 and i<100:
        K_T = 3*H_x**2 + 2*b*H_x
        delta_H_x = res/K_T
        H_x += delta_H_x
        res = a - H_x**3 - b*H_x**2
        print(res / 1000)

        i += 1
        H_list.append(H_x)

    return(H_x, i, H_list)

def newtonraphson_2(H_guess, H_0, q_0, q_x, a, h, E, A, alpha, delta_T):
    # Konstanter
    L = 2*(H_0/q_0) * sinh((q_0*a/(2*H_0)))
    l_0 = L / (1 + H_0*L / (E*A*a))
    l_t = l_0*(1 + alpha*delta_T)
    C = l_t / (E * A * a)

    # Itererer
    i = 0
    H_list = []
    H_x = H_guess
    y = H_x/q_x
    z = a / (2*y)
    res = sqrt((2 * y * sinh(z)) + h ** 2) * (1 - H_x * C) - l_t
    while abs(res)>10 and i<100:
        K_T = -(2*y*sinh(z)**2 - 0.5*sinh(2*z)) \
              /sqrt(H_x**2*sinh(z)**2)*(1 - H_x*C) \
              + sqrt((2*y*sinh(z))**2 + h**2)*C
        delta_H_x = res/K_T
        H_x += delta_H_x
        y = H_x / q_x
        z = a / (2 * y)
        res = sqrt((2 * y * sinh(z)) + h ** 2) * (1 - H_x * C) - l_t
        print(res / 1000)

        i += 1
        H_list.append(H_x)

    return(H_x, i, H_list)

if __name__ == "__main__":

    H_guess = 2480

    H_0 = 8000
    E = 124000
    A = 100
    G_0 = 8.73
    G_x = 8.73
    L = 45
    alpha = 2.3 * 10 ** (-5)
    delta_T = -30

    H_x, i, H_list = newtonraphson(H_guess, H_0, E, A, G_0, G_x, L, alpha, delta_T)

    H_x, i, H_list = newtonraphson_2(H_guess, H_0, G_0, G_x, L, 0, E, A, alpha, delta_T)

    print()
    print("H_x = {:.3g} kN\nAntall iterasjoner: {}".format(H_x/1000, i))
    plt.plot([x for x in range(i)], H_list)
    plt.show(True)










