import math

# Terrengkategorier etter EC1, NA.4.1
kat0 = {"k_r": 0.16, "z_0": 0.003, "z_min": 2.0}
kat1 = {"k_r": 0.17, "z_0": 0.01, "z_min": 2.0}
kat2 = {"k_r": 0.19, "z_0": 0.05, "z_min": 4.0}
kat3 = {"k_r": 0.22, "z_0": 0.3, "z_min": 8.0}
kat4 = {"k_r": 0.24, "z_0": 1.0, "z_min": 16.0}
terrengkategorier = ([kat0, kat1, kat2, kat3, kat4])



def beregn_vindkasthastighetstrykk(z):
    """Beregner dimensjonerende vindkasthastighetstrykk [kN/m^2]."""

    # Inngangsparametre
    c_dir = 1.0     # Retningsfaktor
    c_season = 1.0  # Årstidsfaktor
    c_alt = 1.0     # Nivåfaktor
    c_prob = 1.0    # Faktor dersom returperioden er mer enn 50 år
    v_b_0 = 25      # Referansevindhastighet for aktuell kommune
    kategori = 1
    # ---------------------------!!NB!!-------------------------------#
    #
    #   Hvordan settes terrengformfaktoren c_0 riktig?
    #   Hva med v_b_0 ?
    #
    # ----------------------------------------------------------------#
    c_0 = 1.0       # Terrengformfaktoren


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
    rho = 1.25  # [kg/m^3] lufttettheten
    q_m = 0.5 * rho * (v_m)**2


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


def vindlast_mast(mast, q_p, z):
    """Beregner vindlast på mast pr. meter av konstruksjonen [kN]."""

    cf = 2.2  # Vindkraftfaktor mast
    q = q_p * cf * mast.A_ref  # [N/m]
    q_R = q * z  # Kraftresultant [N]

    return q_R

def total_ledningsdiameter(i, sys):
    """Summerer ledningsdiametere [m] for klimalaster"""

    d_tot = 0  # Total ledningsdiameter for vindlast [mm]

    if i.at_ledn:
        d_tot += 2 * sys.at_ledning["Diameter"]  # 2 stk

    if i.matefjern_ledn:
        n = i.matefjern_antall
        d_tot += n * sys.matefjernledning["Diameter"]  # n stk

    if i.jord_ledn:
        d_tot += sys.jordledning["Diameter"]

    if i.retur_ledn:
        d_tot += 2 * sys.returledning["Diameter"]  # 2 stk

    if i.forbigang_ledn:
        d_tot += sys.returledning["Diameter"]

    if i.fiberoptisk_ledn:
        d_tot += sys.fiberoptisk["Diameter"]

    if i.fixpunktmast or i.fixavspenningsmast or i.avspenningsmast:
        d_tot += sys.fixline["Diameter"]

    # Antall utliggere
    if i.siste_for_avspenning or i.avspenningsmast or i.linjemast_utliggere == 2:
        utliggere = 2
    else:
        utliggere = 1
    for utligger in range(utliggere):
        d_tot += sys.baereline["Diameter"]
        d_tot += sys.kontakttraad["Diameter"]
        d_tot += sys.hengetraad["Diameter"]
        if not sys.navn == "20b":  # 20B mangler Y-line
            d_tot += sys.y_line["Diameter"]

    d_total = d_tot / 1000  # Total ledningsdiameter i [m]

    return d_total

def vindlast_ledninger(i, sys, q_p):
    """Beregner vindlast på ledninger pr. meter [N/m]."""

    d_total = total_ledningsdiameter(i, sys)

    # Vindlast på ledninger
    cf = 1.1                # Vindkraftfaktor ledning
    A_ledn = d_total * 1    # Diameter multiplisert med 1m lengde [m^2]

    q_ledn = q_p * cf * A_ledn  # [N]

    return q_ledn


def isogsno_last(i, sys):
    """Beregner snø og islast basert på SIEMENS System 20."""

    d_total = total_ledningsdiameter(i, sys)

    # Snø- og islast pr. meter ledning [N/m].
    q_sno = (2.5 + 0.5 * d_total)

    return q_sno

