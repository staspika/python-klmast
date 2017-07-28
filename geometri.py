# -*- coding: utf8 -*-
"""Funksjoner for beregning av geometriske systemdata."""
from __future__ import unicode_literals

import math
import lister
import matplotlib.pyplot as plt
import matplotlib.pyplot as tckr
import matplotlib.artist as art
from xlrd import open_workbook

import numpy
from pandas import DataFrame


def beregn_sikksakk(navn, radius):
    """Beregner sikksakk og største tillat utblåsning av KL.

    :param str navn: Systemets navn
    :param int radius: Sporkurvaturens radius :math:`[m]`
    :return: Sikksakkverdier ``B1`` og ``B1`` :math:`[m]`, største tillatt utblåsning ``e_max`` :math:`[m]`
    :rtype: :class:`float`, :class:`float`, :class:`float`
    """

    r = radius
    sikksakk, e_max = 0, 0

    # Systemavhengige sikksakk-verdier til input i største masteavstand.
    # struktur i sikksakk-ordbøker under: { "radius": [B1, B2] } i [m]
    # største tillatt utblåsning e_max i [m], bestemmes i indre if-setning.
    if navn == "20A" or navn == "20B":
        sikksakk = lister.sikksakk_20
        e_max = 0.55
        if r <= 1000:
            e_max = 0.42
        elif 1000 < r <= 2000:
            e_max = 0.42 + (r - 1000) * ((0.50 - 0.42) / (2000 - 1000))
        elif 2000 < r <= 4000:
            e_max = 0.50 + (r - 2000) * ((0.55 - 0.50) / (4000 - 2000))

    elif navn == "25":
        sikksakk = lister.sikksakk_25
        e_max = 0.50
        if 180 <= r <= 300:
            e_max = 0.40 + (r - 180) * ((0.43 - 0.40) / (300 - 180))
        elif 300 < r <= 600:
            e_max = 0.43
        elif 600 < r <= 700:
            e_max = 0.43 + (r - 600) * ((0.44 - 0.43) / (700 - 600))
        elif 700 < r <= 900:
            e_max = 0.44
        elif 900 < r <= 1000:
            e_max = 0.44 + (r - 900) * ((0.45 - 0.44) / (1000 - 900))
        elif 1000 < r <= 2000:
            e_max = 0.45
        elif 2000 < r <= 3000:
            e_max = 0.45 + (r - 2000) * ((0.50 - 0.45) / (3000 - 2000))

    elif navn == "35":
        sikksakk = lister.sikksakk_35
        e_max = 0.7

    B1 = 0
    B2 = 0
    if r in sikksakk:
        B1 = sikksakk[str(r)][0]
        B2 = sikksakk[str(r)][1]
    return B1, B2, e_max


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


def beregn_arm(systemnavn, radius, sms, fh, B1):
    """Beregner momentarm for utligger.

    :param int radius: Sporkurvaturens radius :math:`[m]`
    :param float sms: Avstand senter mast - senter spor :math:`[m]`
    :param float fh: Kontakttrådhøyde :math:`[m]`
    :param float B1: Første sikksakkverdi :math:`[m]`
    :return: Momentarmer ``a_T`` og ``a_T_dot`` :math:`[m]`
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

    # Momentarm [m] for strekkutligger.
    a_T = sms + fh * (ue[str(r)] / 1.435) - b

    # Momentarm [m] for trykkutligger.
    a_T_dot = sms - fh * (ue[str(r)] / 1.435) + b

    return a_T, a_T_dot


def vindutblasning(systemnavn, radius, fh, stromavtaker, v_egendefinert=None):
    """Beregner maksimal tillatt utblåsning av KL.

    Verdien beregnes i henhold til EN 50367 kapittel 5.2.5.3.

    :param str systemnavn:
    :param int radius:
    :param int fh: Kontakttrådhøyde :math:`[m]`
    :param str stromavtaker:
    :param Boolean v_egendefinert:
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


