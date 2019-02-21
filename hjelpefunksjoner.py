# -*- coding: utf8 -*-
"""Diverse funksjoner til bruk andre steder i programmet."""

from __future__ import unicode_literals
import math
import lister


def vindkasthastighetstrykk(v_b_0, c_dir, c_season, c_alt, c_prob, C_0, terrengkategori, z):
    """Beregner dimensjonerende vindkasthastighetstrykk.

    Basert på NS-EN 1991-1-4 seksjon 4, inkl. nasjonalt tillegg.

    :param float v_b_0: Referansevindhastighet for aktuell kommune :math:`[\\frac{m}{s}]`
    :param float c_dir: Retningsfaktor
    :param float c_season: Årstidsfaktor
    :param float c_alt: Nivåfaktor
    :param float c_prob: Faktor dersom returperioden er mer enn 50 år
    :param float C_0: Terrengformfaktor
    :param int terrengkategori: Terrengkategori
    :param float z: Høyde over bakken :math:`[m]`
    :return: Vindkasthastighetstrykk :math:`q_p [\\frac{N}{m^2}]`,
     basisvindhastighet :math:`v_b[\\frac{m}{s}]`,
     middelvindhastighet :math:`v_m [\\frac{m}{s}]`,
     vindhastighet svarende til vindkasthastighetstrykket :math:`v_p [\\frac{m}{s}]`,
     vindhastighetstrykk :math:`q_m [\\frac{N}{m^2}]`,
     turbulensintensitet :math:`I_v`, turbulensfaktor :math:`k_l`
    :rtype: :class:`float`, :class:`float`, :class:`float`, :class:`float`,
     :class:`float`, :class:`float`, :class:`float`
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
    v_m = c_r * C_0 * v_b
    # Stedets vindhastighetstrykk [N/m^2]
    rho = 1.25                  # [kg/m^3] Luftens densitet
    q_m = 0.5 * rho * v_m**2    # [N / m^2]
    # Turbulensintensiteten
    k_l = 1.0  # Turbulensintensiteten, anbefalt verdi er 1.0
    k_p = 3.5
    if z <= z_min:
        I_v = k_l / (C_0 * math.log(z_min / z_0))
    else:
        I_v = k_l / (C_0 * math.log(z / z_0))
    # Vindkasthastigheten
    v_p = v_m * math.sqrt(1 + 2 * k_p * I_v)
    # Vindkasthastighetstrykket
    q_p = q_m * (1 + 2 * k_p * I_v)  # [N/m^2]
    return q_p, v_b, v_m, v_p, q_m, I_v, k_l


def c_alt(v_b_0, region, H):
    """Beregner faktor for vindøkning med høyden over havet.

    Basert på NS-EN 1991-1-4 nasjonalt tillegg NA.4.2(2)P (901.1).

    :param float v_b_0: Referansevindhastighet for aktuell kommune :math:`[\\frac{m}{s}]`
    :param str region: Aktuell region
    :param int H: Høyde over havet for aktuelt byggested :math:`[m]`
    :return: Høydefaktor
    :rtype: :class:`float`
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
    if str(r) in sikksakk:
        B1 = sikksakk[str(r)][0]
        B2 = sikksakk[str(r)][1]
    return B1, B2


def vindutblasning(systemnavn, radius, fh, stromavtakerbredde, v_egendefinert=None):
    """Beregner maksimal tillatt utblåsning av KL.

    Verdien beregnes i henhold til EN 50367 kapittel 5.2.5.3.

    :param str systemnavn: Valgt system
    :param int radius: Sporkurvaturens radius :math:`[m]`
    :param int fh: Kontakttrådhøyde :math:`[m]`
    :param str stromavtakerbredde: Bredde av valgt strømavtaker
    :param int v_egendefinert: Overstyrer automatisk kjørehastighet :math:`[\\frac{m}{s}]`
    :return: Maksimal tillatt vindutblåsning :math:`[m]`
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
    stromavtaker = None
    for s in lister.stromavtakere:
        if s["Navn"] == stromavtakerbredde:
            stromavtaker = s
            break
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
    return d_l
