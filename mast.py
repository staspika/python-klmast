import math
import scipy.integrate as integrate
import matplotlib.pyplot as plt

class Mast(object):
    """Klasse for å representere alle typer master."""

    # Klassevariabler er like for alle master
    E = 210000  # N/mm^2
    G = 80000  # N/mm^2

    def __init__(self, navn, type, egenvekt=0, A_profil=0, Iy_profil=0,
                 Iz_profil=0, Wyp=0, Wzp=0, It=0, Cw=0, noytralakse=0,
                 toppmaal=0, stigning=0, d_h=0, d_b=0,
                 k_g=0, k_d=0, A_ref=0, A_ref_par=0, h_max=0, h=0,
                 s235=False, materialkoeff=1.05):
        """Initialiserer masteobjekt.

        :param str navn: Mastens navn
        :param str type: Mastens type (B, H, bjelke)
        :param int egenvekt: Mastens egenvekt
        :param float A_profil: Arealet av et stegprofil
        :param float Iy_profil: Stegprofilets annet arealmoment om lokal y-akse
        :param float Iz_profil: Stegprofilets annet arealmoment om lokal z-akse
        :param float Wyp: Plastisk tverrsnittsmodul om profilets y-akse
        :param float Wzp: Plastisk tverrsnittsmodul om profilets z-akse
        :param float It: Profilets treghetsmoment for torsjon
        :param float Cw: Profilets hvelvningskonstant
        :param float noytralakse: Avstand ytterkant profil - lokal z-akse
        :param int toppmaal: Tverrsnittsbredde ved mastetopp
        :param float stigning: Mastens helning
        :param float d_h: Tverrsnittshøyde diagonaler
        :param float d_b: Tverrsnittsbredde diagonaler
        :param float k_g: Knekklengdefaktor gurter
        :param float k_d: Knekklengdefaktor diagonaler
        :param float A_ref: Vindareal normalt sporretning
        :param float A_ref_par: Vindareal parallelt sporretning
        :param float h_max: Max tillatt høyde av mast
        :param float h: Faktisk høyde av mast
        :param Boolean s235: Angir valg av flytespenning
        :param float materialkoeff: Materialkoeffisient for dimensjonering
        """

        self.navn = navn  # Mastens lastsituasjon
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
        self.Wzp = Wzp

        self.toppmaal = toppmaal  # Toppmål mast [mm]
        self.stigning = stigning  # Mastens stigning (promille)

        self.noytralakse = noytralakse  # Avstand ytterkant profil til n.a.
        self.d_h = d_h  # Diagonalhøyde [mm]
        self.d_b = d_b  # Diagonalbredde [mm]
        self.k_g = k_g  # Knekklengdefaktor gurt
        self.k_d = k_d  # Knekklengdefaktor diagonal

        # Beregner totalt tverrsnittsareal A [mm^2]
        if type == "B":
            self.A = 2 * A_profil
        elif type == "H":
            self.A = 4 * A_profil
        else:
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

        # Areal og treghetsmoment oppgis framfor diagonaldimensjoner for H6
        self.d_L = math.sqrt((0.9 * self.bredde(h)) ** 2 + 500 ** 2)
        if navn == "H6":
            self.d_A = 691
            self.d_I = 9.44 * 10 ** 4
        else:
            self.d_A = d_b * d_h
            self.d_I = d_b * d_h ** 3 / 12  # Sterk akse [mm^4]

        self.It = It  # St. Venants torsjonskonstant [mm^4]
        if type == "B":
            self.It = 2 * It + 1 / 3 * 0.9 * (self.bredde(h) * (
                               (self.E * 1000 * 0.9 * self.bredde(h) * self.d_A) / (self.G * self.d_L ** 3)))
        self.Cw = Cw  # Hvelvingskonstant [mm^6]
        if type == "B":
            self.Cw = 0.5 * self.Iy_profil * (0.9 * self.bredde(h)) ** 2

        # Lister for å holde last/forskvningstilstander
        self.bruddgrense = []
        self.forskyvning_tot = []
        self.forskyvning_kl = []

        # Variabler for å holde dimensjonerende tilstander
        self.tilstand_UR_max = None
        self.tilstand_My_max = None
        self.tilstand_T_max = None
        self.tilstand_Dz_tot_max = None
        self.tilstand_phi_tot_max = None
        self.tilstand_Dz_kl_max = None
        self.tilstand_phi_kl_max = None


    def __repr__(self):
        Iy = self.Iy(self.h)/10**8
        Iz = self.Iz(self.h)/10**6
        Wy = self.Wy_el/10**3
        Wz = self.Wz_el/10**3
        rep = "{}\nMastetype: {}    Høyde: {}m\n".format(self.navn, self.type, self.h)
        rep += "Iy: {:.3g}*10^8mm^4    Iz: {:.3g}*10^6mm^4\n" \
              "Wy_el = {:.3g}*10^3mm^3  Wz_el = {:.3g}*10^3mm^3\n".format(Iy, Iz, Wz, Wy)
        rep += "Tverrsnittsbredde ved innspenning: {}mm\n".format(self.bredde(self.h))
        rep += "\nSørste utnyttelsesgrad:\n"
        rep += repr(self.tilstand_My_max)
        rep += "\nSørste moment My:\n"
        rep += repr(self.tilstand_UR_max)
        rep += "\nSørste torsjon T:\n"
        rep += repr(self.tilstand_T_max)
        rep += "\nStørste forskyvning Dz (totalt):\n"
        rep += repr(self.tilstand_Dz_tot_max)
        rep += "\nStørste torsjonsvinkel phi (totalt):\n"
        rep += repr(self.tilstand_phi_tot_max)
        rep += "\nStørste forskyvning Dz (KL):\n"
        rep += repr(self.tilstand_Dz_kl_max)
        rep += "\nStørste torsjonsvinkel phi (KL):\n"
        rep += repr(self.tilstand_phi_kl_max)
        return rep

    def bredde(self, x):
        """Beregner total bredde av tverrsnitt.

        :param float x: Avstand fra mastens toppunkt [m]
        :return: Tverrsnittsbredde i angitt høyde [mm]
        :rtype: :class:`float`
        """

        if not self.type == "bjelke":
            return self.toppmaal + 2 * self.stigning * x * 1000
        return self.b

    def Iy(self, x, delta_topp=0, breddefaktor=1.0,):
        """Beregner annet arealmoment om mastens sterk akse.

        Breddefaktor kan oppgis for å ta hensyn til
        redusert effektiv bredde grunnet helning på mast.

        :param x: Avstand fra mastens toppunkt [m]
        :param delta_topp: Konstant tillegg til x (til hjelp ved integrasjon) [m]
        :param breddefaktor: Faktor for å kontrollere effektiv bredde
        :return: Annet arealmoment om y-akse i angitt høyde [mm^2]
        :rtype: :class:`float`
        """

        if self.type == "B":
            z = breddefaktor*self.bredde(x+delta_topp)/2 - self.noytralakse
            Iy = 2 * (self.Iz_profil + self.A_profil * z**2)
        if self.type == "H":
            z = breddefaktor*self.bredde(x+delta_topp)/2 - self.noytralakse
            Iy = 4 * (self.Iy_profil + self.A_profil * z**2)
        elif self.type == "bjelke":
            Iy = self.Iy_profil
        return Iy

    def Iy_int_P(self, x, delta_topp=0):
        """Beregner integralet for Iy ved punktlast.

        :param float x: Lengden det skal integreres over
        :param float delta_topp: Avstand til mastetopp det skal integreres fra
        :return: Summen av Iy-bidrag over angitt høyde
        :rtype: :class:`float`
        """

        return x**2 / self.Iy(x/1000, delta_topp=delta_topp)

    def Iy_int_q(self, x, delta_topp=0):
        """Beregner integralet for Iy ved jevnt fordelt last.

        :param float x: Lengden det skal integreres over
        :param float delta_topp: Avstand til mastetopp det skal integreres fra
        :return: Summen av Iy-bidrag over angitt høyde
        :rtype: :class:`float`
        """

        return x**3 / self.Iy(x/1000, delta_topp=delta_topp)

    def Iz(self, x, delta_topp=0):
        """Beregner annet arealmoment om mastens svake akse.

        :param x: Avstand fra mastens toppunkt [m]
        :param delta_topp: Konstant tillegg til x (til hjelp ved integrasjon) [m]
        :return: Annet arealmoment om z-akse i angitt høyde [mm^2]
        :rtype: :class:`float`
        """

        if self.type == "B":
            Iz = 2 * self.Iy_profil
        if self.type == "H":
            y = self.bredde(x+delta_topp)/2 - self.noytralakse
            Iz = 4 * (self.Iz_profil + self.A_profil * y**2)
        elif self.type == "bjelke":
            Iz = self.Iz_profil
        return Iz

    def Iz_int_P(self, x, delta_topp=0):
        """Beregner integralet for Iz ved punktlast.

        :param float x: Lengden det skal integreres over
        :param float delta_topp: Avstand til mastetopp det skal integreres fra
        :return: Summen av Iy-bidrag over angitt høyde
        :rtype: :class:`float`
        """

        return x**2 / self.Iz(x / 1000, delta_topp=delta_topp)

    def Iz_int_q(self, x, delta_topp=0):
        """Beregner integralet for Iz ved jevnt fordelt last.

        :param float x: Lengden det skal integreres over
        :param float delta_topp: Avstand til mastetopp det skal integreres fra
        :return: Summen av Iy-bidrag over angitt høyde
        :rtype: :class:`float`
        """

        return x**3 / self.Iz(x / 1000, delta_topp=delta_topp)

    def My_Rk(self):
        """Beregner mastens motstandsmoment om sterk akse [Nmm]

        :return: Motstandsmoment om y-aksen
        :rtype: :class:`float`
        """

        if self.type == "B":
            My_Rk = self.A_profil * 0.9 * self.bredde(self.h) * self.fy
        elif self.type == "H":
            My_Rk = 2 * self.A_profil * 0.9 * self.bredde(self.h) * self.fy
        else:
            My_Rk = self.Wyp * self.fy
        return My_Rk

    def Mz_Rk(self):
        """Beregner mastens motstandsmoment om svak akse [Nmm]

        :return: Motstandsmoment om z-aksen
        :rtype: :class:`float`
        """

        if self.type == "B":
            My_Rk = 2 * self.Wyp * self.fy
        elif self.type == "H":
            My_Rk = 2 * self.A_profil * 0.9 * self.bredde(self.h) * self.fy
        else:
            My_Rk = self.Wzp * self.fy
        return My_Rk


    def sorter_grenseverdier(self):
        """Lagrer høyeste verdier av utvalgte parametre i egne variabler.

        Tilstander med høyeste registrerte verdi av gitte parametre sorteres ut
        og lagres i egne variabler tilknyttet :class:`Mast`-objektet.

        Tilstandsparametre for utvelgelse blant bruddgrensetilstander:
        **Utnyttelsesgrad**, **My_max**, **T_max**

        Tilstandsparametre for utvelgelse blant forskyvningstilstander (både total og KL):
        **Dz_max**, **phi_max**
        """

        #Bruddgrense
        self.tilstand_UR_max = self.bruddgrense[0]
        self.tilstand_My_max = self.bruddgrense[0]
        self.tilstand_T_max = self.bruddgrense[0]
        self.tilstand_Dz_tot_max = self.forskyvning_tot[0]
        self.tilstand_phi_tot_max = self.forskyvning_tot[0]
        self.tilstand_Dz_kl_max = self.forskyvning_kl[0]
        self.tilstand_phi_kl_max = self.forskyvning_kl[0]

        for tilstand in self.bruddgrense:
            UR_max = self.tilstand_UR_max.utnyttelsesgrad
            My_max = abs(self.tilstand_My_max.K[0])
            Mz_max = abs(self.tilstand_My_max.K[2])
            T_max = abs(self.tilstand_T_max.K[5])
            UR = tilstand.utnyttelsesgrad
            My = abs(tilstand.K[0])
            Mz = abs(tilstand.K[2])
            T = abs(tilstand.K[5])

            if UR > UR_max:
                self.tilstand_UR_max = tilstand

            if My > My_max:
                self.tilstand_My_max = tilstand
            elif My == My_max:
                if Mz > Mz_max:
                    self.tilstand_My_max = tilstand

            if T > T_max:
                self.tilstand_T_max = tilstand

        # Forskyvning totalt
        self.tilstand_Dz_tot_max = self.forskyvning_tot[0]
        self.tilstand_phi_tot_max = self.forskyvning_tot[0]

        for tilstand in self.forskyvning_tot:
            Dz_max = abs(self.tilstand_Dz_tot_max.K_D[1])
            phi_max = abs(self.tilstand_phi_tot_max.K_D[2])
            Dz = abs(tilstand.K_D[1])
            phi = abs(tilstand.K_D[2])

            if Dz > Dz_max:
                self.tilstand_Dz_tot_max = tilstand

            if phi > phi_max:
                self.tilstand_phi_tot_max = tilstand

        # Forskyvning KL
        self.tilstand_Dz_kl_max = self.forskyvning_kl[0]
        self.tilstand_phi_kl_max = self.forskyvning_kl[0]

        for tilstand in self.forskyvning_kl:
            Dz_max = abs(self.tilstand_Dz_kl_max.K_D[1])
            phi_max = abs(self.tilstand_phi_kl_max.K_D[2])
            Dz = abs(tilstand.K_D[1])
            phi = abs(tilstand.K_D[2])

            if Dz > Dz_max:
                self.tilstand_Dz_kl_max = tilstand

            if phi > phi_max:
                self.tilstand_phi_kl_max = tilstand

    def sorter(self, kriterie):
        """Sorterer :class:`Mast`-objektets tilstander.

        ``kriterie`` oppgis for å styre sortering av bruddgrensetilstander:
        **0** = My
        **1** = utnyttelsesgrad

        :param int kriterie:
        """

        if kriterie == 0:
            self.bruddgrense = sorted(self.bruddgrense, key=lambda tilstand: abs(tilstand.K[0]), reverse=True)
        elif kriterie == 1:
            self.bruddgrense = sorted(self.bruddgrense, key=lambda tilstand: abs(tilstand.utnyttelsesgrad), reverse=True)

        self.forskyvning_tot = sorted(self.forskyvning_tot, key=lambda tilstand: abs(tilstand.K_D[1]), reverse=True)
        self.forskyvning_kl = sorted(self.forskyvning_kl, key=lambda tilstand: abs(tilstand.K_D[1]), reverse=True)

    def lagre_tilstand(self, tilstand):
        """Lagrer tilstand i tilknyttet :class:`Mast`-objekt.

        :param Tilstand tilstand: Tilstand som skal lagres
        """

        if tilstand.type == 0:
            self.bruddgrense.append(tilstand)
        elif tilstand.type == 1:
            self.forskyvning_tot.append(tilstand)
        else:
            self.forskyvning_kl.append(tilstand)


