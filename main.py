import beregning
import time
import resultater

# Tester kjøretid
start_time = time.clock()


###################################################################

print("Velkommen til Bane NORs fantastiske nye beregningsverktøy!")


with open("input.ini", "r") as ini:
    i, master = beregning.beregn(ini)

g, b = resultater.sorter_resultater(master)
mast = master[g]  # g for gitter, b for bjelke
#resultater.skriv_bidrag(i, mast)

print()
print(mast)
metode = "EC3"
if not i.ec3:
    metode = "NEK"
print("Beregningsmetode: {}".format(metode))
mast.print_tilstander()
print()
print()
print("Iy_13: {}".format(mast.Iy(mast.h * (2 / 3))))
print("Iz_13: {}".format(mast.Iz(mast.h * (2 / 3))))

UR = mast.bruddgrense.utnyttelsesgrad
values = [UR, mast.bruddgrense.My_kap,
          mast.bruddgrense.Mz_kap, mast.bruddgrense.N_kap]
#resultater.barplot(values)

###################################################################


print("--- %s seconds ---" % (time.clock() - start_time))


