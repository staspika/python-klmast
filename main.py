import beregning
import time

# Tester kjøretid
start_time = time.clock()


###################################################################

print("Velkommen til Bane NORs fantastiske nye beregningsverktøy!")


with open("input.ini", "r") as ini:
    beregning.beregn(ini)

###################################################################


print("--- %s seconds ---" % (time.clock() - start_time))


