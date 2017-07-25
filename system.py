# -*- coding: utf8 -*-
from __future__ import unicode_literals
import geometri
import klima

class System(object):
    """Klasse for å representere alle valg av system."""

    def __init__(self, navn, baereline, kontakttraad, fixline,
                 forbigangsledning, returledning, matefjernledning,
                 y_line, hengetraad, fiberoptisk, at_ledning,
                 jordledning, utligger, radius, sms, fh):
        """Initialiserer :class:`System`-objekt.

        :param str navn: Systemets navn (20A, 20B, 25, 35)
        :param dict baereline: Systemets bæreline
        :param dict kontakttraad: Systemets kontakttråd
        :param dict fixline: Systemets fixline
        :param dict forbigangsledning: Systemets forbigangsledning
        :param dict returledning: Systemets returledning
        :param dict matefjernledning: Systemets mate-/fjernledning
        :param dict y_line: Systemets y-line
        :param dict hengetraad: Systemets hengetråd
        :param dict fiberoptisk: Systemets fiberoptiske kabel
        :param dict at_ledning: Systemets AT-ledning
        :param dict jordledning: Systemets jordledning
        :param dict utligger: Systemets utligger
        :param int radius: Sporkurvaturens radius :math:`[m]`
        :param float sms: Avstand senter mast - senter spor :math:`[m]`
        :param float fh: Kontakttrådhøyde :math:`[m]`
        """

        self.navn = navn
        self.baereline = baereline
        self.kontakttraad = kontakttraad
        self.fixline = fixline
        self.forbigangsledning = forbigangsledning
        self.returledning = returledning
        self.matefjernledning = matefjernledning
        self.y_line = y_line
        self.hengetraad = hengetraad
        self.fiberoptisk = fiberoptisk
        self.at_ledning = at_ledning
        self.jordledning = jordledning
        self.utligger = utligger
        self.B1, self.B2, self.e_max = geometri.beregn_sikksakk(self.navn, radius)
        self.a_T, self.a_T_dot = geometri.beregn_arm(radius, sms, fh, self.B1)


    def __repr__(self):
        return "System {}".format(self.navn)


