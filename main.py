# -*- coding: utf8 -*-
"""Hovedmodul for styring av beregningsprosess og uthenting av resultater."""
from __future__ import unicode_literals
import beregning
import time
import inndata


def beregn_master(ini):
    """Kjører beregningsprosedyre.

    Mastene deles opp i gittermaster og bjelkemaster før de
    sorteres mhp. utnyttelsesgrad og returneres i to separate lister.

    :return: Lister med ferdige beregnede master ``gittermaster_sortert``, ``bjelkemaster_sortert``
    :rtype: :class:`list`, :class:`list`
    """

    masteliste = []

    # Oppretter inndataobjekt med data fra .ini-fil
    i = inndata.Inndata(ini)
    masteliste.extend(beregning.beregn(i))

    for mast in masteliste:
        mast.sorter_grenseverdier()

    gittermaster = masteliste[0:7]
    bjelkemaster = masteliste[7:]
    gittermaster_sortert = sorted(gittermaster, key=lambda mast: mast.tilstand_UR_max.utnyttelsesgrad, reverse=True)
    bjelkemaster_sortert = sorted(bjelkemaster, key=lambda mast: mast.tilstand_UR_max.utnyttelsesgrad, reverse=True)

    return gittermaster_sortert, bjelkemaster_sortert




if __name__ == "__main__":
    # Kjører kun ved direkte kjøring av main.py

    # Tester kjøretid
    start_time = time.clock()


    ###################################################################

    print("Velkommen til Bane NORs fantastiske nye beregningsverktøy!")

    values = []

    with open("input.ini", "r") as ini:
        # Oppretter inndataobjekt med data fra .ini-fil
        i = inndata.Inndata(ini)
        master = beregning.beregn(i)

    for mast in master:
        mast.sorter(0)
    master_sortert = sorted(master, key=lambda mast:mast.bruddgrense[0].utnyttelsesgrad, reverse=True)

    for mast in master_sortert:
        print("Navn: {}     UR = {:.3g} %".format(mast.navn, 100*mast.bruddgrense[0].utnyttelsesgrad))

    mastetype = "g"  # g for gitter, b for bjelke
    mast = None
    for m in master_sortert:

        # Henter ut H5 for sammenlikning med KL_fund
        if m.navn == "H5":
            mast = m

        """
        
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
        
        """

    mast.sorter_grenseverdier()
    print()
    print("Anbefalt mast:")
    print()
    print(mast)
    print()
    


    ###################################################################


    print("--- %s seconds ---" % (time.clock() - start_time))


