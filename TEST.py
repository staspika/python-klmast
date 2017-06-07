"""Funksjoner for testing av applikasjon"""

import os
import psutil
import numpy
from math import *
from string import Template
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
    pass