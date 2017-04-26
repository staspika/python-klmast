import os
import psutil
import numpy

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
    at_ledninger = []
    Al_400_37 = {"Navn": "Al 400-37 uisolert", "Egenvekt": 10.31,
                         "Diameter": 25.34, "Tverrsnitt": 381.0,
                         "Max tillatt spenning": 50.0}
    Al_240_19 = {"Navn": "Al 240-19 uisolert", "Egenvekt": 6.46,
                         "Diameter": 20.0, "Tverrsnitt": 238.76,
                         "Max tillatt spenning": 50.0}
    Al_150_19 = {"Navn": "Al 150-19 uisolert", "Egenvekt": 4.07,
                         "Diameter": 15.9, "Tverrsnitt": 150.90,
                         "Max tillatt spenning": 50.0}
    BLX_T_241_19_iso = {"Navn": "BLX-T 241-19 isolert", "Egenvekt": 8.13,
                         "Diameter": 26.10, "Tverrsnitt": 241.0,
                         "Max tillatt spenning": 80.0}
    BLX_T_209_9_19_iso = {"Navn": "BLX-T 209,9-19 isolert", "Egenvekt": 7.91,
                         "Diameter": 25.8, "Tverrsnitt": 209.0,
                         "Max tillatt spenning": 80.0}
    BLX_T_111_3_7_iso = {"Navn": "BLX-T 111,3-7 isolert", "Egenvekt": 4.71,
                         "Diameter": 20.4, "Tverrsnitt": 111.0,
                         "Max tillatt spenning": 80.0}
    at_ledninger.extend([Al_400_37, Al_240_19, Al_150_19, BLX_T_241_19_iso,
                        BLX_T_209_9_19_iso, BLX_T_111_3_7_iso])

    # Setter AT-ledning
    for ledning in at_ledninger:
        print(ledning["Navn"])
        if ledning["Navn"] == "Al 400-37 uisolert":
            at_ledning = ledning