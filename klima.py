import math
import numpy

# Terrengkategorier etter EC1, NA.4.1
kat0 = {"k_r": 0.16, "z_0": 0.003, "z_min": 2.0}
kat1 = {"k_r": 0.17, "z_0": 0.01, "z_min": 2.0}
kat2 = {"k_r": 0.19, "z_0": 0.05, "z_min": 4.0}
kat3 = {"k_r": 0.22, "z_0": 0.3, "z_min": 8.0}
kat4 = {"k_r": 0.24, "z_0": 1.0, "z_min": 16.0}
terrengkategorier = ([kat0, kat1, kat2, kat3, kat4])


def beregn_vindkasthastighetstrykk_EC(z):
    """Beregner dimensjonerende vindkasthastighetstrykk [kN/m^2]
    med bruk av Eurokode 1 (EC1)."""

    # Inngangsparametre
    c_dir = 1.0     # [1] Retningsfaktor
    c_season = 1.0  # [1] Årstidsfaktor
    c_alt = 1.0     # [1] Nivåfaktor
    c_prob = 1.0    # [1] Faktor dersom returperioden er mer enn 50 år
    v_b_0 = 25      # [m/s] Referansevindhastighet for aktuell kommune
    kategori = 1
    # ---------------------------!!NB!!-------------------------------#
    #
    #   Hvordan settes terrengformfaktoren c_0 riktig?
    #   Hva med v_b_0 ?
    #
    # ----------------------------------------------------------------#
    c_0 = 1.0       # [1] Terrengformfaktoren

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
    q_m = 0.5 * rho * (v_m)**2  # [(m / s)^2]

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

    cf = 2.2                   # [1] Vindkraftfaktor mast
    q = q_p * cf * mast.A_ref  # [N / m]
    q_R = q * z                # [N] Kraftresultant

    return q_R


def total_ledningsdiameter(i, sys):
    """Summerer ledningsdiametere [m] for klimalaster"""

    d_tot = 0  # [mm] Total ledningsdiameter for vindlast

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

    # Inngangsparametre
    d_total = total_ledningsdiameter(i, sys)
    cf = 1.1                # [1] Vindkraftfaktor ledning
    A_ledn = d_total * 1    # [m^2] Diameter multiplisert med 1m lengde

    # Vindlast på ledninger # [N]
    q_ledn = q_p * cf * A_ledn

    return q_ledn


def isogsno_last(i, sys):
    """Beregner snø og islast basert på SIEMENS System 20."""

    d_total = total_ledningsdiameter(i, sys)

    # Snø- og islast pr. meter ledning [N/m].
    q_sno = (2.5 + 0.5 * d_total)

    return q_sno

# ====================================================================#
#                                                                     #
#               Herfra brukes EN standarder.                          #
#                                                                     #
# ====================================================================#


def beregn_vindtrykk_EN():
    """Denne funksjonen beregner vindtrykket {EN 50 119}."""

    # Inngangsparametre for referansehøyde 10m over bakkenivå
    z = 10              # [m] høyde over bakken
    rho = 1.255         # [kg / m^3]
    G_q = 2.05          # [1] Gust-respons faktor
    G_t = 1.0           # [1] Terrengfaktor av typen åpent
    v_10 = 24           # [m / s] 10-min middelvindhastighet
    # Ruhetsparameteren for ulike terrengkategorier [1]
    alpha = [0.12, 0.16, 0.20, 0.28]

    # Vindhastigheten i høyden z over bakkenivå etter EN 50 125-2.
    v_z = v_10 * (z/10) ** alpha[3]

    # Dynamisk vindtrykk [N / m^2]
    q_z = 0.5 * rho * G_q * G_t * v_z ** 2

    return q_z


