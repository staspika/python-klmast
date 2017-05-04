import math
from kraft import *

import numpy
import deformasjon

# Terrengkategorier etter EC1, NA.4.1
kat0 = {"k_r": 0.16, "z_0": 0.003, "z_min": 2.0}
kat1 = {"k_r": 0.17, "z_0": 0.01, "z_min": 2.0}
kat2 = {"k_r": 0.19, "z_0": 0.05, "z_min": 4.0}
kat3 = {"k_r": 0.22, "z_0": 0.3, "z_min": 8.0}
kat4 = {"k_r": 0.24, "z_0": 1.0, "z_min": 16.0}
terrengkategorier = ([kat0, kat1, kat2, kat3, kat4])


def beregn_vindkasthastighetstrykk_EC(z):
    """Beregner dimensjonerende vindkasthastighetstrykk [kN/m^2]
    med bruk av Eurokode 1 (EC1).
    """

    # Inngangsparametre
    v_b_0 = 22      # [m/s] Referansevindhastighet for aktuell kommune
    c_dir = 1.0     # [1] Retningsfaktor
    c_season = 1.0  # [1] Årstidsfaktor
    c_alt = 1.0     # [1] Nivåfaktor
    c_prob = 1.0    # [1] Faktor dersom returperioden er mer enn 50 år
    c_0 = 1.0       # [1] Terrengformfaktoren
    kategori = 2

    # Basisvindhastighet [m/s]
    v_b = c_dir * c_season * c_alt * c_prob * v_b_0

    k_r = terrengkategorier[kategori]["k_r"]
    z_0 = terrengkategorier[kategori]["z_0"]
    z_min = terrengkategorier[kategori]["z_min"]
    z_max = 200
    c_r = 0

    if z <= z_min:
        c_r = k_r * math.log(z_min / z_0)
    elif z_min < z <= z_max:
        c_r = k_r * math.log(z / z_0)

    # Stedets middelvindhastighet [m/s]
    v_m = c_r * c_0 * v_b

    # Stedets vindhastighetstrykk [N/m^2]
    rho = 1.25                  # [kg/m^3] Luftens densitet
    q_m = 0.5 * rho * v_m ** 2  # [N / m^2]

    # Turbulensintensiteten
    k_l = 1.0  # Turbulensintensiteten, anbefalt verdi er 1.0
    k_p = 3.5
    I_v = 0
    if z <= z_min:
        I_v = k_l / (c_0 * math.log(z_min / z_0))
    elif z_min < z <= z_max:
        I_v = k_l / (c_0 * math.log(z / z_0))


    # Vindkasthastigheten
    # v_p = v_m * math.sqrt(1 + 2 * k_p * I_v)

    # Vindkasthastighetstrykket
    q_p = q_m * (1 + 2 * k_p * I_v)  # [N/m^2]

    return q_p


def q_KL(i, sys, q_p):
    """Beregner vindlast på kontaktledningen. Denne verdien brukes til
    å beregne masteavstanden, a.
    """

    # Inngangsparametre
    cf = 1.1             # [1] Vindkraftfaktor ledning
    d_henge, d_Y = 0, 0  # [m] Diameter hengetraad, lengde Y-line
    q = 0                # [N/m] Brukes til å beregne masteavstand, a

    # Bidrag fra KL, bæreline, hengetråd og Y-line avhenger av utliggere
    utliggere = 1
    if i.siste_for_avspenning or i.linjemast_utliggere == 2:
        utliggere = 2

    # ALTERNATIV #1: q = 1.2 * q_kontakttråd
    q_kl = q_p * cf * sys.kontakttraad["Diameter"] / 1000  # [N / m]
    q += q_kl

    # ALTERNATIV #2: q = q_kontakttråd + q_bæreline + q_henge + q_Y
    # Kontakttråd.
    # q_kl = q_p * cf * sys.kontakttraad["Diameter"] / 1000  # [N / m]
    # q += q_kl

    # Bæreline.
    # q_b = q_p * cf * sys.baereline["Diameter"] / 1000  # [N / m]
    # q += q_b

    # Hengetråd.
    # for utligger in range(utliggere):
    #     d_henge += sys.hengetraad["Diameter"] / 1000   # [m]
    # q_henge = q_p * cf * d_henge  # [N/m]
    # q += q_henge

    # Y-line.
    # if not sys.y_line == None:  # Sjekker at systemet har Y-line
    #     d_Y += sys.y_line["Diameter"] / 1000  # [m]
    #     # L_Y = lengde Y-line
    # q_Y = q_p * cf * d_Y
    # q += q_Y

    return q


