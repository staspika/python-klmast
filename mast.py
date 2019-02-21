# -*- coding: utf8 -*-
from __future__ import unicode_literals
import math
import csv


class Mast(object):
    """Klasse for å representere alle typer master."""
    E = 210000  # [N/mm^2]
    G = 81000  # [N/mm^2]
    h = 0  # [m]
    s235 = False
    materialkoeff = 1.05
    L_e = 0  # [mm]
    L_cr_y = 0  # [mm]
    L_cr_z = 0  # [mm]

    def __init__(self, navn, type, egenvekt=0, A_profil=0, b=0, d=0,
                 Iy_profil=0, Iz_profil=0, Ieta_profil=0, Wyp=0, Wzp=0,
                 It_profil=0, Cw_profil=0, noytralakse=0, toppmaal=0,
                 stigning=0, d_h=0, d_b=0, k_g=0, k_d=0, b_f=0,
                 A_ref=0, A_ref_par=0, h_max=0):
        """Initialiserer :class:`Mast`-objekt.

        :param str navn: Mastens navn
        :param str type: Mastens type (B, H eller bjelke)
        :param int egenvekt: Mastens egenvekt :math:`[\\frac{N}{m}]`
        :param float A_profil: Arealet av et stegprofil :math:`[mm^2]`
        :param float b: Tverrsnittsbredde (z-retning) :math:`[mm]`
        :param float d: Tverrsnittsdybde (y-retning) :math:`[mm]`
        :param float Iy_profil: Stegprofilets annet arealmoment om lokal y-akse :math:`[mm^4]`
        :param float Iz_profil: Stegprofilets annet arealmoment om lokal z-akse :math:`[mm^4]`
        :param float Ieta_profil: Stegprofilets annet arealmoment om dets svakeste akse :math:`[mm^4]`
        :param float Wyp: Plastisk tverrsnittsmodul om profilets y-akse :math:`[mm^3]`
        :param float Wzp: Plastisk tverrsnittsmodul om profilets z-akse :math:`[mm^3]`
        :param float It_profil: Profilets treghetsmoment for torsjon :math:`[mm^4]`
        :param float Cw_profil: Profilets hvelvningskonstant :math:`[mm^6]`
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
        # Totalt tverrsnittsareal A [mm^2]
        if type == "B":
            self.A = 2 * A_profil
        elif type == "H":
            self.A = 4 * A_profil
        else:
            self.A = A_profil
        self.h_max = h_max
        # Tverrsnittsbredde/dybde
        if self.type == "H":
            self.b = self.bredde(self.h)
            self.d = self.b
        elif self.type == "B":
            self.b = self.bredde(self.h)
            self.d = d
        else:  # bjelkemast
            self.b = b
            if self.navn == "HE260M":
                self.d = d
            else:
                self.d = self.b
        # Vindareal og dragkoeffisienter
        self.A_ref = A_ref
        if self.type == "bjelke":
            if A_ref_par == 0:
                self.A_ref_par = A_ref
            else:
                self.A_ref_par = A_ref_par
        else:
            self.A_ref_par = self.vindareal_midlere(self.h)
            if self.type == "H":
                self.A_ref = self.A_ref_par
        self.c_f, self.c_f_par = self.dragkoeffisienter(self.h, True)
        # Stålkvalitet
        if self.s235:
            self.fy = 235
        else:
            self.fy = 355
        # Elastisk momentkapasitet
        self.Wy_el = self.Iy(self.h) / (self.bredde(self.h) / 2)
        self.Wz_el = self.Iz(self.h) / (self.d / 2)
        # Tverrsnittsparametre for diagonaler
        if navn == "H6":
            # Diagonaler av L-profiler
            self.d_A = 691
            self.d_I = 9.43e4
        else:
            # Diagonaler av flattstål
            self.d_A = d_h * d_b
            self.d_I = min(d_h*d_b**3, d_b*d_h**3) / 12
        # Øvrige tverrsnittsparametre
        self.Ieta_profil = Ieta_profil
        self.It_profil, self.Cw_profil = It_profil, Cw_profil
        self.It, self.Cw = self.torsjonsparametre(self.h)  # St. Venants torsjonskonstant [mm^4]
        # Bruddkapasitet
        self.N_Rk = self.A * self.fy
        if self.type == "B":
            self.My_Rk = self.A_profil * 0.9 * self.bredde(self.h) * self.fy
            self.Mz_Rk = 2 * self.Wyp * self.fy
        elif self.type == "H":
            self.My_Rk = 2 * self.A_profil * 0.9 * self.bredde(self.h) * self.fy
            self.Mz_Rk = 2 * self.A_profil * 0.9 * self.bredde(self.h) * self.fy
        else:  # bjelkemast
            self.My_Rk = self.Wyp * self.fy
            self.Mz_Rk = self.Wzp * self.fy
        # Knekkparametre (global knekking)
        self.N_cr_y = math.pi**2*self.E*self.Iy(self.h)/self.L_cr_y**2
        self.lam_y = math.sqrt(self.N_Rk / self.N_cr_y)
        self.N_cr_z = math.pi**2*self.E*self.Iz(self.h)/self.L_cr_z**2
        self.lam_z = math.sqrt(self.N_Rk / self.N_cr_z)
        if self.type == "B":
            # Knekkparametre diagonalstav
            L_d = 0.5 * self.diagonallengde()
            self.alpha_d = 0.49
            self.N_cr_d = (math.pi**2 * self.E * self.d_I) / (L_d**2)
            self.lam_d = math.sqrt(self.d_A * self.fy / self.N_cr_d)
            # Knekkparametre gurt (U-profil)
            L_g = self.beta() * 1000
            self.alpha_g = 0.49
            self.N_cr_g = (math.pi**2 * self.E * self.Iz_profil) / (L_g**2)
            self.lam_g = math.sqrt(self.A_profil * self.fy / self.N_cr_g)
        elif self.type == "H":
            # Knekkparametre diagonalstav
            L_d = self.k_d * 1000
            if self.navn == "H6":
                self.alpha_d = 0.34
            else:
                self.alpha_d = 0.49
            self.N_cr_d = (math.pi**2 * self.E * self.d_I) / (L_d**2)
            self.lam_d = math.sqrt(self.d_A * self.fy / self.N_cr_d)
            # Knekkparametre gurt (L-profil)
            L_g = self.k_g * 1000
            self.alpha_g = 0.34
            self.N_cr_g = (math.pi**2 * self.E * self.Ieta_profil) / (L_g**2)
            self.lam_g = math.sqrt(self.A_profil * self.fy / self.N_cr_g)
        if not self.type == "H":
            # Vippeparametre
            self.psi_v = math.sqrt(1 + (self.E * self.Cw / (self.G * self.It)) * (math.pi / self.L_e) ** 2)
            self.M_cr_0 = (math.pi / self.L_e) * math.sqrt(self.G * self.It * self.E * self.Iz(self.h)) * self.psi_v
        # Lister for å holde last/forskvningstilstander
        self.bruddgrense = []
        self.forskyvning_tot = []
        self.forskyvning_kl = []
        self.ulykke = []
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
        rep = "\n".join(
            "{}\nMastetype: {}    Høyde: {}m".format(self.navn, self.type, self.h),
            "Iy: {:.3g}*10^8mm^4    Iz: {:.3g}*10^6mm^4",
            "Wy_el = {:.3g}*10^3mm^3  Wz_el = {:.3g}*10^3mm^3".format(Iy, Iz, Wz, Wy),
            "Tverrsnittsbredde ved innspenning: {}mm".format(self.bredde(self.h)),
            "Største utnyttelsesgrad: " + repr(self.tilstand_UR_max),
            "Største moment My:" + repr(self.tilstand_My_max),
            "Største torsjon T:" + repr(self.tilstand_T_max),
            "Største torsjon T (ulykkeslast):" + repr(self.tilstand_T_max_ulykke),
            "Største forskyvning Dz (totalt):" + repr(self.tilstand_Dz_tot_max),
            "Største torsjonsvinkel phi (totalt):" + repr(self.tilstand_phi_tot_max),
            "Største forskyvning Dz (KL):" + repr(self.tilstand_Dz_kl_max),
            "Største torsjonsvinkel phi (KL):" + repr(self.tilstand_phi_kl_max))
        return rep

    def bredde(self, x=None):
        """Beregner total bredde av tverrsnitt.

        :param float x: Avstand fra mastens toppunkt :math:`[m]`
        :return: Tverrsnittsbredde :math:`[mm]`
        :rtype: :class:`float`
        """
        if not x:
            x = self.h
        if not self.type == "bjelke":
            return self.toppmaal + 2 * self.stigning * x * 1000
        return self.b

    def Iy(self, x, delta_topp=0, breddefaktor=1.0):
        """Beregner annet arealmoment om mastens sterk akse.

        Steinerbidraget beregnes for B- og H-master
        med hensyn til profilenes arealsenter.

        Breddefaktor kan oppgis for å ta hensyn til
        redusert effektiv bredde grunnet helning på mast.

        :param float x: Avstand fra mastens toppunkt :math:`[m]`
        :param float delta_topp: Konstant tillegg til ``x``, til hjelp ved integrasjon :math:`[m]`
        :param float breddefaktor: Faktor for å kontrollere effektiv bredde
        :return: Annet arealmoment om y-akse i angitt høyde :math:`[mm^4]`
        :rtype: :class:`float`
        """
        if self.type == "B":
            z = breddefaktor*self.bredde(x+delta_topp)/2 - self.noytralakse
            Iy = 2 * (self.Iz_profil + self.A_profil * z**2)
        elif self.type == "H":
            z = breddefaktor*self.bredde(x+delta_topp)/2 - self.noytralakse
            Iy = 4 * (self.Iy_profil + self.A_profil * z**2)
        else:  # bjelkemast
            Iy = self.Iy_profil
        return Iy

    def Iz(self, x, delta_topp=0, breddefaktor=1.0):
        """Beregner annet arealmoment om mastens svake akse.

        Steinerbidraget beregnes for B- og H-master
        med hensyn til profilenes arealsenter.

        Breddefaktor kan oppgis for å ta hensyn til
        redusert effektiv bredde grunnet helning på mast.

        :param float x: Avstand fra mastens toppunkt :math:`[m]`
        :param float delta_topp: Konstant tillegg til ``x``, til hjelp ved integrasjon :math:`[m]`
        :return: Annet arealmoment om z-akse i angitt høyde :math:`[mm^4]`
        :rtype: :class:`float`
        """

        if self.type == "B":
            Iz = 2 * self.Iy_profil
        elif self.type == "H":
            y = breddefaktor*self.bredde(x+delta_topp)/2 - self.noytralakse
            Iz = 4 * (self.Iz_profil + self.A_profil * y**2)
        else:  # bjelkemast
            Iz = self.Iz_profil
        return Iz

    def Iy_int_M(self, x, delta_topp=0):
        """Evaluerer integranden for Iy ved påsatt moment.

        Integralet er utledet fra en energibetraktning basert på
        likevekt mellom indre og ytre arbeid.
        Formlene er hentet fra bjelkens differensialligning
        samt enhetslastmetoden påført en enkel utkragerbjelke.

        :param float x: Høydevariabel for integrasjon :math:`[mm]`
        :param float delta_topp: Avstand til mastetopp det skal integreres fra :math:`[m]`
        :return: Integranden evaluert ved angitt høyde
        :rtype: :class:`float`
        """
        return x / self.Iy(x / 1000, delta_topp=delta_topp)

    def Iy_int_P(self, x, delta_topp=0):
        """Evaluerer integranden for Iy ved punktlast.

        Integralet er utledet fra en energibetraktning basert på
        likevekt mellom indre og ytre arbeid.
        Formlene er hentet fra bjelkens differensialligning
        samt enhetslastmetoden påført en enkel utkragerbjelke.

        :param float x: Høydevariabel for integrasjon :math:`[mm]`
        :param float delta_topp: Avstand til mastetopp det skal integreres fra :math:`[m]`
        :return: Integranden evaluert ved angitt høyde
        :rtype: :class:`float`
        """
        return x**2 / self.Iy(x/1000, delta_topp=delta_topp)

    def Iy_int_q(self, x, delta_topp=0):
        """Evaluerer integranden for Iy ved jevnt fordelt last.

        Integralet er utledet fra en energibetraktning basert på
        likevekt mellom indre og ytre arbeid.
        Formlene er hentet fra bjelkens differensialligning
        samt enhetslastmetoden påført en enkel utkragerbjelke.

        :param float x: Høydevariabel for integrasjon :math:`[mm]`
        :param float delta_topp: Avstand til mastetopp det skal integreres fra :math:`[m]`
        :return: Integranden evaluert ved angitt høyde
        :rtype: :class:`float`
        """
        return x**3 / self.Iy(x/1000, delta_topp=delta_topp)

    def Iz_int_P(self, x, delta_topp=0):
        """Evaluerer integranden for Iz ved punktlast.

        Integralet er utledet fra en energibetraktning basert på
        likevekt mellom indre og ytre arbeid.
        Formlene er hentet fra bjelkens differensialligning
        samt enhetslastmetoden påført en enkel utkragerbjelke.

        :param float x: Høydevariabel for integrasjon :math:`[mm]`
        :param float delta_topp: Avstand til mastetopp det skal integreres fra :math:`[m]`
        :return: Integranden evaluert ved angitt høyde
        :rtype: :class:`float`
        """
        return x**2 / self.Iz(x / 1000, delta_topp=delta_topp)

    def Iz_int_q(self, x, delta_topp=0):
        """Evaluerer integranden for Iz ved jevnt fordelt last.

        Integralet er utledet fra en energibetraktning basert på
        likevekt mellom indre og ytre arbeid.
        Formlene er hentet fra bjelkens differensialligning
        samt enhetslastmetoden påført en enkel utkragerbjelke.

        :param float x: Høydevariabel for integrasjon :math:`[mm]`
        :param float delta_topp: Avstand til mastetopp det skal integreres fra :math:`[m]`
        :return: Integranden evaluert ved angitt høyde
        :rtype: :class:`float`
        """
        return x**3 / self.Iz(x / 1000, delta_topp=delta_topp)

    def Iz_int_M(self, x, delta_topp=0):
        """Evaluerer integranden for Iz ved påsatt moment.

        Integralet er utledet fra en energibetraktning basert på
        likevekt mellom indre og ytre arbeid.
        Formlene er hentet fra bjelkens differensialligning
        samt enhetslastmetoden påført en enkel utkragerbjelke.

        :param float x: Høydevariabel for integrasjon :math:`[mm]`
        :param float delta_topp: Avstand til mastetopp det skal integreres fra :math:`[m]`
        :return: Integranden evaluert ved angitt høyde
        :rtype: :class:`float`
        """
        return x / self.Iz(x / 1000, delta_topp=delta_topp)

    def torsjonsparametre(self, x):
        """Beregner mastas torsjonsparametre ved gitt høyde.

        Torsjonsparametrene som beregnes er treghetsmoment for St. Venants
        torsjon :math:`I_T` og hvelvingskonstanten :math:`C_W`.

        Verdien ``te`` angir ekvivalent platetykkelse av diagonalstavene
        beregnet etter Per Kristian Larsens \\textit{Dimensjonering av stålkonstruksjoner}
        Tabell 5.1.

        :param float x: Avstand fra mastens toppunkt :math:`[m]`
        :return: ``It``, ``Cw``
        :rtype: :class:`float`, :class:`float`
        """
        It, Cw = self.It_profil, self.Cw_profil
        if self.type == "B":
            d_L = self.diagonallengde(x)
            te = (self.E / self.G) * 1000 * 0.9*self.bredde(x) / (d_L**3 / self.d_A)
            It = 2 * self.It_profil + (1/3) * 0.9*self.bredde(x) * te**3
            Cw = 0.5 * self.Iy_profil * (0.9 * self.bredde(x)) ** 2
        return It, Cw

    def beta(self, x=None):
        """Beregner knekklengdefaktor for lokal knekking av gurt i B-mast.

        Knekklengdefaktoren :math:`\\beta` beregnes ut fra metode gitt i
        "Stålkonstruksjoner - Profiler og formler" (Institutt for
        konstruksjonsteknikk, NTNU) Tabell 4.1, med stavsystem IV.

        Utledningen gir følgende formel for :math:`\\gamma` med
        innsatte verdier for fjærstivhet :math:`k_{\\phi}`

        :math:`\\gamma = 8(0.5 + \\frac{L_g}{L_d}\\frac{I_d}{I_g})`

        Subskript :math:`g` angir verdier for gurt,
        mens :math:`d` refererer til diagonalene.

        :math:`\\beta` tilnærmes deretter ut fra lineærinterpolering av
        verdier fra Tabell 4.4 basert på :math:`\\gamma`-verdier
        for mastehøyder mellom :math:`7` og :math:`13m`.

        Det regnes med avstivning fra 1 stk. gurt
        + 2 stk. diagonaler i hver ende.
        Gurtlengde antas lik :math:`1000mm`.

        :param float x: Avstand fra mastens toppunkt :math:`[m]`
        :return: Knekklengdefaktor
        :rtype: :class:`float`
        """
        beta = 1.0
        if self.type == "B":
            if not x:
                x = self.h
            gamma = 8*(0.5+(1000/self.diagonallengde(x-1)
                            * (self.d_I/self.Iz_profil)))
            if self.navn == "B2":
                gamma_0, gamma_1 = 7.30, 6.80
                beta_0, beta_1 = 0.62, 0.63
            elif self.navn == "B3":
                gamma_0, gamma_1 = 5.86, 5.42
                beta_0, beta_1 = 0.65, 0.66
            elif self.navn == "B4":
                gamma_0, gamma_1 = 6.35, 5.80
                beta_0, beta_1 = 0.64, 0.65
            else:  # B6
                gamma_0, gamma_1 = 11.57, 9.80
                beta_0, beta_1 = 0.58, 0.60
            beta = beta_0 + (beta_1-beta_0)/(gamma_1-gamma_0) * (gamma-gamma_0)
        return beta

    def diagonallengde(self, x=None):
        """Beregner lengde av diagonal i høyde x.

        Ved tilfelle B-mast er det påvist at forskjellige tilnærmelser
        gir varierende grad av nøyaktighet for forskjellige mastehøyder.
        Dersom :math:`x >= 6.0m` gjelder konstant innfestingsavstand
        :math:`500mm` for diagonalene, og Pytagoras' læresetning gir
        et godt anslag av diagonallengde. For seksjoner nærmere mastas
        toppunkt vil antakelsen om :math:`[45^{\\circ}]` vinkel mellom
        diagonalen og mastens lengdeakse gi en bedre tilnærmelse, da
        avstanden mellom diagonalenes innfestingspunkt ikke er kjent.

        ``s`` angir avstand fra ytterkant tverrsnitt til innfestingspunkt
        for diagonal (stegtykkelse U-profil, sidelengde L-profil).

        Dersom masta ikke har diagonaler (bjelkemast) returneres 0.

        :param float x: Avstand fra mastens toppunkt :math:`[m]`
        :return: Diagonallengde :math:`[mm]`
        :rtype: :class:`float`
        """

        if not x:
            x = self.h

        if self.type == "bjelke":
            return 0

        elif self.type == "B":
            if self.navn == "B2" or self.navn == "B3":
                s = 7.0
            elif self.navn == "B4":
                s = 7.5
            else:  # B6-mast
                s = 8.5

            if x >= 6.0:
                return math.sqrt((self.bredde(x) - 2*s)**2 + 500**2)

        else:  # H-mast
            s = self.b_f

        return (self.bredde(x) - 2*s) * math.sqrt(2)

    def dragkoeffisienter(self, x, EN1991):
        """Beregner mastens dragkoeffisienter uten islast.

        - Bjelkemaster og B-master med vind normalt spor:

          :math:`c_{f}` beregnes ut fra NS-EN 1991-1-4
          seksjon 7.7 med anbefalt verdi :math:`c_{f0} = 2.0`
          og :math:`\\psi_{\\lambda}` avlest fra figur 7.36
          under seksjon 7.13 med slankhet :math:`\\lambda = 70`.

        - B-master med vind parallelt spor, H-master:

          :math:`c_{f0}` beregnes basert på en 2.-grads
          kurvetilpasning av verdier for firkantet romlig fagverk
          med vind parallelt flatenormal, ref. NS-EN 1991-1-4
          seksjon 7.11, figur 7.34. Videre tilnærmes :math:`\\psi_{\\lambda}`
          ut fra figur 7.36 med slankhet :math:`\\lambda = 70`.

          Dersom ``EN1991`` har verdien False beregnes c_f istedenfor
          etter NS-EN 1993-3-1 seksjon B.2.2. Faktoren :math:`K_{\\theta}`
          settes lik :math:`1.0` da vinkelen :math:`\\theta` grunnet
          mastens helning i denne sammenhengen er neglisjerbar.

        :param float x: Avstand fra mastens toppunkt :math:`[m]`
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
        :math:`0.5m` høydesnitt innenfor oppgitt lengde ``x``.

        :param float x: Avstand fra mastens toppunkt :math:`[m]`
        :return: Gjennomsnittlig massivitetsforhold for vindfang
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

        Massivitetsforholdet er gitt som følger:

        :math:`\\varphi = \\frac{A}{A_c}`

        hvor :math:`A` er horisontalprojeksjonen av mastens areal
        mens :math:`A_c` er arealet av trapeset definert av
        denne projeksjonens omriss.

        Massivitetsforholdet regnes for et representativt høydesnitt
        lik :math:`0.5m` inneholdende én stk diagonal av lengde ``l``.

        Funksjonen tar forbehold om at det regnes på en gitterstruktur
        med flatenormal parallelt vindretningen (B-mast ved vindlast
        parallelt sporettningen eller H-mast ved vilkårlig vindretning).

        :param float x: Avstand fra mastens toppunkt :math:`[m]`
        :return: Massivitetsforhold for vindfang
        :rtype: :class:`float`
        """

        phi = 1.0

        if self.type is not "bjelke":
            A = self.vindareal(x) * 10**6
            A_c = 500*self._b_mid(x)
            phi = A/A_c if (A/A_c < 1.0) else 1.0

        return phi

    def vindareal_midlere(self, x):
        """Beregner midlere vindareal ved gitt mastelengde for gitterstruktur.

        Vindarealet tilnærmes ved å summere :math:`0.5m` masteutsnitt
        med én stk. diagonal per. utsnitt.

        :param float x: Avstand fra mastens toppunkt :math:`[m]`
        :return: Vindareal :math:`[\\frac{m^2}{m}]`
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
        lik :math:`0.5m` inneholdende én stk diagonal av lengde ``l``.

        For H-master regnes også et tilleggsareal fra
        kryssforsterkning ved gitte høyder.

        :param float x: Avstand fra mastens toppunkt :math:`[m]`
        :return: Vindareal :math:`[\\frac{m^2}{m}]`
        :rtype: :class:`float`
        """

        b_mid = self._b_mid(x)
        l = (b_mid-2*self.b_f)*math.sqrt(2)
        A_ref = 2*self.b_f*500 + self.d_h*l

        if self.type == "H":
            if self.navn == "H6" and x == 5.0 or 9.0:
                A_ref += (b_mid - 2 * self.b_f) * 75
            elif x == 10:
                A_ref += (b_mid - 2 * self.b_f) * 75

        return A_ref/10**6

    def _b_mid(self, x):
        """Beregner mastens midlere bredde for et :math:`0.5m` utsnitt.

        :param float x: Avstand fra mastens toppunkt :math:`[m]`
        :return:
        :rtype: :class:`float`
        """

        b = self.bredde(x)
        b0 = self.bredde(x - 0.5) if x >= 0.5 else b
        return (b0 + b) / 2

    def sorter_grenseverdier(self):
        """Lagrer høyeste absoluttverdier av utvalgte parametre i egne
        variabler.

        Tilstander med høyeste registrerte absoluttverdi av gitte
        parametre sorteres ut og lagres i egne variabler tilknyttet
        :class:`Mast`-objektet.

        Tilstandsparametre for utvelgelse blant bruddgrensetilstander:

        - Utnyttelsesgrad
        - :math:`M_{y,storste}`
        - :math:`T_{storste}`

        Tilstandsparametre for utvelgelse blant forskyvningstilstander
        (både total og KL):

        - :math:`D_{z,storste}`
        - :math:`\\phi_{storste}`
        """

        # Bruddgrense
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
            elif Dz == Dz_max:
                if phi > phi_max:
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
            elif Dz == Dz_max:
                if phi > phi_max:
                    self.tilstand_Dz_kl_max = tilstand
            if phi > phi_max:
                self.tilstand_phi_kl_max = tilstand
        # Ulykkeslast
        if self.ulykke:
            self.tilstand_T_max_ulykke = self.ulykke[0]
            for tilstand in self.ulykke:
                T_max = abs(self.tilstand_T_max.K[5])
                T = abs(tilstand.K[5])
                if T > T_max:
                    self.tilstand_T_max_ulykke = tilstand

    def lagre_tilstand(self, tilstand):
        """Lagrer tilstand i tilknyttet :class:`Mast`-objekt.

        :param Tilstand tilstand: :class:`Tilstand` som skal lagres
        """
        if tilstand.grensetilstand == 0:
            self.bruddgrense.append(tilstand)
        elif tilstand.grensetilstand == 1:
            self.forskyvning_tot.append(tilstand)
        elif tilstand.grensetilstand == 2:
            self.forskyvning_kl.append(tilstand)
        elif tilstand.grensetilstand == 3:
            self.ulykke.append(tilstand)


def hent_master(hoyde, s235, materialkoeff, avspenningsmast,
                fixavspenningsmast, avspenningsbardun):
    """Henter liste med master til beregning.
    :param float hoyde: Valgt mastehøyde :math:`[m]`
    :param Boolean s235: Angir valg av flytespenning
    :param float materialkoeff: Materialkoeffisient for dimensjonering
    :param Boolean avspenningsmast: Angir om avspenningsmast er valgt
    :param Boolean fixavspenningsmast: Angir om fixavspenningsmast er valgt
    :param Boolean avspenningsbardun: Angir om avspenningsbardun er valgt
    :return: Liste inneholdende samtlige av programmets master
    :rtype: :class:`list`
    """
    Mast.h = hoyde
    Mast.s235 = s235
    Mast.materialkoeff = materialkoeff
    Mast.L_e = hoyde*1000  # [mm]
    Mast.L_cr_y = Mast.L_e*2
    if (avspenningsmast or fixavspenningsmast) and avspenningsbardun:
        Mast.L_cr_z = Mast.L_e
    else:
        Mast.L_cr_z = Mast.L_e*2
    master = []
    csv.register_dialect('masts', delimiter=',', quoting=csv.QUOTE_NONNUMERIC, skipinitialspace=True)
    with open("data/masts.csv", 'r') as csvfile:
        reader = csv.DictReader(csvfile, dialect='masts')
        for row in reader:
            mast = {k:v for k, v in row.items() if v!=''}
            # ~ print(mast)
            master.append(Mast(**mast))
    # ~ print(master)
    return master
