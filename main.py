import beregning
import time
import resultater
import inndata

# Tester kjøretid
start_time = time.clock()


###################################################################

print("Velkommen til Bane NORs fantastiske nye beregningsverktøy!")


with open("input.ini", "r") as ini:
    # Oppretter inndataobjekt med data fra .ini-fil
    i = inndata.Inndata(ini)
    master = beregning.beregn(i)


master_sortert = sorted(master, key=lambda mast:mast.bruddgrense.utnyttelsesgrad, reverse=True)

for mast in master_sortert:
    print("Navn: {}     UR = {:.3g} %".format(mast.navn, 100*mast.bruddgrense.utnyttelsesgrad))

mastetype = "g"  # g for gitter, b for bjelke
mast = None
for m in master_sortert:
    if mastetype == "g":
        if (m.type == "B" or m.type == "H") and m.bruddgrense.utnyttelsesgrad <= 1.0:
            mast = m
            break
    else:
        if m.type == "bjelke" and m.bruddgrense.utnyttelsesgrad <= 1.0:
            mast = m
            break

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

UR = mast.bruddgrense.utnyttelsesgrad
values = [UR, mast.bruddgrense.My_kap,
          mast.bruddgrense.Mz_kap, mast.bruddgrense.N_kap]
#resultater.barplot(values)

###################################################################


print("--- %s seconds ---" % (time.clock() - start_time))


