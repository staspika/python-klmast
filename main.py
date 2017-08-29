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

    :return: Lister med ferdige beregnede master ``gittermaster_sortert`` og ``bjelkemaster_sortert``, ``i``
    :rtype: :class:`list`, :class:`list`, :class:`Inndata`
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

    return gittermaster_sortert, bjelkemaster_sortert, i



if __name__ == "__main__":
    # Kjører kun ved direkte kjøring av main.py

    # Tester kjøretid
    start_time = time.clock()

    ###################################################################

    print("\nVelkommen til Bane NORs fantastiske nye beregningsverktøy!\n")

    values = []

    with open("input.ini", "r") as ini:
        # Oppretter inndataobjekt med data fra .ini-fil
        i = inndata.Inndata(ini)
        masteliste = beregning.beregn(i)


    for mast in masteliste:
        mast.sorter_grenseverdier()
    master_sortert = sorted(masteliste, key=lambda mast: mast.tilstand_UR_max.utnyttelsesgrad, reverse=True)
    for mast in master_sortert:
        print("Navn: {}     UR = {:.3g} %".format(mast.navn, 100*mast.bruddgrense[0].utnyttelsesgrad))
    print()

    mast = None
    for m in master_sortert:
        if m.navn == "B3":
            mast = m
            break

    print(mast.navn)
    print(mast.tilstand_My_max)
    print("psi_v = {}".format(mast.tilstand_My_max.dimensjonerende_faktorer["psi_v"]))
    print("M_cr_vind = {} kNm".format(2.05 * mast.tilstand_My_max.dimensjonerende_faktorer["M_cr_0"]))
    print("M_cr_punkt = {} kNm".format(1.28 * mast.tilstand_My_max.dimensjonerende_faktorer["M_cr_0"]))
    print("A = {}    B = {}".format(mast.tilstand_My_max.dimensjonerende_faktorer["A"],
                                    mast.tilstand_My_max.dimensjonerende_faktorer["B"]))
    print("M_cr = {} kNm\n".format(mast.tilstand_My_max.dimensjonerende_faktorer["M_cr"]))
    print("My_Rk = {}".format(mast.My_Rk/10**6))
    print("Mz_Rk = {}".format(mast.Mz_Rk/10**6))


    ###################################################################

    print("--- %s seconds ---" % (time.clock() - start_time))


