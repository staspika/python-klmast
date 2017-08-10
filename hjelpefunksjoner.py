# -*- coding: utf8 -*-
"""Diverse funksjoner til bruk andre steder i programmet."""
from __future__ import unicode_literals

import math
import lister

def vindkasthastighetstrykk(v_b_0, c_dir, c_season, c_alt, c_prob, c_0, terrengkategori, z):
    """Beregner dimensjonerende vindkasthastighetstrykk mhp. Eurokode 0.

    :param float v_b_0 Referansevindhastighet for aktuell kommune :math:`[\frac{m}{s}]`
    :param c_dir: Retningsfaktor
    :param c_season: Årstidsfaktor
    :param c_alt: Nivåfaktor
    :param c_prob: Faktor dersom returperioden er mer enn 50 år
    :param c_0: Terrengformfaktor
    :param terrengkategori: Terrengkategori
    :param float z: Høyde over bakken :math:`[m]`
    :return: Vindkasthastighetstrykk :math:`[\\frac{N}{m^2}]`
    :rtype: :class:`float`
    """

    # Basisvindhastighet [m/s]
    v_b = c_dir * c_season * c_alt * c_prob * v_b_0

    k_r = lister.terrengkategorier[terrengkategori]["k_r"]
    z_0 = lister.terrengkategorier[terrengkategori]["z_0"]
    z_min = lister.terrengkategorier[terrengkategori]["z_min"]
    z_max = 200

    if z > z_max:
        z = z_max

    if z <= z_min:
        c_r = k_r * math.log(z_min / z_0)
    else:
        c_r = k_r * math.log(z / z_0)

    # Stedets middelvindhastighet [m/s]
    v_m = c_r * c_0 * v_b

    # Stedets vindhastighetstrykk [N/m^2]
    rho = 1.25                  # [kg/m^3] Luftens densitet
    q_m = 0.5 * rho * v_m**2    # [N / m^2]

    # Turbulensintensiteten
    k_l = 1.0  # Turbulensintensiteten, anbefalt verdi er 1.0
    k_p = 3.5
    if z <= z_min:
        I_v = k_l / (c_0 * math.log(z_min / z_0))
    else:
        I_v = k_l / (c_0 * math.log(z / z_0))


    # Vindkasthastigheten
    v_p = v_m * math.sqrt(1 + 2 * k_p * I_v)

    # Vindkasthastighetstrykket
    q_p = q_m * (1 + 2 * k_p * I_v)  # [N/m^2]

    return q_p, v_b, v_m, v_p, q_m


def _c_alt(v_b_0, region, H):
    """ Beregner faktor for vindøkning med høyden over havet.

    :param v_b_0:
    :param region:
    :param H:
    :return:
    """

    v_0 = 30

    if v_b_0<v_0:
        H_0 = lister.regioner[region]["H_0"]
        H_topp = lister.regioner[region]["H_topp"]
        return 1.0 + (v_0 - v_b_0) * (H - H_0) / (v_b_0 * (H_topp - H_0))
    else:
        return 1.0

def beregn_sikksakk(systemnavn, radius):
    """Beregner sikksakk og største tillat utblåsning av KL.

    :param str systemnavn: Systemets navn
    :param int radius: Sporkurvaturens radius :math:`[m]`
    :return: Sikksakkverdier ``B1`` og ``B1`` :math:`[m]`
    :rtype: :class:`float`, :class:`float`
    """

    r = radius

    # Systemavhengige sikksakk-verdier til input i største masteavstand.
    # struktur i sikksakk-ordbøker under: { "radius": [B1, B2] } i [m]
    # største tillatt utblåsning e_max i [m], bestemmes i indre if-setning.
    if systemnavn == "20A" or systemnavn == "20B":
        sikksakk = lister.sikksakk_20
    elif systemnavn == "25":
        sikksakk = lister.sikksakk_25
    else:  # System 35
        sikksakk = lister.sikksakk_35

    B1 = 0
    B2 = 0
    if r in sikksakk:
        B1 = sikksakk[str(r)][0]
        B2 = sikksakk[str(r)][1]

    return B1, B2


