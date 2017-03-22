import beregning
import time
import resultater

# Tester kjøretid
start_time = time.clock()


###################################################################

print("Velkommen til Bane NORs fantastiske nye beregningsverktøy!")


with open("input.ini", "r") as ini:
    i, master = beregning.beregn(ini)

mast = master[0]
#resultater.skriv_bidrag(i, mast)

###################################################################


print("--- %s seconds ---" % (time.clock() - start_time))


