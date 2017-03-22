import numpy

def _beregn_deformasjon(mast, M, x, fh):
    """Beregner deformasjon D_z i høyde fh som følge av
    moment om y-aksen med angrepspunkt i høyde x.
    Dersom fh > x interpoleres forskyvningen til høyde fh
    ved hjelp av tangens til vinkelen theta i høyde x
    ganget med høydedifferansen fh - x.
    """
    E = mast.E
    Iy = mast.Iy(mast.h)
    M = M * 1000  # Konverterer til [Nmm]
    x = x * 1000  # Konverterer til [mm]
    fh = fh * 1000  # Konverterer til [mm]
    if fh > x:
        theta = (M * x) / (E * Iy)
        D_z = (M * x ** 2) / (2 * E * Iy) \
              + numpy.tan(theta) * (fh - x)
    else:
        D_z = (M * fh ** 2) / (2 * E * Iy)
    return D_z

def beregn_ledninger(sys, i, mast, a_T):
    """Beregner bidrag grunnet egenvekt av ledninger,
    isolatorer, utliggere og eventuell travers.
    """

    masteavstand = i.masteavstand
    sms = i.sms
    fh = i.fh

    # Initierer variabler for kraft/momentsummasjon
    N = 0  # Normalkraft [N]
    M_y = 0  # Moment om sterk akse [Nm]
    M_z = 0  # Moment om svak akse [Nm]
    D_z = 0  # Forskyvning normalt spor
    # Variabel M/M_1/M_2 brukes kun for mellomlagring av M_y-verdier

    # Antall utliggere
    if i.siste_for_avspenning or i.avspenningsmast or i.linjemast_utliggere==2:
        utliggere = 2
        N += 220  # Vekt av travers
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
        N_kl += sys.utligger["Egenvekt"] * sms
        M = sys.utligger["Egenvekt"] * sys.utligger["Momentarm"] * sms ** 2
        M_y_kl += M
        D_z_kl += _beregn_deformasjon(mast, M, h_utligger, fh)

        # Bæreline
        N_kl += sys.baereline["Egenvekt"] * masteavstand
        M = sys.baereline["Egenvekt"] * masteavstand * a_T
        M_y_kl += M
        D_z_kl += _beregn_deformasjon(mast, M, h_utligger, fh)

        # Hengetråd
        N_kl += sys.hengetraad["Egenvekt"] * masteavstand
        M = sys.hengetraad["Egenvekt"] * masteavstand * a_T
        M_y_kl += M
        D_z_kl += _beregn_deformasjon(mast, M, h_utligger, fh)

        # Kontakttråd
        N_kl += sys.kontakttraad["Egenvekt"] * masteavstand
        M = sys.kontakttraad["Egenvekt"] * masteavstand * a_T
        M_y_kl += M
        D_z_kl += _beregn_deformasjon(mast, M, h_utligger, fh)

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
            D_z_kl += _beregn_deformasjon(mast, M, h_utligger, fh)

    # Fixline
    if i.fixpunktmast or i.fixavspenningsmast:
        N += sys.fixline["Egenvekt"] * masteavstand / 2
        if i.fixpunktmast:
            # Eksentrisitet pga. montert på utligger
            N += sys.fixline["Egenvekt"] * masteavstand / 2
            M = sys.fixline["Egenvekt"] * masteavstand * a_T
            M_y += M
            h_utligger = fh + (i.sh / 2)  # Fixline montert på utligger
            D_z += _beregn_deformasjon(mast, M, h_utligger, fh)

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
            D_z += _beregn_deformasjon(mast, M_1 + M_2, i.hf, fh)


    # Returledninger (2 stk.)
    if i.retur_ledn:
        N += 2 * sys.returledning["Egenvekt"] * masteavstand
        N += 2 * 100  # # Isolatorer (2 stk.) for returledninger
        arm = -0.5  # Momentarm 0.5m (retning fra spor)
        M_1 = 2 * sys.returledning["Egenvekt"] * masteavstand * arm
        M_2 = 2 * 100 * arm  # Moment fra isolator
        M_y += M_1 + M_2
        D_z += _beregn_deformasjon(mast, M_1 + M_2, i.hr, fh)

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
            D_z += _beregn_deformasjon(mast, M, i.hj, fh)

    N_avsp = 0
    # Vekt av avspenningslodd
    if i.fixavspenningsmast or i.avspenningsmast:
        utvekslingsforhold = 3
        if sys.navn == "35":
            utvekslingsforhold = 2
        # Strekk i kontakttraad + bæreline, omregnet til [N]
        N_avsp = 2 * 1000 * sys.kontakttraad["Strekk i ledning"] / utvekslingsforhold



    # Fyller inn matrise med kraftbidrag
    R = numpy.zeros((15, 9))
    # HER MÅ DET SORTERES IHHT BIDRAG I KL FUND / bidrag.txt !
    R[0][0] = M_y
    R[0][2] = M_z
    R[0][4] = N
    R[0][8] = D_z
    R[1][0] = M_y_kl
    R[1][4] = N_kl
    R[1][8] = D_z_kl

    if i.fixavspenningsmast:
        R[3][4] = N
    elif i.avspenningsmast:
        R[4][4] = N
    return R



def beregn_mast(mast):
    """Beregner mastens egenvekt [N] ved fundament."""
    N = mast.egenvekt * mast.h  # Egenlast mast
    R = numpy.zeros((15, 9))
    R[0][4] = N
    return R



