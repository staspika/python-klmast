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
    D = numpy.zeros((5, 8, 3))

    for j in F:
        D_0 = numpy.zeros((5, 8, 3))

        # Egenvekt og strekk statiske laster, resten dynamiske

        D_0 += deformasjon.bjelkeformel_M(mast, j, i.fh) \
             + deformasjon.bjelkeformel_P(mast, j, i.fh) \
             + deformasjon.bjelkeformel_q(mast, j, i.fh)

        if mast.type == "bjelke":
            D_0 += deformasjon.torsjonsvinkel(mast, j, i)

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
    # Oppretter systemobjekt med data for ledninger, utliggere og geometri
    sys = system.hent_system(i)


    # UNIKT FOR HVER MAST
    for mast in master:

        F = []
        F.extend(laster.egenvekt_mast(mast))
        F.extend(laster.beregn(i, sys))
        F.extend(klima.vandringskraft(i, sys, mast))
        F.extend(klima.isogsno_last(i, sys))
        F.extend(klima.vindlast_ledninger(i, sys))

        # Sidekrefter til beregning av utliggerens deformasjonsbidrag
        sidekrefter = []
        for j in F:
            if j.navn == "Sidekraft: Bæreline" or j.navn == "Sidekraft: Kontakttråd" \
                    or j.navn == "Sidekraft: Avspenning bæreline" \
                    or j.navn == "Sidekraft: Avspenning kontakttråd":
                sidekrefter.append(j.f[2])

        # Vindretning 0 = Vind fra mast, mot spor
        for vindretning in range(3):
            F.extend(klima.vindlast_mast(i, mast, vindretning))
            if vindretning == 1:
                # Vind fra spor, mot mast
                for j in F:
                    # Snur kraftretningen dersom vindlast
                    if j.type[1] == 4:
                        j.snu_lastretning()
            elif vindretning == 2:
                # Vind parallelt spor
                for j in F:
                    # Nullstiller vindlast
                    if j.type[1] == 4:
                        j.nullstill()

            R_0 = _beregn_reaksjonskrefter(F)
            D_0 = _beregn_deformasjoner(i, sys, mast, F, sidekrefter)

            lastsituasjoner, lastfaktorer = lister.hent_lastkombinasjoner(i.ec3)

            for lastsituasjon in lastsituasjoner:
                # Dimensjonerende krefter i bruddgrensetilstand
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

                                    t = tilstand.Tilstand(mast, i,lastsituasjon, vindretning,
                                                          F=F, R=R, G=G, L=L, T=T, S=S, V=V)
                                    mast.lagre_tilstand(t)

                # TO DO: * Dele opp strekkraft i fastavspente i temp.avhengig og permanent bit
                #        * Regne ut pilhøyde f for hver enkelt fastavspente kabel ved +5C og -40C
                #        * Lage en funksjon for å beregne horisontal spennkraft fra fastavspente kabler
                #          mhp. egenvekt (+snø) og masteavstand (evt: formel fra KL-bibel, eller tabeller)



                D = numpy.zeros((5, 8, 3))
                D[0, :, :] = D_0[0, :, :]
                D[1, :, :] = D_0[1, :, :]
                D[2, :, :] = D_0[2, :, :] * lastsituasjoner.get(lastsituasjon)["psi_T"]
                D[3, :, :] = D_0[3, :, :] * lastsituasjoner.get(lastsituasjon)["psi_S"]
                D[4, :, :] = D_0[4, :, :] * lastsituasjoner.get(lastsituasjon)["psi_V"]
                t = tilstand.Tilstand(mast, i, lastsituasjon, vindretning, D=D)
                mast.lagre_tilstand(t)



            # Regner ulykkeslast
            # pass










            for j in F:
                if j.navn == "Vindlast: Mast":
                    F.remove(j)
                    break


    # Sjekker minnebruk (TEST)
    TEST.print_memory_info()

    return master






















