# -*- coding: utf8 -*-
from __future__ import unicode_literals
import hjelpefunksjoner
import math
import numpy

import lister


class System(object):
    """Klasse for å representere alle valg av system."""

    def __init__(self, navn, ledninger, utligger,
                 B1, B2, arm, arm_sum,
                 G_sno_tung, G_sno_lett):
        """Initialiserer :class:`System`-objekt.

        :param str navn: Systemets navn (20A, 20B, 25, 35)
        :param List ledninger: Ledninger påsatt systemet
        :param dict utligger: Systemets utligger
        :param float B1: Første sikksakkverdi :math:`[m]`
        :param float B2: Andre sikksakkverdi :math:`[m]`
        :param float arm: Momentarm utligger :math:`[m]`
        :param float arm_sum: Sum momentarm aktuell + neste mast :math:`[m]`
        :param float G_sno_tung: Linjelast tung snø :math:`[\frac{N}{m}]`
        :param float G_sno_lett: Linjelast lett snø :math:`[\frac{N}{m}]`
        """

        self.navn = navn
        self.ledninger = ledninger
        self.utligger = utligger
        self.B1 = B1
        self.B2 = B2
        self.arm = arm
        self.arm_sum = arm_sum
        self.G_sno_tung = G_sno_tung
        self.G_sno_lett = G_sno_lett

        self.strekk_kl = sum([l.s for l in self.ledninger
                              if (l.type=="Bæreline" or l.type=="Kontakttråd")])
        self.alpha_kl = 1.7 * 10**(-5)
        self.strekk_fix = sum([l.s for l in self.ledninger if isinstance(l, Fix)])


    def __repr__(self):
        rep = "System {}\n\n".format(self.navn)
        rep += "Ledninger:\n"
        for ledning in self.ledninger:
            rep += "{}  \nSpennkraft: {}    Lengde: {}".format(ledning.navn, ledning.s, ledning.L)
            if isinstance(ledning, Fastavspent):
                for temperatur in ledning.temperaturdata:
                    s = ledning.temperaturdata[temperatur]["s"]
                    s_diff = ledning.temperaturdata[temperatur]["s_diff"]
                    rep += "Strekk ved {}: {}    Diff.strekk: {}\n".format(temperatur, s, s_diff)

            rep += "\n\n"
        return rep


class Ledning(object):
    """Klasse med felles attributter for alle ledninger.

    ``sporhoyde_e`` trekkes fra ``e[0]`` for å konvertere
        ledningens høydekoordinat med nullpunkt i skinneoverkant
        til mastenes lokale aksesystem med origo i mastefot.
    """

    a1 = 0.0
    a2 = 0.0
    a_mid = 0.0
    sporhoyde_e = 0.0
    G_sno_tung = 0.0
    G_sno_lett = 0.0
    rho_sno_tung = 0.0
    rho_sno_lett = 0.0
    ec3 = True

    def __init__(self, navn="", type="", G_0=0.0, d=0.0, A=0.0, L=None, e=(0, 0, 0)):
        """Initialiserer :class:`Ledning`-objekt.

        ``sporhoyde_e`` trekkes fra ``e[0]`` for å konvertere
        kreftenes lastangrepspunkt med nullpunkt i skinneoverkant
        til mastenes lokale aksesystem med origo i mastefot.

        :param str navn: Ledningens navn
        :param str type: Ledningstype
        :param float G_0: Egenvekt :math:`[\\frac{N}{m}]`
        :param float d: Diameter for lastberegninger :math:`[mm]`
        :param float A: Areal for ledningsstrekkberegninger :math:`[mm^2]`
        :param float L: Lengde (dersom ulik midlere spennlengde) :math:`[m]`
        :param List e: Eksentrisitet fra origo [x, y, z] :math:`[m]`
        """
        self.navn = navn
        self.type = type
        self.G_0 = G_0
        self.d = d/1000  #[m]
        self.A = A
        self.L = Ledning.a_mid
        if L is not None:
            self.L = L
        self.e = numpy.array(e)

        # Justerer x-koordinat for fylling/skjæring
        self.e[0] -= Ledning.sporhoyde_e
        self.e[0] = 0 if self.e[0] > 0 else self.e[0]

        # Ett eksemplar av ledningen som standard
        self.n = 1

        # Ingen isolator som standard
        self.isolatorvekt = 0

        # Dictionary med data for forskjellige temperaturer
        self.temperaturdata = {}

        # 5C, ingen snø
        self.temperaturdata["5C"] = {"D": self.d}
        # 0C, tung snø
        self.temperaturdata["0C"] = {"D": self._diameter(G_sno=Ledning.G_sno_tung,
                                                   rho_sno=Ledning.rho_sno_tung)}
        # -25C, lett snø
        self.temperaturdata["-25C"] = {"D": self._diameter(G_sno=Ledning.G_sno_lett,
                                                     rho_sno=Ledning.rho_sno_lett)}
        # -40C, ingen snø
        self.temperaturdata["-40C"] = {"D": self.d}

    def __repr__(self):
        rep = "Type = {}    Navn = {}\n".format(self.type, self.navn)
        rep += "d = {:.4g} mm    L = {:.3g} m\n".format(self.d*1000, self.L)
        rep += "e = {}\n".format(self.e)

        return rep

    def _diameter(self, G_sno, rho_sno):
        """Beregner ekvivalent linediameter for isbelagt line.

        :param G_sno: Snølast per lengdeenhet :math:`[\frac{N}{m}]`
        :param rho_sno: Snøens densitet :math:`[\frac{kg}{m^3}]`
        :return: Ekvivalent linediameter :math:`[m]`
        :rtype: :class:`float`
        """

        if Ledning.ec3:
            return self.d
        else:
            return math.sqrt(self.d**2 + 4*G_sno/(math.pi*9.81*rho_sno))


