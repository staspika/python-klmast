import beregning
import time
import resultater
import inndata

# Tester kjøretid
start_time = time.clock()


###################################################################

print("Velkommen til Bane NORs fantastiske nye beregningsverktøy!")

values = []

for iterasjon in range(1):

    with open("input.ini", "r") as ini:
        # Oppretter inndataobjekt med data fra .ini-fil
        i = inndata.Inndata(ini)
        master = beregning.beregn(i)

    for mast in master:
        mast.sorter()
    master_sortert = sorted(master, key=lambda mast:mast.bruddgrense[0].utnyttelsesgrad, reverse=True)

    for mast in master_sortert:
        print("Navn: {}     UR = {:.3g} %".format(mast.navn, 100*mast.bruddgrense[0].utnyttelsesgrad))

    mastetype = "g"  # g for gitter, b for bjelke
    mast = None
    for m in master_sortert:
        if mastetype == "g":
            if (m.type == "B" or m.type == "H") \
                    and m.h_max >= m.h \
                    and m.bruddgrense[0].utnyttelsesgrad <= 1.0:
                mast = m
                break
        else:
            if m.type == "bjelke" \
                    and m.h_max >= m.h \
                    and m.bruddgrense[0].utnyttelsesgrad <= 1.0:
                mast = m
                break

    #resultater.skriv_bidrag(i, mast)

    print()
    print(mast)
    metode = "EC3" if i.ec3 else "NEK"
    print("Beregningsmetode: {}".format(metode))
    mast.print_tilstander()
    print()
    print(mast.bruddgrense[0].R[3, :, :])
    print()
    print()

    UR = mast.bruddgrense[0].utnyttelsesgrad
    current_values = [UR, mast.bruddgrense[0].My_kap,
              mast.bruddgrense[0].Mz_kap, mast.bruddgrense[0].N_kap]
    values.append(current_values)


#resultater.barplot(values)

###################################################################


print("--- %s seconds ---" % (time.clock() - start_time))