def beregn_vindforskyvning_mast(mast, i):
    """Denne funksjonen beregner forskyvning Dz av masten på grunn av
    vindlast på masten, vinkelrett på sporet."""

    # Inngangsparametre
    E = mast.E                              # [N/mm^2] E-modul, stål
    FH = i.fh * 1000                        # [mm] Høyde, KL
    H = i.h * 1000                          # [mm] Høyde, mast
    Iy_13 = mast.Iy(mast.h * (2 / 3))       # [mm^4] Iy i 1/3-punktet
    q_z = beregn_vindtrykk_EN() / 1000 ** 2 # [N / mm^2]

    # Forskyvning dz [mm] i høyde FH pga. vindlasten q_z på masten.
    D_z = ((q_z * FH ** 2) / (24 * E * Iy_13)) * (6 * H ** 2 - 4 * H * (FH ** 3) + FH ** 2)

    return D_z


def vindlast_ledninger_EN(sys, i, a):
    """Denne funksjonen beregner vindkraft på KL {EN 50 119}. Denne
    gjelder kun for vindretning fra mast vinkelrett mot spor."""

    # Inngangsparametre
    FH = i.fh                    # [m] Kontaktledninshøyden
    SH = i.sh                    # [m] Systemhøyde
    Hf = i.hf                    # [m] Høyde, forbigangsledning
    Hj = i.hj                    # [m] Høyde, jordledning
    Hr = i.hr                    # [m] Høyde, returledning
    Hfj = i.hfj                  # [m] Høyde, fjernledning
    phi = 0                      # [rad] Innfallsvinkel vind normalt
    G_C = 0.75                   # [1] Responsfaktor
    C_C = 1.0                    # [1] Drag-faktor
    q_z = beregn_vindtrykk_EN()  # [N / m^2]
    V_z = 0                      # [N] Skjærkraft pga. vindlast
    M_y = 0                      # [Nm] Moment pga. vindlast

    if i.at_ledn:
        # Alltid 2 AT-ledninger
        d = 2 * sys.at_ledning["Diameter"] / 1000              # [m]
        V_z += q_z * G_C * C_C * d * a * (math.cos(phi) ** 2)  # [N]
        M_y += V_z * Hfj                                       # [Nm]

    if i.matefjern_ledn:
        n = i.matefjern_antall
        d = n * sys.matefjernledning["Diameter"] / 1000        # [m]
        V_z += q_z * G_C * C_C * d * a * (math.cos(phi) ** 2)  # [N]
        M_y += V_z * Hfj                                       # [Nm]

    if i.jord_ledn:
        d = sys.jordledning["Diameter"] / 1000                 # [m]
        V_z += q_z * G_C * C_C * d * a * (math.cos(phi) ** 2)  # [N]
        M_y += V_z * Hj                                        # [Nm]

    if i.retur_ledn:
        # Alltid 2 returledninger
        d = 2 * sys.returledning["Diameter"] / 1000            # [m]
        V_z += q_z * G_C * C_C * d * a * (math.cos(phi) ** 2)  # [N]
        M_y += V_z * Hr                                        # [Nm]

    if i.forbigang_ledn:
        d = sys.returledning["Diameter"] / 1000                # [m]
        V_z += q_z * G_C * C_C * d * a * (math.cos(phi) ** 2)  # [N]
        M_y += V_z * Hf                                        # [Nm]

    if i.fiberoptisk_ledn:
        d = sys.fiberoptisk["Diameter"] / 1000                 # [m]
        V_z += q_z * G_C * C_C * d * a * (math.cos(phi) ** 2)  # [N]
        M_y += V_z * FH                                        # [Nm]

    if i.fixpunktmast or i.fixavspenningsmast or i.avspenningsmast:
        d = sys.fixline["Diameter"] / 1000                     # [m]
        V_z += q_z * G_C * C_C * d * a * (math.cos(phi) ** 2)  # [N]
        M_y += V_z * (FH + SH)                                 # [Nm]

    # Vindlast på KL
    d_KL = sys.kontakttraad["Diameter"] / 1000                 # [m]
    V_z += q_z * G_C * C_C * d_KL * a * (math.cos(phi) ** 2)   # [N]
    M_y += V_z * FH                                            # [Nm]

    # Vindlast på bæreline
    d_bl = sys.baereline["Diameter"] / 1000                    # [m]
    V_z += q_z * G_C * C_C * d_bl * a * (math.cos(phi) ** 2)   # [N]
    M_y += V_z * (FH + (SH / 2))                               # [Nm]

    # Bidrag fra hengetråder ??????????????????????????????????????????

    R = numpy.zeros((15, 9))
    R[12][0] = M_y
    R[12][3] = V_z

    return R