def vindlast_mast(mast, q_p):
    """Definerer vindlast på mast"""

    cf = 2.2                           # [1] Vindkraftfaktor mast
    h = mast.h                            # [m] Høyde mast
    q_normalt = q_p * cf * mast.A_ref  # [N/m] Normalt spor
    q_par = q_p * cf * mast.A_ref_par  # [N/m] Parallelt spor

    # Liste over krefter som skal returneres
    F = []

    F.append(Kraft(navn="Vindlast: Mast (fra mast mot spor)", type=12,
                   q=[0, 0, q_normalt],
                   b=h,
                   e=[-h/2, 0, 0]))

    F.append(Kraft(navn="Vindlast: Mast (fra spor mot mast)", type=13,
                   q=[0, 0, -q_normalt],
                   b=h,
                   e=[-h/2, 0, 0]))

    F.append(Kraft(navn="Vindlast: Mast (parallelt spor)", type=14,
                   q=[0, q_par, 0],
                   b=h,
                   e=[-h/2, 0, 0]))

    return F


def vindlast_ledninger(i, sys, q_p):
    """Her avledes krefter på mast på grunn av vindlast på
    ledninger."""

    # Inngangsparametre
    a = (i.a2 + i.a1) / 2        # [m] Midlere masteavstand
    a2 = i.a2                    # [m] Avstand til nest mast
    cf = 1.1                     # [1] Vindkraftfaktor ledning
    d_henge, d_Y, L_Y = 0, 0, 0  # [m] Diameter hengetraad, Y-line

    # F = liste over krefter som skal returneres
    F = []

    # Antall utliggere
    n = 1
    if i.siste_for_avspenning or i.linjemast_utliggere == 2:
        n = 2


    # Kontakttråd
    f_z = n * a * q_p * cf * sys.kontakttraad["Diameter"] / 1000
    F.append(Kraft(navn="Vindlast: Kontakttråd", type=12,
                   f=[0, 0, f_z], e=[-i.fh, 0, 0]))
    F.append(Kraft(navn="Vindlast: Kontakttråd", type=13,
                   f=[0, 0, - f_z], e=[-i.fh, 0, 0]))

    # Bæreline
    f_z = n * a * q_p * cf * sys.baereline["Diameter"] / 1000
    F.append(Kraft(navn="Vindlast: Bæreline", type=12,
                   f=[0, 0, f_z], e=[-i.fh - i.sh, 0, 0]))
    F.append(Kraft(navn="Vindlast: Bæreline", type=13,
                   f=[0, 0, - f_z], e=[-i.fh - i.sh, 0, 0]))

    # Hengetråd
    d_henge = sys.hengetraad["Diameter"] / 1000  # [m]
    # Bruker lineær interpolasjon for å finne lengde av hengetråd
    L_henge = 8 * a / 60
    q_henge = q_p * cf * d_henge  # [N/m]
    f_z = n * L_henge * q_henge
    F.append(Kraft(navn="Vindlast: Hengetråd", type=12,
                   f=[0, 0, f_z], e=[-i.fh - i.sh/2, 0, 0]))
    F.append(Kraft(navn="Vindlast: Hengetråd", type=13,
                   f=[0, 0, - f_z], e=[-i.fh - i.sh / 2, 0, 0]))

    # Y-line
    if not sys.y_line == None:  # Sjekker at systemet har Y-line
        d_Y += sys.y_line["Diameter"] / 1000  # [m]
        # L_Y = lengde Y-line
        if (sys.navn == "20a" or sys.navn == "35") and i.radius >= 800:
            L_Y = 14
        elif sys.navn == "25" and i.radius >= 1200:
            L_Y = 18
        q_Y = q_p * cf * d_Y  # [N/m]
        f_z = n * L_Y * q_Y
        F.append(Kraft(navn="Vindlast: Y-line", type=12,
                       f=[0, 0, f_z], e=[-i.fh - i.sh, 0, 0]))
        F.append(Kraft(navn="Vindlast: Y-line", type=13,
                       f=[0, 0, - f_z], e=[-i.fh - i.sh, 0, 0]))

    # Fikspunktmast
    if i.fixpunktmast:
        f_z = a * q_p * cf * sys.fixline["Diameter"] / 1000
        F.append(Kraft(navn="Vindlast: Fixpunktmast", type=12,
                       f=[0, 0, f_z], e=[-i.fh - i.sh, 0, 0]))
        F.append(Kraft(navn="Vindlast: Fixpunktmast", type=13,
                       f=[0, 0, - f_z], e=[-i.fh - i.sh, 0, 0]))

    # Fiksavspenningsmast
    if i.fixavspenningsmast:
        f_z = (a2 / 2) * q_p * cf * sys.fixline["Diameter"] / 1000
        F.append(Kraft(navn="Vindlast: Fixavspenningsmast", type=12,
                       f=[0, 0, f_z], e=[-i.fh - i.sh, 0, 0]))
        F.append(Kraft(navn="Vindlast: Fixavspenningsmast", type=13,
                   f=[0, 0, - f_z], e=[-i.fh - i.sh, 0, 0]))

    # Avspenningsmast
    if i.avspenningsmast:
        f_z = (a2 / 2) * q_p * cf * ((sys.baereline["Diameter"] + sys.kontakttraad["Diameter"]) / 1000)
        F.append(Kraft(navn="Vindlast: Avspenningsmast", type=12,
                       f=[0, 0, f_z], e=[-i.fh - i.sh, 0, 0]))
        F.append(Kraft(navn="Vindlast: Avspenningsmast", type=13,
                       f=[0, 0, - f_z], e=[-i.fh - i.sh, 0, 0]))

    # Forbigangsledning
    if i.forbigang_ledn:
        f_z = a * q_p * cf * sys.forbigangsledning["Diameter"] / 1000
        F.append(Kraft(navn="Vindlast: Forbigangsledn", type=12,
                       f=[0, 0, f_z], e=[-i.hf, 0, 0]))
        F.append(Kraft(navn="Vindlast: Forbigangsledn", type=13,
                       f=[0, 0, - f_z], e=[-i.hf, 0, 0]))

    # Returledning (2 stk.)
    if i.retur_ledn:
        f_z = 2 * a * q_p * cf * sys.returledning["Diameter"] / 1000
        F.append(Kraft(navn="Vindlast: Returledning", type=12,
                       f=[0, 0, f_z], e=[-i.hr, 0, 0]))
        F.append(Kraft(navn="Vindlast: Returledning", type=13,
                       f=[0, 0, - f_z], e=[-i.hr, 0, 0]))


    # Fiberoptisk ledning
    if i.fiberoptisk_ledn:
        f_z = a * q_p * cf * sys.fiberoptisk["Diameter"] / 1000
        F.append(Kraft(navn="Vindlast: Fiberoptisk ledning", type=12,
                       f=[0, 0, f_z], e=[-i.fh, 0, 0]))
        F.append(Kraft(navn="Vindlast: Fiberoptisk ledning", type=13,
                       f=[0, 0, - f_z], e=[-i.fh, 0, 0]))

    # Mate-/fjernledning (2 stk.)
    if i.matefjern_ledn:
        n = i.matefjern_antall
        f_z = n * a * q_p * cf * sys.matefjernledning["Diameter"] / 1000
        F.append(Kraft(navn="Vindlast: Mate-/fjernledning", type=12,
                       f=[0, 0, f_z], e=[-i.hfj, 0, 0]))
        F.append(Kraft(navn="Vindlast: Mate-/fjernledning", type=13,
                       f=[0, 0, - f_z], e=[-i.hfj, 0, 0]))

    # AT-ledning (2 stk.)
    if i.at_ledn:
        f_z = 2 * a * q_p * cf * sys.at_ledning["Diameter"] / 1000
        F.append(Kraft(navn="Vindlast: AT-ledning", type=12,
                       f=[0, 0, f_z], e=[-i.hfj, 0, 0]))
        F.append(Kraft(navn="Vindlast: AT-ledning", type=13,
                       f=[0, 0, - f_z], e=[-i.hfj, 0, 0]))

    # Jordledning
    if i.jord_ledn:
        f_z = a * (q_p * cf * sys.jordledning["Diameter"] / 1000)
        F.append(Kraft(navn="Vindlast: AT-ledning", type=12,
                       f=[0, 0, f_z], e=[-i.hj, 0, 0]))
        F.append(Kraft(navn="Vindlast: AT-ledning", type=13,
                       f=[0, 0, - f_z], e=[-i.hj, 0, 0]))

    return F


