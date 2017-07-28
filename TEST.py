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

    master = mast.hent_master(10, False, 1.05)

    B_master = [mast for mast in master if mast.type == "B"]
    H_master = [mast for mast in master if mast.type == "H"]
    bjelke_master = [mast for mast in master if mast.type == "bjelke"]

    H = [h / 10 for h in range(0, 135, 5)]

    i = 1
    plt.subplot(len(B_master),1,1)
    plt.title("St. Venants torsjonskonstant I_T for B-master")
    for mast in B_master:
        It = []
        Cw = []
        for h in H:
            it, cw = mast.torsjonsparametre(h)
            It.append(it/10**3)
            Cw.append(cw)
        if i>1:
            plt.subplot(len(B_master),1,i)

        plt.plot(H, It, c="b", ls="-", lw=2.0, label="{}".format(mast.navn))
        plt.ylabel("It [10^3 * mm^4]")
        plt.xlim(0,13)
        plt.legend(loc=2)
        plt.grid()
        i += 1
    plt.xlabel("x [m]")
    plt.show()

    i = 1
    plt.subplot(len(H_master),1,1)
    plt.title("St. Venants torsjonskonstant I_T for H-master")
    for mast in H_master:
        It = []
        Cw = []
        for h in H:
            it, cw = mast.torsjonsparametre(h)
            It.append(it/10**3)
            Cw.append(cw)

        if i>1:
            plt.subplot(len(H_master),1,i)

        plt.plot(H, It, c="b", ls="-", lw=2.0, label="{}".format(mast.navn))
        plt.ylabel("It [10^3 * mm^4]")
        plt.xlim(0,13)
        plt.legend(loc=2)
        plt.grid()
        i += 1
    plt.xlabel("x [m]")
    plt.show()

    i = 1
    plt.subplot(len(bjelke_master),1,1)
    plt.title("St. Venants torsjonskonstant I_T for bjelkemaster")
    for mast in bjelke_master:
        It = []
        Cw = []
        for h in H:
            it, cw = mast.torsjonsparametre(h)
            It.append(it/10**3)
            Cw.append(cw)
        if i>1:
            plt.subplot(len(bjelke_master),1,i)

        plt.plot(H, It, c="b", ls="-", lw=2.0, label="{}".format(mast.navn))
        plt.ylabel("It [10^3 * mm^4]")
        plt.xlim(0,13)
        plt.legend(loc=2)
        plt.grid()
        i += 1
    plt.xlabel("x [m]")
    plt.show()















