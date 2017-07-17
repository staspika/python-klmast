"""Funksjoner for testing av applikasjon"""

import os
import psutil




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
    max_bredde_navn = 20
    kolonnebredde = 6

    s = "Navn:".ljust(max_bredde_navn)
    s += "My{0}Vy{0}Mz{0}Vz{0}N{1}T{1}".format(" " * (kolonnebredde - 2), " " * (kolonnebredde - 1))

    for k in range(6):
        print(k)

    print(s)