def isogsno_last(i, sys, a_T, a_T_dot):
    """Beregner krefter på mast på grunn av is- og snølast på
    ledninger.
    """

    a = (i.a2 + i.a1) / 2  # [m] Midlere masteavstand
    a2 = i.a2              # [m] Avstand til neste mast

    # Snø- og islast pr. meter ledning [N/m].
    # q = (2.5 + 0.5 * d)

    arm = a_T_dot
    if i.strekkutligger:
        arm = a_T

    # F = liste over krefter som skal returneres
    F = []

    # Antall utliggere
    n = 1
    if i.siste_for_avspenning or i.linjemast_utliggere == 2:
        n = 2
        F.append(Kraft(navn="Islast: Travers", type=11,
                       f=[2 * i.traverslengde * (2.5 + 0.5 * 100), 0, 0],
                       e=[-i.fh - i.sh/2, 0, 0]))

    # Utliggere
    F.append(Kraft(navn="Islast: Utligger", type=11,
                   f=[n * i.sms * (2.5 + 0.5 * 50), 0, 0],
                   e=[-i.fh - i.sh, 0, i.sms/2]))

    # Bæreline
    F.append(Kraft(navn="Islast: Bæreline", type=11,
                   f=[n * a * (2.5 + 0.5 * sys.baereline["Diameter"]), 0, 0],
                   e=[-i.fh - i.sh, 0, i.sms]))

    # Hengetråd: Ingen snølast.

    # Kontakttråd
    F.append(Kraft(navn="Islast: Kontakttråd", type=11,
                   f=[n * a * (2.5 + 0.5 * sys.kontakttraad["Diameter"]), 0, 0],
                   e=[-i.fh, 0, arm]))

    # Y-line
    if not sys.y_line == None:  # Sjekker at systemet har Y-line
        # L = lengde Y-line
        L = 0
        if (sys.navn == "20a" or sys.navn == "35") and i.radius >= 800:
            L = 14
        elif sys.navn == "25" and i.radius >= 1200:
            L = 18
        F.append(Kraft(navn="Islast: Y-line", type=11,
                       f=[n * L * (2.5 + 0.5 * sys.y_line["Diameter"]), 0, 0],
                       e=[-i.fh, 0, i.sms]))

    # Fikspunktmast
    if i.fixpunktmast:
        F.append(Kraft(navn="Islast: Fixpunktmast", type=11,
                       f=[a * (2.5 + 0.5 * sys.fixline["Diameter"]), 0, 0],
                       e=[-i.fh - i.sh, 0, i.sms]))

    # Fiksavspenningsmast
    if i.fixavspenningsmast:
        F.append(Kraft(navn="Islast: Fixavspenningsmast", type=11,
                       f=[(a2 / 2) * (2.5 + 0.5 * sys.fixline["Diameter"]), 0, 0],
                       e=[-i.fh - i.sh, 0, 0]))
        F.append(Kraft(navn="Islast: Avspenningslodd", type=11,
                       f=[50, 0, 0], e=[-i.fh - i.sh, 0, 0]))

    # Avspenningsmast
    if i.avspenningsmast:
        F.append(Kraft(navn="Islast: Avspenningsmast", type=11,
                       f=[(a2 / 2) * (2.5 + 0.5 * ((sys.baereline["Diameter"] + sys.kontakttraad["Diameter"]) / 1000)), 0, 0],
                       e=[-i.fh - i.sh/2, 0, 0]))
    F.append(Kraft(navn="Islast: Avspenningslodd", type=11,
                   f=[50, 0, 0], e=[-i.fh - i.sh/2, 0, 0]))

    # Forbigangsledning
    if i.forbigang_ledn:
        # Snølast på isolator antas lik 30 N.
        F.append(Kraft(navn="Islast: Forbigangsledning", type=11,
                       f=[30 + a * (2.5 + 0.5 * sys.forbigangsledning["Diameter"]), 0, 0],
                       e=[-i.hf, 0, 0]))
        if i.matefjern_ledn or i.at_ledn or i.jord_ledn:
            # Forbigangsledning montert på baksiden av mast
            F.append(Kraft(navn="Islast: Forbigangsledning", type=11,
                           f=[30 + a * (2.5 + 0.5 * sys.forbigangsledning["Diameter"]), 0, 0],
                           e=[-i.hf, 0, -0.3]))

    # Returledninger (2 stk.)
    if i.retur_ledn:
        # Snølast på isolator antas lik 20 N
        F.append(Kraft(navn="Islast: Returledning", type=11,
                       f=[2 * (20 + a * (2.5 + 0.5 * sys.returledning["Diameter"])), 0, 0],
                       e=[-i.hr, 0, -0.5]))

    # Mate-/fjernledning (n stk.)
    if i.matefjern_ledn:
        # Snølast på isolator for mate-/fjernledning antas lik 220 N
        n = i.matefjern_antall
        F.append(Kraft(navn="Islast: Mate-/fjernledning", type=11,
                       f=[n * a * (220 + (2.5 + 0.5 * sys.matefjernledning["Diameter"])), 0, 0],
                       e=[-i.hfj, 0, 0]))

    # Fiberoptisk
    if i.fiberoptisk_ledn:
        F.append(Kraft(navn="Islast: Fiberoptisk ledning", type=11,
                       f=[a * (2.5 + 0.5 * sys.fiberoptisk["Diameter"]), 0, 0],
                       e=[-i.fh, 0, -0.3]))

    # AT-ledninger (2 stk.)
    if i.at_ledn:
        F.append(Kraft(navn="Islast: AT-ledning", type=11,
                       f=[2 * a * (2.5 + 0.5 * sys.at_ledning["Diameter"]), 0, 0],
                       e=[-i.hfj, 0, 0]))

    # Jordledning
    if i.jord_ledn:
        e_z = 0
        if i.matefjern_ledn or i.at_ledn or i.forbigang_ledn:
            e_z = -0.3
        F.append(Kraft(navn="Islast: Jordledning", type=11,
                       f=[a * (2.5 + 0.5 * sys.returledning["Diameter"]), 0, 0],
                       e=[-i.hj, 0, e_z]))


    return F


