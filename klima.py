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


def vindlast_mast(mast, i, q_p):
    """Definerer vindlast på mast"""

    cf = 2.2                           # [1] Vindkraftfaktor mast
    h = i.h                            # [m] Høyde mast
    q_normalt = q_p * cf * mast.A_ref  # [N/m] Normalt spor
    q_par = q_p * cf * mast.A_ref_par  # [N/m] Parallelt spor

    # Liste over krefter som skal returneres
    F = []

    F.append(Kraft(navn="Vindlast: Mast", type=12,
                   q=[0, 0, q_normalt],
                   b=h,
                   e=[-h/2, 0, 0]))

    F.append(Kraft(navn="Vindlast: Fra Mast", type=13,
                   q=[0, 0, -q_normalt],
                   b=h,
                   e=[-h/2, 0, 0]))

    F.append(Kraft(navn="Vindlast: Mast", type=14,
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
    F.append(Kraft(navn="Vindlast: Bæreline", type=1,
                   f=[0, 0, n * a * q_p * cf * sys.baereline["Diameter"] / 1000],
                   e=[-i.fh - i.sh, 0, 0]))

    # Hengetråd
    d_henge = sys.hengetraad["Diameter"] / 1000  # [m]
    # Bruker lineær interpolasjon for å finne lengde av hengetråd
    L_henge = 8 * a / 60
    q_henge = q_p * cf * d_henge  # [N/m]
    F.append(Kraft(navn="Vindlast: Hengetråd", type=1,
                   f=[0, 0, n * L_henge * q_henge],
                   e=[-i.fh - i.sh/2, 0, 0]))

    # Y-line
    if not sys.y_line == None:  # Sjekker at systemet har Y-line
        d_Y += sys.y_line["Diameter"] / 1000  # [m]
        # L_Y = lengde Y-line
        if (sys.navn == "20a" or sys.navn == "35") and i.radius >= 800:
            L_Y = 14
        elif sys.navn == "25" and i.radius >= 1200:
            L_Y = 18
        q_Y = q_p * cf * d_Y  # [N/m]
        F.append(Kraft(navn="Vindlast: Y-line", type=1,
                       f=[0, 0, n * L_Y * q_Y],
                       e=[-i.fh - i.sh/2, 0, 0]))

    # Fikspunktmast
    if i.fixpunktmast:
        F.append(Kraft(navn="Vindlast: Fixpunktmast", type=2,
                       f=[0, 0, a * q_p * cf * sys.fixline["Diameter"] / 1000],
                       e=[-i.fh - i.sh, 0, 0]))

    # Fiksavspenningsmast
    if i.fixavspenningsmast:
        F.append(Kraft(navn="Vindlast: Fixavspenningsmast", type=3,
                       f=[0, 0, (a2 / 2) * q_p * cf * sys.fixline["Diameter"] / 1000],
                       e=[-i.fh - i.sh, 0, 0]))

    # Avspenningsmast
    if i.avspenningsmast:
        F.append(Kraft(navn="Vindlast: Avspenningsmast", type=4,
                       f=[0, 0, (a2 / 2) * q_p * cf * ((sys.baereline["Diameter"] + sys.kontakttraad["Diameter"]) / 1000)],
                       e=[-i.fh - i.sh, 0, 0]))

    # Forbigangsledning
    if i.forbigang_ledn:
        F.append(Kraft(navn="Vindlast: Forbigangsledn", type=5,
                       f=[0, 0, a * q_p * cf * sys.forbigangsledning["Diameter"] / 1000],
                       e=[-i.hf, 0, 0]))

    # Returledning (2 stk.)
    if i.retur_ledn:
        F.append(Kraft(navn="Vindlast: Returledning", type=6,
                       f=[0, 0, 2 * a * q_p * cf * sys.returledning["Diameter"] / 1000],
                       e=[-i.hr, 0, 0]))

    # Fiberoptisk ledning
    if i.fiberoptisk_ledn:
        F.append(Kraft(navn="Vindlast: Fiberoptisk ledning", type=7,
                       f=[0, 0, a * q_p * cf * sys.fiberoptisk["Diameter"] / 1000],
                       e=[-i.fh, 0, 0]))

    # Mate-/fjernledning (2 stk.)
    if i.matefjern_ledn:
        n = i.matefjern_antall
        F.append(Kraft(navn="Vindlast: Mate-/fjernledning", type=8,
                       f=[0, 0, n * a * q_p * cf * sys.matefjernledning["Diameter"] / 1000],
                       e=[-i.hfj, 0, 0]))

    # AT-ledning (2 stk.)
    if i.at_ledn:
        F.append(Kraft(navn="Vindlast: AT-ledning", type=9,
                       f=[0, 0, 2 * a * q_p * cf * sys.at_ledning["Diameter"] / 1000],
                       e=[-i.hfj, 0, 0]))

    # Jordledning
    if i.jord_ledn:
        F.append(Kraft(navn="Vindlast: AT-ledning", type=10,
                       f=[0, 0, a * (q_p * cf * sys.jordledning["Diameter"] / 1000)],
                       e=[-i.hj, 0, 0]))

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


def _beregn_vindtrykk_NEK():
    """Denne funksjonen beregner vindtrykket {NEK EN 50119}."""

    # Inngangsparametre for referansehøyde 10m over bakkenivå
    z = 10              # [m] høyde over bakken
    rho = 1.255         # [kg / m^3]
    G_q = 2.05          # [1] Gust-respons faktor
    G_t = 1.0           # [1] Terrengfaktor av typen åpent
    v_10 = 24           # [m / s] 10-min middelvindhastighet
    # Ruhetsparameteren for ulike terrengkategorier [1]
    alpha = [0.12, 0.16, 0.20, 0.28]

    # Vindhastigheten i høyden z over bakkenivå etter NEK EN 50125-2.
    v_z = v_10 * (z/10) ** alpha[3]

    # Dynamisk vindtrykk [N / m^2]
    q_z = 0.5 * rho * G_q * G_t * v_z ** 2

    return q_z


def _beregn_deformasjon(mast, M, x, fh):
    """Beregner deformasjon D_z i høyde fh som følge av
    moment om y-aksen med angrepspunkt i høyde x.
    Dersom fh > x interpoleres forskyvningen til høyde fh
    ved hjelp av tangens til vinkelen theta i høyde x
    ganget med høydedifferansen fh - x.
    """
    E = mast.E
    Iy = mast.Iy(mast.h)
    M = M * 1000  # Konverterer til [Nmm]
    x = x * 1000  # Konverterer til [mm]
    fh = fh * 1000  # Konverterer til [mm]
    if fh > x:
        theta = (M * x) / (E * Iy)
        D_z = (M * x ** 2) / (2 * E * Iy) \
              + numpy.tan(theta) * (fh - x)
    else:
        D_z = (M * fh ** 2) / (2 * E * Iy)
    return D_z


def _beregn_vindforskyvning_Dz(mast, i, EC3, q_p=0):
    """Denne funksjonen beregner forskyvning Dz av masten på grunn av
    vindlast på masten, normalt sporet.
    """

    # Inngangsparametre
    E = mast.E                            # [N/mm^2] E-modul, stål
    FH = i.fh * 1000                      # [mm] Høyde, KL
    H = i.h * 1000                        # [mm] Høyde, mast
    Iy_13 = mast.Iy(mast.h * (2 / 3))     # [mm^4] Iy i 1/3-punktet
    q_z = _beregn_vindtrykk_NEK() / 1000  # [N / mm^2]

    if EC3:
        cf = 2.2
        q_z = q_p * cf * mast.A_ref / 1000

    # Forskyvning dz [mm] i høyde FH pga. vindlasten q_z på masten.
    D_z = ((q_z * FH ** 2) / (24 * E * Iy_13)) * (6 * H ** 2 - 4 * H * FH + FH ** 2)

    return D_z


def _beregn_vindforskyvning_Dy(mast, i, EC3, q_p=0):
    """Denne funksjonen beregner forskyvning Dz av masten på grunn av
    vindlast på masten, parallelt med sporet.
    """

    # Inngangsparametre
    E = mast.E                            # [N/mm^2] E-modul, stål
    FH = i.fh * 1000                      # [mm] Høyde, KL
    H = i.h * 1000                        # [mm] Høyde, mast
    Iz_13 = mast.Iz(mast.h * (2 / 3))     # [mm^4] Iz i 1/3-punktet
    q_z = _beregn_vindtrykk_NEK() / 1000  # [N / mm^2]

    if EC3:
        cf = 2.2
        q_z = q_p * cf * mast.A_ref / 1000

    # Forskyvning dz [mm] i høyde FH pga. vindlasten q_z på masten.
    D_y = ((q_z * FH ** 2) / (24 * E * Iz_13)) * (6 * H ** 2 - 4 * H * FH + FH ** 2)

    return D_y

def _beregn_vindforskyvning_ledninger(V_z, mast, i):

    FH = i.fh                          # [m] Kontaktledninshøyden
    H = i.h                            # [m] Høyde, mast
    E = mast.E                         # [N / mm^2] E-modul, stål
    Iy_13 = mast.Iy(mast.h * (2 / 3))  # [mm^4] i 1/3 - pkt.

    # Deformasjon D_z pga. vindlast på ledninger.
    D_z = (V_z / (2 * E * Iy_13)) * (H * FH ** 2 - (1 / 3) * FH ** 2)

    return D_z


def vindlast_ledninger_NEK(sys, mast, i, a):
    """Beregner reaksjonskrefter grunnet vind på ledninger {NEK EN 50119}.
    Kun gyldig for vindretning normalt spor.
    """

    # Inngangsparametre
    FH = i.fh                      # [m] Kontaktledninshøyden
    SH = i.sh                      # [m] Systemhøyde
    Hf = i.hf                      # [m] Høyde, forbigangsledning
    Hj = i.hj                      # [m] Høyde, jordledning
    Hr = i.hr                      # [m] Høyde, returledning
    Hfj = i.hfj                    # [m] Høyde, fjernledning
    r = i.radius                   # [m] kurveradius
    G_C = 0.75                     # [1] Responsfaktor
    C_C = 1.0                      # [1] Drag-faktor
    q_z = _beregn_vindtrykk_NEK()  # [N / m^2]
    V_z, M_y = 0, 0                # [N] skjær og [Nm] moment pga. vind

    if i.at_ledn:
        # Alltid 2 AT-ledninger
        d = 2 * sys.at_ledning["Diameter"] / 1000              # [m]
        V_z += q_z * G_C * C_C * d * a                         # [N]
        M_y += q_z * G_C * C_C * d * a * Hfj                   # [Nm]

    if i.matefjern_ledn:
        n = i.matefjern_antall
        d = n * sys.matefjernledning["Diameter"] / 1000        # [m]
        V_z += q_z * G_C * C_C * d * a                         # [N]
        M_y += q_z * G_C * C_C * d * a * Hfj                   # [Nm]

    if i.jord_ledn:
        d = sys.jordledning["Diameter"] / 1000                 # [m]
        V_z += q_z * G_C * C_C * d * a                         # [N]
        M_y += q_z * G_C * C_C * d * a * Hj                    # [Nm]

    if i.retur_ledn:
        # Alltid 2 returledninger
        d = 2 * sys.returledning["Diameter"] / 1000            # [m]
        V_z += q_z * G_C * C_C * d * a                         # [N]
        M_y += q_z * G_C * C_C * d * a * Hr                    # [Nm]

    if i.forbigang_ledn:
        d = sys.returledning["Diameter"] / 1000                # [m]
        V_z += q_z * G_C * C_C * d * a                         # [N]
        M_y += q_z * G_C * C_C * d * a * Hf                    # [Nm]

    if i.fiberoptisk_ledn:
        d = sys.fiberoptisk["Diameter"] / 1000                 # [m]
        V_z += q_z * G_C * C_C * d * a                         # [N]
        M_y += q_z * G_C * C_C * d * a  * FH                   # [Nm]

    if i.fixpunktmast or i.fixavspenningsmast:
        d = sys.fixline["Diameter"] / 1000                     # [m]
        V_z += q_z * G_C * C_C * d * a                         # [N]
        M_y += q_z * G_C * C_C * d * a * (FH + SH)             # [Nm]

    # Vindlast på KL
    d = sys.kontakttraad["Diameter"] / 1000                    # [m]
    V_z += q_z * G_C * C_C * d * a                             # [N]
    M_y += q_z * G_C * C_C * d * a * FH                        # [Nm]

    # Vindlast på bæreline
    d = sys.baereline["Diameter"] / 1000                       # [m]
    V_z += q_z * G_C * C_C * d * a                             # [N]
    M_y += q_z * G_C * C_C * d * a * (FH + (SH / 2))           # [Nm]

    # Vindlast på hengetråd.
    # Det regnes med 8m hengetråd for et mastefelt på 60m.
    d = sys.hengetraad["Diameter"] / 1000                       # [m]
    V_z += q_z * G_C * C_C * d * 8                              # [N]
    M_y += V_z * (FH + SH / 2)                                  # [Nm]

    # Vindlast på Y-line
    if not sys.y_line == None:
        d = sys.y_line["Diameter"] / 1000                        # [m]
        L = 0  # Lengde av Y-line; systemavhengig
        if (sys.navn == "20a" or sys.navn == "35") and r >= 800:
            L = 14
        elif sys.navn == "25" and r >= 1200:
            L = 18
        V_z += q_z * G_C * C_C * d * L                            # [N]
        M_y += q_z * G_C * C_C * d * L * (FH + SH / 2)            # [Nm]

    # Deformasjon D_z pga. vindlast på ledninger.
    D_z = _beregn_vindforskyvning_ledninger(V_z, mast, i)

    R = numpy.zeros((15, 9))
    R[12][0] = M_y
    R[12][3] = V_z
    R[12][8] = D_z
    R[13][0] = - M_y
    R[13][3] = - V_z
    R[13][8] = - D_z

    return R


def vindlast_mast_normalt_spor_NEK(mast, i):
    """Denne funksjonen beregner resultantkraften på masten og
    deformasjon pga. vind når vinden blåser normalt på sporet
    {EN 50 119}. Vinkelen (phi) bestemmer hvorvidt viden blåser fra
    mast mot spor (0 rad) eller fra spor mot mast ((pi) rad)."""

    # Antar konservativt en rektangulær vindlastfordeling på masten.

    # Inngangsparametre
    H = i.h                        # [m] Høyde av mast.
    G_str = 1.0                    # [1] Resonansfaktor for stål
    phi = 0                        # [rad] Vindens innfallsvinkel
    A_str = mast.A_ref             # [m^2] Mastens referanseareal
    q_z = _beregn_vindtrykk_NEK()  # [N / m^2]
    V_z, M_y, D_z = 0, 0, 0        # [N], [Nm], [mm]

    if mast.type == "bjelke":
        C_str = 1.4
        # Vindkraft på mast, vind normalt spor [N]
        V_z = q_z * G_str * C_str * A_str
        M_y = V_z * (H / 2)
    elif mast.type == "B":
        C_str = 2.0
        # Vindkraft på mast, vind normalt spor [N]
        V_z = q_z * G_str * C_str * A_str
        M_y = V_z * (H / 2)
    elif mast.type == "H":
        G_lat = 1.05  # [1] Resonansfaktor for H-mast
        C_lat = 2.80  # [1] Drag faktor for H-mast
        V_z = q_z * G_lat * (1.0 + 0.2 * (math.sin(2 * phi) ** 2)) * C_lat * A_str
        M_y = V_z * (H / 2)

    # Forskyvning dz [mm] i høyde FH pga. vindlasten q_z på masten.
    D_z = _beregn_vindforskyvning_Dz(mast, i, False)

    R = numpy.zeros((15, 9))
    R[12][0] = M_y
    R[12][3] = V_z
    R[12][8] = D_z
    R[13][0] = - M_y
    R[13][3] = - V_z
    R[13][8] = - D_z

    return R


def vindlast_mast_parallelt_spor_NEK(mast, i):
    """Denne funksjonen beregner resultantkraften på mast og isolatorer
     pga. vind når vinden blåser parallelt sporet {EN 50 119}."""

    # Antar konservativt en rektangulær vindlastfordeling på masten.

    # Inngangsparametre
    H = i.h                        # [m] Høyde på masten
    G_str = 1.0                    # [1] Resonansfaktor for stål
    phi = math.pi / 2              # [rad] Vindens innfallsvinkel
    A_str = mast.A_ref_par         # [m^2]
    q_z = _beregn_vindtrykk_NEK()  # [N / m^2]
    V_y, M_z, T = 0, 0, 0          # [N], [Nm], [Nm]

    if mast.type == "bjelkemast" or mast.type == "B-mast":
        C_str = 1.4
        # Vindkraft på mast [N]
        V_y = q_z * G_str * C_str * A_str
        M_z = V_y * (H / 2)
    elif mast.type == "H-mast":
        G_lat = 1.05  # [1] Resonansfaktor for H-mast
        C_lat = 2.80  # [1] Drag faktor for H-mast
        V_y = q_z * G_lat * (1.0 + 0.2 * (math.sin(2 * phi) ** 2)) * C_lat * A_str
        M_z = V_y * (H / 2)

    # Bidrag fra isolatorer.
    FH = i.fh     # [m] KL-høyde
    SH = i.sh     # [m] Systemhøyde
    G_ins = 1.05  # [1] Resonansfaktor for isolator
    C_ins = 1.20  # [1] Dragfaktor for isolator
    A_ins = 1.0     # [m^2] Arealet av isolator??????????????????????????
    q_z = _beregn_vindtrykk_NEK()

    # Vindkraften på en isolator [N]. Det er to isolatorer på utligger.
    V_y_ins = q_z * G_ins * C_ins * A_ins

    # Det er en isolator i høyde FH og en i høyde (FH + SH).
    # Dette gir følgende moment- og torsjonsbidrag [Nm]
    M_z_ins = V_y_ins * FH + V_y_ins * (FH + SH)

    # Finner mastebredden i høyde FH og (FH + SH).
    b_FH = mast.bredde((H - FH)) / 2
    T += V_y_ins * b_FH
    b_SH = mast.bredde((H - (FH + SH))) / 2
    T += V_y_ins * b_SH

    # Foeskyvning pga. vindlast parallelt sporet.
    D_y = _beregn_vindforskyvning_Dy(mast, i, False)

    R = numpy.zeros((15, 9))
    # Utliggeren har 2 isolatorer
    R[14][1] = V_y + 2 * V_y_ins
    R[14][2] = M_z + M_z_ins
    R[14][5] = T
    R[14][7] = D_y

    return R


def snolast_ledninger_NEK(mast, sys, i, a_T):
    """Beregner snølast på ledninger etter tips fra Svein Fikke"""

    # ISO 12494, Tabell 5: Snølast på ledning
    # Navn: [RX], Vekt: [kg/m], L_10: [mm], D_10: [mm], L_30: [mm], D_30: [mm]
    R1 = {"Navn": "R1", "Vekt": 0.5, "L_10": 54, "D_10": 22, "L_30": 34, "D_30": 35}
    R2 = {"Navn": "R2", "Vekt": 0.9, "L_10": 78, "D_10": 28, "L_30": 54, "D_30": 40}
    R3 = {"Navn": "R3", "Vekt": 1.6, "L_10": 109, "D_10": 36, "L_30": 82, "D_30": 47}
    R4 = {"Navn": "R4", "Vekt": 2.8, "L_10": 150, "D_10": 46, "L_30": 120, "D_30": 56}
    R5 = {"Navn": "R5", "Vekt": 5.0, "L_10": 207, "D_10": 60, "L_30": 174, "D_30": 70}

    g = 9.81            # [m / s^2]
    a = i.masteavstand  # [m]
    r = i.radius        # [m]
    sms = i.sms         # [m]
    FH = i.fh

    # Representativ snølast på én ledning [N / m]
    q_sno = R3["Vekt"] * g

    # Snølastens bidrag til [R]
    N, M_y, D_z = 0, 0, 0

    h_utligger = FH + (i.sh / 2)

    # Utliggere
    N += q_sno * sms
    M = q_sno * (sms / 2) * a_T
    M_y += M
    D_z += deformasjon._beregn_deformasjon_M(mast, M, h_utligger, FH)

    # Bæreline
    N += q_sno * a
    M = q_sno * a * a_T
    M_y += M
    D_z += deformasjon._beregn_deformasjon_M(mast, M, h_utligger, FH)

    # Kontakttråd
    N += q_sno * a
    M = q_sno * a * a_T
    M_y += M
    D_z += deformasjon._beregn_deformasjon_M(mast, M, h_utligger, FH)

    # AT-ledninger (2 stk.)
    if i.at_ledn:
        N += 2 * q_sno * a                                      # [N]

    # Mate-/fjernledning (n stk.)
    if i.matefjern_ledn:
        N += i.matefjern_antall * q_sno * a                     # [N]

    # Jordledning (1 stk.)
    if i.jord_ledn:
        N += q_sno * a                                          # [N]
        if i.matefjern_ledn or i.at_ledn or i.forbigang_ledn:
            arm = -0.3
            M = q_sno * a * arm
            M_y += M
            D_z += deformasjon._beregn_deformasjon_M(mast, M, i.hj, FH)

    # Returledning (2 stk.)
    if i.retur_ledn:
        N += 2 * q_sno * a
        arm = -0.5
        M = 2 * q_sno * a * arm
        M_y += M
        D_z += deformasjon._beregn_deformasjon_M(mast, M, i.hr, FH)

    # Forbigangsledning (1 stk.)
    if i.forbigang_ledn:
        N += q_sno * a
        if i.matefjern_ledn or i.at_ledn or i.jord_ledn:
            # Eksentrisitet, forbigangsledning henger i bakkant av mast
            arm = -0.3
            M = q_sno * a * arm
            M_y += M
            D_z += deformasjon._beregn_deformasjon_M(mast, M, i.hf, FH)

    # Fiberoptisk ledning (1 stk.)
    if i.fiberoptisk_ledn:
        N += q_sno * a

    # Y-line
    if not sys.y_line == None:
        L = 0  # Lengde av Y-line; systemavhengig
        if (sys.navn == "20a" or sys.navn == "35") and r >= 800:
            L = 14
        elif sys.navn == "25" and r >= 1200:
            L = 18
        N += q_sno * L
        M = q_sno * L * a_T
        M_y += M

    # Fixline
    if i.fixpunktmast or i.fixavspenningsmast:
        N += q_sno * (a / 2)
        if i.fixpunktmast:
            N += q_sno * (a / 2)
            M = q_sno * a * a_T
            M_y += M
            D_z += deformasjon._beregn_deformasjon_M(mast, M, h_utligger, FH)

    R = numpy.zeros((15, 9))
    R[11][0] = M_y
    R[11][4] = N
    R[11][8] = D_z

    return R
