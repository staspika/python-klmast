class Mast(object):
    """Parent class for alle masteyper"""

    # Klassevariabler er like for alle master
    E = 210000  # N/mm^2
    G = 80000  # N/mm^2

    def __init__(self, navn, type, egenvekt=0, Asteg=0, Iy=0, Iz=0, Wyp=0,
                 Wzp=0, It=0, Cw=0, topp=0, stign=0, d_h=0, d_b=0,
                 k_g=0, k_d=0, Aref=0, Aref_par=0, Iy_mast=0, Iz_mast=0,
                 max_hoyde=0):
        """Oppretter nytt masteobjekt"""
        self.navn = navn  # Mastens navn
        self.type = type  # Støttede mastetyper: B, S, Bjelke
        self.egenvekt = egenvekt  # Egenvekt [N/m]
        self.Asteg = Asteg  # Profilets areal [mm]

        # Aref_par, Iz og Wzp trenger ikke oppgis dersom overflødige
        # Settes lik hhv. Aref, Iy og Wyp dersom ikke oppgitt i argument
        self.Aref = Aref  # Eff. areal for vind [m^2/m], par=parallelt spor
        if Aref_par == 0:
            self.Aref_par = Aref
        else:
            self.Aref_par = Aref_par

        self.Iy = Iy  # Andre arealmoment om profilets sterke akse [mm^4]
        if Iz == 0:
            self.Iz = Iy
        else:
            self.Iz = Iz

        self.Wyp = Wyp  # Plastisk tverrsnittsmodul om profilets sterke akse [mm^3]
        if Wzp == 0:
            self.Wzp = Wyp
        else:
            self.Wzp = Wzp

        self.It = It  # St. Venants torsjonskonstant [mm^4]
        self.Cw = Cw  # Hvelvingskonstant [mm^6]
        self.d_h = d_h  # Diagonalhøyde [mm]
        self.d_b = d_b  # Diagonalbredde [mm]
        self.topp = topp  # Toppmål mast [mm]
        self.stign = stign   # Mastens stigning (promille)
        self.k_g = k_g  # Knekklengdefaktor gurt
        self.k_d = k_d  # Knekklengdefaktordiagonal
        self.Iy_mast = Iy_mast  # For hele tverrsnittet, sterk akse [mm^4]
        self.Iz_mast = Iz_mast  # For hele tverrsnittet, svak akse [mm^4]

        # Unntak for mast H6 (?)
        if type == "H6":
            self.d_treghetsmoment = 9.44*10**4
            self.d_areal = 691

        # Beregner totalt tverrsnittsareal A [mm^2]
        if type == "B":
            self.A = 2 * Asteg
        elif type == "H":
            self.A = 4 * Asteg
        elif type == "bjelke":
            self.A = Asteg

        self.max_hoyde = max_hoyde

        self.h = max_hoyde
        if not self.type == "bjelke":
            self.b = self.topp + self.stign * self.h
            self.b_13 = self.topp + (2 / 3) * self.stign * self.h
            if self.type == "H":
                self.d = self.b
            elif self.type == "B":
                if self.navn == "B2":
                    self.d = 120
                elif self.navn == "B3":
                    self.d = 140
                elif self.navn == "B4":
                    self.d = 160
                elif self.navn == "B6":
                    self.d = 200

    def __repr__(self):
        """Funksjon for enkel utskrift av attributer via print()"""
        rep = "{}\nMastetype: {}\n".format(self.navn, self.type)
        rep += "Egenvekt: {} N/m    ".format(self.egenvekt)
        rep += "Asteg = {:.2e} mm^2\n".format(self.Asteg)
        rep += "Iy = {:.2e} mm^4    ".format(self.Iy)
        rep += "Iz = {:.2e} mm^4\n".format(self.Iz)
        rep += "Wyp = {:.2e} mm^3   ".format(self.Wyp)
        rep += "Wzp = {:.2e} mm^3\n".format(self.Wzp)
        rep += "It = {:.2e} mm^4    ".format(self.It)
        rep += "Cw = {:.2e} mm^6\n".format(self.Cw)
        rep += "Aref = {} m^2/m    ".format(self.Aref)
        rep += "Aref_par = {} m^2/m\n".format(self.Aref_par)
        if not self.type=="bjelke":
            rep += "topp = {} mm    ".format(self.topp)
            rep += "stign = {} mm/mm\n".format(self.stign)
            rep += "d_h = {} mm    ".format(self.d_h)
            rep += "d_b = {} mm\n".format(self.d_b)
            if self.type=="S":
                rep += "k_g = {}     ".format(self.k_g)
                rep += "k_d = {}\n".format(self.k_d)
            elif self.type=="B":
                rep += "Iy_mast = {:.2e} mm^4     ".format(self.Iy_mast)
                rep += "Iz_mast = {:.2e} mm^4\n".format(self.Iz_mast)
        return rep


