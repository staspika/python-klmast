import numpy
import matplotlib.pyplot as plt

"""Div. funksjoner for sortering og utskrift av resultater"""

def _tilpass(a, b):
    """Formaterer teksstrenger a, b og c med korrekt antall mellomrom
    mellom verdier for å sikre lett lesbarhet av bidrag.
    """

    abc = a
    for spaces in range(57-len(a)):
        abc += " "
    abc += b
    abc += "\n"

    return abc

def sorter_resultater(master):
    g = 0  # Index for anbefalt gittermast
    b = 0  # Index for anbefalt bjelkemast
    t = 0  # Teller for å loppe gjennom master
    mast = master[t]
    sf = 1
    while (mast.type == "H" or mast.type == "B") \
            and t < len(master):
        mast = master[t]
        if (1 - mast.bruddgrense.utnyttelsesgrad > 0) \
            and (1 - mast.bruddgrense.utnyttelsesgrad < sf):
            sf = 1 - mast.bruddgrense.utnyttelsesgrad
            g = t
        t += 1
    sf = 1
    while mast.type == "bjelke" and t < len(master):
        mast = master[t]
        if (1 - mast.bruddgrense.utnyttelsesgrad > 0) \
                and (1 - mast.bruddgrense.utnyttelsesgrad < sf):
            sf = 1 - mast.bruddgrense.utnyttelsesgrad
            b = t
        t += 1
    return g, b

def barplot(values):
    teller = 0
    for current_values in values:
        plt.figure(teller)
        colors = []
        for v in current_values:
            if v > 1.0:
                colors.append("r")
            elif v > 0.8:
                colors.append("y")
            else:
                colors.append("g")
        N = numpy.arange(4)
        plt.bar(N, current_values, color=colors)
        plt.title("Utnyttelsesgrad")
        plt.xticks(N + 0.5, ("UR", "My", "Mz", "N"))
        plt.yticks(numpy.arange(0, max(current_values) + 0.1, 0.1))
        teller += 1
    plt.show(True)


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
    F = mast.bruddgrense.R[1][5] / 1000
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

