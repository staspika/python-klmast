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


def beregn_vindkasthastighetstrykk_EC(i, z):
    """Beregner dimensjonerende vindkasthastighetstrykk [kN/m^2]
    med bruk av Eurokode 1 (EC1).
    """

    # Inngangsparametre
    v_b_0 = i.referansevindhastighet  # [m/s] Referansevindhastighet for aktuell kommune
    c_dir = 1.0                       # [1] Retningsfaktor
    c_season = 1.0                    # [1] Årstidsfaktor
    c_alt = 1.0                       # [1] Nivåfaktor
    c_prob = 1.0                      # [1] Faktor dersom returperioden er mer enn 50 år
    c_0 = 1.0                         # [1] Terrengformfaktoren
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


def q_KL(i, sys):
    """Beregner vindlast på kontaktledningen. Denne verdien brukes til
    å beregne masteavstanden, a.
    """

    # Inngangsparametre
    q_p = i.vindkasthasstighetstrykk
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


def vindlast_mast_normalt(i, mast):
    """Definerer vindlast på mast når
    vinden blåser normalt sporet
    """

    # Liste over krefter som skal returneres
    F = []

    if i.ec3:
        q_p = i.vindkasthastighetstrykk   # [N/m^2]
        cf = 2.2                           # [1] Vindkraftfaktor mast
        q_normalt = q_p * cf * mast.A_ref  # [N/m] Normalt spor

        F.append(Kraft(navn="Vindlast: Mast", type=(0, 4),
                       q=[0, 0, q_normalt],
                       b=mast.h,
                       e=[-mast.h/2, 0, 0]))
    else:
        q_K = _beregn_vindtrykk_NEK(i)

        if mast.type == "H":
            # Inngangsparametre
            G_lat = 1.05  # [1] Resonans faktor
            C_lat = 2.80  # [1] Drag faktor
            A_lat = mast.A_ref  # [m^2 / m] Mastens referanseareal
            q_normalt = q_K * G_lat * (1.0 + 0.2 * (math.sin(2 * (math.pi / 2)) ** 2)) * C_lat * A_lat

            F.append(Kraft(navn="Vindlast: Mast", type=(0, 4),
                           q=[0, 0, q_normalt],
                           b=mast.h,
                           e=[-mast.h / 2, 0, 0]))
        else:
            C_str = 2.0
            if mast.type == "B":
                C_str = 1.4
            q_normalt = q_K * C_str * mast.A_ref

            F.append(Kraft(navn="Vindlast: Mast", type=(0, 4),
                           q=[0, 0, q_normalt],
                           b=mast.h,
                           e=[-mast.h / 2, 0, 0]))

    return F


def vindlast_mast_par(i, mast):
    """Definerer vindlast på mast når
    vinden blåser parallelt sporet
    """

    # Liste over krefter som skal returneres
    F = []

    if i.ec3:
        q_p = i.vindkasthastighetstrykk   # [N/m^2]
        cf = 2.2                           # [1] Vindkraftfaktor mast
        q_par = q_p * cf * mast.A_ref_par  # [N/m] Parallelt spor

        F.append(Kraft(navn="Vindlast: Mast", type=(0, 4),
                       q=[0, q_par, 0],
                       b=mast.h,
                       e=[-mast.h / 2, 0, 0]))
    else:
        q_K = _beregn_vindtrykk_NEK(i)

        # Vindlast på isolator når vinden blåser parallelt sporet.
        A_ins = 0.001  # [m^2] ????????????????????????????????????????????
        G_ins = 1.05  # [1] Resonans faktor
        C_ins = 1.20  # [1] Drag faktor
        q_ins = q_K * G_ins * C_ins * A_ins

        if mast.type == "H":
            # Inngangsparametre
            G_lat = 1.05  # [1] Resonans faktor
            C_lat = 2.80  # [1] Drag faktor
            A_lat = mast.A_ref  # [m^2 / m] Mastens referanseareal
            q_par = q_K * G_lat * (1.0 + 0.2 * (math.sin(2 * (math.pi / 2)) ** 2)) * C_lat * A_lat

            F.append(Kraft(navn="Vindlast: Mast", type=(0, 4),
                           q=[0, q_par + q_ins, 0],
                           b=mast.h,
                           e=[-mast.h / 2, 0, 0]))
        else:
            # Inngangsparametre
            C_str = 1.4  # [1] Drag faktor
            q_par = q_K * C_str * mast.A_ref_par

            F.append(Kraft(navn="Vindlast: Mast", type=(0, 4),
                           q=[0, q_par + q_ins, 0],
                           b=mast.h,
                           e=[-mast.h / 2, 0, 0]))

    return F


