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

    alle = []

    master = mast.hent_master(10, False, 1.05)

    B_master = [mast for mast in master if mast.type == "B"]
    H_master = [mast for mast in master if mast.type == "H"]
    bjelke_master = [mast for mast in master if mast.type == "bjelke"]

    alle.extend(B_master)
    alle.extend(H_master)
    alle.extend(bjelke_master)

    for m in alle:
        print(m.navn)












