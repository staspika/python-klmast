import numpy
import mast
import inndata
import system
import momentarm
import egenvekt
import k1
import k2
import klima


master = mast.hent_master()

def beregn(ini):

    # R = bidrag til reaksjonskrefter og forskyvninger
    # Oppretter og beregninger ny R for hver mast i mastelista

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

    # Oppretter inndataobjekt med data fra .ini-fil, setter mastehøyde
    i = inndata.Inndata(ini)
    # Oppretter systemobjekt med data for ledninger og utliggere
    sys = system.hent_system(i)
    q_p = klima.beregn_vindkasthastighetstrykk(i.h)
    B1, B2, e = momentarm.beregn_sikksakk(sys, i)
    a = momentarm.beregn_masteavstand(sys, i, B1, B2, e, q_p)
    a_T, a_T_dot = momentarm.beregn_arm(i, B1)



    # TEST
    print(sys)
    print("Radius = {}".format(i.radius))
    print("q_p = {}".format(q_p))
    print("B1 = {}".format(B1))
    print("B2 = {}".format(B2))
    print("e = {}".format(e))
    print("a = {}".format(a))

    # g = egenvekt, l = loddavspente, f = fastavspente/fix, k = klima
    bruddgrense = {"navn": "bruddgrense", "g": [1.0, 1.2], "l": [0.9, 1.2], "f": [0.0, 1.2], "k": [1.5]}
    forskyvning_kl = {"navn": "forskyvning_kl", "g": [0.0], "l": [0.0], "f": [-0.25, 0.7], "k": [1.0]}
    forskyvning_tot = {"navn": "forskyvning_tot", "g": [1.0], "l": [1.0], "f": [0.0, 1.0], "k": [1.0]}

    grensetilstander = [bruddgrense, forskyvning_kl, forskyvning_tot]

    hei = 0
    for mast in master:
        R = numpy.zeros((15, 9))
        R += egenvekt.beregn_mast(mast, i.h)
        R += egenvekt.beregn_ledninger(sys, i, a_T)
        R += k1.sidekraft1(mast, sys, i, B1, B2, a, a_T)
        R += k2.beregn_fixpunkt(sys, i, mast, a_T, a_T_dot, a)
        R += k2.beregn_fixavspenning(sys, i, mast, a_T, a, B1, B2)
        R += k2.beregn_avspenning(sys, i, mast, a_T, a, B1, B2)
        R += k2.sidekraft_forbi(sys, i, mast, a_T, a_T_dot, a)
        R += k2.sidekraft_retur(sys, i, mast, a_T, a_T_dot, a)
        R += k2.sidekraft_fiber(sys, i, mast, a_T, a_T_dot, a)
        R += k2.sidekraft_matefjern(sys, i, mast, a_T, a_T_dot, a)
        R += k2.sidekraft_at(sys, i, mast, a_T, a_T_dot, a)
        R += k2.sidekraft_jord(sys, i, mast, a_T, a_T_dot, a)

        resultater = []

        # Faktor g
        gravitasjonslast = R[0,:]

        # Faktor l
        loddavspente = R[1,:]

        # Faktor f (f1)
        fix = R[2:4,:]
        fix = numpy.sum(fix, axis=0)

        # Faktor f (f2)
        fastavspente = R[4:8,:]
        fastavspente = numpy.sum(fastavspente, axis=0)

        # Faktor f (f3)
        toppmonterte = R[8:11,:]
        toppmonterte = numpy.sum(toppmonterte, axis=0)

        # Faktor k brukes for beregning av klimalaster
        sno = R[11,:]
        vind_max = R[12,:]  # Vind fra mast, mot spor
        vind_min = R[13,:]  # Vind fra spor, mot mast
        vind_par = R[14,:]  # Vind parallelt sor

        """Sammenligner alle mulige kombinasjoner av lastfaktorer
        for hver enkelt grensetilstand og lagrer resultat av hver enkelt
        sammenligning som en kandidat for dimensjonerende tilfelle.
        """
        for grensetilstand in grensetilstander:
            kandidater = []
            for g in grensetilstand["g"]:
                for l in grensetilstand["l"]:
                    for f1 in grensetilstand["f"]:
                        for f2 in grensetilstand["f"]:
                            for f3 in grensetilstand["f"]:
                                for k in grensetilstand["k"]:
                                    kandidat = (g * gravitasjonslast
                                                + l * loddavspente
                                                + f1 * fix
                                                + f2 * fastavspente
                                                + f3 * toppmonterte
                                                + k * sno)
                                    kandidater.append(kandidat + k * vind_max)
                                    kandidater.append(kandidat + k * vind_min)
                                    kandidater.append(kandidat + k * vind_par)
                                    print(mast.navn)
                                    print(grensetilstand["navn"])
                                    print(g, l, f1, f2, f3, k)
                                    bjarne = ""
                                    for j in kandidat:
                                        bjarne += "{:.2} ".format(j)
                                    print(bjarne)
                                    hei += 1
                                    print("Loop nr {}".format(hei))
                                    print()

            """
            print(mast.navn)
            print(grensetilstand["navn"])
            print(kandidat)
            print()
            """




















