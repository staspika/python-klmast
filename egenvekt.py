import numpy
import deformasjon


def beregn_egenvekt(sys, i, mast, a_T):
    """Beregner bidrag grunnet egenvekt av ledninger,
    isolatorer, utliggere og eventuell travers.
    """

    masteavstand = i.masteavstand
    sms = i.sms
    fh = i.fh

    R = numpy.zeros((15, 9))

    # Initierer variabler for kontaktledninger
    N_kl, M_y_kl, D_z_kl = 0, 0, 0  # [N], [Nm], [mm]

    # Variabel M/M_1/M_2 brukes kun for mellomlagring av M_y-verdier

    R[0][4] = mast.egenvekt * mast.h  # [N] Egenlast, mast

    # Antall utliggere
    if i.siste_for_avspenning or i.avspenningsmast or i.linjemast_utliggere==2:
        utliggere = 2
        R[0][4] += 220  # Vekt av travers
    else:
        utliggere = 1

    for utligger in range(utliggere):

        """Setter vertikal momentarm til kontakttrådhøyde
        + halvparten av systemhøyden, et konservativt estimat for
        angrepshøyden til det horisontalte kraftparet
        i utliggerens innspenning grunnet gravitasjonlast.
        """
        h_utligger = fh + (i.sh/2)

        # Utliggere
        R[0][4] += sys.utligger["Egenvekt"] * sms
        M = sys.utligger["Egenvekt"] * sys.utligger["Momentarm"] * sms ** 2
        R[0][0] += M
        R[0][8] += deformasjon._beregn_deformasjon_M(mast, M, h_utligger, fh)

        # Bæreline
        N_kl += sys.baereline["Egenvekt"] * masteavstand
        M = sys.baereline["Egenvekt"] * masteavstand * a_T
        M_y_kl += M
        D_z_kl += deformasjon._beregn_deformasjon_M(mast, M, h_utligger, fh)

        # Hengetråd
        N_kl += sys.hengetraad["Egenvekt"] * masteavstand
        M = sys.hengetraad["Egenvekt"] * masteavstand * a_T
        M_y_kl += M
        D_z_kl += deformasjon._beregn_deformasjon_M(mast, M, h_utligger, fh)

        # Kontakttråd
        N_kl += sys.kontakttraad["Egenvekt"] * masteavstand
        M = sys.kontakttraad["Egenvekt"] * masteavstand * a_T
        M_y_kl += M
        D_z_kl += deformasjon._beregn_deformasjon_M(mast, M, h_utligger, fh)

        # Y-line
        if not sys.y_line == None:  # Sjekker at systemet har Y-line
            # L = lengde Y-line
            L = 0
            if (sys.navn == "20a" or sys.navn == "35") and i.radius >= 800:
                L = 14
            elif sys.navn == "25" and i.radius >= 1200:
                L = 18
            N_kl += sys.y_line["Egenvekt"] * L
            M = sys.y_line["Egenvekt"] * L * a_T
            M_y_kl += M
            D_z_kl += deformasjon._beregn_deformasjon_M(mast, M, h_utligger, fh)

    # Fixpunktmast
    if i.fixpunktmast:
        R[2][4] = sys.fixline["Egenvekt"] * masteavstand
        M = sys.fixline["Egenvekt"] * masteavstand * a_T
        R[2][0] = M
        h_utligger = fh + (i.sh / 2)  # Fixline montert på utligger
        R[2][8] = deformasjon._beregn_deformasjon_M(mast, M, h_utligger, fh)

    # Fixavspenningsmast
    if i.fixavspenningsmast:
        R[3][4] += sys.fixline["Egenvekt"] * masteavstand / 2

    # Forbigangsledning
    if i.forbigang_ledn:
        R[5][4] = sys.forbigangsledning["Egenvekt"] * masteavstand
        R[5][4] += 150  # Isolator for forbigangsledning
        if i.matefjern_ledn or i.at_ledn or i.jord_ledn:
            # Eksentrisitet pga montert på siden av mast
            arm = -0.3  # Momentarm 0.3m (retning fra spor)
            M_1 = sys.forbigangsledning["Egenvekt"] * masteavstand * arm
            M_2 = 150 * arm  # Moment fra isolator
            R[5][0] = M_1 + M_2
            R[5][8] = deformasjon._beregn_deformasjon_M(mast, M_1 + M_2, i.hf, fh)


    # Returledninger (2 stk.)
    if i.retur_ledn:
        R[6][4] = 2 * sys.returledning["Egenvekt"] * masteavstand
        R[6][4] += 2 * 100  # # Isolatorer (2 stk.) for returledninger
        arm = -0.5  # Momentarm 0.5m (retning fra spor)
        M_1 = 2 * sys.returledning["Egenvekt"] * masteavstand * arm
        M_2 = 2 * 100 * arm  # Moment fra isolator
        R[6][0] = M_1 + M_2
        R[6][8] = deformasjon._beregn_deformasjon_M(mast, M_1 + M_2, i.hr, fh)

    # Mate-/fjernledning (n stk.)
    if i.matefjern_ledn:
        n = i.matefjern_antall
        R[8][4] = n * sys.matefjernledning["Egenvekt"] * masteavstand
        R[8][4] += 220  # Travers/isolator for mate-/fjern

    # Fiberoptisk
    if i.fiberoptisk_ledn:
        R[7][4] = sys.fiberoptisk["Egenvekt"] * masteavstand

    # AT-ledninger (2 stk.)
    if i.at_ledn:
        R[9][4] = 2 * sys.at_ledning["Egenvekt"] * masteavstand

    # Jordledning
    if i.jord_ledn:
        R[10][4] = sys.jordledning["Egenvekt"] * masteavstand
        if i.matefjern_ledn or i.at_ledn or i.forbigang_ledn:
            arm = -0.3  # Momentarm 0.3m (retning fra spor)
            M = sys.jordledning["Egenvekt"] * masteavstand * arm
            R[10][0] = M
            R[10][8] = deformasjon._beregn_deformasjon_M(mast, M, i.hj, fh)

    N_avsp = 0
    # Vekt av avspenningslodd
    if i.fixavspenningsmast or i.avspenningsmast:
        utvekslingsforhold = 3
        if sys.navn == "35":
            utvekslingsforhold = 2
        # Strekk i kontakttraad + bæreline, omregnet til [N]
        N_avsp = 2 * 1000 * sys.kontakttraad["Strekk i ledning"] / utvekslingsforhold
    if i.fixavspenningsmast:
        R[3][4] = N_avsp
    elif i.avspenningsmast:
        R[4][4] = N_avsp


    # Fyller inn matrise med kraftbidrag
    # HER MÅ DET SORTERES IHHT BIDRAG I KL FUND / bidrag.txt !
    R[1][0] = M_y_kl
    R[1][4] = N_kl
    R[1][8] = D_z_kl

    return R




