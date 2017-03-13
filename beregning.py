import numpy
import inndata
import system
import momentarm
import egenvekt
import k1
import k2
import klima
import tilstand
import TEST

def beregn(ini):
    import mast

    # R = bidrag til reaksjonskrefter og forskyvninger
    # R opprettes og beregnes for hver mast i mastelista

    #
    #                   R
    #
    #               Indekser:
    #   0   1   2   3   4   5   6    7   8
    #   My  Vy  Mz  Vz  N   T   phi  Dy  Dz
    #  _____________________________________
    # |                                     | 0  Egenvekt (mast, utligger, ledninger)
    # |                                     | 1  Kontaktledning (strekk i loddavspente)
    # |                                     | 2  Fixpunkt
    # |                                     | 3  Fixavspenning
    # |                                     | 4  Avspenning
    # |                                     | 5  Forbigangsledning
    # |                                     | 6  Returledning
    # |                                     | 7  Fiberoptisk ledning
    # |                                     | 8  Mate-/fjernledning
    # |                                     | 9  AT-ledning
    # |                                     | 10 Jordledning
    # |                                     | 11 Snø og is
    # |                                     | 12 Vind (fra mast, mot spor)
    # |                                     | 13 Vind (fra spor, mot mast)
    # |                                     | 14 Vind (parallelt spor)
    #  -------------------------------------

    # Oppretter inndataobjekt med data fra .ini-fil
    i = inndata.Inndata(ini)
    # Oppretter masteobjekt med brukerdefinert høyde
    master = mast.hent_master(i.gittermast, i.h, i.s235, i.materialkoeff)
    # Oppretter systemobjekt med data for ledninger og utliggere
    sys = system.hent_system(i)
    q_p = klima.beregn_vindkasthastighetstrykk(i.h)
    B1, B2, e = momentarm.beregn_sikksakk(sys, i)
    a = momentarm.beregn_masteavstand(sys, i, B1, B2, e, q_p)
    a_T, a_T_dot = momentarm.beregn_arm(i, B1)

    # Definerer grensetilstander inkl. lastfaktorer for ulike lastfaktorer i EC3
    # g = egenvekt, l = loddavspente, f = fastavspente/fix, k = klima
    bruddgrense = {"navn": "bruddgrense", "g": [1.0, 1.2], "l": [0.9, 1.2],
                   "f": [0.0, 1.2], "k": [1.5]}
    forskyvning_kl = {"navn": "forskyvning_kl",
                      "g": [0.0], "l": [0.0], "f": [-0.25, 0.7], "k": [1.0]}
    forskyvning_tot = {"navn": "forskyvning_tot",
                       "g": [1.0], "l": [1.0], "f": [0.0, 1.0], "k": [1.0]}

    grensetilstander = [bruddgrense, forskyvning_kl, forskyvning_tot]


    for mast in master:
        R = numpy.zeros((15, 9))
        R += egenvekt.beregn_mast(mast, i.h)
        R += egenvekt.beregn_ledninger(sys, i, mast, a_T)
        R += k1.sidekraft(sys, i, mast, a_T, a_T_dot, a, B1, B2)
        if i.fixpunktmast:
            R += k2.beregn_fixpunkt(sys, i, mast, a_T, a_T_dot, a)
        if i.fixavspenningsmast:
            R += k2.beregn_fixavspenning(sys, i, mast, a_T, a, B1, B2)
        if i.avspenningsmast:
            R += k2.beregn_avspenning(sys, i, mast, a_T, a, B1, B2)
        if i.forbigang_ledn:
            R += k2.sidekraft_forbi(sys, i, mast, a_T, a_T_dot, a)
        if i.retur_ledn:
            R += k2.sidekraft_retur(sys, i, mast, a_T, a_T_dot, a)
        if i.fiberoptisk_ledn:
            R += k2.sidekraft_fiber(sys, i, mast, a_T, a_T_dot, a)
        if i.matefjern_ledn:
            R += k2.sidekraft_matefjern(sys, i, mast, a_T, a_T_dot, a)
        if i.at_ledn:
            R += k2.sidekraft_at(sys, i, mast, a_T, a_T_dot, a)
        if i.jord_ledn:
            R += k2.sidekraft_jord(sys, i, mast, a_T, a_T_dot, a)

        if i.ec3:
            # Beregninger med lastfaktorkombinasjoner ihht. EC3

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
                                            + f3 * toppmonterte
                                            + k * sno)
                                        t = tilstand.Tilstand(mast, e, K,
                                                              grensetilstand,
                                                              g, l, f1, f2,
                                                              f3, k)
                                        mast.lagre_tilstand(t)
                                        """
                                        kandidater.append(kandidat + k * vind_max)
                                        kandidater.append(kandidat + k * vind_min)
                                        kandidater.append(kandidat + k * vind_par)
                                        """
        else:
            # Beregninger med lasttilfeller fra bransjestandard EN 50119

            GK = 1.2
            QCK = 1.5

            # Permanente laster (lastfaktor GK)
            permanente = R[0:11][:]
            permanente = numpy.sum(permanente, axis=0)

            # Variable laster (lastfaktor QCK)
            variable = R[11:][:]
            variable = numpy.sum(variable, axis=0)

            for grensetilstand in grensetilstander:
                K = GK * permanente + QCK * variable
                t = tilstand.Tilstand(mast, e, K, grensetilstand)
                mast.lagre_tilstand(t)

        if mast.navn == "H6" or mast.navn == "HE200B":
            print()
            print(mast)
            mast.print_tilstander()
            print()
            print("Vindkasthastighetstrykk: {:.3g} N/m^2".format(q_p))
            print("Vindlast på mast: {:.3g} N".format(klima.vindlast_mast(mast, q_p, i.h)))
            print("Ca. resulterende moment: {:.3g} kNm".format(klima.vindlast_mast(mast, q_p, i.h)*mast.h/2000))
            print("Vindlast på ledninger: {:.3g} N".format(klima.vindlast_ledninger(i, sys, q_p)))
            print("Total ledningsdiameter: {:.3g} m".format(klima.total_ledningsdiameter(i, sys)))
            print("isogsnolast: {:.3g} N/m".format(klima.isogsno_last(i, sys)))



    # Sjekker minnebruk (TEST)
    TEST.print_memory_info()





















