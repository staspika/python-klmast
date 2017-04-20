class Mast(object):
    """Parent class for alle masteyper"""

    # Klassevariabler er like for alle master
    E = 210000  # N/mm^2
    G = 80000  # N/mm^2

    def __init__(self, navn, type, egenvekt=0, A_profil=0, Iy_profil=0,
                 Iz_profil=0, Wyp=0, Wzp=0, It=0, Cw=0, noytralakse=0,
                 toppmaal=0, stigning=0, d_h=0, d_b=0,
                 k_g=0, k_d=0, A_ref=0, A_ref_par=0, h_max=0, h=0,
                 s235=False, materialkoeff=1.05):
        """Oppretter nytt masteobjekt"""
        self.navn = navn  # Mastens navn
        self.type = type  # Støttede mastetyper: B, H, bjelke
        self.egenvekt = egenvekt  # Egenvekt [N/m]
        self.A_profil = A_profil  # Profilets areal [mm]

        # A_ref_par, Iz_profil og Wzp trenger ikke oppgis dersom overflødige
        # Settes lik hhv. A_ref, Iy_profil og Wyp dersom ikke oppgitt i argument
        self.A_ref = A_ref  # Eff. areal for vind [m^2/m], par=parallelt spor
        if A_ref_par == 0:
            self.A_ref_par = A_ref
        else:
            self.A_ref_par = A_ref_par

        self.Iy_profil = Iy_profil  # Andre arealmoment om profilets sterke akse [mm^4]
        if Iz_profil == 0:
            self.Iz_profil = Iy_profil
        else:
            self.Iz_profil = Iz_profil

        self.Wyp = Wyp  # Plastisk tverrsnittsmodul om profilets sterke akse [mm^3]
        if Wzp == 0:
            self.Wzp = Wyp
        else:
            self.Wzp = Wzp

        self.It = It  # St. Venants torsjonskonstant [mm^4]
        self.Cw = Cw  # Hvelvingskonstant [mm^6]
        self.noytralakse = noytralakse  # Avstand ytterkant profil til n.a.
        self.d_h = d_h  # Diagonalhøyde [mm]
        self.d_b = d_b  # Diagonalbredde [mm]
        self.toppmaal = toppmaal  # Toppmål mast [mm]
        self.stigning = stigning   # Mastens stigning (promille)
        self.k_g = k_g  # Knekklengdefaktor gurt
        self.k_d = k_d  # Knekklengdefaktor diagonal

        # Areal og treghetsmoment oppgis framfor diagonaldimensjoner for H6
        if navn == "H6":
            self.d_A = 691
            self.d_I = 9.44*10**4
        else:
            self.d_A = d_b * d_h
            self.d_I = d_b * d_h**3 / 12

        # Beregner totalt tverrsnittsareal A [mm^2]
        if type == "B":
            self.A = 2 * A_profil
        elif type == "H":
            self.A = 4 * A_profil
        elif type == "bjelke":
            self.A = A_profil

        self.h_max= h_max

        # Setter mastehøyde h samt hødeavhengige attributter
        self.h = h
        if not self.type == "bjelke":
            self.b = self.bredde(self.h)
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
        else:
            if self.navn == "HE200B":
                self.b = 200
                self.d = self.b
            elif self.navn == "HE220B":
                self.b = 220
                self.d = self.b
            elif self.navn == "HE240B":
                self.b = 240
                self.d = self.b
            elif self.navn == "HE260B":
                self.b = 260
                self.d = self.b
            elif self.navn == "HE280B":
                self.b = 280
                self.d = self.b
            elif self.navn == "HE260M":
                self.b = 290
                self.d = 268

        self.materialkoeff = materialkoeff

        # Setter stålkvalitet
        self.fy = 355
        if s235:
            self.fy = 235


        self.Wy_el = self.Iy(h) / (self.bredde(h) / 2)
        self.Wz_el = self.Iz(h) / (self.d / 2)

        # Variabler for å holde dimensjonerende last/forskvningstilfeller
        self.bruddgrense = None
        self.forskyvning_kl = None
        self.forskyvning_tot = None

        self.F = []

    def __repr__(self):
        Iy = self.Iy(self.h)/10**8
        Iz = self.Iz(self.h)/10**6
        Wy = self.Wy_el/10**3
        Wz = self.Wz_el/10**3
        rep = "{}\nMastetype: {}    Høyde: {}m\n".format(self.navn, self.type, self.h)
        rep += "Iy: {:.3g}*10^8mm^4    Iz: {:.3g}*10^6mm^4\n" \
              "Wy_el = {:.3g}*10^3mm^3  Wz_el = {:.3g}*10^3mm^3\n".format(Iy, Iz, Wz, Wy)
        rep += "Tverrsnittsbredde ved innspenning: {}mm\n".format(self.bredde(self.h))
        return rep

    def bredde(self, x):
        """Beregner tverrsnittsbredde b [mm]
        i avstand x [m] fra mastens toppunkt.
        Stigningen multipliseres med 2 da
        masten skråner til begge sider.
        """
        if not self.type == "bjelke":
            return self.toppmaal + 2 * self.stigning * x * 1000
        return self.b

    def Iy(self, x):
        """Beregner annet arealmoment om sterk akse
        i avstand x fra mastens toppunkt [mm^4]
        """
        if self.type == "B":
            z = self.bredde(x)/2 - self.noytralakse
            Iy = 2 * (self.Iy_profil + self.A_profil * z**2)
        if self.type == "H":
            z = self.bredde(x)/2 - self.noytralakse
            Iy = 4 * (self.Iy_profil + self.A_profil * z**2)
        elif self.type == "bjelke":
            Iy = self.Iy_profil
        return Iy

    def Iz(self, x):
        """Beregner annet arealmoment om svak akse
        i avstand x fra mastens toppunkt [mm^4]
        """
        if self.type == "B":
            Iz = 2 * self.Iz_profil
        if self.type == "H":
            y = self.bredde(x)/2 - self.noytralakse
            Iz = 4 * (self.Iz_profil + self.A_profil * y**2)
        elif self.type == "bjelke":
            Iz = self.Iz_profil
        return Iz

    def _sammenlign_tilstander(self, t1, t2):
        """Sjekker om t1 er dimensjonerende framfor t2.
        Dersom t2 ikke har fått noen verdi enda, returneres True
        slik at t1 blir satt som dimensjonerende tilfelle.
        """
        if t2 == None:
            return True
        if t1.navn == "bruddgrense":
            # Sammenligner My
            if abs(t1.K[0]) > abs(t2.K[0]):
                return True
            elif abs(t1.K[0]) == abs(t2.K[0]):
                # Sammenligner Vz
                if abs(t1.K[3]) > abs(t2.K[3]):
                    return True
                elif abs(t1.K[0]) == abs(t2.K[0]):
                    # Sammenligner N
                    if abs(t1.K[4]) > abs(t2.K[4]):
                        return True
        return False

    def lagre_tilstand(self, tilstand):
        """Lagrer tilstand dersom dimensjonerende tilfelle"""
        if tilstand.navn == "bruddgrense":
            if self._sammenlign_tilstander(tilstand, self.bruddgrense):
                self.bruddgrense = tilstand
        elif tilstand.navn == "forskyvning_kl":
            if self._sammenlign_tilstander(tilstand, self.forskyvning_kl):
                self.forskyvning_kl = tilstand
        elif tilstand.navn == "forskyvning_tot":
            if self._sammenlign_tilstander(tilstand, self.forskyvning_tot):
                self.forskyvning_tot = tilstand

    def print_tilstander(self):
        print()
        print("Bruddgrensetilstand:")
        print(self.bruddgrense)
        print()
        print("Bruksgrensetilstand for forskyvning av kontakttråd:")
        print(self.forskyvning_kl)
        print()
        print("Bruksgrensetilstand for total forskyvning:")
        print(self.forskyvning_tot)

