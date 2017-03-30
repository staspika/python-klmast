import os
import psutil
import configparser

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
    cfg = configparser.ConfigParser()
    cfg.read("input.ini")
    s = "cfg[\"Info\"] = OrderedDict(["
    t = 0
    for key in cfg["Info"]:
        s += "(\"{}\", {}.get()), ".format(key, key)
        if t % 2 == 0:
            s += "\n\t\t\t\t\t   "
    s += " ])\n\n"

    s += "cfg[\"Mastealternativer\"] = OrderedDict(["
    t = 0
    for key in cfg["Mastealternativer"]:
        s += "(\"{}\", {}.get()), ".format(key, key)
        if t % 2 == 0:
            s += "\n\t\t\t\t\t\t\t"
    s += " ])\n\n"

    s += "cfg[\"Fastavspent\"] = OrderedDict(["
    t = 0
    for key in cfg["Fastavspent"]:
        s += "(\"{}\", {}.get()), ".format(key, key)
        if t % 2 == 0:
            s += "\n\t\t\t\t\t  "
    s += " ])\n\n"

    s += "cfg[\"System\"] = OrderedDict(["
    t = 0

    for key in cfg["System"]:
        s += "(\"{}\", {}.get()), ".format(key, key)
        if t % 2 == 0:
            s += "\n\t\t\t\t "
    s += " ])\n\n"

    s += "cfg[\"Geometri\"] = OrderedDict(["
    t = 1
    for key in cfg["Geometri"]:
        s += "(\"{}\", {}.get()), ".format(key, key)
        if t % 2 == 0:
            s += "\n\t\t\t\t   "
        t = t+1
    s += " ])\n\n"

    s += "cfg[\"Div\"] = OrderedDict(["
    t = 1
    for key in cfg["Div"]:
        s += "(\"{}\", {}.get()), ".format(key, key)
        if t % 2 == 0:
            s += "\n\t\t\t  "
        t = t+1
    s += " ])\n\n"

    with open("kode.txt", "w") as kode:
        kode.write(s)
