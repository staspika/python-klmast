# ====================================================================#
# Dette skriptet beregner krefter fra loddavspente ledninger (KL):
#   (1) Normal ledningsføring
#   (2) Vandringskraft
# 21.02.2017
# ====================================================================#
"""Pga. ledningens sikksakk og sporets kurvatur vil ledningens
strekkraft gi en komponent normalt på sporet. Kraften overføres
til fundament som moment og skjærkraft."""

import numpy


def beregn_torsjonsarm(mast, i):
    """Finner avstand fra flens til senter mast i høyde FH."""

    if not mast.type == "bjelke":
        return mast.topp + 2 * (i.h - i.fh) * mast.stign

    return mast.b


def sidekraft(sys, i, mast, a_T, a_T_dot, a, B1, B2):
    """Beregner sidekraft [kN] og moment [kNm] ved normal ledningsføring,
    samt forskyvning [mm]. Videre beregnes vandringskraften pga.
    temperatureffekter."""

    # Inngangsparametre
    S = 1000 * sys.kontakttraad["Strekk i ledning"]  # [N]
    b_mast = beregn_torsjonsarm(mast, i) / 2  # Avstand flens - C mast
    r = i.radius
    FH = i.fh
    E = mast.E                  # E-modulen for stål [N/mm^2]
    alpha = 1.7 * 10 ** (-5)    # [1/(grader Celsius)]
    delta_t = 45                # Temperaturdifferanse i [(grader Celsius)]
    a_s = 2.0                   # avstand fra c mast til KL [m]

    # Initierer Vz, Vy, Mz, My, T dz_kl, dy_kl = 0 av hensyn til Python
    V_z = 0
    V_y = 0
    M_z = 0
    M_y = 0
    T = 0
    dz_kl = 0
    dy_vandre = 0

    if not i.fixpunktmast and not i.fixavspenningsmast:
        if i.strekkutligger:
            # Strekkraft virker i positiv z-retning [N]
            V_z += S * ((a / r) + 2 * ((B2 - B1) / a))

            # Tilleggskraft hvis siste seksjonsmast før avspenning [N]
            # Neste mast på den andre siden av sporet.
            if i.siste_for_avspenning and i.master_bytter_side:
                V_z += S * (a_T / a)
                # Neste mast på samme side av sporet.
            elif i.siste_for_avspenning and not i.master_bytter_side:
                V_z -= S * (a_T / a)
            # Momentet gir strekk på baksiden av mast ift. spor. [Nm]
            M_y += V_z * FH
        else:
            # Trykkraft virker i negativ z-retning [N]
            V_z -= - S * ((a / r) + 2 * ((B2 - B1) / a))

            # Tilleggskraft hvis siste seksjonsmast før avspenning [N]
            # Neste mast på den andre siden av sporet.
            if i.siste_for_avspenning and i.master_bytter_side:
                V_z += S * (a_T_dot / a)
                # Neste mast på den samme siden av sporet.
            elif i.siste_for_avspenning and not i.master_bytter_side:
                V_z -= S * (a_T_dot / a)
            # Momentet gir strekk på sporsiden av masten [Nm]
            M_y -= - V_z * FH

    # Forskyvning dz [mm] pga. V_z
    if mast.type == "B" or mast.type == "H":
        Iy_steg = mast.Iy
        A_steg = mast.Asteg
        b_13 = mast.b_13
        Iy_13 = mast.Iy_13

        dz_kl = (V_z / (2 * E * Iy_13)) * ((2 / 3) * FH ** 3)
    elif mast.type == "bjelke":
        Iy = mast.Iy

        dz_kl = (V_z / (2 * E * Iy)) * ((2 / 3) * FH ** 3)

    R = numpy.zeros((15, 9))
    R[1][0] = M_y
    R[1][3] = V_z
    R[1][8] = dz_kl

    # Ved temperaturendring vil KL vandre og utligger følge med.
    # Beregner maksimal skråstilling av utligger [m]
    dl = alpha * delta_t * i.avstand_fixpunkt

    if i.siste_for_avspenning or i.avspenningsmast or i.linjemast_utliggere == 2:
        # Ingen vandringskraft i parallellfelt (to utliggere)
        V_y = 0
    else:
        # Kraft parallelt spor i primærfelt (én utligger) [N]
        V_y = V_z * (dl / a_T)
        M_z = V_y * FH
        T = V_y * b_mast

    # Forskyvning dy [mm] pga vandringskraften V_y
    if mast.type == "B":
        # B-mast har ulike tv.sn. egenskaper i x- og y-retning.
        Iz_steg = mast.Iz
        A_steg = mast.Asteg
        d = mast.d  # Dybden av B-mast er konstant.

        Iz_13 = (Iz_steg + A_steg * (d / 2) ** 2) * 2

        dy_vandre = (V_y / (2 * E * Iz_13)) * ((2 / 3) * FH ** 3)
    elif mast.type == "H":
        # H-mast har like tv.sn. egenskaper i begge retninger.
        Iz_steg = mast.Iy  # pga symmetri er Iz == Iy
        A_steg = mast.Asteg
        d_13 = mast.b_13   # pga symmetri er d_13 == b_13

        Iz_13 = ((Iz_steg + A_steg * (d_13 / 2) ** 2) * 2) * 2

        dy_vandre = (V_y / (2 * E * Iz_13)) * ((2 / 3) * FH ** 3)
    elif mast.type == "bjelke":
        Iz = mast.Iz

        dy_vandre = (V_z / (2 * E * Iz)) * ((2 / 3) * FH ** 3)

    R = numpy.zeros((15, 9))
    R[1][1] = V_y
    R[1][2] = M_z
    R[1][5] = T
    R[1][7] = dy_vandre

    return R
