import numpy

"""Div. funksjoner for utskrift av resultater"""

def _tilpass(a, b):
    """Formaterer teksstrenger a, b og c med korrekt antall mellomrom
    mellom verdier for å sikre lett lesbarhet av bidrag.
    """
    abc = a
    for spaces in range(56-len(a)):
        abc += " "
    abc += b
    abc += "\n"

    return abc


def skriv_bidrag(i, mast):
    """Skriver bidrag fra dimensjonerende tilfelle for aktuell mast
    til tekstfilen bidrag.txt.
    """
    s = []  # String-liste

    # Normalkrefter (N)
    s.append(_tilpass("Normalkraft i bruddgrensetilstand", "N_max (kN)"))
    s.append("\n")
    n = i.linjemast_utliggere
    F = mast.bruddgrense.R[1][4] / 1000
    s.append(_tilpass(str(n) + " stk KL", "{:.2f}".format(F)))
    if i.fixpunktmast:
        F = mast.bruddgrense.R[2][4] / 1000
        s.append(_tilpass("Fixpunktmast", "{:.2f}".format(F)))
    elif i.fixavspenningsmast:
        F = mast.bruddgrense.R[3][4] / 1000
        s.append(_tilpass("Fixavspenningsmast", "{:.2f}".format(F)))
    elif i.avspenningsmast:
        F = mast.bruddgrense.R[4][4] / 1000
        s.append(_tilpass("Avspenningsmast", "{:.2f}".format(F)))
    else:
        s.append("\n")
    if i.matefjern_ledn:
        n = i.matefjern_antall
        F = mast.bruddgrense.R[8][4] / 1000
        s.append(_tilpass(str(n) + " stk mate-/fjernledninger", "{:.2f}".format(F)))
    else:
        s.append("\n")
    if i.at_ledn:
        F = mast.bruddgrense.R[9][4] / 1000
        s.append(_tilpass("2 stk AT-ledninger", "{:.2f}".format(F)))
    else:
        s.append("\n")
    if i.jord_ledn:
        F = mast.bruddgrense.R[10][4] / 1000
        s.append(_tilpass("1 stk jordledning", "{:.2f}".format(F)))
    else:
        s.append("\n")
    if i.forbigang_ledn:
        F = mast.bruddgrense.R[5][4] / 1000
        s.append(_tilpass("1 stk forbigangsledning", "{:.2f}".format(F)))
    elif i.fiberoptisk_ledn:
        F = mast.bruddgrense.R[7][4] / 1000
        s.append(_tilpass("1 stk fiberoptisk ledning", "{:.2f}".format(F)))
    else:
        s.append("\n")
    if i.retur_ledn:
        F = mast.bruddgrense.R[6][4] / 1000
        s.append(_tilpass("2 stk returledninger", "{:.2f}".format(F)))
    else:
        s.append("\n")
    F = mast.bruddgrense.R[0][4] / 1000
    s.append(_tilpass("Mast", "{:.2f}".format(F)))
    s.append("\n")
    F = numpy.sum(mast.bruddgrense.R[:11][4], axis=0) / 1000
    s.append(_tilpass("SUM", "{:.2f}".format(F)))
    s.append("\n\n\n")

    # Skjærkrefter (V_z)
    s.append(_tilpass("Skjærkraft i bruddgrensetilstand", "Vz_max (kN)"))
    s.append("\n")
    n = i.linjemast_utliggere
    F = mast.bruddgrense.R[1][3] / 1000
    s.append(_tilpass(str(n) + " stk KL", "{:.2f}".format(F)))
    if i.fixpunktmast:
        F = mast.bruddgrense.R[2][3] / 1000
        s.append(_tilpass("Fixpunktmast", "{:.2f}".format(F)))
    elif i.fixavspenningsmast:
        F = mast.bruddgrense.R[3][3] / 1000
        s.append(_tilpass("Fixavspenningsmast", "{:.2f}".format(F)))
    elif i.avspenningsmast:
        F = mast.bruddgrense.R[4][3] / 1000
        s.append(_tilpass("Avspenningsmast", "{:.2f}".format(F)))
    else:
        s.append("\n")
    if i.matefjern_ledn:
        n = i.matefjern_antall
        F = mast.bruddgrense.R[8][3] / 1000
        s.append(_tilpass(str(n) + " stk mate-/fjernledninger", "{:.2f}".format(F)))
    else:
        s.append("\n")
    if i.at_ledn:
        F = mast.bruddgrense.R[9][3] / 1000
        s.append(_tilpass("2 stk AT-ledninger", "{:.2f}".format(F)))
    else:
        s.append("\n")
    if i.jord_ledn:
        F = mast.bruddgrense.R[10][3] / 1000
        s.append(_tilpass("1 stk jordledning", "{:.2f}".format(F)))
    else:
        s.append("\n")
    if i.forbigang_ledn:
        F = mast.bruddgrense.R[5][3] / 1000
        s.append(_tilpass("1 stk forbigangsledning", "{:.2f}".format(F)))
    elif i.fiberoptisk_ledn:
        F = mast.bruddgrense.R[7][3] / 1000
        s.append(_tilpass("1 stk fiberoptisk ledning", "{:.2f}".format(F)))
    else:
        s.append("\n")
    if i.retur_ledn:
        F = mast.bruddgrense.R[6][3] / 1000
        s.append(_tilpass("2 stk returledninger", "{:.2f}".format(F)))
    else:
        s.append("\n")
    F = mast.bruddgrense.R[0][3] / 1000
    s.append(_tilpass("Mast", "{:.2f}".format(F)))
    s.append("\n")
    F = numpy.sum(mast.bruddgrense.R[:11][3], axis=0) / 1000
    s.append(_tilpass("SUM", "{:.2f}".format(F)))
    s.append("\n\n\n")

    # Momenter (M_y)
    s.append(_tilpass("Moment i bruddgrensetilstand", "My_max (kNm)"))
    s.append("\n")
    n = i.linjemast_utliggere
    F = mast.bruddgrense.R[1][0] / 1000
    s.append(_tilpass(str(n) + " stk KL", "{:.2f}".format(F)))
    if i.fixpunktmast:
        F = mast.bruddgrense.R[2][0] / 1000
        s.append(_tilpass("Fixpunktmast", "{:.2f}".format(F)))
    elif i.fixavspenningsmast:
        F = mast.bruddgrense.R[3][0] / 1000
        s.append(_tilpass("Fixavspenningsmast", "{:.2f}".format(F)))
    elif i.avspenningsmast:
        F = mast.bruddgrense.R[4][0] / 1000
        s.append(_tilpass("Avspenningsmast", "{:.2f}".format(F)))
    else:
        s.append("\n")
    if i.matefjern_ledn:
        n = i.matefjern_antall
        F = mast.bruddgrense.R[8][0] / 1000
        s.append(_tilpass(str(n) + " stk mate-/fjernledninger", "{:.2f}".format(F)))
    else:
        s.append("\n")
    if i.at_ledn:
        F = mast.bruddgrense.R[9][0] / 1000
        s.append(_tilpass("2 stk AT-ledninger", "{:.2f}".format(F)))
    else:
        s.append("\n")
    if i.jord_ledn:
        F = mast.bruddgrense.R[10][0] / 1000
        s.append(_tilpass("1 stk jordledning", "{:.2f}".format(F)))
    else:
        s.append("\n")
    if i.forbigang_ledn:
        F = mast.bruddgrense.R[5][0] / 1000
        s.append(_tilpass("1 stk forbigangsledning", "{:.2f}".format(F)))
    elif i.fiberoptisk_ledn:
        F = mast.bruddgrense.R[7][0] / 1000
        s.append(_tilpass("1 stk fiberoptisk ledning", "{:.2f}".format(F)))
    else:
        s.append("\n")
    if i.retur_ledn:
        F = mast.bruddgrense.R[6][0] / 1000
        s.append(_tilpass("2 stk returledninger", "{:.2f}".format(F)))
    else:
        s.append("\n")
    F = mast.bruddgrense.R[0][0] / 1000
    s.append(_tilpass("Mast", "{:.2f}".format(F)))
    s.append("\n")
    F = numpy.sum(mast.bruddgrense.R[:11][0], axis=0) / 1000
    s.append(_tilpass("SUM", "{:.2f}".format(F)))
    s.append("\n\n\n")

    # Torsjon (T)
    s.append(_tilpass("Torsjonsmoment i bruddgrensetilstand / ulykkestilstand", "T_max (kNm)"))
    s.append("\n")
    F = mast.bruddgrense.R[1][7] / 1000
    s.append(_tilpass("Fra KL", "{:.2f}".format(F)))
    F = numpy.sum(mast.bruddgrense.R[2:11][7], axis=0) / 1000
    s.append(_tilpass("Differansestrekk + vandringskrefter", "{:.2f}".format(F)))
    s.append("\n")
    F = numpy.sum(mast.bruddgrense.R[1:11][7], axis=0) / 1000
    s.append(_tilpass("SUM", "{:.2f}".format(F)))
    s.append("\n\n\n")


    tekst = "".join(s)  # Føyer sammen elementer i string-liste s

    with open("bidrag.txt", "w") as bidrag:
        bidrag.write(tekst)

