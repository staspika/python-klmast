import numpy
import system
import lister
import laster
import klima
import tilstand
import TEST
import deformasjon


def _beregn_reaksjonskrefter(F):
    """Beregner reaksjonskrefter og plasserer bidragene i riktig rad
    og kolonne i R-matrisen."""

    # Initierer R-matrisen for reaksjonskrefter
    R = numpy.zeros((5, 8, 6))

    for j in F:
        R_0 = numpy.zeros((5, 8, 6))
        f = j.f
        if not numpy.count_nonzero(j.q) == 0:
            f = numpy.array([j.q[0] * j.b, j.q[1] * j.b, j.q[2] * j.b])

        # Sorterer bidrag til reaksjonskrefter
        R_0[j.type[1], j.type[0], 0] = (f[0] * j.e[2]) + (f[2] * -j.e[0])
        R_0[j.type[1], j.type[0], 1] = f[1]
        R_0[j.type[1], j.type[0], 2] = (f[0] * -j.e[1]) + (f[1] * j.e[0])
        R_0[j.type[1], j.type[0], 3] = f[2]
        R_0[j.type[1], j.type[0], 4] = f[0]
        R_0[j.type[1], j.type[0], 5] = abs(f[1] * -j.e[2]) + abs(f[2] * j.e[1])
        R += R_0

    return R


def _beregn_deformasjoner(i, sys, mast, F, sidekrefter):
    """Beregner deformasjoner og plasserer bidragene
     i riktig rad og kolonne i D-matrisen.
    """

    # Initierer deformasjonsmatrisen, D
    D = numpy.zeros((2, 8, 6))

    for j in F:
        D_0 = numpy.zeros((2, 8, 6))

        # Egenvekt og strekk statiske laster, resten dynamiske
        etasje = 0 if j.type[1] < 2 else 1

        D_0 += deformasjon.bjelkeformel_M(mast, j, i.fh, etasje) \
             + deformasjon.bjelkeformel_P(mast, j, i.fh, etasje) \
             + deformasjon.bjelkeformel_q(mast, j, i.fh, etasje)

        if mast.type == "bjelke":
            D_0 += deformasjon.torsjonsvinkel(mast, j, i, etasje)

        D += D_0

    D += deformasjon.utliggerbidrag(sys, sidekrefter)

    return D


def beregn(i):
    import mast

    # Indeksering av 3D-matriser:
    # [etasje, rad, kolonne]
    #
    #
    # R = reaksjonskrefter ved mastens innspenning
    #
    #              R
    #
    #          Indekser:
    #   0   1   2   3   4   5
    #   My  Vy  Mz  Vz  N   T
    #  ________________________
    # |                        | 0  Mast + utligger
    # |                        | 1  Kontaktledning
    # |                        | 2  Fixline
    # |                        | 3  Avspenning
    # |                        | 4  Bardunering
    # |                        | 5  Fastavspente (sidemontert)
    # |                        | 6  Fastavspente (toppmontert)
    # |                        | 7  Brukerdefinert last
    #  ------------------------
    #
    # Etasjer: 0 = egenvekt, 1 = strekk,
    #          2 = temperatur, 3 = snø, 4 = vind
    #
    #
    # D = forskyvning av mast i kontakttrådhøyde FH
    #
    #       D
    #
    #   Indekser:
    #   0   1   2
    #   Dy  Dz  phi
    #  _____________
    # |             | 0  Mast + utligger
    # |             | 1  Kontaktledning
    # |             | 2  Fixline
    # |             | 3  Avspenning
    # |             | 4  Bardunering
    # |             | 5  Fastavspente (sidemontert)
    # |             | 6  Fastavspente (toppmontert)
    # |             | 7  Brukerdefinert last
    #  -------------
    #
    # Etasjer: 0 = statisk, 1 = dynamisk
    #


    # Oppretter masteobjekt med brukerdefinert høyde
    master = mast.hent_master(i.h, i.s235, i.materialkoeff)
    # Oppretter systemobjekt med data for ledninger og utliggere
    sys = system.hent_system(i)


    # FELLES FOR ALLE MASTER
    F_generell = []
    F_generell.extend(laster.beregn(i, sys))
    F_generell.extend(klima.isogsno_last(i, sys))
    F_generell.extend(klima.vindlast_ledninger(i, sys))

    # Sidekrefter til beregning av utliggerens deformasjonsbidrag
    sidekrefter = []
    for j in F_generell:
        if j.navn == "Sidekraft: Bæreline" or j.navn == "Sidekraft: Kontakttråd"\
                or j.navn == "Sidekraft: Avspenning bæreline" \
                or j.navn == "Sidekraft: Avspenning kontakttråd":
            sidekrefter.append(j.f[2])


    # UNIKT FOR HVER MAST
    for mast in master:

        F = []
        F.extend(F_generell)
        F.extend(laster.egenvekt_mast(mast))
        F.extend(klima.vandringskraft(i, sys, mast))
        F.extend(klima.vindlast_mast_normalt(i, mast))



        # Debug-print for krefter i systemet
        if mast.navn == "H5":
            for j in F:
                print(j)



        # Vindretning 0 = Vind fra mast, mot spor
        for vindretning in range(3):
            if vindretning == 1:
                # Vind fra spor, mot mast
                for j in F:
                    # Snur kraftretningen dersom vindlast
                    j.f = -j.f if j.type[1] == 4 else j.f
            elif vindretning == 2:
                # Vind parallelt spor
                for j in F:
                    # Nullstiller vindlast
                    if j.type[1] == 4:
                        F.remove(j)
                    # Påfører vindlast mast parallelt spor
                F.extend(klima.vindlast_mast_par(i, mast))

            R_0 = _beregn_reaksjonskrefter(F)

            lastsituasjoner, lastfaktorer = lister.hent_lastkombinasjoner(i.ec3)

            for lastsituasjon in lastsituasjoner:
                R = numpy.zeros((5, 8, 6))
                for G in lastfaktorer["G"]:
                    # Egenvekt
                    R[0, :, :] = R_0[0, :, :] * G
                    for L in lastfaktorer["L"]:
                        # Strekk
                        R[1, :, :] = R_0[1, :, :] * L
                        for T in lastfaktorer["T"]:
                            # Temperatur
                            R[2, :, :] = R_0[2, :, :] * lastsituasjoner.get(lastsituasjon)["psi_T"] * T
                            for S in lastfaktorer["S"]:
                                # Snø
                                R[3, :, :] = R_0[3, :, :] * lastsituasjoner.get(lastsituasjon)["psi_S"] * S
                                for V in lastfaktorer["V"]:
                                    # Vind
                                    R[4, :, :] = R_0[4, :, :] * lastsituasjoner.get(lastsituasjon)["psi_V"] * V

                                    t = tilstand.Tilstand(mast, i, R, F, lastsituasjon,
                                                          vindretning, G, L, T, S, V)
                                    mast.lagre_tilstand(t)


            # Regner ulykkeslast
            # pass

            # Regner deformasjoner
            # D = _beregn_deformasjoner(i, sys, mast, F, sidekrefter)


    # Sjekker minnebruk (TEST)
    TEST.print_memory_info()

    return master






