class Loddavspent(Ledning):
    """Klasse for å representere loddavspente ledninger."""

    def __init__(self, s=0.0, **kwargs):
        """Initialiserer :class:`Loddavspent`-objekt.

        :param float s: Strekkraft :math:`[kN]`
        :param kwargs: Argumenter til superklasse :class:`Ledning`
        """

        super().__init__(**kwargs)

        self.s = s * 1000  #[N]


class Fix(Ledning):
    """Klasse for å representere fixline."""

    def __init__(self, s=0.0, **kwargs):
        """Initialiserer :class:`Loddavspent`-objekt.

        :param float s: Strekkraft :math:`[kN]`
        :param kwargs: Argumenter til superklasse :class:`Ledning`
        """

        super().__init__(**kwargs)

        self.s = s * 1000  # [N]


class Fastavspent(Ledning):
    """Klasse for å representere fastavspente ledninger."""

    auto_differansestrekk = True
    differansestrekk_manuelt = 0.0

    def __init__(self, E, alpha, s, n=1, isolatorvekt=0, **kwargs):
        """Initialiserer :class:`Fastavspent`-objekt.

        Strekk i ledning under forskjellige klimatiske forhold
         beregnes ut fra initielle spennkrefter ved temperatur
         :math:`T=5^{\\circ}C` og hhv. 30m og 70m spennlengde
         (``s30``, ``s70``).

        :param float E: E-modul :math:`[\\frac{N}{mm^2}]`
        :param float alpha: Lengdeutvidelseskoeffisient :math:`[\\frac{1}{^{\\circ}C}]`
        :param tuple s: Initiell strekkraft ved spennlengde hhv. (30m, 70m) :math:`[kN]`
        :param float n: Antall eksemplarer av gitt ledning
        :param float isolatorvekt: Vekt av isolator (per. ledning) :math:`[N]`
        :param kwargs: Argumenter til superklasse :class:`Ledning`
        """

        super().__init__(**kwargs)

        self.E = E
        self.alpha = alpha
        self.n = n
        self.isolatorvekt = isolatorvekt

        # Initialstrekk ved 5C (ingen snø)
        self.temperaturdata["5C"].update(self._strekk_initiell(s))
        # Bruker initialstrekk ved 5C som standard strekkverdi
        self.s = self.temperaturdata["5C"]["s"]
        # Strekk ved 0C (tung snø)
        self.temperaturdata["0C"].update(self._strekk(G_sno=Ledning.G_sno_tung, T=0))
        # Strekk ved -25C (lett snø)
        self.temperaturdata["-25C"].update(self._strekk(G_sno=Ledning.G_sno_lett, T=-25))
        # Strekk ved -40C (ingen snø)
        self.temperaturdata["-40C"].update(self._strekk(G_sno=0.0, T=-40))


    def _strekk_initiell(self, s_init):
        """Beregner initiell strekkraft mhp. masteavstand.

        Kraften beregnes ut fra lineærinterpolering mellom
        tabulerte verdier for strekkrefter `` s30`` og ``s70``
        ved temperatur :math:`T=5^{\\circ}C`.

        :param float s30: Strekk ved 30m masteavstand :math:`[kN]`
        :param float s70: Strekk ved 70m masteavstand :math:`[kN]`
        :param float masteavstand: Faktisk masteavstand :math:`[m]`
        :return: Strekkraft :math:`[N]`, differansestrekk :math:`[N]`
        :rtype: :class:`dict`
        """

        (s30, s70) = s_init
        s = 1000 * (s30 + (Ledning.a_mid - 30) * (s70 - s30) / 40)
        s_diff = self._strekk(G_sno=0.0, T=5, H_0=s)["s_diff"]

        return {"s": s, "s_diff": s_diff}

    def _strekk(self, G_sno, T, H_0=None):
        """Beregner strekk og differansestrekk under gitte forhold.

        :param float G_sno: Egenvekt snølast :math:`[\\frac{N}{m}]`
        :param float T: Lufttemperatur :math:`[^{\\circ}C]`
        :param float H_0: Initiell spennkraft i kabel :math:`[N]`
        :return: Strekkraft :math:`[N]`, differansestrekk :math:`[N]`
        :rtype: :class:`dict`
        """

        s = self._strekklikevekt(L=Ledning.a_mid, G_sno=G_sno, T=T, H_0=H_0)

        if Fastavspent.auto_differansestrekk:
            s_1 = self._strekklikevekt(L=Ledning.a1, G_sno=G_sno, T=T, H_0=H_0)
            s_2 = self._strekklikevekt(L=Ledning.a2, G_sno=G_sno, T=T, H_0=H_0)
            s_diff = abs(s_1-s_2)
        else:
            s_diff = Fastavspent.differansestrekk_manuelt

        return {"s": s, "s_diff": s_diff}

    def _strekklikevekt(self, L, G_sno, T, H_0=None):
        """Finner kabelstrekk under gitte forhold for fastavspent ledning.

        Følgende likevektsligning ligger til grunn for beregningene:

        :math:`H_x^2 [H_x - H_0 + \\frac{EA(G_0 L)^2}{24H_0^2} + EA\\alpha \\Delta_T]
        = \\frac{EA(G_x L)^2}{24}`

        Løsningen finnes ved å finne den reelle, positive egenverdien
        tilhørende "companion matrix" for residualfunksjonens koeffisienter.

        :param float H_0: Initiell spennkraft i kabel :math:`[N]`
        :param float E: Kabelens E-modul :math:`[\\frac{N}{mm^2}]`
        :param float A: Kabelens tverrsnittsareal :math:`[mm^2]`
        :param float G_0: Kabelens egenvekt :math:`[\\frac{N}{m}]`
        :param float G_sno: Egenvekt snølast :math:`[\\frac{N}{m}]`
        :param float L: Masteavstand :math:`[m]`
        :param float alpha: Lengdeutvidelseskoeffisient :math:`[\\frac{1}{^{\\circ}C}]`
        :param float T: Lufttemperatur :math:`[^{\\circ}C]`
        :return: Endelig kabelstrekk ``H_x`` :math:`[N]`
        :rtype: :class:`float`
        """

        # Inngangsparametre
        if H_0 is not None:
            H_0 = H_0
        else:
            H_0 = self.temperaturdata["5C"]["s"]
        E = self.E
        A = self.A
        G_0 = self.G_0
        alpha = self.alpha
        G_x = G_0 + G_sno
        delta_T = T - 5

        # Konstanter
        a = E * A * (G_x * L) ** 2 / 24
        b = - H_0 + E * A * (G_0 * L) ** 2 / (24 * H_0 ** 2) + E * A * alpha * delta_T

        roots = numpy.roots([-1, -b, 0, a])
        H_x = 0
        for r in roots:
            if numpy.isreal(r) and r > 0:
                H_x = numpy.real(r)
                break

        return H_x