def beregn_masteavstand(sys, radius, B1, B2, e_max, q):
    """Beregner største tillatt masteavstand.

    :param System sys: Data for ledninger og utligger
    :param int radius: Sporkurvaturens radius :math:`[m]`
    :param float B1: Første sikksakkverdi :math:`[m]`
    :param float B2: Andre sikksakkverdi :math:`[m]`
    :param float e_max: Max tillatt utblåsning :math:`[m]`
    :param float q: Vindlast på kontaktledningen :math:`[\\frac{N}{m}]`
    :return: Max tillatt masteavstand :math:`[m]`
    :rtype: :class:`float`
    """

    r = radius                                          # [m]
    s_kl = sys.kontakttraad["Strekk i ledning"] * 1000  # [N]

    # KL blåser UT fra kurven
    a1 = math.sqrt(((2 * s_kl) / (q - (s_kl / r))) * ((2 * e_max - B1 - B2)
                   + math.sqrt((2 * e_max - B1 - B2) ** 2 - (B1 - B2) ** 2)))

    # KL blåser INN i kurven
    a2 = math.sqrt(((2 * s_kl) / (q + (s_kl / r))) * ((2 * e_max + B1 + B2)
                   + math.sqrt((2 * e_max + B1 + B2) ** 2 - (B1 - B2) ** 2)))

    a = min(a1, a2)

    if a > 60 and sys.navn == "35":
        a = 60
        print(a)

    if a > 65 and (sys.navn == "25" or
                     sys.navn == "20A" or
                     sys.navn == "20B"):
        a = 65
        print(a)

    return a


def vindutblasning(systemnavn, radius, fh, stromavtaker, v_egendefinert=None):
    """Beregner maksimal tillatt utblåsning av KL.

    Verdien beregnes i henhold til EN 50367 kapittel 5.2.5.3.

    :param str systemnavn: Valgt system
    :param int radius: Sporkurvaturens radius :math:`[m]`
    :param int fh: Kontakttrådhøyde :math:`[m]`
    :param str stromavtaker: Valgt strømavtaker
    :param int v_egendefinert: Overstyrer automatisk kjørehastighet :math:`[\frac{m}{s}]`
    :return: Maksimal tillatt vindutblåsning
    :rtype: :class:`float`
    """

    R = radius
    h_nom = fh

    if systemnavn=="20A":
        S_OCL = 20000
        v = 200
        D = lister.D_20A[str(R)]
    elif systemnavn == "20B":
        S_OCL = 20000
        v = 160
        D = lister.D_20B_35[str(R)]
    elif systemnavn=="25":
        S_OCL = 30000
        v = 250
        D = lister.D_25[str(R)]
    else:  # System 35
        S_OCL = 14126
        v = 150
        D = lister.D_20B_35[str(R)]

    if v_egendefinert is not None:
        v = v_egendefinert

    if v<=200:
        F_m = 0.00047 * v**2 + 90
    else:
        F_m = 0.00097 * v**2 + 70

    b_v = stromavtaker["b_v"]
    b_w = stromavtaker["b_w"]
    b_wc = stromavtaker["b_wc"]
    alpha = math.radians(stromavtaker["alpha"])

    d = 1.410
    d_cant = 0.010
    d_inst = 0.030
    d_instv = 0.030
    d_mess = 0.015
    d_pole = 0.025
    d_supp = 0.010

    D_0 = 0.066
    e_po = 0.170
    e_pu = 0.110
    f_s = 0.22

    h_c0 = 0.50

    h_o_merket = 6.50
    h_u_merket = 5.00

    k_merket = 1.0
    l_max = 1.465
    L = 1.500
    L_sp = 75

    s_0_merket = 0.225
    T_charge = math.radians(0.77)
    T_D = 0.015
    T_osc = 0.065
    T_susp = math.radians(0.23)
    T_voie = 0.025

    h_ref = h_nom + f_s + d_instv

    # Sportoleranser (nedre verifikasjonspunkt)
    h_delta = (h_u_merket-h_c0)
    sum_T_Tu_2 = (T_voie**2 +
                  (T_D/L*h_u_merket + s_0_merket/L*T_D*h_delta)**2 +
                  (math.tan(T_susp)*h_delta)**2 +
                  (math.tan(T_charge)*h_delta)**2 +
                  (s_0_merket/L*T_osc*h_delta)**2)

    # Sportoleranser (øvre verifikasjonspunkt)
    h_delta = (h_o_merket-h_c0)
    sum_T_To_2 = (T_voie**2 +
                  (T_D/L*h_o_merket + s_0_merket/L*T_D*h_delta)**2 +
                  (math.tan(T_susp)*h_delta)**2 +
                  (math.tan(T_charge)*h_delta)**2 +
                  (s_0_merket/L*T_osc*h_delta)**2)

    # Tilleggskast innerside/ytterside av kurver
    s_ia_merket = 2.5/R + (l_max-d)/2

    # Kvasistatisk effekt
    if D-D_0 >= 0:
        qs_ia_merket = s_0_merket/L * (D-D_0) * (h_ref-h_c0)
    else:
        qs_ia_merket = 0

    # Sideveis bevegelse av kontakttråd grunnet ikke-horisontale
    # deler av straømavtakerens vippeprofil
    u_p = (L_sp * F_m * math.tan(alpha)) / (4 * S_OCL)

    # Kontaktledningens toleranser
    sum_T_OCL_2 = d_cant**2 + d_inst**2 + d_mess**2 + d_pole**2 + d_supp**2 + u_p**2

    # Stabilitetsgrense til mekanisk frittromsprofil for strømavtaker (nedre verifikasjonspunkt)
    b_u_mec_merket = b_v + e_pu + s_ia_merket + qs_ia_merket + \
                     k_merket * math.sqrt(sum_T_Tu_2+sum_T_OCL_2)

    # Stabilitetsgrense til mekanisk frittromsprofil for strømavtaker (øvre verifikasjonspunkt)
    b_o_mec_merket = b_v + e_po + s_ia_merket + qs_ia_merket + \
                     k_merket * math.sqrt(sum_T_To_2 + sum_T_OCL_2)

    # Stabilitetsgrense til mekanisk frittromsprofil for samspill mellom
    # strømavtaker og kontakttråd i referansehøyde h_ref
    b_h_mec_merket = b_u_mec_merket + \
                     (h_ref-h_u_merket)/(h_o_merket-h_u_merket)*(b_o_mec_merket-b_u_mec_merket)

    # Stabilitetsgrense for tillat sideveis forskyvning av kontakttråd uten trådavsporing
    d_lv = b_w + b_v - b_h_mec_merket

    # Driftsgrense til mekanisk frittromsprofil for strømavtaker (nedre verifikasjonspunkt)
    b_u_OCL_merket = b_w + e_pu + s_ia_merket + qs_ia_merket

    # Driftsgrense til mekanisk frittromsprofil for strømavtaker (øvre verifikasjonspunkt)
    b_o_OCL_merket = b_w + e_po + s_ia_merket + qs_ia_merket

    # Driftsgrense til mekanisk frittromsprofil for samspill mellom
    # strømavtaker og kontakttråd i referansehøyde h_ref
    b_h_OCL_merket = b_u_OCL_merket + \
                     (h_ref-h_u_merket)/(h_o_merket-h_u_merket)*(b_o_OCL_merket-b_u_OCL_merket)

    # Driftsgrense for tillat sideveis forskyvning av kontakttråd uten trådavsporing
    d_lg = b_w + b_wc - b_h_OCL_merket

    # Tillat sideveis forskyvning av kontakttråd fra spormidt
    d_l = min([d_lv, d_lg])

    return d_l, v




