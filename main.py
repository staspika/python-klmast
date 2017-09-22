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

    :return: Lister med ferdige beregnede master ``gittermaster_sortert``
     og ``bjelkemaster_sortert``, kopi av input for aktuell beregning ``i``
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
    # Oppretter inndataobjekt med data fra .ini-fil
    i = inndata.Inndata()
    i.from_ini_file("input.ini")
    masteliste = beregning.beregn(i)
    for mast in masteliste:
        mast.sorter_grenseverdier()
    master_sortert = sorted(masteliste, key=lambda mast: mast.tilstand_UR_max.utnyttelsesgrad, reverse=True)
    for mast in master_sortert:
        print("Navn: {}     UR = {:.3g} %".format(mast.navn, 100*mast.bruddgrense[0].utnyttelsesgrad))
    print()
    ###################################################################
    print("--- %s seconds ---" % (time.clock() - start_time))
