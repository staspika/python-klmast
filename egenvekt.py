import numpy

def beregn_deformasjon(mast, M, h, fh):
    """Beregner deformasjon D_z i høyde fh som følge av
    moment om y-aksen med angrepspunkt i høyde h.
    Dersom fh > h interpoleres forskyvningen til høyde fh
    ved hjelp av sinus til vinkelen theta i høyde h
    ganget med høydedifferansen fh - h.
    """
    M = M * 1000  # Konverterer til [Nmm]
    h = h * 1000  # Konverterer til [mm]
    fh = fh * 1000  # Konverterer til [mm]
    E = mast.E
    I_y = mast.Iy  #BØR IMPLEMENTERE IY LIKT FOR GITTERMASTER SOM BJELKEMASTER
    if fh > h:
        theta = (M * h) / (E * I_y)
        D_z = (M * h ** 2) / (2 * E * I_y) \
              + numpy.sin(theta) * ( fh - h )
    else:
        D_z = (M * fh ** 2) / (2 * E * I_y)
    return D_z

def beregn_ledninger(sys, i, mast, a_T):

    masteavstand = i.masteavstand
    sms = i.sms
    radius = i.radius
    fh = i.fh

    # Initierer variabler for kraft/momentsummasjon
    N = 0  # Normalkraft [N]
    M_y = 0  # Moment om sterk akse [Nm]
    D_z = 0  # Forskyvning normalt spor
    # Variabel M brukes kun for mellomlagring av M_y-verdier

    # Antall utliggere
    if i.siste_for_avspenning or i.avspenningsmast or i.linjemast_utliggere==2:
        utliggere = 2
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
        N += sys.utligger["Egenvekt"] * sms
        M = sys.utligger["Egenvekt"] * sys.utligger["Momentarm"] * sms ** 2
        M_y += M
        D_z += beregn_deformasjon(mast, M, h_utligger, fh)

        # Bæreline
        N += sys.baereline["Egenvekt"] * masteavstand
        M = sys.baereline["Egenvekt"] * masteavstand * a_T
        M_y += M
        D_z += beregn_deformasjon(mast, M, h_utligger, fh)

        # Hengetråd
        N += sys.hengetraad["Egenvekt"] * masteavstand
        M = sys.hengetraad["Egenvekt"] * masteavstand * a_T
        M_y += M
        D_z += beregn_deformasjon(mast, M, h_utligger, fh)

        # Kontakttråd
        N += sys.kontakttraad["Egenvekt"] * masteavstand
        M = sys.kontakttraad["Egenvekt"] * masteavstand * a_T
        M_y += M
        D_z += beregn_deformasjon(mast, M, h_utligger, fh)

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
            M = sys.y_line["Egenvekt"] * L * a_T
            M_y += M
            D_z += beregn_deformasjon(mast, M, h_utligger, fh)

    # Fixline
    if i.fixpunktmast or i.fixavspenningsmast:
        N += sys.fixline["Egenvekt"] * masteavstand / 2
        if i.fixpunktmast:
            # Eksentrisitet pga. montert på utligger
            N += sys.fixline["Egenvekt"] * masteavstand / 2
            M = sys.fixline["Egenvekt"] * masteavstand * a_T
            M_y += M
            h_utligger = fh + (i.sh / 2)  # Fixline montert på utligger
            D_z += beregn_deformasjon(mast, M, h_utligger, fh)

    # Forbigangsledning
    if i.forbigang_ledn:
        N += sys.forbigangsledning["Egenvekt"] * masteavstand
        N += 150  # Isolator for forbigangsledning
        if i.matefjern_ledn or i.at_ledn or i.jord_ledn:
            # Eksentrisitet pga montert på siden av mast
            arm = -0.3  # Momentarm 0.3m (retning fra spor)
            M_1 = sys.forbigangsledning["Egenvekt"] * masteavstand * arm
            M_2 = 150 * arm  # Moment fra isolator
            M_y += M_1 + M_2
            D_z += beregn_deformasjon(mast, M_1 + M_2, i.hf, fh)


    # Returledninger (2 stk.)
    if i.retur_ledn:
        N += 2 * sys.returledning["Egenvekt"] * masteavstand
        N += 2 * 100  # # Isolatorer (2 stk.) for returledninger
        arm = -0.5  # Momentarm 0.5m (retning fra spor)
        M_1 = 2 * sys.returledning["Egenvekt"] * masteavstand * arm
        M_2 = 2 * 100 * arm  # Moment fra isolator
        M_y += M_1 + M_2
        D_z += beregn_deformasjon(mast, M_1 + M_2, i.hr, fh)

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
            M = sys.jordledning["Egenvekt"] * masteavstand * arm
            M_y += M
            D_z += beregn_deformasjon(mast, M, i.hj, fh)


    # Fyller inn matrise med kraftbidrag
    R = numpy.zeros((15, 9))
    R[0][4] = N  # Kraftbidrag i [N]
    R[0][0] = M_y  # Momentbidrag i [Nm]
    R[0][8] = D_z  # FOrskyvningsbidrag i [mm]
    return R



def beregn_mast(mast, h):
    N = 0
    N += mast.egenvekt * h  # Egenlast mast
    # Fyller inn matrise med kraftbidrag
    R = numpy.zeros((15, 9))
    R[0][4] = N  # Kraftbidrag i [N]
    return R