# ====================================================================#
#                                                                     #
#              Herfra brukes bransjestandarder (NEK).                 #
#                                                                     #
# ====================================================================#


def _beregn_vindtrykk_NEK(z):
    """Denne funksjonen beregner vindtrykket etter NEK EN 50119."""

    """
    # Alternativ #1: NEK EN 50125-2
    # Inngangsparametre for referansehøyde 10m over bakkenivå
    z = 10              # [m] høyde over bakken
    v_10 = 24           # [m / s] 10-min middelvindhastighet
    # Ruhetsparameteren for ulike terrengkategorier [1]
    alpha = [0.12, 0.16, 0.20, 0.28]

    # Vindhastigheten i høyden z over bakkenivå etter NEK EN 50125-2.
    v_z = v_10 * (z/10) ** alpha[3]
    """

    # Alternativ 2: EC1
    # Terrengkategori II velges
    v_b_0 = 22      # [m/s] Referansevindhastighet for aktuell kommune
    c_dir = 1.0     # [1] Retningsfaktor
    c_season = 1.0  # [1] Årstidsfaktor
    c_alt = 1.0     # [1] Nivåfaktor
    c_prob = 1.0    # [1] Faktor dersom returperioden er mer enn 50 år
    c_0 = 1.0       # [1] Terrengformfaktoren
    k_r = 0.19      # [1]
    z_0 = 0.05      # [m]
    z_min = 4       # [m]
    z_max = 200     # [m]
    c_r = 0

    # Basisvindhastighet [m/s]
    v_b = c_dir * c_season * c_alt * c_prob * v_b_0

    if z <= z_min:
        c_r = k_r * math.log(z_min / z_0)
    elif z_min < z <= z_max:
        c_r = k_r * math.log(z / z_0)

    # Stedets middelvindhastighet [m/s]
    v_z = c_r * c_0 * v_b

    # Dynamisk vindtrykk [N / m^2]
    rho = 1.255  # [kg / m^3]
    G_q = 2.05   # [1] Gust-respons faktor
    G_t = 1.0    # [1] Terrengfaktor av typen åpent

    q_K = 0.5 * rho * G_q * G_t * v_z ** 2

    return q_K


