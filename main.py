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
    i = inndata.Inndata(ini)  # Oppretter inndataobjekt fra .ini-fil
    masteliste.extend(beregning.beregn(i))
    for mast in masteliste:
        mast.sorter_grenseverdier()
    gittermaster = masteliste[0:7]
    bjelkemaster = masteliste[7:]
    gittermaster_sortert = sorted(
        gittermaster,
        key=lambda mast: mast.tilstand_UR_max.utnyttelsesgrad,
        reverse=True)
    bjelkemaster_sortert = sorted(
        bjelkemaster,
        key=lambda mast: mast.tilstand_UR_max.utnyttelsesgrad,
        reverse=True)
    return gittermaster_sortert, bjelkemaster_sortert, i


if __name__ == "__main__":
    start_time = time.clock()
    print()
    print("Velkommen til Bane NORs fantastiske nye beregningsverktøy!")
    print()
    with open("input.ini", "r") as ini:
        i = inndata.Inndata(ini)
        masteliste = beregning.beregn(i)
    for mast in masteliste:
        mast.sorter_grenseverdier()
    master_sortert = sorted(
        masteliste,
        key=lambda mast: mast.tilstand_UR_max.utnyttelsesgrad,
        reverse=True)
    for mast in master_sortert:
        print("Type {:6} UR = {:>6.2%}".format(
            mast.navn, mast.bruddgrense[0].utnyttelsesgrad))
    exec_time = time.clock() - start_time
    print("Executed in {:.3f} s.".format(exec_time))