def hent_system(i):
    """Henter :class:`System` med data for ledninger, utliggere og strømavtaker.

    Ledningenes strekkraft ved snøfri line og :math:`T = -40^{\\circ}C`
    samt strekk ved snøbelastet line og :math:`T = -25^{\\circ}C` beregnes
    ved hjelp av Newton-Raphson-iterasjon ut fra tabulerte verdier for
    kabelstrekk ved :math:`T = 5^{\\circ}C`.

    :param Inndata i: Input fra bruker
    :return: Systemkonfigurasjon
    :rtype: :class:`System`
    """

    Ledning.a1 = i.a1
    Ledning.a2 = i.a2
    a_mid = (i.a1+i.a2)/2
    Ledning.a_mid = a_mid
    Ledning.delta_h1 = i.delta_h1
    Ledning.delta_h2 = i.delta_h2
    Ledning.sporhoyde_e = i.e
    Ledning.G_sno_lett = float(i.isklasse[i.isklasse.find("(")+1:i.isklasse.find("N")-1])
    Ledning.G_sno_tung = Ledning.G_sno_lett * 2
    Ledning.rho_sno_tung = 700
    Ledning.rho_sno_lett = 600
    Ledning.ec3 = i.ec3
    Fastavspent.auto_differansestrekk = i.auto_differansestrekk
    Fastavspent.differansestrekk_manuelt = i.differansestrekk

    systemnavn = i.systemnavn.split()[1] if i.systemnavn.startswith("System") else i.systemnavn

    # Beregner geometrikonstanter for aktuell systemkonfigurasjon
    B1, B2 = hjelpefunksjoner.beregn_sikksakk(systemnavn, i.radius)
    arm, arm_sum = _beregn_arm(systemnavn, i.radius, i.sms, i.fh, i.strekkutligger, B1)

    # HUSK TRAVERSLENGDE e_t VED DOBBEL UTLIGGER

    # Bæreliner
    e_x_bl = -(i.sh + i.fh)
    Cu_50_7 = Loddavspent(navn="Cu 50/7", type="Bæreline",
                          G_0=4.46, d=9.0, A=49.48, s=7.1,
                          e=(e_x_bl, 0, arm))
    Bz_II_50_19 = Loddavspent(navn="Bz II 50/19", type="Bæreline",
                              G_0=4.37, d=9.0, A=48.35, s=10.0,
                              e=(e_x_bl, 0, arm))
    Bz_II_70_19 = Loddavspent(navn="Bz II 70/19", type="Bæreline",
                              G_0=5.96, d=10.5, A=65.81, s=15.0,
                              e=(e_x_bl, 0, arm))
    # Kontakttråder
    Ri_100_Cu_s35 = Loddavspent(navn="Ri 100 Cu", type="Kontakttråd",
                                G_0=8.9, d=12.0, A=100.0, s=7.1,
                                e=(-i.fh, 0, arm))
    Ri_100_Cu = Loddavspent(navn="Ri 100 Cu", type="Kontakttråd",
                            G_0=8.9, d=12.0, A=100.0, s=10.0,
                            e=(-i.fh, 0, arm))
    Ri_120_CuAg = Loddavspent(navn="Ri 120 CuAg", type="Kontakttråd",
                              G_0=10.7, d=13.2, A=120.0, s=15.0,
                              e=(-i.fh, 0, arm))

    # Hengetråd (inkl. klemmer)
    L_h = 8 * a_mid / 60
    e_x_ht = -(i.fh + i.sh/2)
    Bz_II_10_49 = Loddavspent(navn="Bz II 10/49", type="Hengetråd",
                              G_0=4.69, d=4.5, A=9.6, L=L_h,
                              e=(e_x_ht, 0, arm))
    Bz_II_10_49_35 = Loddavspent(navn="Bz II 10/49", type="Hengetråd",
                                 G_0=10.69, d=4.5, A=9.6, L=L_h,
                                 e=(e_x_ht, 0, arm))
    # Y-line
    L_y = 0
    e_x_yl = -(i.sh + i.fh)
    if (systemnavn == "20A" or systemnavn == "35") and i.radius >= 800:
        L_y = 14
    elif systemnavn == "25" and i.radius >= 1200:
        L_y = 18
    Bz_II_35_7 = Loddavspent(navn="Bz II 35/7", type="Y-line",
                             G_0=3.1, d=7.5, A=34.36, L=L_y,
                             e=(e_x_yl, 0, arm))
    Bz_II_35_7_25 = Loddavspent(navn="Bz II 35/7", type="Y-line",
                                G_0=16.1, d=7.5, A=34.36, L=L_y,
                                e=(e_x_yl, 0, arm))
    # Fixliner
    L_fix = 0
    e_x_fix = -(i.sh + i.fh)
    e_z_fix = 0
    if i.fixpunktmast:
        L_fix = a_mid
        e_z_fix = i.sms
    elif i.fixavspenningsmast:
        L_fix = i.a1 / 2
    Bz_II_50_19_fix = Fix(navn="Bz II 50/19", type="Fixline",
                          G_0=4.37, d=9.0, A=48.35,
                          s=10.0, L=L_fix, e=(e_x_fix, 0, e_z_fix ))
    Bz_II_70_19_fix = Fix(navn="Bz II 70/19", type="Fixline",
                          G_0=5.96, d=10.5, A=65.81,
                          s=10.0, L=L_fix, e=(e_x_fix, 0, e_z_fix ))


    # Forbigangsledning
    e_z_forbigang = -0.3
    if not i.matefjern_ledn and not i.at_ledn and not i.jord_ledn:
        e_z_forbigang = 0
    Al_240_61 = Fastavspent(navn="Al 240-61", type="Forbigangsledning",
                            G_0=6.43, d=20.3, A=242.54, E=56000,
                            alpha=2.3 * 10 ** (-5), s=(2.48, 2.78),
                            isolatorvekt=150, e=[-i.hf, 0, e_z_forbigang])

    # Returledninger
    Al_240_61_iso = Fastavspent(navn="Al 240-61 isolert", type="Returledninger",
                                G_0=7.63, d=23.9, A=242.54, E=56000,
                                alpha=2.3 * 10 ** (-5), s=(2.95, 3.28),
                                n=2, isolatorvekt=100, e=[-i.hr, 0, -0.5])

    # Mate-/fjernledninger
    ending = "er" if i.matefjern_antall > 1 else ""
    SAHF_120_26_7 = Fastavspent(navn="SAHF 120 Feral", type="Mate-/fjernledning{}".format(ending),
                                G_0=7.56, d=19.38, A=222.35, E=76000,
                                alpha=1.9 * 10 ** (-5), s=(2.77, 3.06),
                                n=i.matefjern_antall, isolatorvekt=110,
                                e=[-i.hfj, 0, 0])

    # Fiberoptiske kabler
    # Det antas en (konservativ) oppspenningskraft på 1.5kN for fiberoptisk kabel.
    ADSS_GRHSLLDV_9_125 = Fastavspent(navn="ADSS GRHSLLDV 9/125", type="Fiberoptisk ledning",
                                      G_0=2.65, d=18.5, A=268.9, E=12000,
                                      alpha=3.94 * 10 ** (-5), s=(1.5, 1.5),
                                      e=[-i.hf, 0, -0.3])

    # AT-ledninger
    # Ved manglende strekktabeller for Al 400-37 og 240-19 er verdier for
    # Al 400-61 og 240-61 benyttet. Strekkverdier for Al 150-19 ekstrapoleres
    # ut fra arealforholdet mellom denne og Al 400-37 (ca. 40%).
    e_at = [-i.hfj, 0, 0]
    Al_400_37 = Fastavspent(navn="Al 400-37", type="AT-ledninger",
                            G_0=10.31, d=25.34, A=381.0, E=56000,
                            alpha=2.3 * 10 ** (-5), s=(4.09, 4.59),
                            n=2, e=e_at)
    Al_240_19 = Fastavspent(navn="Al 240-19", type="AT-ledninger",
                            G_0=6.46, d=20.0, A=238.76, E=56000,
                            alpha=2.3 * 10 ** (-5), s=(2.48, 2.78),
                            n=2, e=e_at)
    Al_150_19 = Fastavspent(navn="Al 150-19", type="AT-ledninger",
                            G_0=4.07, d=15.9, A=150.90, E=56000,
                            alpha=2.3 * 10 ** (-5),
                            s=(0.4 * 4.09, 0.4 * 4.59),
                            n=2, e=e_at)

    # Jordledninger
    e_z_jord = -0.3
    if not i.matefjern_ledn and not i.at_ledn and not i.forbigang_ledn:
        e_z_jord = 0
    e_jord = [-i.hj, 0, e_z_jord]
    KHF_70 = Fastavspent(navn="KHF-70", type="Jordledning",
                         G_0=5.81, d=10.5, A=66.75, E=116000,
                         alpha=1.7 * 10 ** (-5), s=(2.09, 2.25),
                         e=e_jord)
    KHF_95 = Fastavspent(navn="KHF-95", type="Jordledning",
                         G_0=8.25, d=12.5, A=94.7, E=116000,
                         alpha=1.7 * 10 ** (-5), s=(2.97, 3.20),
                         e=e_jord)


    # Utliggere (s2x for system 20A/20B/25, s3x for system 35)
    utligger_s2x = {"Egenvekt": 170, "Momentarm": 0.35}
    utligger_s3x = {"Egenvekt": 200, "Momentarm": 0.40}

    # Legger til ledninger og utligger avhengig av valgt system
    if systemnavn == "20A":
        ledninger = [Bz_II_50_19, Ri_100_Cu, Bz_II_10_49]
        if i.radius >= 800:
            ledninger.append(Bz_II_35_7)
        utligger = utligger_s2x

    elif systemnavn == "20B":
        ledninger = [Bz_II_50_19, Ri_100_Cu, Bz_II_10_49]
        utligger = utligger_s2x

    elif systemnavn == "25":
        ledninger = [Bz_II_70_19, Ri_120_CuAg, Bz_II_10_49_35]
        if i.radius >= 1200:
            ledninger.append(Bz_II_35_7_25)
        utligger = utligger_s2x

    else:  # System 35
        ledninger = [Cu_50_7, Ri_100_Cu_s35, Bz_II_10_49]
        if i.radius >= 800:
            ledninger.append(Bz_II_35_7)
        utligger = utligger_s3x

    # Legger til eventuell fixline
    if i.fixpunktmast or i.fixavspenningsmast:
        if systemnavn == "25":
            ledninger.append(Bz_II_70_19_fix)
        else:
            ledninger.append(Bz_II_50_19_fix)

    # Legger til valgte fastavspente ledninger
    if i.matefjern_ledn:
        ledninger.append(SAHF_120_26_7)
    if i.at_ledn:
        for l in [Al_400_37, Al_240_19, Al_150_19]:
            if l.navn == i.at_type:
                ledninger.append(l)
                break
    if i.forbigang_ledn:
        ledninger.append(Al_240_61)
    if i.jord_ledn:
        for l in [KHF_70, KHF_95]:
            if l.navn == i.jord_type:
                ledninger.append(l)
                break
    if i.fiberoptisk_ledn:
        ledninger.append(ADSS_GRHSLLDV_9_125)
    if i.retur_ledn:
        ledninger.append(Al_240_61_iso)

    return System(systemnavn, ledninger, utligger, B1, B2, arm, arm_sum, Ledning.G_sno_tung, Ledning.G_sno_lett)