def vindlast_mast_NEK(mast, q_K):
    """Vindlast på mast etter NEK EN 50119. Antar en 
    firkantet jevnt fordelt vindlast på masten.
    """

    h = mast.h  # [m] Mastens høyde

    # Liste over krefter som skal returneres
    F = []

    # Vindlast på isolator når vinden blåser parallelt sporet.
    A_ins = 0.01  # [m^2]
    G_ins = 1.05  # [1] Resonans faktor
    C_ins = 1.20  # [1] Drag faktor
    q_ins = q_K * G_ins * C_ins * A_ins

    if mast.type == "H":
        # Inngangsparametre
        G_lat = 1.05  # [1] Resonans faktor
        C_lat = 2.80  # [1] Drag faktor
        A_lat = mast.A_ref  # [m^2 / m] Mastens referanseareal
        q_normalt = q_K * G_lat * C_lat * A_lat
        q_par = q_ins + q_K * G_lat * (1.0 + 0.2 * (math.sin(2 * (math.pi / 2)) ** 2)) * C_lat * A_lat

        F.append(Kraft(navn="Vindlast: Mast (fra mast mot spor)", type=12,
                       q=[0, 0, q_normalt],
                       b=h,
                       e=[-h/2, 0, 0]))

        F.append(Kraft(navn="Vindlast: Mast (fra spor mot mast)", type=13,
                       q=[0, 0, -q_normalt],
                       b=h,
                       e=[-h/2, 0, 0]))

        F.append(Kraft(navn="Vindlast: Mast (parallelt spor)", type=14,
                       q=[0, q_par, 0],
                       b=h,
                       e=[-h/2, 0, 0]))
    else:
        C_str = 1.4  # [1] Drag faktor for vind parallelt spor
        q_par = q_ins + q_K * C_str * mast.A_ref_par
        q_normalt = q_K * C_str * mast.A_ref
        if mast.type == "B":
            q_normalt = q_K * 2.0 * mast.A_ref

        F.append(Kraft(navn="Vindlast: Mast (fra mast mot spor)", type=12,
                       q=[0, 0, q_normalt],
                       b=h,
                       e=[-h / 2, 0, 0]))

        F.append(Kraft(navn="Vindlast: Mast (fra spor mot mast)", type=13,
                       q=[0, 0, -q_normalt],
                       b=h,
                       e=[-h / 2, 0, 0]))

        F.append(Kraft(navn="Vindlast: Mast (parallelt spor)", type=14,
                       q=[0, q_par, 0],
                       b=h,
                       e=[-h / 2, 0, 0]))

    return F


