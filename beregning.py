import numpy
import inndata
import system
import geometri
import laster
import klima
import tilstand
import TEST
import deformasjon


def _beregn_reaksjonskrefter(F):
    """Beregner reaksjonskrefter og plasserer bidragene i riktig rad
    og kolonne i R-matrisen."""

    # Initierer R-matrisen for reaksjonskrefter
    R = numpy.zeros((15, 6))

    for j in F:
        R_0 = numpy.zeros((15, 6))
        f = j.f
        if not numpy.count_nonzero(j.q) == 0:
            f = numpy.array([j.q[0] * j.b, j.q[1] * j.b, j.q[2] * j.b])

        # Sorterer bidrag til reaksjonskrefter
        R_0[j.type][0] = (f[0] * j.e[2]) + (f[2] * -j.e[0])
        R_0[j.type][1] = f[1]
        R_0[j.type][2] = (f[0] * -j.e[1]) + (f[1] * j.e[0])
        R_0[j.type][3] = f[2]
        R_0[j.type][4] = f[0]
        R_0[j.type][5] = abs(f[1] * -j.e[2]) + abs(f[2] * j.e[1])
        R += R_0

    return R


def _beregn_deformasjoner(mast, F, i):
    """Beregner deformasjoner og plasserer bidragene
     i riktig rad og kolonne i D-matrisen.
    """

    # Initerer deformasjonsmatrisen, D
    D = numpy.zeros((15, 3))

    for j in F:
        D_0 = numpy.zeros((15, 3))

        D_0 += deformasjon.bjelkeformel_M(mast, j, i.fh) \
            + deformasjon.bjelkeformel_P(mast, j, i.fh) \
            + deformasjon.bjelkeformel_q(mast, j, i.fh)

        if mast.type == "bjelke":
            D_0 += deformasjon.torsjonsvinkel(mast, j, i.fh)

        D += D_0

    return D