def _beregn_arm(systemnavn, radius, sms, fh, strekkutligger, B1):
    """Beregner momentarm for utligger.

    ``arm`` angir KLs faktiske momentarm i forhold til nullpunkt
    i mastens koordinatsystem, mens ``arm_sum`` angir summen av
    denne og arm for neste mast dersom master bytter side av sporet.
    Det antas i dette tilfellet at én mast har trykkutligger, mens
    den andre har strekkutligger.

    :param int radius: Sporkurvaturens radius :math:`[m]`
    :param float sms: Avstand senter mast - senter spor :math:`[m]`
    :param float fh: Kontakttrådhøyde :math:`[m]`
    :param float B1: Første sikksakkverdi :math:`[m]`
    :return: Momentarmer ``arm`` og ``arm_sum`` :math:`[m]`
    :rtype: :class:`float`
    """

    r = radius
    b = abs(B1)

    # Overhøyde, UE i [m], pga kurveradius i [m]
    if systemnavn=="20A":
        ue = lister.D_20A
    elif systemnavn == "20B":
        ue = lister.D_20B_35
    elif systemnavn=="25":
        ue = lister.D_25
    else:  # System 35
        ue = lister.D_20B_35

    # Momentarm [m] for strekkutligger
    a_T = sms + fh * (ue[str(r)] / 1.435) - b
    # Momentarm [m] for trykkutligger
    a_T_dot = sms - fh * (ue[str(r)] / 1.435) + b

    arm = a_T
    if not strekkutligger:
        arm = a_T_dot

    arm_sum = a_T + a_T_dot

    return arm, arm_sum


if __name__=="__main__":
    pass