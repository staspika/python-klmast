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

    master = mast.hent_master(10, True, 1.05)

    B_master = [mast for mast in master if mast.type == "B"]
    H_master = [mast for mast in master if mast.type == "H"]

    # B-master
    i = 1
    plt.subplot(len(B_master), 1, i)
    plt.title("Effektivt vindareal for B-master (vind parallelt spor)")

    B_diff = []
    for mast in B_master:
        H = [x/10 for x in range(0, 135, 5)]
        A = []
        A_justert = []
        A_KL_fund = []
        A_KL_fund_justert = []
        for h in H:
            a = mast.vindareal_midlere(h)
            c_f, c_f_par = mast.dragkoeffisienter(h, True)
            A.append(a)
            A_justert.append(a*c_f_par)
            A_KL_fund.append(mast.A_ref_par)
            A_KL_fund_justert.append(mast.A_ref_par*2.2)

            B_diff.append(a*c_f_par / (mast.A_ref_par*2.2))

        if i>1:
            plt.subplot(len(B_master), 1, i)
        plt.plot(H, A_KL_fund, c="r", ls="--", lw=2.0, label="{}, A_ref (KL_fund)".format(mast.navn))
        plt.plot(H, A_KL_fund_justert, c="g", lw=2.0, label="{}, A_eff (KL_fund)".format(mast.navn))
        plt.plot(H, A, c="y", ls="--", lw=2.0, label="{}, A_ref (KL_mast)".format(mast.navn))
        plt.plot(H, A_justert, c="b", lw=2.0, label="{}, A_eff (KL_mast)".format(mast.navn))
        plt.axis([0, 13, 0.9 * min(A), 1.1 * max(A_KL_fund_justert)])
        plt.grid()
        if i==len(B_master):
            plt.xlabel("x [m]")
        plt.ylabel("Vindareal [m^2/m]")
        plt.legend(loc=2, fontsize=11)
        i += 1

    print(B_diff)
    diff = sum(B_diff)/len(B_diff)
    print("Midlere andel vindareal for B-master: {} %".format(diff*100))

    plt.show()

    # H-master
    i = 1
    plt.subplot(len(H_master), 1, i)
    plt.title("Effektivt vindareal for H-master")

    H_diff = []
    for mast in H_master:
        H = [x/10 for x in range(0, 135, 5)]
        A = []
        A_justert = []
        A_KL_fund = []
        A_KL_fund_justert = []
        for h in H:
            a = mast.vindareal_midlere(h)
            c_f, c_f_par = mast.dragkoeffisienter(h, True)
            A.append(a)
            A_justert.append(a*c_f_par)
            A_KL_fund.append(mast.A_ref_par)
            A_KL_fund_justert.append(mast.A_ref_par * 2.2)

            H_diff.append(a*c_f_par / (mast.A_ref_par*2.2))

        if i>1:
            plt.subplot(len(H_master), 1, i)
        plt.plot(H, A_KL_fund, c="r", ls="--", lw=2.0, label="{}, A_ref (KL_fund)".format(mast.navn))
        plt.plot(H, A_KL_fund_justert, c="g", lw=2.0, label="{}, A_eff (KL_fund)".format(mast.navn))
        plt.plot(H, A, c="y", ls="--", lw=2.0, label="{}, A_ref (KL_mast)".format(mast.navn))
        plt.plot(H, A_justert, c="b", lw=2.0, label="{}, A_eff (KL_mast)".format(mast.navn))
        plt.axis([0, 13, 0.9 * min(A), 1.1 * max(A_KL_fund_justert)])
        plt.grid()
        if i==len(H_master):
            plt.xlabel("x [m]")
        plt.ylabel("Vindareal [m^2/m]")
        plt.legend(loc=2, fontsize=11)
        i += 1
    plt.show()

    print(H_diff)
    diff = sum(H_diff)/len(H_diff)
    print("Midlere andel vindareal for H-master: {} %".format(diff*100))