def vindlast_ledninger_NEK(i, q_K, sys):
    """Beregner reaksjonskrefter grunnet vind på ledninger NEK EN 50119.
    Kun gyldig for vindretning vinkelrett på sporet.
    """

    # Inngangsparametre
    r = i.radius                 # [m] kurveradius
    a = (i.a1 + i.a2)/2          # [m] masteavstand
    a2 = i.a2                    # [m] Avstand til neste mast
    G_C = 0.75                   # [1] Respons faktor
    C_C = 1.0                    # [1] Drag faktor
    d_henge, d_Y, L_Y = 0, 0, 0  # [m] Diameter hengetråd, Y-line

    # Liste over krefter som skal returneres
    F = []

    # Antall utliggere
    n = 1
    if i.siste_for_avspenning or i.linjemast_utliggere == 2:
        n = 2

    # Kontakttråd
    f_z = n * q_K * G_C * sys.kontakttraad["Diameter"] / 1000 * C_C * a
    F.append(Kraft(navn="Vindlast: Kontakttråd", type=12,
                   f=[0, 0, f_z], e=[-i.fh, 0, 0]))
    F.append(Kraft(navn="Vindlast: Kontakttråd", type=13,
                   f=[0, 0, - f_z], e=[-i.fh, 0, 0]))

    # Bæreline
    f_z = n * q_K * G_C * sys.baereline["Diameter"] / 1000 * C_C * a
    F.append(Kraft(navn="Vindlast: Bæreline", type=12,
                   f=[0, 0, f_z], e=[-i.fh - i.sh, 0, 0]))
    F.append(Kraft(navn="Vindlast: Bæreline", type=13,
                   f=[0, 0, - f_z], e=[-i.fh - i.sh, 0, 0]))

    # Hengetråd
    d_henge = sys.hengetraad["Diameter"] / 1000  # [m]
    # Bruker lineær interpolasjon for å finne lengde av hengetråd
    L_henge = 8 * a / 60
    f_z = n * q_K * G_C * d_henge * C_C * L_henge
    F.append(Kraft(navn="Vindlast: Hengetråd", type=12,
                   f=[0, 0, f_z], e=[-i.fh - i.sh / 2, 0, 0]))
    F.append(Kraft(navn="Vindlast: Hengetråd", type=13,
                   f=[0, 0, - f_z], e=[-i.fh - i.sh / 2, 0, 0]))

    # Y-line
    if not sys.y_line == None:  # Sjekker at systemet har Y-line
        # L_Y = lengde Y-line
        if (sys.navn == "20a" or sys.navn == "35") and i.radius >= 800:
            L_Y = 14
        elif sys.navn == "25" and i.radius >= 1200:
            L_Y = 18
        f_z = n * q_K * G_C * sys.y_line["Diameter"] / 1000 * C_C * L_Y
        F.append(Kraft(navn="Vindlast: Y-line", type=12,
                       f=[0, 0, f_z], e=[-i.fh - i.sh, 0, 0]))
        F.append(Kraft(navn="Vindlast: Y-line", type=13,
                       f=[0, 0, - f_z], e=[-i.fh - i.sh, 0, 0]))

    # Fikspunktmast
    if i.fixpunktmast:
        f_z = q_K * G_C * sys.fixline["Diameter"] / 1000 * C_C * a
        F.append(Kraft(navn="Vindlast: Fixpunktmast", type=12,
                       f=[0, 0, f_z], e=[-i.fh - i.sh, 0, 0]))
        F.append(Kraft(navn="Vindlast: Fixpunktmast", type=13,
                       f=[0, 0, - f_z], e=[-i.fh - i.sh, 0, 0]))

    # Fiksavspenningsmast
    if i.fixavspenningsmast:
        f_z = q_K * G_C * sys.fixline["Diameter"] / 1000 * C_C * (a2 / 2)
        F.append(Kraft(navn="Vindlast: Fixavspenningsmast", type=12,
                       f=[0, 0, f_z], e=[-i.fh - i.sh, 0, 0]))
        F.append(Kraft(navn="Vindlast: Fixavspenningsmast", type=13,
                       f=[0, 0, - f_z], e=[-i.fh - i.sh, 0, 0]))

    # Avspenningsmast
    if i.avspenningsmast:
        f_z = q_K * G_C * ((sys.baereline["Diameter"] + sys.kontakttraad["Diameter"]) / 1000) * C_C * (a2 / 2)
        F.append(Kraft(navn="Vindlast: Avspenningsmast", type=12,
                       f=[0, 0, f_z], e=[-i.fh - i.sh, 0, 0]))
        F.append(Kraft(navn="Vindlast: Avspenningsmast", type=13,
                       f=[0, 0, - f_z], e=[-i.fh - i.sh, 0, 0]))

    # Forbigangsledning
    if i.forbigang_ledn:
        f_z = q_K * G_C * sys.forbigangsledning["Diameter"] / 1000 * C_C * a
        F.append(Kraft(navn="Vindlast: Forbigangsledn", type=12,
                       f=[0, 0, f_z], e=[-i.hf, 0, 0]))
        F.append(Kraft(navn="Vindlast: Forbigangsledn", type=13,
                       f=[0, 0, - f_z], e=[-i.hf, 0, 0]))

    # Returledning (2 stk.)
    if i.retur_ledn:
        f_z = 2 * q_K * G_C * sys.returledning["Diameter"] / 1000 * C_C * a
        F.append(Kraft(navn="Vindlast: Returledning", type=12,
                       f=[0, 0, f_z], e=[-i.hr, 0, 0]))
        F.append(Kraft(navn="Vindlast: Returledning", type=13,
                       f=[0, 0, - f_z], e=[-i.hr, 0, 0]))


    # Fiberoptisk ledning
    if i.fiberoptisk_ledn:
        f_z = q_K * G_C * sys.fiberoptisk["Diameter"] / 1000 * C_C * a
        F.append(Kraft(navn="Vindlast: Fiberoptisk ledning", type=12,
                       f=[0, 0, f_z], e=[-i.fh, 0, 0]))
        F.append(Kraft(navn="Vindlast: Fiberoptisk ledning", type=13,
                       f=[0, 0, - f_z], e=[-i.fh, 0, 0]))

    # Mate-/fjernledning (2 stk.)
    if i.matefjern_ledn:
        n = i.matefjern_antall
        f_z = n * q_K * G_C * sys.matefjernledning["Diameter"] / 1000 * C_C * a
        F.append(Kraft(navn="Vindlast: Mate-/fjernledning", type=12,
                       f=[0, 0, f_z], e=[-i.hfj, 0, 0]))
        F.append(Kraft(navn="Vindlast: Mate-/fjernledning", type=13,
                       f=[0, 0, - f_z], e=[-i.hfj, 0, 0]))

    # AT-ledning (2 stk.)
    if i.at_ledn:
        f_z = 2 * q_K * G_C * sys.at_ledning["Diameter"] / 1000 * C_C * a
        F.append(Kraft(navn="Vindlast: AT-ledning", type=12,
                       f=[0, 0, f_z], e=[-i.hfj, 0, 0]))
        F.append(Kraft(navn="Vindlast: AT-ledning", type=13,
                       f=[0, 0, - f_z], e=[-i.hfj, 0, 0]))

    # Jordledning
    if i.jord_ledn:
        f_z = q_K * G_C * sys.jordledning["Diameter"] / 1000 * C_C * a
        F.append(Kraft(navn="Vindlast: AT-ledning", type=12,
                       f=[0, 0, f_z], e=[-i.hj, 0, 0]))
        F.append(Kraft(navn="Vindlast: AT-ledning", type=13,
                       f=[0, 0, - f_z], e=[-i.hj, 0, 0]))

    return F