def vindlast_mast_normalt_spor(mast, i):
    """Denne funksjonen beregner resultantkraften på masten og
    deformasjon pga. vind når vinden blåser normalt på sporet
    {EN 50 119}. Vinkelen (phi) bestemmer hvorvidt viden blåser fra
    mast mot spor (0 rad) eller fra spor mot mast ((pi) rad)."""

    # Antar konservativt en rektangulær vindlastfordeling på masten.

    # Inngangsparametre
    H = i.h                      # [m] Høyde av mast.
    G_str = 1.0                  # [1] Resonansfaktor for stål
    phi = 0                      # [rad] Vindens innfallsvinkel
    A_str = mast.A_ref           # [m^2] Mastens referanseareal
    q_z = beregn_vindtrykk_EN()  # [N / m^2]
    V_z, M_y, D_z = 0, 0, 0      # [N], [Nm], [mm]

    if mast.type == "bjelkemast":
        C_str = 1.4
        # Vindkraft på mast, vind normalt spor [N]
        V_z = q_z * G_str * C_str * A_str
        M_y = V_z * (H / 2)
    elif mast.type == "B-mast":
        C_str = 2.0
        # Vindkraft på mast, vind normalt spor [N]
        V_z = q_z * G_str * C_str * A_str
        M_y = V_z * (H / 2)
    elif mast.type == "H-mast":
        G_lat = 1.05  # [1] Resonansfaktor for H-mast
        C_lat = 2.80  # [1] Drag faktor for H-mast
        V_z = q_z * G_lat * (1.0 + 0.2 * (math.sin(2 * phi) ** 2)) * C_lat * A_str
        M_y = V_z * (H / 2)

    # Forskyvning dz [mm] i høyde FH pga. vindlasten q_z på masten.
    D_z = beregn_vindforskyvning_mast(mast, i)

    R = numpy.zeros((15, 9))
    # Her plasseres resultatene i rad #12, siden (phi) = 0.
    # Det betyr at vinden blåser fra mast mot spor.
    R[12][0] = M_y
    R[12][3] = V_z
    R[12][8] = D_z


def vindlast_mast_parallelt_spor(mast, i):
    """Denne funksjonen beregner resultantkraften på mast og isolatorer
     pga. vind når vinden blåser parallelt sporet {EN 50 119}."""

    # Antar konservativt en rektangulær vindlastfordeling på masten.

    # Inngangsparametre
    H = i.h                      # [m] Høyde på masten
    G_str = 1.0                  # [1] Resonansfaktor for stål
    phi = math.pi / 2            # [rad] Vindens innfallsvinkel
    A_str = mast.A_ref           # [m^2]
    q_z = beregn_vindtrykk_EN()  # [N / m^2]
    V_y, M_z = 0, 0              # [N], [Nm]

    if mast.type == "bjelkemast" or mast.type == "B-mast":
        C_str = 1.4
        # Vindkraft på mast [N]
        # Hva blir A_Str for denne retningen???????????????????????????
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
    A_ins = 1     # [m^2] Arealet av isolator??????????????????????????
    q_z = beregn_vindtrykk_EN()

    # Vindkraften på en isolator [N]
    V_y_ins = q_z * G_ins * C_ins * A_ins

    # Det er en isolator i høyde FH og en i høyde (FH + SH).
    # Dette gir følgende momentbidrag [Nm]
    M_z_ins = V_y_ins * FH + V_y_ins * (FH + SH)  # ???????????????????

    R = numpy.zeros((15, 9))
    R[14][1] = V_y + V_y_ins
    R[14][2] = M_z + M_z_ins  # ??????????????? M_z_ins ???????????????

    return R
