from last import *
from numpy import array


def beregn_egenvekt(sys, i, mast, a_T, a_T_dot):
    """Beregner bidrag grunnet egenvekt av ledninger,
    isolatorer, utliggere og eventuell travers.
    """

    masteavstand = i.masteavstand
    sms = i.sms
    fh = i.fh
    sh = i.sh

    # Mastens genvekt [N]
    f = array([mast.egenvekt * mast.h, 0, 0])
    e = array([0, 0, 0])
    egenvekt = Last(navn="mast, egenvekt", type=0, f=f, e=e, kat="g")

    # Antall utliggere
    if i.siste_for_avspenning or i.linjemast_utliggere == 2:
        utliggere = 2
        f = array([220, 0, 0])
        e = array([0, 0, 0])
        travers = Last(navn="Travers", type=0, f=f, e=e, kat="g")
    else:
        utliggere = 1

    for utligger in range(utliggere):

        """Setter vertikal momentarm til kontakttrådhøyde
        + halvparten av systemhøyden, et konservativt estimat for
        angrepshøyden til det horisontalte kraftparet
        i utliggerens innspenning grunnet gravitasjonlast.
        """

        # Utligger
        f = array([sys.utligger["Egenvekt"] * sms, 0, 0])
        e = array([fh + sh/2, 0, sys.utligger["Momentarm"] * sms])
        utligger = Last(navn="Utligger", type=0, f=f, e=e, kat="g")

        # Eksentrisitet i z-retning for KL.
        if i.strekkutligger:
            ez = a_T
        else:
            ez = a_T_dot

        # Bæreline
        fx = sys.baereline["Egenvekt"] * masteavstand
        f = array([fx, 0, 0])
        e = array([fh + sh, 0, ez])
        baereline = Last(navn="Baereline", type=1, f=f, e=e, kat="g")

        # Hengetråd
        L_henge = 8 * (masteavstand / 60)
        f = array([sys.hengetraad["Egenvekt"] * L_henge, 0, 0])
        e = array([fh + sh, 0, ez])
        hengetraad = Last(navn="Hengetraad", type=1, f=f, e=e, kat="g")

        # Kontakttråd
        f = array([sys.kontakttraad["Egenvekt"] * masteavstand, 0, 0])
        e = ([fh, 0, ez])
        kontakttraad = Last(navn="kontakttraad", type=1, f=f, e=e, kat="g")

        # Y-line
        if not sys.y_line == None:  # Sjekker at systemet har Y-line
            # L = lengde Y-line
            L = 0
            if (sys.navn == "20a" or sys.navn == "35") and i.radius >= 800:
                L = 14
            elif sys.navn == "25" and i.radius >= 1200:
                L = 18
            f = array([sys.y_line["Egenvekt"] * L, 0, 0])
            e = array([fh + sh, 0, ez])
            y_line = Last(navn="Y-line", type=1, f=f, e=e, kat="g")

    # Fixpunktmast
    if i.fixpunktmast:
        f = array([sys.fixline["Egenvekt"] * masteavstand, 0, 0])
        e = array([fh + sh, 0, sms])
        fixpunkt = Last(navn="fixpunkt", type=2, f=f, e=e, kat="g")

    # Fixavspenningsmast
    if i.fixavspenningsmast:
        f = array([sys.fixline["Egenvekt"] * masteavstand / 2, 0, 0])
        e = array ([fh+sh, 0, 0])
        fixavspenning = Last(navn="fixavspenningsmast", type=3, f=f, e=e, kat="g")

    # Forbigangsledning
    if i.forbigang_ledn:
        # Isolatorens egenvekt er 150 [N] for forbigangsledning
        fx = sys.forbigangsledning["Egenvekt"] * masteavstand + 150
        f = array([fx, 0, 0])
        e = array([i.hf, 0, 0])
        forbigangsledn = Last(navn="Forbigangsledn", type=5, f=f, e=e, kat="g")

        # Forbigangsledn henger i bakkant av mast dersom dette stemmer:
        if i.matefjern_ledn or i.at_ledn or i.jord_ledn:
            f = array([fx, 0, 0])
            e = array([i.hf, 0, -0.3])
            forbigangsledn = Last(navn="Forbigangsledn", type=5, f=f, e=e, kat="g")

            """
            # Eksentrisitet pga montert på siden av mast
            arm = -0.3  # Momentarm 0.3m (retning fra spor)
            M_1 = sys.forbigangsledning["Egenvekt"] * masteavstand * arm
            M_2 = 150 * arm  # Moment fra isolator
            R[5][0] = M_1 + M_2
            R[5][8] = deformasjon._beregn_deformasjon_M(mast, M_1 + M_2, i.hf, fh)
            """

    # Returledninger (2 stk.)
    if i.retur_ledn:
        # Isolatorens egenvekt er 150 [N] pr returledning
        fx = 2 * (sys.returledning["Egenvekt"] * masteavstand + 100)
        f = array([fx, 0, 0])
        e = array([i.hr, 0, -0.5])
        returledn = Last(navn="Returledn", type=6, f=f, e=e, kat=0)

        """
        R[6][4] = 2 * sys.returledning["Egenvekt"] * masteavstand
        R[6][4] += 2 * 100  # # Isolatorer (2 stk.) for returledninger
        arm = -0.5  # Momentarm 0.5m (retning fra spor)
        M_1 = 2 * sys.returledning["Egenvekt"] * masteavstand * arm
        M_2 = 2 * 100 * arm  # Moment fra isolator
        R[6][0] = M_1 + M_2
        R[6][8] = deformasjon._beregn_deformasjon_M(mast, M_1 + M_2, i.hr, fh)
        """

    # Fiberoptisk
    if i.fiberoptisk_ledn:
        f = array([sys.fiberoptisk["Egenvekt"] * masteavstand, 0, 0])
        e = array([i.fh, 0, -0.3])
        fiberoptisk = Last(navn="Fiberoptisk", type=7, f=f, e=e, kat="g")

    # Mate-/fjernledning (n stk.)
    if i.matefjern_ledn:
        # Det kan henge én eller to mate-/fjernledn. i masten.
        n = i.matefjern_antall
        # Isolatorens egenvekt er 220 [N] for mate-/fjernledn.
        fx = n * sys.matefjernledning["Egenvekt"] * masteavstand + 220
        f = array([fx, 0, 0])
        e = array([i.hfj, 0, 0])
        matefjernledn = Last(navn="Matefjernledn", type=8, f=f, e=e, kat="g")

    # AT-ledninger (2 stk.)
    if i.at_ledn:
        f = array([2 * sys.at_ledning["Egenvekt"] * masteavstand, 0, 0])
        e = array([i.hfj, 0, 0])
        at_ledn = Last(navn="AT-ledn", type=9, f=f, e=e, kat="g")

    # Jordledning
    if i.jord_ledn:
        f = array([sys.jordledning["Egenvekt"] * masteavstand, 0, 0])
        e = array([i.hj, 0, 0])
        jordledn = Last(navn="Jordledning", type=10, f=f, e=e, kat="g")

        # Jordledninger henger i bakkant av mast dersom dette stemmer:
        if i.matefjern_ledn or i.at_ledn or i.forbigang_ledn:
            f = array([sys.jordledning["Egenvekt"] * masteavstand, 0, 0])
            e = array([i.hj, 0, -0.3])
            jordledn = Last(navn="Jordledning", type=10, f=f, e=e, kat="g")

    # Loddavspenning
    N_avsp = 0
    if i.fixavspenningsmast or i.avspenningsmast:
        utvekslingsforhold = 3
        if sys.navn == "35":
            utvekslingsforhold = 2
        # Strekk i kontakttraad + bæreline, omregnet til [N]
        N_avsp = 2 * 1000 * sys.kontakttraad["Strekk i ledning"] / utvekslingsforhold
    if i.fixavspenningsmast:
        f = array([N_avsp, 0, 0])
        e = array(0, 0, 0)
        loddavsp = Last(navn="Loddavspenning", type=3, f=f, e=e, kat="g")
    elif i.avspenningsmast:
        f = array([N_avsp, 0, 0])
        e = array(0, 0, 0)
        loddavsp = Last(navn="Loddavspenning", type=4, f=f, e=e, kat="g")

    return utligger, baereline, hengetraad, y_line, kontakttraad, fixpunkt,\
           fixavspenning, forbigangsledn, returledn, fiberoptisk, \
           matefjernledn, at_ledn, jordledn, loddavsp