def hent_system(i):
    """Henter :class:`System` med data for ledninger og utliggere.

    Ledningenes strekkraft ved snøfri line og :math:`T = -40^{\\circ}C`
    samt strekk ved snøbelastet line og :math:`T = -25^{\\circ}C` beregnes
    ved hjelp av Newton-Raphson-iterasjon ut fra tabulerte verdier for
    kabelstrekk ved :math:`T = 5^{\\circ}C`.

    :param Inndata i: Input fra bruker
    :return: Systemkonfigurasjon
    :rtype: :class:`System`
    """

    a = (i.a1 + i.a2)/2

    # Bære/fixliner
    Bz_II_50_19 = {"Egenvekt": 4.37, "Diameter": 9.0,
                   "Tverrsnitt": 48.35, "Strekk i ledning": 10.0}
    Bz_II_70_19 = {"Egenvekt": 5.96, "Diameter": 10.5,
                   "Tverrsnitt": 65.81, "Strekk i ledning": 15.0}
    # Bz II 70/19 skal ha 10kN strekk ved bruk som fix
    Bz_II_70_19_fix = {"Egenvekt": 5.96, "Diameter": 10.5,
                       "Tverrsnitt": 65.81, "Strekk i ledning": 10.0}
    Cu_50_7 = {"Egenvekt": 4.46, "Diameter": 9.0,
               "Tverrsnitt": 49.48, "Strekk i ledning": 7.1}

    # Kontakttråder
    Ri_100_Cu = {"Egenvekt": 8.9, "Diameter": 12.0,
                 "Tverrsnitt": 100.0, "Strekk i ledning": 10.0}
    Ri_120_CuAg = {"Egenvekt": 10.7, "Diameter": 13.2,
                   "Tverrsnitt": 120.0, "Strekk i ledning": 15.0}
    Ri_100_Cu_s35 = {"Egenvekt": 8.9, "Diameter": 12.0,
                     "Tverrsnitt": 100.0, "Strekk i ledning": 7.1}

    # Y-liner
    Bz_II_35_7 = {"Egenvekt": 3.10, "Diameter": 7.5, "Tverrsnitt": 34.36}

    # Hengetråder
    Bz_II_10_49 = {"Egenvekt": 0.53, "Diameter": 4.5, "Tverrsnitt": 9.6}


    # Forbigangsledninger
    Al_240_61 = {"Navn": "Al 240-61", "Egenvekt": 6.43,
                 "Diameter": 20.3, "Tverrsnitt": 242.54,
                 "E-modul": 56000, "Max tillatt spenning": 50.0,
                 "Lengdeutvidelseskoeffisient": 2.3*10**(-5),
                 "Strekk 5C": _strekkraft(2.48, 2.78, a)}

    # Returledninger
    Al_240_61_iso = {"Navn": "Al 240-61 isolert", "Egenvekt": 7.63,
                     "Diameter": 23.9, "Tverrsnitt": 242.54,
                     "E-modul": 56000, "Max tillatt spenning": 50.0,
                     "Lengdeutvidelseskoeffisient": 2.3 * 10 ** (-5),
                     "Strekk 5C": _strekkraft(2.95, 3.28, a)}

    # Mate-/fjernledninger
    SAHF_120_26_7 = {"Navn": "SAHF 120 Feral", "Egenvekt": 7.56,
                     "Diameter": 19.38, "Tverrsnitt": 222.35,
                     "E-modul": 76000, "Max tillatt spenning": 95.0,
                     "Lengdeutvidelseskoeffisient": 1.9 * 10 ** (-5),
                     "Strekk 5C": _strekkraft(2.77, 3.06, a)}

    # Fiberoptiske kabler
    # Det antas en oppspenningskraft på 3kN og ingen temperaturutvidelse av
    # fiberoptisk kabel da denne er metallfri.
    ADSS_GRHSLLDV_9_125 = {"Navn": "ADSS GRHSLLDV 9/125",
                           "Egenvekt": 2.6, "Diameter": 18.5,
                           "Tverrsnitt": 268.9, "Max tillatt spenning": 59.5,
                           "Strekk 5C": 3.0, "Strekk -40C": 3.0,
                           "Strekk med snø -25C": 9.0}

    # AT-ledninger
    # Ved manglende strekktabeller for Al 400-37 og 240-19 er verdier for
    # Al 400-61 og 240-61 benyttet. Strekkverdier for Al 150-19 ekstrapoleres
    # ut fra arealforholdet mellom denne og Al 400-37 (ca. 40%).
    at_ledninger = []
    Al_400_37 = {"Navn": "Al 400-37", "Egenvekt": 10.31,
                 "Diameter": 25.34, "Tverrsnitt": 381.0,
                 "E-modul": 56000, "Max tillatt spenning": 50.0,
                 "Lengdeutvidelseskoeffisient": 2.3 * 10 ** (-5),
                 "Strekk 5C": _strekkraft(4.09, 4.59, a)}
    Al_240_19 = {"Navn": "Al 240-19", "Egenvekt": 6.46,
                 "Diameter": 20.0, "Tverrsnitt": 238.76,
                 "E-modul": 56000, "Max tillatt spenning": 50.0,
                 "Lengdeutvidelseskoeffisient": 2.3 * 10 ** (-5),
                 "Strekk 5C": _strekkraft(2.48, 2.78, a)}
    Al_150_19 = {"Navn": "Al 150-19", "Egenvekt": 4.07,
                 "Diameter": 15.9, "Tverrsnitt": 150.90,
                 "E-modul": 56000, "Max tillatt spenning": 50.0,
                 "Lengdeutvidelseskoeffisient": 2.3 * 10 ** (-5),
                 "Strekk 5C": _strekkraft(0.4*4.09, 0.4*4.59, a)}
    at_ledninger.extend([Al_400_37, Al_240_19, Al_150_19])

    # Jordledninger
    jordledninger = []
    KHF_70 = {"Navn": "KHF-70", "Egenvekt": 5.81,
              "Diameter": 10.5, "Tverrsnitt": 66.75,
              "E-modul": 116000, "Max tillatt spenning": 125.0,
              "Lengdeutvidelseskoeffisient": 1.7 * 10 ** (-5),
              "Strekk 5C": _strekkraft(2.09, 2.25, a)}
    KHF_95 = {"Navn": "KHF-95", "Egenvekt": 8.25,
              "Diameter": 12.5, "Tverrsnitt": 94.7,
              "E-modul": 116000, "Max tillatt spenning": 125.0,
              "Lengdeutvidelseskoeffisient": 1.7 * 10 ** (-5),
              "Strekk 5C": _strekkraft(2.97, 3.20, a)}
    jordledninger.extend([KHF_70, KHF_95])

    # Utliggere (s2x for system 20A/20B/25, s3x for system 35)
    utligger_s2x = {"Egenvekt": 170, "Momentarm": 0.35}
    utligger_s3x = {"Egenvekt": 200, "Momentarm": 0.40}


    # Beregner ledningsstrekk vha. lekevektsbetraktning med Newton-Raphson-iterasjoner
    # Fiberoptisk kabel inkluderes IKKE grunnet manglende E-modul og lengdeutvidelseskoeffisient
    ledninger = [Al_240_61, Al_240_61_iso, SAHF_120_26_7]
    ledninger.extend(at_ledninger)
    ledninger.extend(jordledninger)

    for ledning in ledninger:
        H_0 = ledning["Strekk 5C"]
        E = ledning["E-modul"]
        A = ledning["Tverrsnitt"]
        G_0 = ledning["Egenvekt"]
        G_sno = klima._g_sno(i.ec3, i.isklasse, ledning["Diameter"])
        L = a
        alpha = ledning["Lengdeutvidelseskoeffisient"]

        # Beregner strekk ved snøfri kabel og -40C
        ledning["Strekk -40C"], iter_40, list_40 = _newtonraphson(H_0, E, A, G_0, G_0, L, alpha, -40)
        # Beregner strekk ved snøbelastet kabel og -25C
        ledning["Strekk med snø -25C"], iter_sno_25, list_sno_25 = _newtonraphson(H_0, E, A, G_0, G_0+G_sno, L, alpha, -25)

        # Beregner differansestrekk ved -40C
        s_1, s_11, s_111 = _newtonraphson(H_0, E, A, G_0, G_0, i.a1, alpha, -40)
        s_2, s_22, s_222 = _newtonraphson(H_0, E, A, G_0, G_0, i.a2, alpha, -40)
        ledning["Differansestrekk"] = abs(s_1-s_2)

        """
        print()
        print("Ledning: {}".format(ledning["Navn"]))
        print("Differansestrekk: {} kN".format(ledning["Differansestrekk"]))
        print("Initiell strekkraft: {} kN".format(ledning["Strekk 5C"]))
        print("-40C, fri line: H_x = {:.3g} kN    Antall iterasjoner: {}".format(ledning["Strekk -40C"] / 1000, iter_40))
        print("-25C, inkl snølast: H_x = {:.3g} kN    Antall iterasjoner: {}".format(ledning["Strekk med snø -25C"] / 1000, iter_sno_25))
        okning = ledning["Strekk med snø -25C"]-ledning["Strekk 5C"]
        print("Økning fra snølast: {} kN    = {} %".format(okning, okning/ledning["Strekk 5C"]*100))

        plt.plot([x for x in range(iter_40+1)], list_40, "b", [x for x in range(iter_sno_25+1)], list_sno_25, "y--",)
        plt.show(True)
        """

    # Antatt verdi for diff.strekk i fiberoptisk kabel
    SAHF_120_26_7["Differansestrekk"] = Al_240_61["Differansestrekk"]

    at_ledning = None
    # Setter AT-ledning
    for ledning in at_ledninger:
        if ledning["Navn"] == i.at_type:
            at_ledning = ledning
            break

    jordledning = None
    # Setter jordledning
    for ledning in jordledninger:
        if ledning["Navn"] == i.jord_type:
            jordledning = ledning
            break

    systemnavn = i.systemnavn.split()[1] if i.systemnavn.startswith("System") else i.systemnavn

    # Setter utligger
    utligger = utligger_s2x
    if systemnavn=="35":
        utligger = utligger_s3x

    if systemnavn == "20A":
        return System(navn="20A", baereline=Bz_II_50_19, kontakttraad=Ri_100_Cu,
                      fixline=Bz_II_50_19, forbigangsledning=Al_240_61,
                      returledning=Al_240_61_iso, matefjernledning=SAHF_120_26_7,
                      y_line=Bz_II_35_7, hengetraad=Bz_II_10_49,
                      fiberoptisk=ADSS_GRHSLLDV_9_125, at_ledning=at_ledning,
                      jordledning=jordledning, utligger=utligger,
                      radius=i.radius, sms=i.sms, fh=i.fh)
    elif systemnavn == "20B":
        return System(navn="20B", baereline=Bz_II_50_19, kontakttraad=Ri_100_Cu,
                      fixline=Bz_II_50_19, forbigangsledning=Al_240_61,
                      returledning=Al_240_61_iso, matefjernledning=SAHF_120_26_7,
                      y_line=None, hengetraad=Bz_II_10_49,
                      fiberoptisk=ADSS_GRHSLLDV_9_125, at_ledning=at_ledning,
                      jordledning=jordledning, utligger=utligger,
                      radius=i.radius, sms=i.sms, fh=i.fh)
    elif systemnavn == "25":
        return System(navn="25", baereline=Bz_II_70_19, kontakttraad=Ri_120_CuAg,
                     fixline=Bz_II_70_19_fix, forbigangsledning=Al_240_61,
                     returledning=Al_240_61_iso, matefjernledning=SAHF_120_26_7,
                     y_line=Bz_II_35_7, hengetraad=Bz_II_10_49,
                     fiberoptisk = ADSS_GRHSLLDV_9_125, at_ledning=at_ledning,
                     jordledning=jordledning, utligger=utligger,
                      radius=i.radius, sms=i.sms, fh=i.fh)
    elif systemnavn == "35":
        return System(navn="35", baereline=Cu_50_7, kontakttraad=Ri_100_Cu_s35,
                     fixline=Bz_II_50_19, forbigangsledning=Al_240_61,
                     returledning=Al_240_61_iso, matefjernledning=SAHF_120_26_7,
                     y_line=Bz_II_35_7, hengetraad=Bz_II_10_49,
                     fiberoptisk = ADSS_GRHSLLDV_9_125, at_ledning=at_ledning,
                     jordledning=jordledning, utligger=utligger,
                      radius=i.radius, sms=i.sms, fh=i.fh)

