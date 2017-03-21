class System(object):
    """Parent class for alle systemteyper"""

    def __init__(self, navn, baereline, kontakttraad, fixline,
                 forbigangsledning, returledning, matefjernledning,
                 y_line, hengetraad, fiberoptisk,
                 at_ledning, jordledning, utligger):
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

    def __repr__(self):
        return "System {}".format(self.navn)


def hent_system(i):
    """Returnerer navngitt system"""
    navn = i.systemnavn


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

    # Forbigangsledninger
    Al_240_61 = {"Egenvekt": 6.7, "Diameter": 20.3,
                 "Tverrsnitt": 222.35, "Max tillatt spenning": 50.0}

    # Returledninger
    Al_240_61_iso = {"Egenvekt": 9.2, "Diameter": 25.0,
                     "Tverrsnitt": 242.54, "Max tillatt spenning": 50.0}

    # Mate-/fjernledninger
    SAHF_120_26_7 = {"Egenvekt": 7.77, "Diameter": 19.38,
                     "Tverrsnitt": 222.35, "Max tillatt spenning": 95.0}

    # Y-lineer
    Bz_II_35_7 = {"Egenvekt": 3.10, "Diameter": 7.5, "Tverrsnitt": 34.36}

    # Hengetråder
    Bz_II_10_49 = {"Egenvekt": 0.53, "Diameter": 4.5, "Tverrsnitt": 9.6}

    # Fiberoptiske kabler
    ADSS_GRHSLLDV_9_125 = {"Egenvekt": 2.6, "Diameter": 18.5,
                     "Tverrsnitt": 268.9, "Max tillatt spenning": 59.5}

    # AT-ledninger
    Al_400_37 = {"Navn": "Al_400_37", "Egenvekt": 10.31,
                         "Diameter": 25.34, "Tverrsnitt": 381.0,
                         "Max tillatt spenning": 50.0}
    Al_240_19 = {"Navn": "Al_240_19", "Egenvekt": 6.46,
                         "Diameter": 20.0, "Tverrsnitt": 238.76,
                         "Max tillatt spenning": 50.0}
    Al_150_19 = {"Navn": "Al_150_19", "Egenvekt": 4.07,
                         "Diameter": 15.9, "Tverrsnitt": 150.90,
                         "Max tillatt spenning": 50.0}
    BLX_T_241_19_iso = {"Navn": "BLX_T_241_19_iso", "Egenvekt": 8.13,
                         "Diameter": 26.10, "Tverrsnitt": 241.0,
                         "Max tillatt spenning": 80.0}
    BLX_T_209_9_19_iso = {"Name": "BLX_T_209_9_19_iso", "Egenvekt": 7.91,
                         "Diameter": 25.8, "Tverrsnitt": 209.0,
                         "Max tillatt spenning": 80.0}
    BLX_T_111_3_7_iso = {"Navn": "BLX_T_111_3_7_iso", "Egenvekt": 4.71,
                         "Diameter": 20.4, "Tverrsnitt": 111.0,
                         "Max tillatt spenning": 80.0}

    # Jordledninger
    KHF_70 = {"Navn": "KHF_70", "Egenvekt": 6.23,
                          "Diameter": 10.7, "Tverrsnitt": 70.0,
                          "Max tillatt spenning": 125.0}
    KHF_95 = {"Navn": "KHF_95", "Egenvekt": 8.44,
                          "Diameter": 12.6, "Tverrsnitt": 95.0,
                          "Max tillatt spenning": 125.0}

    # Setter AT-ledning
    if i.at_type == 0:
        at_ledning = Al_400_37
    elif i.at_type == 1:
        at_ledning = Al_240_19
    elif i.at_type == 2:
        at_ledning = Al_150_19
    elif i.at_type == 3:
        at_ledning = BLX_T_241_19_iso
    elif i.at_type == 4:
        at_ledning = BLX_T_209_9_19_iso
    elif i.at_type == 5:
        at_ledning = BLX_T_111_3_7_iso

    # Setter jordledning
    if i.jord_type == 0:
        jordledning = KHF_70
    elif i.jord_type == 1:
        jordledning = KHF_95

    # Utliggere (s2x for system 20A/20B/25, s3x for system 35)
    utligger_s2x = {"Egenvekt": 170, "Momentarm": 0.35}
    utligger_s3x = {"Egenvekt": 200, "Momentarm": 0.40}

    # Setter utligger
    if i.systemnavn=="35":
        utligger = utligger_s3x
    else:
        utligger = utligger_s2x


    if navn == "20a":
        return System(navn="20a", baereline=Bz_II_50_19, kontakttraad=Ri_100_Cu,
                      fixline=Bz_II_50_19, forbigangsledning=Al_240_61,
                      returledning=Al_240_61_iso, matefjernledning=SAHF_120_26_7,
                      y_line=Bz_II_35_7, hengetraad=Bz_II_10_49,
                      fiberoptisk=ADSS_GRHSLLDV_9_125, at_ledning=at_ledning,
                      jordledning=jordledning, utligger=utligger)
    elif navn == "20b":
        return System(navn="20b", baereline=Bz_II_50_19, kontakttraad=Ri_100_Cu,
                      fixline=Bz_II_50_19, forbigangsledning=Al_240_61,
                      returledning=Al_240_61_iso, matefjernledning=SAHF_120_26_7,
                      y_line=None, hengetraad=Bz_II_10_49,
                      fiberoptisk=ADSS_GRHSLLDV_9_125, at_ledning=at_ledning,
                      jordledning=jordledning, utligger=utligger)
    elif navn == "25":
        return System(navn="25", baereline=Bz_II_70_19, kontakttraad=Ri_120_CuAg,
                     fixline=Bz_II_70_19_fix, forbigangsledning=Al_240_61,
                     returledning=Al_240_61_iso, matefjernledning=SAHF_120_26_7,
                     y_line=Bz_II_35_7, hengetraad=Bz_II_10_49,
                     fiberoptisk = ADSS_GRHSLLDV_9_125, at_ledning=at_ledning,
                     jordledning=jordledning, utligger=utligger)
    elif navn == "35":
        return System(navn="35", baereline=Cu_50_7, kontakttraad=Ri_100_Cu_s35,
                     fixline=Bz_II_50_19, forbigangsledning=Al_240_61,
                     returledning=Al_240_61_iso, matefjernledning=SAHF_120_26_7,
                     y_line=Bz_II_35_7, hengetraad=Bz_II_10_49,
                     fiberoptisk = ADSS_GRHSLLDV_9_125, at_ledning=at_ledning,
                     jordledning=jordledning, utligger=utligger)










