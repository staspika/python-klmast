import geometri

class System(object):
    """Parent class for alle systemteyper"""

    def __init__(self, navn, baereline, kontakttraad, fixline,
                 forbigangsledning, returledning, matefjernledning,
                 y_line, hengetraad, fiberoptisk, at_ledning,
                 jordledning, utligger, radius, sms, fh):
        """Initierer objekt med dictionaries som inngangsparametre"""
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
        self.B1, self.B2, self.e_max = geometri.beregn_sikksakk(self, radius)
        self.a_T, self.a_T_dot = geometri.beregn_arm(radius, sms, fh, self.B1)


    def __repr__(self):
        return "System {}".format(self.navn)


def hent_system(i):
    """Returnerer navngitt system"""

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
    # Ri/RiS 120 CuAG
    Ri_120_CuAg = {"Egenvekt": 10.7, "Diameter": 13.2,
                   "Tverrsnitt": 120.0, "Strekk i ledning": 15.0}
    # 7.1 kN strekk i System 35
    Ri_100_Cu_s35 = {"Egenvekt": 8.9, "Diameter": 12.0,
                     "Tverrsnitt": 100.0, "Strekk i ledning": 7.1}

    # Y-liner
    Bz_II_35_7 = {"Egenvekt": 3.10, "Diameter": 7.5, "Tverrsnitt": 34.36}

    # Hengetråder
    Bz_II_10_49 = {"Egenvekt": 0.53, "Diameter": 4.5, "Tverrsnitt": 9.6}


    # Forbigangsledninger
    Al_240_61 = {"Egenvekt": 6.7, "Diameter": 20.3,
                 "Tverrsnitt": 222.35, "Max tillatt spenning": 50.0,
                 "Strekk 5C": _strekkraft(2.48, 2.78, a),
                 "Strekk -40C": _strekkraft(10.22, 5.21, a)}

    # Returledninger
    Al_240_61_iso = {"Egenvekt": 9.2, "Diameter": 25.0,
                     "Tverrsnitt": 242.54, "Max tillatt spenning": 50.0,
                     "Strekk 5C": _strekkraft(2.95, 3.28, a),
                     "Strekk -40C": _strekkraft(10.74, 5.87, a)}

    # Mate-/fjernledninger
    SAHF_120_26_7 = {"Egenvekt": 7.77, "Diameter": 19.38,
                     "Tverrsnitt": 222.35, "Max tillatt spenning": 95.0,
                     "Strekk 5C": _strekkraft(2.77, 3.06, a),
                     "Strekk -40C": _strekkraft(10.70, 4.73, a)}

    # Fiberoptiske kabler
    ADSS_GRHSLLDV_9_125 = {"Egenvekt": 2.6, "Diameter": 18.5,
                     "Tverrsnitt": 268.9, "Max tillatt spenning": 59.5}

    # AT-ledninger
    at_ledninger = []
    Al_400_37 = {"Navn": "Al 400-37 uisolert", "Egenvekt": 10.31,
                         "Diameter": 25.34, "Tverrsnitt": 381.0,
                         "Max tillatt spenning": 50.0}
    Al_240_19 = {"Navn": "Al 240-19 uisolert", "Egenvekt": 6.46,
                         "Diameter": 20.0, "Tverrsnitt": 238.76,
                         "Max tillatt spenning": 50.0}
    Al_150_19 = {"Navn": "Al 150-19 uisolert", "Egenvekt": 4.07,
                         "Diameter": 15.9, "Tverrsnitt": 150.90,
                         "Max tillatt spenning": 50.0}
    at_ledninger.extend([Al_400_37, Al_240_19, Al_150_19])

    # Jordledninger
    jordledninger = []
    KHF_70 = {"Navn": "KHF-70", "Egenvekt": 6.23,
                          "Diameter": 10.7, "Tverrsnitt": 70.0,
                          "Max tillatt spenning": 125.0}
    KHF_95 = {"Navn": "KHF-95", "Egenvekt": 8.44,
                          "Diameter": 12.6, "Tverrsnitt": 95.0,
                          "Max tillatt spenning": 125.0}
    jordledninger.extend([KHF_70, KHF_95])

    # Utliggere (s2x for system 20A/20B/25, s3x for system 35)
    utligger_s2x = {"Egenvekt": 170, "Momentarm": 0.35}
    utligger_s3x = {"Egenvekt": 200, "Momentarm": 0.40}

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

    # Setter utligger
    utligger = utligger_s2x
    if i.systemnavn=="35":
        utligger = utligger_s3x


    if i.systemnavn == "20a":
        return System(navn="20a", baereline=Bz_II_50_19, kontakttraad=Ri_100_Cu,
                      fixline=Bz_II_50_19, forbigangsledning=Al_240_61,
                      returledning=Al_240_61_iso, matefjernledning=SAHF_120_26_7,
                      y_line=Bz_II_35_7, hengetraad=Bz_II_10_49,
                      fiberoptisk=ADSS_GRHSLLDV_9_125, at_ledning=at_ledning,
                      jordledning=jordledning, utligger=utligger,
                      radius=i.radius, sms=i.sms, fh=i.fh)
    elif i.systemnavn == "20b":
        return System(navn="20b", baereline=Bz_II_50_19, kontakttraad=Ri_100_Cu,
                      fixline=Bz_II_50_19, forbigangsledning=Al_240_61,
                      returledning=Al_240_61_iso, matefjernledning=SAHF_120_26_7,
                      y_line=None, hengetraad=Bz_II_10_49,
                      fiberoptisk=ADSS_GRHSLLDV_9_125, at_ledning=at_ledning,
                      jordledning=jordledning, utligger=utligger,
                      radius=i.radius, sms=i.sms, fh=i.fh)
    elif i.systemnavn == "25":
        return System(navn="25", baereline=Bz_II_70_19, kontakttraad=Ri_120_CuAg,
                     fixline=Bz_II_70_19_fix, forbigangsledning=Al_240_61,
                     returledning=Al_240_61_iso, matefjernledning=SAHF_120_26_7,
                     y_line=Bz_II_35_7, hengetraad=Bz_II_10_49,
                     fiberoptisk = ADSS_GRHSLLDV_9_125, at_ledning=at_ledning,
                     jordledning=jordledning, utligger=utligger,
                      radius=i.radius, sms=i.sms, fh=i.fh)
    elif i.systemnavn == "35":
        return System(navn="35", baereline=Cu_50_7, kontakttraad=Ri_100_Cu_s35,
                     fixline=Bz_II_50_19, forbigangsledning=Al_240_61,
                     returledning=Al_240_61_iso, matefjernledning=SAHF_120_26_7,
                     y_line=Bz_II_35_7, hengetraad=Bz_II_10_49,
                     fiberoptisk = ADSS_GRHSLLDV_9_125, at_ledning=at_ledning,
                     jordledning=jordledning, utligger=utligger,
                      radius=i.radius, sms=i.sms, fh=i.fh)

def _strekkraft(a, b, masteavstand):
    """
    Beregner strekkraft i [N] mhp. masteavstand.
    
    :param a: Strekk ved 30m masteavstand [kN]
    :param b: Strekk ved 70m masteavstand [kN]
    :param masteavstand: Faktisk masteavstand [m]
    :return: Strekkraft ved faktisk masteavstand [N]
    """

    s = 1000 * (a + (masteavstand-30) * (b - a)/40)
    return s