def vindlast_ledninger(i, sys):
    """I denne funksjonen avledes krefter på 
    mast på grunn av vindlast på ledninger.
    """

    # Liste over krefter som skal returneres
    F = []

    a = (i.a1 + i.a2) / 2  # [m] masteavstand
    a2 = i.a2  # [m] Avstand til neste mast
    d_henge, d_Y, L_Y = 0, 0, 0  # [m] Diameter hengetråd, Y-line

    if i.ec3:
        q_p = i.vindkasthastighetstrykk  # [N/m^2]
        cf = 1.1                         # [1] Vindkraftfaktor ledning
        q = q_p * cf

    else:
        q_K = _beregn_vindtrykk_NEK(i)
        G_C = 0.75  # [1] Respons faktor
        C_C = 1.0  # [1] Drag faktor
        q = q_K * G_C * C_C

    # Antall utliggere
    n = 1
    if i.siste_for_avspenning or i.linjemast_utliggere == 2:
        n = 2

    # Kontakttråd
    f_z = n * a * q * sys.kontakttraad["Diameter"] / 1000
    F.append(Kraft(navn="Vindlast: Kontakttråd", type=(1, 4),
                   f=[0, 0, f_z], e=[-i.fh, 0, 0]))

    # Bæreline
    f_z = n * a * q * sys.baereline["Diameter"] / 1000
    F.append(Kraft(navn="Vindlast: Bæreline", type=(1, 4),
                   f=[0, 0, f_z], e=[-i.fh - i.sh, 0, 0]))

    # Hengetråd
    d_henge = sys.hengetraad["Diameter"] / 1000  # [m]
    # Bruker lineær interpolasjon for å finne lengde av hengetråd
    L_henge = 8 * a / 60
    q_henge = q * d_henge  # [N/m]
    f_z = n * L_henge * q_henge
    F.append(Kraft(navn="Vindlast: Hengetråd", type=(1, 4),
                   f=[0, 0, f_z], e=[-i.fh - i.sh/2, 0, 0]))

    # Y-line
    if not sys.y_line == None:  # Sjekker at systemet har Y-line
        d_Y += sys.y_line["Diameter"] / 1000  # [m]
        # L_Y = lengde Y-line
        if (sys.navn == "20a" or sys.navn == "35") and i.radius >= 800:
            L_Y = 14
        elif sys.navn == "25" and i.radius >= 1200:
            L_Y = 18
        q_Y = q * d_Y  # [N/m]
        f_z = n * L_Y * q_Y
        F.append(Kraft(navn="Vindlast: Y-line", type=(1, 4),
                       f=[0, 0, f_z], e=[-i.fh - i.sh, 0, 0]))

    # Fikspunktmast
    if i.fixpunktmast:
        f_z = a * q * sys.fixline["Diameter"] / 1000
        F.append(Kraft(navn="Vindlast: Fixpunktmast", type=(2, 4),
                       f=[0, 0, f_z], e=[-i.fh - i.sh, 0, 0]))

    # Fiksavspenningsmast
    if i.fixavspenningsmast:
        f_z = (a2 / 2) * q * sys.fixline["Diameter"] / 1000
        F.append(Kraft(navn="Vindlast: Fixavspenningsmast", type=(2, 4),
                       f=[0, 0, f_z], e=[-i.fh - i.sh, 0, 0]))

    # Avspenningsmast
    if i.avspenningsmast:
        f_z = (a2 / 2) * q * ((sys.baereline["Diameter"] + sys.kontakttraad["Diameter"]) / 1000)
        F.append(Kraft(navn="Vindlast: Avspenningsmast", type=(3, 4),
                       f=[0, 0, f_z], e=[-i.fh - i.sh, 0, 0]))

    # Forbigangsledning
    if i.forbigang_ledn:
        f_z = a * q * sys.forbigangsledning["Diameter"] / 1000
        kategori = 5  # Fastavspent, side
        if not i.matefjern_ledn and not i.at_ledn and not i.jord_ledn:
            kategori = 6  # Fastavspent, topp
        F.append(Kraft(navn="Vindlast: Forbigangsledn", type=(kategori, 4),
                       f=[0, 0, f_z], e=[-i.hf, 0, 0]))

    # Returledning (2 stk.)
    if i.retur_ledn:
        f_z = 2 * a * q * sys.returledning["Diameter"] / 1000
        F.append(Kraft(navn="Vindlast: Returledning", type=(5, 4),
                       f=[0, 0, f_z], e=[-i.hr, 0, 0]))


    # Fiberoptisk ledning
    if i.fiberoptisk_ledn:
        f_z = a * q * sys.fiberoptisk["Diameter"] / 1000
        F.append(Kraft(navn="Vindlast: Fiberoptisk ledning", type=(5, 4),
                       f=[0, 0, f_z], e=[-i.fh, 0, 0]))

    # Mate-/fjernledning(er) (n stk.)
    if i.matefjern_ledn:
        n = i.matefjern_antall
        f_z = n * a * q * sys.matefjernledning["Diameter"] / 1000
        er = "er" if n > 1 else ""
        F.append(Kraft(navn="Vindlast: Mate-/fjernledning{}".format(er), type=(6, 4),
                       f=[0, 0, f_z], e=[-i.hfj, 0, 0]))

    # AT-ledning (2 stk.)
    if i.at_ledn:
        f_z = 2 * a * q * sys.at_ledning["Diameter"] / 1000
        F.append(Kraft(navn="Vindlast: AT-ledning", type=(6, 4),
                       f=[0, 0, f_z], e=[-i.hfj, 0, 0]))

    # Jordledning
    if i.jord_ledn:
        f_z = a * (q * sys.jordledning["Diameter"] / 1000)
        kategori = 5  # Fastavspent, side
        e_z = -0.3
        if not i.matefjern_ledn and not i.at_ledn and not i.forbigang_ledn:
            kategori = 6  # Fastavspent, topp
            e_z = 0
        F.append(Kraft(navn="Vindlast: AT-ledning", type=(kategori, 4),
                       f=[0, 0, f_z], e=[-i.hj, 0, e_z]))

    return F


