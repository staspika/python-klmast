from kraft import *


def beregn_egenvekt(sys, i, mast, a_T, a_T_dot):
    """Beregner bidrag grunnet egenvekt av ledninger,
    isolatorer, utliggere og eventuell travers.
    """

    a = (i.a1 + i.a2) / 2
    a1 = i.a1
    a2 = i.a2
    sms = i.sms
    fh = i.fh
    sh = i.sh

    # Eksentrisitet i z-retning for KL.
    arm = a_T_dot
    if i.strekkutligger:
        arm = a_T

    # F = liste over krefter som skal returneres
    F = []

    # Mastens egenvekt [N]
    F.append(Kraft(navn="Egenvekt: Mast", type=0,
                   f=[mast.egenvekt * mast.h, 0, 0]))

    # Antall utliggere
    utliggere = 1
    if i.siste_for_avspenning or i.linjemast_utliggere == 2:
        utliggere = 2
        F.append(Kraft(navn="Egenvekt: Travers", type=0,
                       f=[220, 0, 0]))

    for utligger in range(utliggere):

        """Setter vertikal momentarm til kontakttrådhøyde
        + halvparten av systemhøyden, et konservativt estimat for
        angrepshøyden til det horisontalte kraftparet
        i utliggerens innspenning grunnet gravitasjonlast.
        """

        # Utligger
        F.append(Kraft(navn="Egenvekt: Utligger", type=0,
                       f=[sys.utligger["Egenvekt"] * sms, 0, 0],
                       e=[-fh - sh/2, 0, sys.utligger["Momentarm"] * sms]))

        """Kontaktledning (type=1) er et paraplybegrep som innebærer
        bæreline, hengetråd, y-line og kontakttråd.
        """

        # Bæreline
        F.append(Kraft(navn="Egenvekt: Bæreline", type=1,
                       f=[sys.baereline["Egenvekt"] * a, 0, 0],
                       e=[-fh - sh, 0, sms]))

        # Hengetråd
        L_henge = 8 * (a / 60)
        F.append(Kraft(navn="Egenvekt: Hengetråd", type=1,
                       f=[sys.hengetraad["Egenvekt"] * L_henge, 0, 0],
                       e=[-fh - sh, 0, arm]))

        # Kontakttråd
        F.append(Kraft(navn="Egenvekt: Kontakttråd", type=1,
                       f=[sys.kontakttraad["Egenvekt"] * a, 0, 0],
                       e=[-fh, 0, arm]))

        # Y-line
        if not sys.y_line == None:  # Sjekker at systemet har Y-line
            # L = lengde Y-line
            L = 0
            if (sys.navn == "20a" or sys.navn == "35") and i.radius >= 800:
                L = 14
            elif sys.navn == "25" and i.radius >= 1200:
                L = 18
            F.append(Kraft(navn="Egenvekt: Y-line", type=1,
                           f=[sys.y_line["Egenvekt"] * L, 0, 0],
                           e=[-fh - sh, 0, arm]))

    # Fixpunktmast
    if i.fixpunktmast:
        F.append(Kraft(navn="Egenvekt: Fixpunkt", type=2,
                       f=[sys.fixline["Egenvekt"] * a, 0, 0],
                       e=[-fh - sh, 0, sms]))

    # Fixavspenningsmast
    if i.fixavspenningsmast:
        F.append(Kraft(navn="Egenvekt: fixavspenningsmast", type=3,
                       f=[sys.fixline["Egenvekt"] * a2 / 2, 0, 0],
                       e=[-fh - sh, 0, 0]))

    # Forbigangsledning
    if i.forbigang_ledn:
        # Isolatorens egenvekt er 150 [N] for forbigangsledning
        F.append(Kraft(navn="Egenvekt: Forbigangsledning", type=5,
                       f=[sys.forbigangsledning["Egenvekt"] * a + 150, 0, 0],
                       e=[-i.hf, 0, 0]))
        # Forbigangsledn henger i bakkant av mast dersom dette stemmer:
        if i.matefjern_ledn or i.at_ledn or i.jord_ledn:
            F.append(Kraft(navn="Egenvekt: Forbigangsledning", type=5,
                           f=[sys.forbigangsledning["Egenvekt"] * a + 150, 0, 0],
                           e=[-i.hf, 0, -0.3]))

    # Returledninger (2 stk.)
    if i.retur_ledn:
        # Isolatorens egenvekt er 150 [N] pr returledning
        F.append(Kraft(navn="Egenvekt: Returledning", type=6,
                       f=[2 * (sys.returledning["Egenvekt"] * a + 150), 0, 0],
                       e=[-i.hr, 0, -0.5]))

    # Fiberoptisk
    if i.fiberoptisk_ledn:
        F.append(Kraft(navn="Egenvekt: Fiberoptisk", type=7,
                       f=[sys.fiberoptisk["Egenvekt"] * a, 0, 0],
                       e=[-i.fh, 0, -0.3]))

    # Mate-/fjernledning (n stk.)
    if i.matefjern_ledn:
        n = i.matefjern_antall
        # Isolatorens egenvekt er 220 [N] for mate-/fjernledn.
        F.append(Kraft(navn="Egenvekt: Mate-/fjernledning", type=8,
                       f=[n * sys.matefjernledning["Egenvekt"] * a + 220, 0, 0],
                       e=[-i.hfj, 0, 0]))

    # AT-ledninger (2 stk.)
    if i.at_ledn:
        F.append(Kraft(navn="Egenvekt: AT-ledning", type=9,
                       f=[2 * sys.at_ledning["Egenvekt"] * a, 0, 0],
                       e=[-i.hfj, 0, 0]))

    # Jordledning
    if i.jord_ledn:
        F.append(Kraft(navn="Jordledning", type=10,
                       f=[sys.jordledning["Egenvekt"] * a, 0, 0],
                       e=[-i.hj, 0, 0]))
        # Jordledninger henger i bakkant av mast dersom dette stemmer:
        if i.matefjern_ledn or i.at_ledn or i.forbigang_ledn:
            F.append(Kraft(navn="Egenvekt: Jordledning", type=10,
                           f=[sys.jordledning["Egenvekt"] * a, 0, 0],
                           e=[-i.hj, 0, -0.3]))

    # Loddavspenning
    N_avsp = 0
    if i.fixavspenningsmast or i.avspenningsmast:
        utvekslingsforhold = 3
        if sys.navn == "35":
            utvekslingsforhold = 2
        # Strekk i kontakttraad + bæreline, omregnet til [N]
        N_avsp = 2 * 1000 * sys.kontakttraad["Strekk i ledning"] / utvekslingsforhold
    if i.fixavspenningsmast:
        F.append(Kraft(navn="Egenvekt: Loddavspenning", type=0,
                       f=[N_avsp, 0, 0]))
    elif i.avspenningsmast:
        F.append(Kraft(navn="Egenvekt: Loddavspenning", type=0,
                       f=[N_avsp, 0, 0]))

    # Bidrag til normalkraft dersom ulik høyde mellom nabomaster:
    N = i.delta_h1 / a1 + i.delta_h2 / a2

    return F
