# -*- coding: utf8 -*-
from __future__ import unicode_literals
import math
import numpy

class Mast(object):
    """Klasse for å representere alle typer master."""

    E = 210000  # N/mm^2
    G = 80000  # N/mm^2

    def __init__(self, navn, type, egenvekt=0, A_profil=0, Iy_profil=0,
                 Iz_profil=0, Wyp=0, Wzp=0, It=0, Cw=0, noytralakse=0,
                 toppmaal=0, stigning=0, d_h=0, d_b=0, k_g=0, k_d=0,
                 b_f=0, A_ref=0, A_ref_par=0, h_max=0, h=0,
                 s235=False, materialkoeff=1.05):
        """Initialiserer :class:`Mast`-objekt.

        :param str navn: Mastens navn
        :param str type: Mastens type (B, H eller bjelke)
        :param int egenvekt: Mastens egenvekt :math:`[\\frac{N}{m}]`
        :param float A_profil: Arealet av et stegprofil :math:`[mm^2]`
        :param float Iy_profil: Stegprofilets annet arealmoment om lokal y-akse :math:`[mm^4]`
        :param float Iz_profil: Stegprofilets annet arealmoment om lokal z-akse :math:`[mm^4]`
        :param float Wyp: Plastisk tverrsnittsmodul om profilets y-akse :math:`[mm^3]`
        :param float Wzp: Plastisk tverrsnittsmodul om profilets z-akse :math:`[mm^3]`
        :param float It: Profilets treghetsmoment for torsjon :math:`[mm^4]`
        :param float Cw: Profilets hvelvningskonstant :math:`[mm^6]`
        :param float noytralakse: Avstand ytterkant profil - lokal z-akse :math:`[mm]`
        :param int toppmaal: Tverrsnittsbredde ved mastetopp :math:`[mm]`
        :param float stigning: Mastens helning :math:`[\\frac{1}{1000}]`
        :param float d_h: Tverrsnittshøyde diagonaler :math:`[mm]`
        :param float d_b: Tverrsnittsbredde diagonaler :math:`[mm]`
        :param float k_g: Knekklengdefaktor gurter
        :param float k_d: Knekklengdefaktor diagonaler
        :param float b_f: Flensbredde for beregning av massivitetsforhold :math:`[mm]`
        :param float A_ref: Vindareal normalt sporretning :math:`[\\frac{m^2}{m}]`
        :param float A_ref_par: Vindareal parallelt sporretning :math:`[\\frac{m^2}{m}]`
        :param float h_max: Max tillatt høyde av mast :math:`[m]`
        :param float h: Faktisk høyde av mast :math:`[m]`
        :param Boolean s235: Angir valg av flytespenning :math:`[\\frac{N}{mm^2}]`
        :param float materialkoeff: Materialkoeffisient for dimensjonering
        """

        self.navn = navn
        self.type = type
        self.egenvekt = egenvekt
        self.A_profil = A_profil

        self.Iy_profil = Iy_profil
        if Iz_profil == 0:
            self.Iz_profil = Iy_profil
        else:
            self.Iz_profil = Iz_profil

        self.Wyp = Wyp
        self.Wzp = Wzp
        self.toppmaal = toppmaal
        self.stigning = stigning
        self.noytralakse = noytralakse
        self.d_h = d_h
        self.d_b = d_b
        self.k_g = k_g
        self.k_d = k_d
        self.b_f = b_f

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

        # Setter vindareal
        self.A_ref = A_ref
        if self.type == "bjelke":
            if A_ref_par == 0:
                self.A_ref_par = A_ref
            else:
                self.A_ref_par = A_ref_par
        else:
            self.A_ref_par = self.vindareal_midlere(h)
            if self.type == "H":
                self.A_ref = self.A_ref_par
        # Dragkoeffisienter
        self.c_f, self.c_f_par = self.dragkoeffisienter(h, True)

        # Setter stålkvalitet
        self.materialkoeff = materialkoeff
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

        self.My_Rk = self.Wyp * self.fy
        if self.type == "B":
            self.My_Rk = self.A_profil * 0.9 * self.bredde(self.h) * self.fy
        elif self.type == "H":
            self.My_Rk = 2 * self.A_profil * 0.9 * self.bredde(self.h) * self.fy

        self.Mz_Rk = self.Wzp * self.fy
        if self.type == "B":
            self.Mz_Rk = 2 * self.Wyp * self.fy
        elif self.type == "H":
            self.Mz_Rk = 2 * self.A_profil * 0.9 * self.bredde(self.h) * self.fy

        # Lister for å holde last/forskvningstilstander
        self.bruddgrense = []
        self.forskyvning_tot = []
        self.forskyvning_kl = []

        # Variabler for å holde dimensjonerende tilstander
        self.tilstand_UR_max = None
        self.tilstand_My_max = None
        self.tilstand_T_max = None
        self.tilstand_T_max_ulykke = None
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
        rep += repr(self.tilstand_UR_max)
        rep += "\nSørste moment My:\n"
        rep += repr(self.tilstand_My_max)
        rep += "\nSørste torsjon T:\n"
        rep += repr(self.tilstand_T_max)
        rep += "\nSørste torsjon T (ulykkeslast):\n"
        rep += repr(self.tilstand_T_max_ulykke)
        rep += "\nStørste forskyvning Dz (totalt):\n"
        rep += repr(self.tilstand_Dz_tot_max)
        rep += "\nStørste torsjonsvinkel phi (totalt):\n"
        rep += repr(self.tilstand_phi_tot_max)
        rep += "\nStørste forskyvning Dz (KL):\n"
        rep += repr(self.tilstand_Dz_kl_max)
        rep += "\nStørste torsjonsvinkel phi (KL):\n"
        rep += repr(self.tilstand_phi_kl_max)
        rep += "\n"
        return rep

    def bredde(self, x):
        """Beregner total bredde av tverrsnitt.

        :param float x: Avstand fra mastens toppunkt :math:`[m]`
        :return: Tverrsnittsbredde :math:`[mm]`
        :rtype: :class:`float`
        """

        if not self.type == "bjelke":
            return self.toppmaal + 2 * self.stigning * x * 1000
        return self.b

    def Iy(self, x, delta_topp=0, breddefaktor=1.0,):
        """Beregner annet arealmoment om mastens sterk akse.

        Breddefaktor kan oppgis for å ta hensyn til
        redusert effektiv bredde grunnet helning på mast.

        :param x: Avstand fra mastens toppunkt :math:`[m]`
        :param delta_topp: Konstant tillegg til ``x``, til hjelp ved integrasjon :math:`[m]`
        :param breddefaktor: Faktor for å kontrollere effektiv bredde
        :return: Annet arealmoment om y-akse i angitt høyde :math:`[mm^4]`
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

    def Iz(self, x, delta_topp=0):
        """Beregner annet arealmoment om mastens svake akse.

        :param x: Avstand fra mastens toppunkt :math:`[m]`
        :param delta_topp: Konstant tillegg til ``x``, til hjelp ved integrasjon :math:`[m]`
        :return: Annet arealmoment om z-akse i angitt høyde :math:`[mm^4]`
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

    def Iy_int_M(self, x, delta_topp=0):
        """Evaluerer integranden for Iy ved påsatt moment.

        :param float x: Høydevariabel for integrasjon :math:`[mm]`
        :param float delta_topp: Avstand til mastetopp det skal integreres fra :math:`[m]`
        :return: Integranden evaluert ved angitt høyde
        :rtype: :class:`float`
        """

        return x / self.Iy(x / 1000, delta_topp=delta_topp)

    def Iy_int_P(self, x, delta_topp=0):
        """Evaluerer integranden for Iy ved punktlast.

        :param float x: Høydevariabel for integrasjon :math:`[mm]`
        :param float delta_topp: Avstand til mastetopp det skal integreres fra :math:`[m]`
        :return: Integranden evaluert ved angitt høyde
        :rtype: :class:`float`
        """

        return x**2 / self.Iy(x/1000, delta_topp=delta_topp)

    def Iy_int_q(self, x, delta_topp=0):
        """Evaluerer integranden for Iy ved jevnt fordelt last.

        :param float x: Høydevariabel for integrasjon :math:`[mm]`
        :param float delta_topp: Avstand til mastetopp det skal integreres fra :math:`[m]`
        :return: Integranden evaluert ved angitt høyde
        :rtype: :class:`float`
        """

        return x**3 / self.Iy(x/1000, delta_topp=delta_topp)

    def Iz_int_P(self, x, delta_topp=0):
        """Evaluerer integranden for Iz ved punktlast.

        :param float x: Høydevariabel for integrasjon :math:`[mm]`
        :param float delta_topp: Avstand til mastetopp det skal integreres fra :math:`[m]`
        :return: Integranden evaluert ved angitt høyde
        :rtype: :class:`float`
        """

        return x**2 / self.Iz(x / 1000, delta_topp=delta_topp)

    def Iz_int_q(self, x, delta_topp=0):
        """Evaluerer integranden for Iz ved jevnt fordelt last.

        :param float x: Høydevariabel for integrasjon :math:`[mm]`
        :param float delta_topp: Avstand til mastetopp det skal integreres fra :math:`[m]`
        :return: Integranden evaluert ved angitt høyde
        :rtype: :class:`float`
        """

        return x**3 / self.Iz(x / 1000, delta_topp=delta_topp)

    def Iz_int_M(self, x, delta_topp=0):
        """Evaluerer integranden for Iz ved påsatt moment.

        :param float x: Høydevariabel for integrasjon :math:`[mm]`
        :param float delta_topp: Avstand til mastetopp det skal integreres fra :math:`[m]`
        :return: Integranden evaluert ved angitt høyde
        :rtype: :class:`float`
        """

        return x / self.Iz(x / 1000, delta_topp=delta_topp)

    def dragkoeffisienter(self, x, EN1991):
        """Beregner mastens dragkoeffisienter uten islast.

        - Bjelkemaster og B-master med vind normalt spor:

          :math:`c_{f}` beregnes ut fra NS-EN 1991-1-4
          seksjon 7.7 med anbefalt verdi :math:`c_{f0} = 2.0`
          og :math:`\psi_{\lambda}` avlest fra figur 7.36
          under seksjon 7.13 med slankhet :math:`\lambda = 70`.

        - B-master med vind parallelt spor, H-master:

          :math:`c_{f0}` beregnes basert på en 2.-grads
          kurvetilpasning av verdier for firkantet romlig fagverk
          med vind parallelt flatenormal, ref. NS-EN 1991-1-4
          seksjon 7.11, figur 7.34. Videre tilnærmes :math:`\psi_{\lambda}`
          ut fra figur 7.36 med slankhet :math:`\lambda = 70`.

          Dersom ``EN1991`` har verdien False beregnes c_f istedenfor
          etter NS-EN 1993-3-1 seksjon B.2.2. Faktoren :math:`K_{\theta}`
          settes lik :math:`1.0` da vinkelen :math:`\theta` grunnet
          mastens helning i denne sammenhengen er neglisjerbar.

        :param: float x: Avstand fra mastens toppunkt :math:`[m]`
        :param Boolean EN1991: Styrer valg av beregningsmetode for dragkoeffisient
        :return: Dragkoeffisienter ``c_f``, ``c_f_par`` (normalt spor, parallelt spor)
        :rtype: :class:`float`, :class:`float`
        """

        c_f, c_f_par = 1.83, 1.83

        if self.type is not "bjelke":

            phi = self._massivitetsforhold_midlere(x)

            if EN1991:
                f_c = [3.61742424, -5.52765152, 3.8385]
                f_p = [-0.05294386, -0.01594173, 0.99789576]
                c_f0 = f_c[0] * phi ** 2 + f_c[1] * phi + f_c[2]
                psi = f_p[0] * phi ** 2 + f_p[1] * phi + f_p[2]
                c_f_par = c_f0 * psi
            else:
                C_1 = 2.25
                C_2 = 1.5
                c_f_par = 1.76 * C_1 * (1 - C_2 * phi + phi**2)

            if self.type == "H":
                c_f = c_f_par

        return c_f, c_f_par

    def _massivitetsforhold_midlere(self, x):
        """Beregner midlere massivitetsforhold over lengden x.

        Verdien beregnes som et gjennomsnitt av verdiene for samtlige
        0.5m høydesnitt innenfor oppgitt lengde ``x``.

        :param: float x: Avstand fra mastens toppunkt :math:`[m]`
        :return: Gjennomsnittlig massivitetsforhold for vindlast
        :rtype: :class:`float`
        """

        phi = 0

        x = int(10*x)
        H = [h/10 for h in range(0, x+5, 5)]
        for h in H:
            phi += self._massivitetsforhold(h)

        return phi/len(H)


    def _massivitetsforhold(self, x):
        """Beregner tverrsnittets massivitetsforhold ved gitt høyde.

        Massivitetsforholdet regnes for et representativt høydesnitt
        lik 0.5m inneholdende én stk diagonal av lengde ``l``.

        Funksjonen tar forbehold om at det regnes på en gitterstruktur
        med flatenormal parallelt vindretningen (B-mast ved vindlast
        parallelt sporettningen eller H-mast ved vilkårlig vindretning).

        :param float x: Avstand fra mastens toppunkt :math:`[m]`
        :return: Massivitetsforhold for vindlast
        :rtype: :class:`float`
        """

        phi = 1.0

        if self.type is not "bjelke":
            A = self.vindareal(x) * 10**6
            A_c = 500*self._b_mid(x)
            phi = A/A_c if A/A_c<1.0 else 1.0

        return phi


    def vindareal_midlere(self, x):
        """Beregner midlere vindareal ved gitt mastelengde for gitterstruktur.

        Vindarealet tilnærmes ved å summere 0.5m masteutsnitt
        med én stk. diagonal per. utsnitt.

        :param x: Avstand fra mastens toppunkt :math:`[m]`
        :return: Vindareal :math:`[\frac{m^2}{}m]`
        :rtype: :class:`float`
        """

        A_ref = 0

        x = int(10 * x)
        H = [h / 10 for h in range(0, x + 5, 5)]
        for h in H:
            A_ref += self.vindareal(h)

        return A_ref/len(H)


    def vindareal(self, x):
        """Beregner effektivt vindareal ved gitt høyde for gitterstruktur.

        Vindarealet regnes for et representativt høydesnitt
        lik 0.5m inneholdende én stk diagonal av lengde ``l``.

        :param x: Avstand fra mastens toppunkt :math:`[m]`
        :return: Vindareal :math:`[\frac{m^2}{}m]`
        :rtype: :class:`float`
        """

        b_mid = self._b_mid(x)
        l = (b_mid - 2 * self.b_f) * math.sqrt(2)
        A_ref = 2 * self.b_f * 500 + self.d_h * l

        return A_ref/10**6


    def _b_mid(self, x):
        """Beregner mastens midlere bredde for et 0.5m utsnitt.

        :param x: Avstand fra mastens toppunkt :math:`[m]`
        :return:
        :rtype: :class:`float`
        """

        b = self.bredde(x)
        b0 = self.bredde(x - 0.5) if x >= 0.5 else b
        return (b0 + b) / 2


    def sorter_grenseverdier(self):
        """Lagrer høyeste absoluttverdier av utvalgte parametre i egne variabler.

        Tilstander med høyeste registrerte absoluttverdi av gitte parametre sorteres ut
        og lagres i egne variabler tilknyttet :class:`Mast`-objektet.

        Tilstandsparametre for utvelgelse blant bruddgrensetilstander:

        - Utnyttelsesgrad
        - :math:`M_{y,max}`
        - :math:`T_{max}`

        Tilstandsparametre for utvelgelse blant forskyvningstilstander (både total og KL):

        - :math:`D_{z,max}`
        - :math:`\\phi_{max}`
        """

        #Bruddgrense
        self.tilstand_UR_max = self.bruddgrense[0]
        self.tilstand_My_max = self.bruddgrense[0]
        self.tilstand_T_max = self.bruddgrense[0]
        self.tilstand_Dz_tot_max = self.forskyvning_tot[0]
        self.tilstand_phi_tot_max = self.forskyvning_tot[0]
        self.tilstand_Dz_kl_max = self.forskyvning_kl[0]
        self.tilstand_phi_kl_max = self.forskyvning_kl[0]

        ulykkeslast_initiert = False

        for tilstand in self.bruddgrense:
            UR_max = self.tilstand_UR_max.utnyttelsesgrad
            My_max = abs(self.tilstand_My_max.K[0])
            Mz_max = abs(self.tilstand_My_max.K[2])
            T_max = abs(self.tilstand_T_max.K[5])
            UR = tilstand.utnyttelsesgrad
            My = abs(tilstand.K[0])
            Mz = abs(tilstand.K[2])
            T = abs(tilstand.K[5])

            if ulykkeslast_initiert:
                T_max_ulykke = abs(self.tilstand_T_max_ulykke.K[5])

            if UR > UR_max:
                self.tilstand_UR_max = tilstand

            if My > My_max:
                self.tilstand_My_max = tilstand
            elif My == My_max:
                if Mz > Mz_max:
                    self.tilstand_My_max = tilstand

            if tilstand.lastsituasjon == "Ulykkeslast":
                if not ulykkeslast_initiert:
                    self.tilstand_T_max_ulykke = self.bruddgrense[0]
                    T_max_ulykke = abs(self.tilstand_T_max_ulykke.K[5])
                    ulykkeslast_initiert = True
                if T > T_max_ulykke:
                    self.tilstand_T_max_ulykke = tilstand
            else:
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

        - 0: Sortering mhp. :math:`M_y`
        - 1: Sortering mhp. utnyttelsesgrad

        :param int kriterie: Kriterie for sortering
        """

        if kriterie == 0:
            self.bruddgrense = sorted(self.bruddgrense, key=lambda tilstand: abs(tilstand.K[0]), reverse=True)
        elif kriterie == 1:
            self.bruddgrense = sorted(self.bruddgrense, key=lambda tilstand: abs(tilstand.utnyttelsesgrad), reverse=True)

        self.forskyvning_tot = sorted(self.forskyvning_tot, key=lambda tilstand: abs(tilstand.K_D[1]), reverse=True)
        self.forskyvning_kl = sorted(self.forskyvning_kl, key=lambda tilstand: abs(tilstand.K_D[1]), reverse=True)

    def lagre_tilstand(self, tilstand):
        """Lagrer tilstand i tilknyttet :class:`Mast`-objekt.

        :param Tilstand tilstand: :class:`Tilstand` som skal lagres
        """

        if tilstand.type == 0:
            self.bruddgrense.append(tilstand)
        elif tilstand.type == 1:
            self.forskyvning_tot.append(tilstand)
        else:
            self.forskyvning_kl.append(tilstand)


def hent_master(hoyde, s235, materialkoeff):
    """Henter liste med master til beregning.

    :param float hoyde: Valgt mastehøyde :math:`[m]`
    :param Boolean s235: Angir valg av flytespenning :math:`[\\frac{N}{mm^2}]`
    :param float materialkoeff: Materialkoeffisient for dimensjonering
    :return: Liste inneholdende samtlige av programmets master
    :rtype: :class:`list`
    """

    # B-master
    B2 = Mast(navn="B2", type="B", egenvekt=360, A_profil=1.70 * 10 ** 3,
              A_ref=0.12, Iy_profil=3.64 * 10 ** 6, Iz_profil=4.32 * 10 ** 5,
              Wyp=7.46 * 10 ** 4, It=4.15 * 10 ** 4, noytralakse=17.45,
              toppmaal=150, stigning=14 / 1000, d_h=10, d_b=50, b_f=55, h_max=8.0,
              h=hoyde, s235=s235, materialkoeff=materialkoeff)
    B3 = Mast(navn="B3", type="B", egenvekt=510, A_profil=2.04 * 10 ** 3,
              A_ref=0.14, Iy_profil=6.05 * 10 ** 6, Iz_profil=6.27 * 10 ** 5,
              Wyp=1.05 * 10 ** 5, It=5.68 * 10 ** 4, noytralakse=19.09,
              toppmaal=255, stigning=23 / 1000, d_h=10, d_b=50, b_f=60, h_max=9.5,
              h=hoyde, s235=s235, materialkoeff=materialkoeff)
    B4 = Mast(navn="B4", type="B", egenvekt=560, A_profil=2.40 * 10 ** 3,
              A_ref=0.16, Iy_profil=9.25 * 10 ** 6, Iz_profil=8.53 * 10 ** 5,
              Wyp=1.38 * 10 ** 5, It=7.39 * 10 ** 4, noytralakse=20.05,
              toppmaal=255, stigning=23 / 1000, d_h=10, d_b=60, b_f=65, h_max=11.0,
              h=hoyde, s235=s235, materialkoeff=materialkoeff)
    B6 = Mast(navn="B6", type="B", egenvekt=700, A_profil=3.22 * 10 ** 3,
              A_ref=0.20, Iy_profil=1.91 * 10 ** 7, Iz_profil=1.48 * 10 ** 6,
              Wyp=2.28 * 10 ** 5, It=1.19 * 10 ** 5, noytralakse=22.01,
              toppmaal=255, stigning=23 / 1000, d_h=12, d_b=100, b_f=75, h_max=13.0,
              h=hoyde, s235=s235, materialkoeff=materialkoeff)

    # H-master
    H3 = Mast(navn="H3", type="H", egenvekt=520, A_profil=1.15 * 10 ** 3,
              A_ref=0.20, Iy_profil=5.89 * 10 ** 5, noytralakse=21.69,
              toppmaal=200, stigning=20 / 1000, d_h=50, d_b=10, k_g=0.85, k_d=0.55,
              b_f=75, h_max=13.0, h=hoyde, s235=s235, materialkoeff=materialkoeff)
    H5 = Mast(navn="H5", type="H", egenvekt=620, A_profil=1.41 * 10 ** 3,
              A_ref=0.20, Iy_profil=5.89 * 10 ** 5, noytralakse=22.41,
              toppmaal=200, stigning=20 / 1000, d_h=50, d_b=10, k_g=0.85, k_d=0.55,
              b_f=75, h_max=13.0, h=hoyde, s235=s235, materialkoeff=materialkoeff)
    H6 = Mast(navn="H6", type="H", egenvekt=620, A_profil=1.41 * 10 ** 3,
              A_ref=0.20, Iy_profil=5.89 * 10 ** 5, noytralakse=22.41,
              toppmaal=200, stigning=20 / 1000, d_h=75, d_b=75, k_g=0.85, k_d=0.55,
              b_f=75, h_max=13.0, h=hoyde, s235=s235, materialkoeff=materialkoeff)

    # Bjelkemaster
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
