# Følgende funksjoner for valdiering av inputdata er uferdige!

def sjekk_fh(i):
    """Kontrollerer FH: Høyde av kontakttråd."""

    if i.fh > 6.5 or i.fh < 4.8:
        print("Kontakttrådhøyden er ikke gyldig.")
        return False
    print("FH er OK.")
    return True


def sjekk_sh(i):
    """Kontrollerer SH: Systemhøyden."""

    if i.sh > 2.0 or i.sh < 0.2:
        print("Systemhøyden er ikke gyldig.")
        return False
    print("SH er OK.")
    return True


def sjekk_e(i):
    """Kontrollerer e: Avstanden SOK - toppmaal fundament."""

    if i.e > 3.0 or i.e < -(i.FH - 0.6):
        print("Ugyldig avstand til toppmaal fundament.")
        return False
    print("e er OK.")
    return True


def sjekk_sms(i):
    """Kontrollerer SMS: Avstanden s_mast - s_spor."""

    if i.sms > 6.0 or i.sms < 2.0:
        print("SMS avstanden er ugyldig.")
        return False
    print("SMS er OK.")
    return True


def valider_ledn(i):
    """Validerer gyldige kombinasjoner av ledninger."""

    if i.at_ledn and i.matefjern_ledn:
        print("Mate-/fjern- og AT-ledning kan ikke henges opp samtidig.")
        return False
    elif i.at_ledn and i.forbigang_ledn:
        print("Forbigangs- og AT-ledning kan ikke henges opp samtidig.")
        return False
    elif i.at_ledn and i.retur_ledn:
        print("Retur- og AT-ledning kan ikke henges opp samtidig.")
        return False
    elif i.forbigang_ledn and i.fiberoptisk_ledn:
        print("Forbigangs- og fiberoptisk ledning kan ikke henges opp samtidig.")
        return False
    else:
        print("Kombinasjonen av ledninger er OK.")
        return True