if __name__ == "__main__":

    wb = open_workbook("vindutblasning_sammenligning.xlsx")

    # v = 130
    # [R, 1600mm, 1850mm, 1950mm]
    ark = wb.sheets()[0]
    excel = [[],[],[],[]]
    klmast = [[],[],[],[]]
    for col in range(4):
        for row in range(6,40):
            val = ark.cell(row, col).value
            excel[col].append(val)
    for col in range(5,9):
        for row in range(9,33):
            val = ark.cell(row, col).value
            klmast[col-5].append(val)

    # 1600mm
    plt.figure(figsize=(15,10))
    plt.plot(excel[0], excel[1], lw=2.0, label="Excel")
    plt.plot(klmast[0], klmast[1], lw=2.0, label="KL_mast")
    plt.title("Max. vindutblåsning for System 35 (v=130km/t)\nStrømavtaker 1600mm")
    plt.legend(loc=4)
    plt.xlabel("R [m]")
    plt.ylabel("d_l [m]")
    plt.grid()
    plt.show()
    # 1800mm
    plt.figure(figsize=(15, 10))
    plt.plot(excel[0], excel[2], lw=2.0, label="Excel")
    plt.plot(klmast[0], klmast[2], lw=2.0, label="KL_mast")
    plt.title("Max. vindutblåsning for System 35 (v=130km/t)\nStrømavtaker 1800mm")
    plt.legend(loc=4)
    plt.xlabel("R [m]")
    plt.ylabel("d_l [m]")
    plt.grid()
    plt.show()
    # 1950mm
    plt.figure(figsize=(15, 10))
    plt.plot(excel[0], excel[3], lw=2.0, label="Excel")
    plt.plot(klmast[0], klmast[3], lw=2.0, label="KL_mast")
    plt.title("Max. vindutblåsning for System 35 (v=130km/t)\nStrømavtaker 1950mm")
    plt.legend(loc=4)
    plt.xlabel("R [m]")
    plt.ylabel("d_l [m]")
    plt.grid()
    plt.show()


    # v = 200
    # [R, 1600mm, 1850mm, 1950mm]
    ark = wb.sheets()[1]
    excel = [[],[],[],[]]
    klmast = [[],[],[],[]]
    for col in range(4):
        for row in range(6,31):
            val = ark.cell(row, col).value
            excel[col].append(val)
    for col in range(5,9):
        for row in range(6,17):
            val = ark.cell(row, col).value
            klmast[col-5].append(val)

    # 1600mm
    plt.figure(figsize=(15, 10))
    plt.plot(excel[0], excel[1], lw=2.0, label="Excel")
    plt.plot(klmast[0], klmast[1], lw=2.0, label="KL_mast")
    plt.title("Max. vindutblåsning for System 20A (v=200km/t)\nStrømavtaker 1600mm")
    plt.legend(loc=4)
    plt.xlabel("R [m]")
    plt.ylabel("d_l [m]")
    plt.grid()
    plt.show()
    # 1800mm
    plt.figure(figsize=(15, 10))
    plt.plot(excel[0], excel[2], lw=2.0, label="Excel")
    plt.plot(klmast[0], klmast[2], lw=2.0, label="KL_mast")
    plt.title("Max. vindutblåsning for System 20A (v=200km/t)\nStrømavtaker 1800mm")
    plt.legend(loc=4)
    plt.xlabel("R [m]")
    plt.ylabel("d_l [m]")
    plt.grid()
    plt.show()
    # 1950mm
    plt.figure(figsize=(15, 10))
    plt.plot(excel[0], excel[3], lw=2.0, label="Excel")
    plt.plot(klmast[0], klmast[3], lw=2.0, label="KL_mast")
    plt.title("Max. vindutblåsning for System 20A (v=200km/t)\nStrømavtaker 1950mm")
    plt.legend(loc=4)
    plt.xlabel("R [m]")
    plt.ylabel("d_l [m]")
    plt.grid()
    plt.show()