def hent_master(hoyde, s235, materialkoeff):
    """Returnerer liste med master til beregning."""

    # B-master (tverrsnittsklasse 3)
    B2 = Mast(navn="B2", type="B", egenvekt=360, A_profil=1.70 * 10 ** 3, A_ref=0.12,
              Iy_profil=3.64 * 10 ** 6, Iz_profil=4.32 * 10 ** 5, Wyp=7.46 * 10 ** 4, It=4.15 * 10 ** 4,
              noytralakse=17.45, toppmaal=150, stigning=14 / 1000, d_h=50, d_b=10, h_max=8.0, h=hoyde,
              s235=s235, materialkoeff=materialkoeff)
    B3 = Mast(navn="B3", type="B", egenvekt=510, A_profil=2.04 * 10 ** 3, A_ref=0.14,
              Iy_profil=6.05 * 10 ** 6, Iz_profil=6.27 * 10 ** 5, Wyp=1.05 * 10 ** 5, It=5.68 * 10 ** 4,
              noytralakse=19.09, toppmaal=255, stigning=23 / 1000, d_h=50, d_b=10, h_max=9.5, h=hoyde,
              s235=s235, materialkoeff=materialkoeff)
    B4 = Mast(navn="B4", type="B", egenvekt=560, A_profil=2.40 * 10 ** 3, A_ref=0.16,
              Iy_profil=9.25 * 10 ** 6, Iz_profil=8.53 * 10 ** 5, Wyp=1.38 * 10 ** 5, It=7.39 * 10 ** 4,
              noytralakse=20.05, toppmaal=255, stigning=23 / 1000, d_h=60, d_b=10, h_max=11.0, h=hoyde,
              s235=s235, materialkoeff=materialkoeff)
    B6 = Mast(navn="B6", type="B", egenvekt=700, A_profil=3.22 * 10 ** 3, A_ref=0.20,
              Iy_profil=1.91 * 10 ** 7, Iz_profil=1.48 * 10 ** 6, Wyp=2.28 * 10 ** 5, It=1.19 * 10 ** 5,
              noytralakse=22.01, toppmaal=255, stigning=23 / 1000, d_h=100, d_b=12, h_max=13.0, h=hoyde,
              s235=s235, materialkoeff=materialkoeff)

    # H-master (tverrsnittsklasse 3)
    H3 = Mast(navn="H3", type="H", egenvekt=520, A_profil=1.15 * 10 ** 3, A_ref=0.20,
              Iy_profil=5.89 * 10 ** 5, noytralakse=21.69, toppmaal=200, stigning=20 / 1000, d_h=50, d_b=10,
              k_g=0.85, k_d=0.55, h_max=13.0, h=hoyde, s235=s235, materialkoeff=materialkoeff)
    H5 = Mast(navn="H5", type="H", egenvekt=620, A_profil=1.41 * 10 ** 3, A_ref=0.20,
              Iy_profil=5.89 * 10 ** 5, noytralakse=22.41, toppmaal=200, stigning=20 / 1000, d_h=50, d_b=10,
              k_g=0.85, k_d=0.55, h_max=13.0, h=hoyde, s235=s235, materialkoeff=materialkoeff)
    H6 = Mast(navn="H6", type="H", egenvekt=620, A_profil=1.41 * 10 ** 3, A_ref=0.20,
              Iy_profil=5.89 * 10 ** 5, noytralakse=22.41, toppmaal=200, stigning=20 / 1000,
              k_g=0.85, k_d=0.55, h=hoyde, s235=s235, materialkoeff=materialkoeff)

    # Bjelkemaster (tverrsnittsklasse 1)
    HE200B = Mast(navn="HE200B", type="bjelke", egenvekt=613, A_profil=7.81 * 10 ** 3,
                  A_ref=0.20, Iy_profil=5.70 * 10 ** 7, Iz_profil=2.00 * 10 ** 7, Wyp=6.42 * 10 ** 5,
                  Wzp=3.00*10**5, It=5.95*10**5, Cw=1.71*10**11, h_max=9.5, h=hoyde,
                  s235=s235, materialkoeff=materialkoeff)
    HE220B = Mast(navn="HE220B", type="bjelke", egenvekt=715, A_profil=9.10 * 10 ** 3,
                  A_ref=0.22, Iy_profil=8.09 * 10 ** 7, Iz_profil=2.84 * 10 ** 7, Wyp=8.28 * 10 ** 5,
                  Wzp=3.87*10**5, It=7.68*10**5, Cw=2.95*10**11, h_max=11.0, h=hoyde,
                  s235=s235, materialkoeff=materialkoeff)
    HE240B = Mast(navn="HE240B", type="bjelke", egenvekt=832, A_profil=1.06 * 10 ** 4,
                  A_ref=0.24, Iy_profil=1.13 * 10 ** 8, Iz_profil=3.92 * 10 ** 7, Wyp=1.05 * 10 ** 6,
                  Wzp=4.90*10**5, It=1.03*10**6, Cw=4.87*10**11, h_max=12.0, h=hoyde,
                  s235=s235, materialkoeff=materialkoeff)
    HE260B = Mast(navn="HE260B", type="bjelke", egenvekt=930, A_profil=1.18 * 10 ** 4,
                  A_ref=0.26, Iy_profil=1.49 * 10 ** 8, Iz_profil=5.13 * 10 ** 7, Wyp=1.28 * 10 ** 6,
                  Wzp=5.92*10**5, It=1.24*10**6, Cw=7.54*10**11, h_max=13.0, h=hoyde,
                  s235=s235, materialkoeff=materialkoeff)
    HE280B = Mast(navn="HE280B", type="bjelke", egenvekt=1030, A_profil=1.31 * 10 ** 4,
                  A_ref=0.28, Iy_profil=1.93 * 10 ** 8, Iz_profil=6.59 * 10 ** 7, Wyp=1.53 * 10 ** 6,
                  Wzp=7.06*10**5, It=1.44*10**6, Cw=1.13*10**12, h_max=13.0, h=hoyde,
                  s235=s235, materialkoeff=materialkoeff)
    HE260M = Mast(navn="HE260M", type="bjelke", egenvekt=1720, A_profil=2.20 * 10 ** 4,
                  A_ref=0.268, Iy_profil=3.13 * 10 ** 8, Iz_profil=2.00 * 10 ** 8, Wyp=2.52 * 10 ** 6,
                  Wzp=1.17*10**6, It=7.22*10**6, Cw=1.73*10**12, A_ref_par=0.29,
                  h_max=13.0, h=hoyde, s235=s235, materialkoeff=materialkoeff)

    master = []
    master.extend([B2, B3, B4, B6, H3, H5, H6])
    master.extend([HE200B, HE220B, HE240B, HE260B, HE280B, HE260M])

    return master