def isogsno_last(i, sys):
    """Beregner krefter på mast på grunn av is- og snølast på
    ledninger.
    """

    a = (i.a2 + i.a1) / 2  # [m] Midlere masteavstand
    a2 = i.a2              # [m] Avstand til neste mast
    a_T, a_T_dot = sys.a_T, sys.a_T_dot

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
        F.append(Kraft(navn="Islast: Travers", type=(0, 3),
                       f=[2 * i.traverslengde * (2.5 + 0.5 * 50), 0, 0],
                       e=[-i.fh - i.sh/2, 0, 0]))

    # Utliggere
    F.append(Kraft(navn="Islast: Utligger", type=(0, 3),
                   f=[n * i.sms * (2.5 + 0.5 * 55), 0, 0],
                   e=[-i.fh - i.sh, 0, i.sms/2]))

    # Bæreline
    F.append(Kraft(navn="Islast: Bæreline", type=(1, 3),
                   f=[n * a * (2.5 + 0.5 * sys.baereline["Diameter"]), 0, 0],
                   e=[-i.fh - i.sh, 0, i.sms]))

    # Hengetråd: Ingen snølast.

    # Kontakttråd
    F.append(Kraft(navn="Islast: Kontakttråd", type=(1, 3),
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
        F.append(Kraft(navn="Islast: Y-line", type=(1, 3),
                       f=[n * L * (2.5 + 0.5 * sys.y_line["Diameter"]), 0, 0],
                       e=[-i.fh, 0, i.sms]))

    # Fikspunktmast
    if i.fixpunktmast:
        F.append(Kraft(navn="Islast: Fixline", type=(2, 3),
                       f=[a * (2.5 + 0.5 * sys.fixline["Diameter"]), 0, 0],
                       e=[-i.fh - i.sh, 0, i.sms]))

    # Fiksavspenningsmast
    if i.fixavspenningsmast:
        F.append(Kraft(navn="Islast: Fixline", type=(2, 3),
                       f=[a * (2.5 + 0.5 * sys.fixline["Diameter"]), 0, 0],
                       e=[-i.fh - i.sh, 0, 0]))

    # Avspenningsmast
    if i.avspenningsmast:
        F.append(Kraft(navn="Islast: Avspenningsmast", type=(3, 3),
                       f=[a * (2.5 + 0.5 * ((sys.baereline["Diameter"] + sys.kontakttraad["Diameter"]) / 1000)), 0, 0],
                       e=[-i.fh - i.sh/2, 0, 0]))
        # Antar 50 N snølast på lodd
        F.append(Kraft(navn="Islast: Avspenningslodd", type=(3, 3),
                       f=[50, 0, 0], e=[-i.fh - i.sh/2, 0, 0]))

    # Forbigangsledning
    if i.forbigang_ledn:
        # Snølast på isolator antas lik 30 N.
        e_z = -0.3
        kategori = 5
        if not i.matefjern_ledn and not i.at_ledn and not i.jord_ledn:
            # Forbigangsledning montert på baksiden av mast
            e_z = 0
            kategori = 6
        F.append(Kraft(navn="Islast: Forbigangsledning", type=(kategori, 3),
                       f=[30 + a * (2.5 + 0.5 * sys.forbigangsledning["Diameter"]), 0, 0],
                       e=[-i.hf, 0, e_z]))

    # Returledninger (2 stk.)
    if i.retur_ledn:
        # Snølast på isolator antas lik 20 N
        F.append(Kraft(navn="Islast: Returledning", type=(5, 3),
                       f=[2 * (20 + a * (2.5 + 0.5 * sys.returledning["Diameter"])), 0, 0],
                       e=[-i.hr, 0, -0.5]))

    # Mate-/fjernledning(er) (n stk.)
    if i.matefjern_ledn:
        # Snølast på isolator for mate-/fjernledning antas lik 20 N
        n = i.matefjern_antall
        er = "er" if n > 1 else ""
        F.append(Kraft(navn="Islast: Mate-/fjernledning{}".format(er), type=(6, 3),
                       f=[n * (20 + a * (2.5 + 0.5 * sys.matefjernledning["Diameter"])), 0, 0],
                       e=[-i.hfj, 0, 0]))

    # Fiberoptisk
    if i.fiberoptisk_ledn:
        F.append(Kraft(navn="Islast: Fiberoptisk ledning", type=(5, 3),
                       f=[a * (2.5 + 0.5 * sys.fiberoptisk["Diameter"]), 0, 0],
                       e=[-i.fh, 0, -0.3]))

    # AT-ledninger (2 stk.)
    if i.at_ledn:
        F.append(Kraft(navn="Islast: AT-ledning", type=(6, 3),
                       f=[2 * a * (2.5 + 0.5 * sys.at_ledning["Diameter"]), 0, 0],
                       e=[-i.hfj, 0, 0]))

    # Jordledning
    if i.jord_ledn:
        e_z = -0.3
        kategori = 5
        if not i.matefjern_ledn and not i.at_ledn and not i.forbigang_ledn:
            e_z = 0
            kategori = 6
        F.append(Kraft(navn="Islast: Jordledning", type=(kategori, 3),
                       f=[a * (2.5 + 0.5 * sys.returledning["Diameter"]), 0, 0],
                       e=[-i.hj, 0, e_z]))

    return F


def vandringskraft(i, sys, mast):
    """Kraft i sporets lengderetning fordi utliggeren
    ikke står normalt på masten.
    """

    # Inngangsparametre
    B1, B2 = sys.B1, sys.B2
    a_T, a_T_dot = sys.a_T, sys.a_T_dot

    # Liste over krefter som returneres
    F = []

    a1, a2 = i.a1, i.a2  # [m] Avstand til forrige og neste mast
    alpha = 1.7 * 10 ** (-5)  # [1] Lengdeutvidelseskoeffisient
    delta_t = 45  # [grader C] maksimal temperaturendring
    arm = a_T_dot
    if i.strekkutligger:
        arm = a_T
    s = 1000 * sys.kontakttraad["Strekk i ledning"]  # [N]
    f_z_kurvatur = - s * (a1 + a2) / (2 * i.radius)
    f_z_sikksakk = - s * ((B2 - B1) / a1 + (B2 - B1) / a2)
    if i.strekkutligger:
        f_z_kurvatur, f_z_sikksakk = - f_z_kurvatur, - f_z_sikksakk

    avstand_fixpunkt = i.avstand_fixpunkt if not i.fixavspenningsmast \
        else (a1 + a2) / 2
    if i.fixpunktmast or i.siste_for_avspenning or i.linjemast_utliggere == 2:
        avstand_fixpunkt = 0

    dl = alpha * delta_t * avstand_fixpunkt
    F.append(Kraft(navn="Vandringskraft: Bæreline", type=(1, 2),
                   f=[0, f_z_kurvatur * (dl / i.sms), 0],
                   e=[-i.fh - i.sh, 0, mast.bredde(mast.h - (i.fh + i.sh))/2000]))
    F.append(Kraft(navn="Vandringskraft: Kontakttråd", type=(1, 2),
                   f=[0, (f_z_kurvatur + f_z_sikksakk) * (dl / arm), 0],
                   e=[-i.fh, 0, mast.bredde(mast.h - i.fh)/2000]))

    return F


# ====================================================================#
#                                                                     #
#              Herfra brukes bransjestandarder (NEK).                 #
#                                                                     #
# ====================================================================#


def _beregn_vindtrykk_NEK(i):
    """Denne funksjonen beregner 
    vindtrykket etter NEK EN 50119.
    """

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
    v_b_0 = i.referansevindhastighet  # [m/s] Referansevindhastighet for aktuell kommune

    # Dynamisk vindtrykk [N / m^2]
    rho = 1.255  # [kg / m^3]
    G_q = 2.05   # [1] Gust-respons faktor
    G_t = 1.0    # [1] Terrengfaktor av typen åpent

    q_K = 0.5 * rho * G_q * G_t * v_b_0 ** 2

    return q_K