def _strekkraft(a, b, masteavstand):
    """Beregner strekkraft i fastavspent ledning mhp. masteavstand.

    Strekkraften beregnes ut fra lineærinterpolering mellom
    tabulerte verdier for strekkrefter ``a`` og ``b``

    :param float a: Strekk ved 30m masteavstand :math:`[kN]`
    :param float b: Strekk ved 70m masteavstand :math:`[kN]`
    :param float masteavstand: Faktisk masteavstand :math:`[m]`
    :return: Strekkraft ved faktisk masteavstand :math:`[N]`
    :rtype: :class:`float`
    """

    s = 1000 * (a + (masteavstand-30) * (b - a)/40)

    return s



def _newtonraphson(H_0, E, A, G_0, G_x, L, alpha, T):
    """Numerisk løsning av kabelstrekk i fastavspente ledninger.

    Følgende likevektsligning ligger til grunn for beregningene:

    :math:`H_x^2 [H_x - H_0 + \\frac{EA(G_0 L)^2}{24H_0^2} + EA\\alpha \\Delta_T]
    = \\frac{EA(G_x L)^2}{24}`

    Løsningen finnes ved hjelp av Newton-Raphson-iterasjoner
    for en residualfunksjon utledet fra likevekstligningen
    til en fastavspent kabel.
    Løsning returneres dersom feilkriteriet ``e`` er innenfor
    valgt grense eller antall iterasjoner overgår 1000.

    :param float H_0: Initiell spennkraft i kabel :math:`[N]`
    :param float E: Kabelens E-modul :math:`[\\frac{N}{mm^2}]`
    :param float A: Kabelens tverrsnittsareal :math:`[mm^2]`
    :param float G_0: Kabelens egenvekt :math:`[\\frac{N}{m}]`
    :param float G_x: Kabelens egenvekt + eventuell snølast :math:`[\\frac{N}{m}]`
    :param float L: Masteavstand :math:`[m]`
    :param float alpha: Lengdeutvidelseskoeffisient :math:`[\\frac{1}{^{\\circ}C}]`
    :param float T: Lufttemperatur :math:`[^{\\circ}C]`
    :return: Endelig kabelstrekk ``H_x`` :math:`[N]`, antall iterasjoner ``iterasjoner``,
     kabelstrekk ved hver iterasjon ``H_list`` :math:`[N]`
    :rtype: :class:`float`, :class:`int`, :class:`list`
    """

    # Konstanter
    delta_T = T - 5
    a = E*A*(G_x*L)**2/24
    b = - H_0 + E*A*(G_0*L)**2/(24*H_0**2) + E*A*alpha*delta_T

    # Initialverdier
    iterasjoner = 0
    H_x = H_0
    H_list = []
    delta_H_x = 0

    while iterasjoner<1000:
        H_x -= delta_H_x
        H_list.append(H_x)
        r = a - H_x**3 - b*H_x**2
        e = abs(r/a)

        if e < 10**(-2):
            return (H_x, iterasjoner, H_list)

        r_d = - 3*H_x**2 - 2*b*H_x
        delta_H_x = r/r_d

        iterasjoner += 1

    return(H_x, iterasjoner, H_list)