def beregn(ini):
    import mast

    # R = reaksjonskrefter ved mastens innspenning
    #
    #              R
    #
    #          Indekser:
    #   0   1   2   3   4   5
    #   My  Vy  Mz  Vz  N   T
    #  ________________________
    # |                        | 0  Egenvekt (mast, utligger, ledninger)
    # |                        | 1  Kontaktledning
    # |                        | 2  Fixpunkt
    # |                        | 3  Fixavspenning
    # |                        | 4  Avspenning
    # |                        | 5  Forbigangsledning
    # |                        | 6  Returledning
    # |                        | 7  Fiberoptisk ledning
    # |                        | 8  Mate-/fjernledning
    # |                        | 9  AT-ledning
    # |                        | 10 Jordledning
    # |                        | 11 Snø og is
    # |                        | 12 Vind (fra mast, mot spor)
    # |                        | 13 Vind (fra spor, mot mast)
    # |                        | 14 Vind (parallelt spor)
    #  ------------------------
    #
    #
    # D = forskyvning av mast i kontakttradhøyde FH
    #
    #       D
    #
    #   Indekser:
    #   0   1   2
    #   Dy  Dz  phi
    #  _____________
    # |             | 0  Egenvekt (mast, utligger, ledninger)
    # |             | 1  Kontaktledning
    # |             | 2  Fixpunkt
    # |             | 3  Fixavspenning
    # |             | 4  Avspenning
    # |             | 5  Forbigangsledning
    # |             | 6  Returledning
    # |             | 7  Fiberoptisk ledning
    # |             | 8  Mate-/fjernledning
    # |             | 9  AT-ledning
    # |             | 10 Jordledning
    # |             | 11 Snø og is
    # |             | 12 Vind (fra mast, mot spor)
    # |             | 13 Vind (fra spor, mot mast)
    # |             | 14 Vind (parallelt spor)
    #  -------------



    # Oppretter inndataobjekt med data fra .ini-fil
    i = inndata.Inndata(ini)
    # Oppretter masteobjekt med brukerdefinert høyde
    master = mast.hent_master(i.h, i.s235, i.materialkoeff)
    # Oppretter systemobjekt med data for ledninger og utliggere
    sys = system.hent_system(i)
    # q_p = klima.beregn_vindkasthastighetstrykk_EC(i.h)
    q_p = i.vindkasthastighetstrykk * 1000
    B1, B2, e_max = geometri.beregn_sikksakk(sys, i)
    a_T, a_T_dot = geometri.beregn_arm(i, B1)


    # Definerer grensetilstander inkl. lastfaktorer for ulike lastfaktorer i EC3
    # g = egenvekt, l = loddavspente, f = fastavspente/fix, k = klima
    bruddgrense = {"Navn": "bruddgrense", "g": [1.0, 1.2], "l": [0.9, 1.2],
                   "f": [0.0, 1.2], "k": [1.5]}
    forskyvning_kl = {"Navn": "forskyvning_kl",
                      "g": [0.0], "l": [0.0], "f": [-0.25, 0.7], "k": [1.0]}
    forskyvning_tot = {"Navn": "forskyvning_tot",
                       "g": [1.0], "l": [1.0], "f": [0.0, 1.0], "k": [1.0]}

    grensetilstander = [bruddgrense]

    # FELLES FOR ALLE MASTER
    F_generell = []
    F_generell.extend(laster.beregn(sys, i, a_T, a_T_dot, B1, B2))
    F_generell.extend(klima.vindlast_ledninger(i, sys, q_p))
    #F_generell.extend(klima.isogsno_last(i, sys, a_T, a_T_dot))


    # UNIKT FOR HVER MAST
    for mast in master:

        F = []
        F.extend(F_generell)
        F.extend(laster.egenvekt_mast(mast))
        F.extend(klima.vindlast_mast(mast, q_p))


        if mast.navn == "H5":
            for j in F:
                print(j)


        if i.ec3:
            # Beregninger med lastfaktorkombinasjoner ihht. EC3

            R = _beregn_reaksjonskrefter(F)


            # Samler laster med lastfaktor g
            gravitasjonslast = R[0][:]

            # Samler laster med lastfaktor l
            loddavspente = R[1][:]

            # Samler laster med lastfaktor f (f1)
            fix = R[2:4][:]
            fix = numpy.sum(fix, axis=0)

            # Samler laster med lastfaktor f (f2)
            fastavspente = R[4:8][:]
            fastavspente = numpy.sum(fastavspente, axis=0)

            # Samler laster med lastfaktor f (f3)
            toppmonterte = R[8:11][:]
            toppmonterte = numpy.sum(toppmonterte, axis=0)

            # Faktor k brukes for beregning av klimalaster
            sno = R[11][:]
            vind_max = R[12][:]  # Vind fra mast, mot spor
            vind_min = R[13][:]  # Vind fra spor, mot mast
            vind_par = R[14][:]  # Vind parallelt sor

            """Sammenligner alle mulige kombinasjoner av lastfaktorer
            for hver enkelt grensetilstand og lagrer resultat av hver enkelt
            sammenligning i sitt respektive masteobjekt
            """
            for grensetilstand in grensetilstander:
                for g in grensetilstand["g"]:
                    for l in grensetilstand["l"]:
                        for f1 in grensetilstand["f"]:
                            for f2 in grensetilstand["f"]:
                                for f3 in grensetilstand["f"]:
                                    for k in grensetilstand["k"]:
                                        K = (g * gravitasjonslast
                                            + l * loddavspente
                                            + f1 * fix
                                            + f2 * fastavspente
                                            + f3 * toppmonterte)
                                        K1 = K + k * (sno + vind_max)
                                        K2 = K + k * (sno + vind_min)
                                        K3 = K + k * (sno + vind_par)
                                        t1 = tilstand.Tilstand(mast, i, R, K1,
                                                              grensetilstand, 1,
                                                              g, l, f1, f2,
                                                              f3, k)
                                        t2 = tilstand.Tilstand(mast, i, R, K2,
                                                               grensetilstand, 2,
                                                               g, l, f1, f2,
                                                               f3, k)
                                        t3 = tilstand.Tilstand(mast, i, R, K3,
                                                               grensetilstand, 3,
                                                               g, l, f1, f2,
                                                               f3, k)
                                        mast.lagre_tilstand(t1)
                                        mast.lagre_tilstand(t2)
                                        mast.lagre_tilstand(t3)
                                        """
                                        kandidater.append(kandidat + k * vind_max)
                                        kandidater.append(kandidat + k * vind_min)
                                        kandidater.append(kandidat + k * vind_par)
                                        """
        else:
            # Beregninger med lasttilfeller fra bransjestandard EN 50119

            GK = 1.2
            QCK = 1.5

            R += klima.vindlast_ledninger_NEK(sys, mast, i, a)
            R += klima.vindlast_mast_normalt_spor_NEK(mast, i)
            R += klima.vindlast_mast_parallelt_spor_NEK(mast, i)

            # Permanente laster (lastfaktor GK)
            permanente = R[0:11][:]
            permanente = numpy.sum(permanente, axis=0)

            # Variable laster (lastfaktor QCK)
            sno = R[11][:]
            vind_max = R[12][:]  # Vind fra mast, mot spor
            vind_min = R[13][:]  # Vind fra spor, mot mast
            vind_par = R[14][:]  # Vind parallelt sor

            for grensetilstand in grensetilstander:
                K1 = GK * permanente + QCK * (sno + vind_max)
                K2 = GK * permanente + QCK * (sno + vind_min)
                K3 = GK * permanente + QCK * (sno + vind_par)
                t1 = tilstand.Tilstand(mast, i, R, K1, grensetilstand, 1)
                t2 = tilstand.Tilstand(mast, i, R, K2, grensetilstand, 2)
                t3 = tilstand.Tilstand(mast, i, R, K3, grensetilstand, 3)
                mast.lagre_tilstand(t1)
                mast.lagre_tilstand(t2)
                mast.lagre_tilstand(t3)

    # Sjekker minnebruk (TEST)
    TEST.print_memory_info()

    return i, master






















