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
    from tkinter import *

    root = Tk()
    sv = StringVar()


    def callback():
        print(sv.get())
        return False


    e = Entry(root, textvariable=sv, validate="focusout", validatecommand=callback)
    e.grid()
    e = Entry(root)
    e.grid()
    root.mainloop()













