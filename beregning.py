import numpy
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
    # [etasje][rad][kolonne]
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
    # q_p = klima.beregn_vindkasthastighetstrykk_EC(i.h)
    q_p = i.vindkasthastighetstrykk * 1000  # [N/m^2]
    B1, B2, e_max = geometri.beregn_sikksakk(sys, i)
    a_T, a_T_dot = geometri.beregn_arm(i, B1)

    # FELLES FOR ALLE MASTER
    F_generell = []
    F_generell.extend(laster.beregn(sys, i, a_T, a_T_dot, B1, B2))
    F_generell.extend(klima.isogsno_last(i, sys, a_T, a_T_dot))

    # Sidekrefter til beregning av utliggerens deformasjonsbidrag
    sidekrefter = []
    for j in F_generell:
        if j.navn == "Sidekraft: Bæreline" or j.navn == "Sidekraft: Kontakttråd"\
                or j.navn == "Sidekraft: Avspenning bæreline" \
                or j.navn == "Sidekraft: Avspenning kontakttråd":
            sidekrefter.append(j.f[2])

    if i.ec3:
        # Beregninger med lastfaktorkombinasjoner ihht. EC3

        F_generell.extend(klima.vindlast_ledninger_EC(i, sys, q_p))

        # UNIKT FOR HVER MAST
        for mast in master:

            F = []
            F.extend(F_generell)
            F.extend(laster.egenvekt_mast(mast))
            F.extend(klima.vandringskraft(i, sys, mast, B1, B2, a_T, a_T_dot))
            F.extend(klima.vindlast_mast_normalt_EC(mast, q_p))

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
                    F.extend(klima.vindlast_mast_par_EC(mast, q_p))

                R = _beregn_reaksjonskrefter(F)
                #D = _beregn_deformasjoner(i, sys, mast, F, sidekrefter)

                lastsituasjoner = {"Temperatur dominerende": {"psi_T": 1.0, "psi_S": 0.7, "psi_V": 0.6},
                                   "Snølast dominerende": {"psi_T": 0.6, "psi_S": 1.0, "psi_V": 0.6},
                                   "Vind dominerende": {"psi_T": 0.6, "psi_S": 0.7, "psi_V": 1.0}}

                lastfaktorer = {"G": (1.2, 1.0), "L": (1.2, 1.0), "T": (1.5, 0),
                                "S": (1.5, 0), "V": (1.5, 0)}

                for lastsituasjon in lastsituasjoner:
                    for G in lastfaktorer["G"]:
                        for L in lastfaktorer["L"]:
                            for T in lastfaktorer["T"]:
                                for S in lastfaktorer["S"]:
                                    for V in lastfaktorer["V"]:

                                        R_0 = numpy.zeros((5, 8, 6))

                                        # Egenvekt
                                        R_0[0, :, :] = R[0, :, :] * G
                                        # Strekk
                                        R_0[1, :, :] = R[1, :, :] * L
                                        # Temperatur
                                        R_0[2, :, :] = R[2, :, :] * lastsituasjoner.get(lastsituasjon)["psi_T"] * T
                                        # Snø
                                        R_0[3, :, :] = R[3, :, :] * lastsituasjoner.get(lastsituasjon)["psi_S"] * S
                                        # Vind
                                        R_0[4, :, :] = R[4, :, :] * lastsituasjoner.get(lastsituasjon)["psi_V"] * V

                                        # Nullstiller fixline (rad 2)
                                        R_0[:, 2, :] = 0

                                        K = numpy.sum(numpy.sum(R_0, axis=0), axis=0)
                                        t = tilstand.Tilstand(mast, i, R_0, K, F, lastsituasjon,
                                                              vindretning, G, L, T, S, V)
                                        mast.lagre_tilstand(t)



    else:
        # Beregninger med lasttilfeller fra bransjestandard EN 50119


        bruddgrense = {"Navn": "bruddgrense", "G": [1.3], "Q": [1.3]}
        forskyvning_kl = {"Navn": "forskyvning_kl", "G": [0], "Q": [1.0]}
        forskyvning_tot = {"Navn": "forskyvning_tot", "G": [1.0], "Q": [1.0]}

        grensetilstander = [bruddgrense, forskyvning_kl, forskyvning_tot]


        F_generell.extend(klima.vindlast_ledninger_NEK(i, sys))

        # UNIKT FOR HVER MAST
        for mast in master:

            F = []
            F.extend(F_generell)
            F.extend(laster.egenvekt_mast(mast))
            F.extend(klima.vandringskraft(i, sys, mast, B1, B2, a_T, a_T_dot))
            F.extend(klima.vindlast_mast_normalt_NEK(mast))

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
                    F.extend(klima.vindlast_mast_par_NEK(mast, q_p))

                R = _beregn_reaksjonskrefter(F)
                D = _beregn_deformasjoner(i, sys, mast, F, sidekrefter)


                for grensetilstand in grensetilstander:
                    G = grensetilstand["G"]
                    Q = grensetilstand["Q"]
                    index = 1
                    if grensetilstand["Navn"] == "bruddgrense":
                        index = 0
                    K = G * permanente[index] + Q * (sno[index] + vind_max[index])
                    t = tilstand.Tilstand(mast, i, R, K, vindretning,
                                           grensetilstand, F,
                                           G=G, Q=Q)
                    mast.lagre_tilstand(t)

    # Sjekker minnebruk (TEST)
    TEST.print_memory_info()

    return master






















