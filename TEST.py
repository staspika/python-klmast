import os
import psutil

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
    def yc(h,b,tw,tf):
        teller = b**2*tf + 0.5*tw**2*(h-2*tf)
        nevner = 2*b*tf + (h-2*tf)*tw
        return teller/nevner

    print("UNP120: {}".format(yc(120, 55, 7, 9)))
    print("UNP140: {}".format(yc(140, 60, 7, 10)))
    print("UNP160: {}".format(yc(160, 65, 7.5, 10.5)))
    print("UNP200: {}".format(yc(200, 75, 8.5, 11.5)))

    def yc2(b,t):
        teller = b**2*t + (b-t)*t**2
        nevner = b*t + (b-t)*t
        return 0.5*teller/nevner

    print("L75x75x8: {}".format(yc2(75,8)))
    print("L75x75x10: {}".format(yc2(75, 10)))