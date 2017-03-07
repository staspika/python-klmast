import beregning
import time

# Tester kjøretid
start_time = time.time()


###################################################################

print("Velkommen til Bane NORs fantastiske nye beregningsverktøy!")


with open("input.ini", "r") as ini:
    beregning.beregn(ini)

###################################################################


print("--- %s seconds ---" % (time.time() - start_time))