def hent_master():
    """Returnerer list med samtlige master"""
    master = []

    # B-master (tverrsnittsklasse 3)
    B2 = Mast(navn="B2", type="B", egenvekt=360, Asteg=1.70*10**3, Aref=0.12,
              Iy=3.64*10**6, Iz=4.32*10**5, Wyp=7.46*10**4, It=4.15*10**4,
              topp=150, stign=14/1000, d_h=50, d_b=10,
              Iy_mast=9.72*10**7, Iz_mast=7.28*10**6, max_hoyde=8.0)
    B3 = Mast(navn="B3", type="B", egenvekt=510, Asteg=2.04*10**3, Aref=0.14,
              Iy=6.05*10**6, Iz=6.27*10**5, Wyp=1.05*10**5, It=5.68*10**4,
              topp=255, stign=23/1000, d_h=50, d_b=10,
              Iy_mast=3.22*10**8, Iz_mast=1.21*10**7, max_hoyde=9.5)
    B4 = Mast(navn="B4", type="B", egenvekt=560, Asteg=2.40*10**3, Aref=0.16,
              Iy=9.25*10**6, Iz=8.53*10**5, Wyp=1.38*10**5, It=7.39*10**4,
              topp=255, stign=23/1000, d_h=50, d_b=10,
              Iy_mast=3.79*10**8, Iz_mast=1.85*10**7, max_hoyde=11.0)
    B6 = Mast(navn="B6", type="B", egenvekt=700, Asteg=3.22*10**3, Aref=0.20,
              Iy=1.91*10**7, Iz=1.48*10**6, Wyp=2.28*10**5, It=1.19*10**5,
              topp=255, stign=23/1000, d_h=50, d_b=10,
              Iy_mast=5.09*10**8, Iz_mast=3.82*10**7, max_hoyde=13.0)
    master.extend([B2, B3, B4, B6])

    # S-master (tverrsnittsklasse 3)
    H3 = Mast(navn="H3", type="S", egenvekt=520, Asteg=1.15*10**3, Aref=0.20,
              Iy=5.89*10**5, topp=200, stign=20/1000, d_h=50, d_b=10,
              k_g=0.85, k_d=0.55, max_hoyde=13.0)
    H5 = Mast(navn="H5", type="S", egenvekt=620, Asteg=1.41*10**3, Aref=0.20,
              Iy=5.89*10**5, topp=200, stign=20/1000, d_h=50, d_b=10,
              k_g=0.85, k_d=0.55, max_hoyde=13.0)
    H6 = Mast(navn="H6", type="S", egenvekt=620, Asteg=1.41*10**3, Aref=0.20,
              Iy=5.89*10**5, topp=200, stign=20/1000, d_h=50, d_b=10,
              k_g=0.85, k_d=0.55)
    master.extend([H3, H5, H6])

    # Bjelkemaster (tverrsnittsklasse 1)
    IPE400 = Mast(navn="IPE400", type="bjelke", egenvekt=663, Asteg=8.45*10**3,
                  Aref=0.18, Iy=2.31 * 10 ** 8, Iz=1.32 * 10 ** 7, Wyp=1.31 * 10 ** 6,
                  Wzp=2.19*10**5, It=5.14*10**5, Cw=4.90*10**11, Aref_par=0.40)
    HE200B = Mast(navn="HE200B", type="bjelke", egenvekt=613, Asteg=7.81*10**3,
                  Aref=0.20, Iy=5.70 * 10 ** 7, Iz=2.00 * 10 ** 7, Wyp=6.42 * 10 ** 5,
                  Wzp=3.00*10**5, It=5.95*10**5, Cw=1.71*10**11, max_hoyde=9.5)
    HE220B = Mast(navn="HE220B", type="bjelke", egenvekt=715, Asteg=9.10*10**3,
                  Aref=0.22, Iy=8.09 * 10 ** 7, Iz=2.84 * 10 ** 7, Wyp=8.28 * 10 ** 5,
                  Wzp=3.87*10**5, It=7.68*10**5, Cw=2.95*10**11, max_hoyde=11.0)
    HE240B = Mast(navn="HE240B", type="bjelke", egenvekt=832, Asteg=1.06*10**4,
                  Aref=0.24, Iy=1.13 * 10 ** 8, Iz=3.92 * 10 ** 7, Wyp=1.05 * 10 ** 6,
                  Wzp=4.90*10**5, It=1.03*10**6, Cw=4.87*10**11, max_hoyde=12.0)
    HE260B = Mast(navn="HE260B", type="bjelke", egenvekt=930, Asteg=1.18*10**4,
                  Aref=0.26, Iy=1.49 * 10 ** 8, Iz=5.13 * 10 ** 7, Wyp=1.28 * 10 ** 6,
                  Wzp=5.92*10**5, It=1.24*10**6, Cw=7.54*10**11, max_hoyde=13.0)
    HE280B = Mast(navn="HE280B", type="bjelke", egenvekt=1030, Asteg=1.31*10**4,
                  Aref=0.28, Iy=1.93 * 10 ** 8, Iz=6.59 * 10 ** 7, Wyp=1.53 * 10 ** 6,
                  Wzp=7.06*10**5, It=1.44*10**6, Cw=1.13*10**12, max_hoyde=13.0)
    HE260M = Mast(navn="HE260M", type="bjelke", egenvekt=1720, Asteg=2.20*10**4,
                  Aref=0.268, Iy=3.13 * 10 ** 8, Iz=2.00 * 10 ** 8, Wyp=2.52 * 10 ** 6,
                  Wzp=1.17*10**6, It=7.22*10**6, Cw=1.73*10**12, Aref_par=0.29, max_hoyde=13.0)
    master.extend([IPE400, HE200B, HE220B, HE240B, HE260B, HE280B, HE260M])

    return master

def sett_hoyde(h):
    """Setter mastehøyde h og beregner høydeavhengige attributer"""
    self.h = h
    if not self.type == "bjelke":
        self.b = self.topp + self.stign * self.h
        self.b_13 = self.topp + (2 / 3) * self.stign * self.h
        if self.type == "H":
            self.d = self.b
        elif self.type == "B":
            if self.navn == "B2":
                self.d = 120
            elif self.navn == "B3":
                self.d = 140
            elif self.navn == "B4":
                self.d = 160
            elif self.navn == "B6":
                self.d = 200


def lagre_resultater(resultater):
    """Lagrer resultater av utregninger for aktuell mast"""
    self.resultater = resultater