def hoyde_mast(i):
    """Høyde av KL-mast målt fra toppmaal fundament."""

    # Dersom mate-/fjern, AT- eller jordledning henger i masten.
    if i.matefjern_ledn or i.at_ledn or i.jord_ledn:
        H = i.fh + i.sh + i.e + 2.5
        if sjekk_h(H):
            return H
    # Dersom forbigangs- OG returledning henger i masten.
    elif i.forbigang_ledn and i.retur_ledn:
        H = i.fh + i.sh + i.e + 2.0
        if sjekk_h(H):
            return H
    # Hvis, og bare hvis, returledning henger alene i masten.
    elif i.retur_ledn and (not i.matefjern_ledn
                           and not i.at_ledn
                           and not i.forbigang_ledn
                           and not i.jord_ledn
                           and not i.fiberoptisk_ledn):
        H = i.fh + i.sh + i.e + 0.7
        if sjekk_h(H):
            return H
    # Mastehøyde dersom ingen fastavspente ledninger i masten.
    else:
        H = i.fh + i.sh + i.e + 0.7
        if sjekk_h(H):
            return H


def sjekk_h(H):
    """Kontrollerer høyde av KL-mast."""

    if (H - 1.5) < H < (H + 5.0):
        return True
    return False


def hoyde_fjernledn(i):
    """Høyde av mate-/fjern- eller AT-ledning målt fra SOK."""

    # Mate-/fjern- eller AT- og forbigangsledning i masten.
    if i.matefjern_ledn or (i.at_ledn and i.forbigang_ledn):
        return i.h - i.e + 0.5
    # Mate-/fjern- eller AT-ledning alene i masten
    elif (i.matefjern_ledn or i.at_ledn) and not i.forbigang_ledn:
        return i.fh + i.sh + 3.0
    else:
        print("Jordledningen henger i toppen av masten.")
        return False


def sjekk_atledn(i):
    """AT-ledningen kan ikke henge lavere enn Hfj = FH + SH + 3.3m."""

    if i.at_ledn:
        if i.hfj < (i.fh + i.sh + 3.3):
            print("Kritisk liten avstand mellom AT-ledning og KL-anlegget")
            return False


def sjekk_hfj(i):
    """Kontrollerer Hfj: Høyde av forbigangsledning."""
    if i.hfj > (i.max_hoyde + 2.0):
        print("Mate-/fjern- eller AT-ledningen henger for høyt.")
        return False
    elif i.hfj < (i.h - i.e):
        print("Mate-/fjern- eller AT-ledningen henger for lavt.")
        return False
    else:
        print("Hfj er OK.")
        return True


def hoyde_forbigangledn(i):
    """Høyde, samt kontroll av høyde, for forbigangsledning målt fra SOK."""

    # Forbigangsledning alene i masten => Hf i toppen.
    if i.forbigang_ledn and (not i.matefjern_ledn
                             and not i.at_ledn
                             and not i.jord_ledn):
        print("Forbigangsledningen henger i toppen av masten.")
        hf = i.fh + i.sh + 2.5
        if hf > (i.max_hoyde + 2.0):
            return False
        elif hf < (i.h - i.e):
            return False
        else:
            return i.fh + i.sh + 2.5
    # Mate-/fjern- i tillegg til forbigangsledning i masten, Hf i topp.
    elif i.forbigang_ledn and (i.matefjern_ledn or i.at_ledn):
        hf = i.h - i.e + 0.5
        if hf > (i.max_hoyde + 2.0):
            return False
        elif hf < (i.h - i.e):
            return False
        else:
            return True
    # Mate-/fjern, AT- eller jordledning i masten => Hf i bakkant.
    else:
        print("Forbigangsledningen henger 0.5 m over returledningen.")
        hf = i.fh + i.sh + 0.5
        if hf > (i.hfj - 2.0):
            return False
        elif hf < (hf - 1.0):
            return False
        else:
            return i.fh + i.sh + 0.5


def hoyde_returledn(i):
    """Høyde, samt kontroll av høyde, for returledning målt fra SOK."""

    # Dersom mate-/fjern-, AT- eller jordledning i masten.
    hr = i.fh + i.sh
    if i.retur_ledn and (i.matefjern_ledn
                         or i.at_ledn
                         or i.jord_ledn):
        if hr > (i.hfj - 0.5):
            return False
        elif hr < (hr - 1.0):
            return False
    # Dersom forbigangsledning er i masten.
    if i.retur_ledn and i.forbigang_ledn:
        if hr > (i.hf - 0.5):
            return False
        elif hr < (hr - 1.0):
            return False
    # Hvis, og bare hvis, returledningen henger alene i masten.
    elif i.retur_ledn and (not i.matefjern_ledn
                           and not i.at_ledn
                           and not i.jord_ledn
                           and not i.fiberoptisk_ledn
                           and not i.forbigang_ledn):
        if hr > (i.h - i.e - 0.1):
            return False
        elif hr < (hr - 1.0):
            return False




if __name__ == "__main__":
    pass