def hent_master(hoyde, s235, materialkoeff):
    """Henter liste med master til beregning.

    :param float hoyde: Valgt mastehøyde
    :param Boolean s235: Angir valg av flytespenning
    :param float materialkoeff: Materialkoeffisient for dimensjonering
    :return: Liste inneholdende samtlige av programmets master
    :rtype: :class:`list`
    """

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
              k_g=0.85, k_d=0.55, h_max=13.0, h=hoyde, s235=s235, materialkoeff=materialkoeff)

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



if __name__ == "__main__":
    master = hent_master(8, True, 1.05)
    mazt = master[6]
    x = []
    y_ny = []
    y_gammel = []
    y_ekv = []
    print("Mast: {}\n".format(mazt.navn))
    for h in range(80, 135, 5):
        h *= 1/10
        Iy_ny = mazt.Iy(2/3*h)
        Iy_gammel = mazt.Iy_KL_fund(2/3*h)

        delta_topp = 0
        L = (h-delta_topp) * 1000  # FH + SH/2

        delta = integrate.quad(mazt.Iy_int_P, 0, L, args=(delta_topp,))
        Iy_ekv = L ** 3 / (3 * delta[0])

        x.append(h)
        y_ny.append(Iy_ny)
        y_gammel.append(Iy_gammel)
        y_ekv.append(Iy_ekv)

        print("")
        print("I_ekv =")
        print("H = {} m".format(h))
        print("Iy, ny beregning = {:.3g}".format((Iy_ny)))
        print("Iy, gammel beregning = {:.3g}".format((Iy_gammel)))
        print("Iy_ekv = {:.3g}".format(Iy_ekv))


    ny, = plt.plot(x, y_ny, "b--", label="Eksakt i 1/3-dels punkt")
    plt.hold(True)
    gammel, = plt.plot(x, y_gammel, "r", label="Stivhet KL_fund")
    ekv, = plt.plot(x, y_ekv, "g", label="Midlere stivhet, kontakttrådhøyde")
    plt.title("Iy for mast {}".format(mazt.navn))
    first_legend = plt.legend(handles=[ny, gammel, ekv], loc=0)
    plt.ylabel("Annet arealmoment [mm^4]")
    plt.xlabel("Mastehøyde [m]")
    plt.show()
























