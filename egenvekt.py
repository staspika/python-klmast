import numpy

def beregn_ledninger(sys, i, a_T):

    masteavstand = i.masteavstand
    sms = i.sms
    radius = i.radius

    # Initierer variabler for kraft/momentsummasjon
    N = 0  # Normalkraft [N]
    M_y = 0  # Moment om sterk akse [Nm]

    # Antall utliggere
    if i.siste_for_avspenning or i.avspenningsmast or i.linjemast_utliggere==2:
        utliggere = 2
    else:
        utliggere = 1

    for utligger in range(utliggere):

        # Utliggere
        N += sys.utligger["Egenvekt"] * sms
        M_y += sys.utligger["Egenvekt"] * sys.utligger["Momentarm"] * sms ** 2

        # Bæreline
        N += sys.baereline["Egenvekt"] * masteavstand
        M_y += sys.baereline["Egenvekt"] * masteavstand * a_T

        # Hengetråd
        N += sys.hengetraad["Egenvekt"] * masteavstand
        M_y += sys.hengetraad["Egenvekt"] * masteavstand * a_T

        # Kontakttråd
        N += sys.kontakttraad["Egenvekt"] * masteavstand
        M_y += sys.kontakttraad["Egenvekt"] * masteavstand * a_T

        # Y-line
        if not sys.y_line == None:  # Sjekker at systemet har Y-line
            # L = lengde Y-line
            if (sys.navn == "20a" or sys.navn == "35") and radius >= 800:
                L = 14
            elif sys.navn == "25" and radius >= 1200:
                L = 18
            else:
                L = 0  # HAR VI DA INGEN Y-LINE? sjekk hjelpedokument s. 27-29
            N += sys.y_line["Egenvekt"] * L
            M_y += sys.y_line["Egenvekt"] * L * a_T

    # Fixline
    if i.fixpunktmast or i.fixavspenningsmast:
        N += sys.fixline["Egenvekt"] * masteavstand
        if i.fixpunktmast:  # Momentbidrag pga. montert på utligger
            M_y += sys.fixline["Egenvekt"] * masteavstand * a_T

    # Forbigangsledning
    if i.forbigang_ledn:
        N += sys.forbigangsledning["Egenvekt"] * masteavstand
        N += 150  # Isolator for forbigangsledning
        if i.matefjern_ledn or i.at_ledn or i.jord_ledn:
            arm = -0.3  # Momentarm 0.3m (retning fra spor)
            M_y += sys.forbigangsledning["Egenvekt"] * masteavstand * arm
            M_y += 150 * arm  # Moment fra isolator

    # Returledninger (2 stk.)
    if i.retur_ledn:
        N += 2 * sys.returledning["Egenvekt"] * masteavstand
        arm = -0.5  # Momentarm 0.5m (retning fra spor)
        M_y += 2 * sys.returledning["Egenvekt"] * masteavstand * arm
        N += 2 * 100  # # Isolatorer (2 stk.) for returledninger
        M_y += 2 * 100 * arm  # Moment fra isolator

    # Mate-/fjernledning (n stk.)
    if i.matefjern_ledn:
        n = i.matefjern_antall
        N += n * sys.matefjernledning["Egenvekt"] * masteavstand
        N += 220  # Travers/isolator for mate-/fjern

    # Fiberoptisk
    if i.fiberoptisk_ledn:
        N += sys.fiberoptisk["Egenvekt"] * masteavstand

    # AT-ledninger (2 stk.)
    if i.at_ledn:
        N += 2 * sys.at_ledning["Egenvekt"] * masteavstand

    # Jordledning
    if i.jord_ledn:
        N += sys.jordledning["Egenvekt"] * masteavstand
        if i.matefjern_ledn or i.at_ledn or i.forbigang_ledn:
            arm = -0.3  # Momentarm 0.3m (retning fra spor)
            M_y += sys.jordledning["Egenvekt"] * masteavstand * arm


    # Fyller inn matrise med kraftbidrag
    R = numpy.zeros((15, 9))
    R[0][4] = N  # Kraftbidrag i [N]
    R[0][0] = M_y  # Momentbidrag i [Nm]
    return R



def beregn_mast(mast, h):
    N = 0
    N += mast.egenvekt * h  # Egenlast mast
    # Fyller inn matrise med kraftbidrag
    R = numpy.zeros((15, 9))
    R[0][4] = N  # Kraftbidrag i [N]
    return R



