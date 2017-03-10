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


def sidekraft(sys, i, mast, a_T, a_T_dot, a, B1, B2):
    """Beregner sidekraft [kN] og moment [kNm] ved normal ledningsføring,
    samt forskyvning [mm]. Videre beregnes vandringskraften pga.
    temperatureffekter."""

    # Inngangsparametre
    S = 1000 * sys.kontakttraad["Strekk i ledning"]  # [N]
    b_mast = mast.bredde(i.h - i.fh) / 1000          # [m]
    r = i.radius                                     # [m]
    FH = i.fh                                        # [m]
    E = mast.E                                       # [N/(mm^2)]
    alpha = 1.7 * 10 ** (-5)                         # [1/(grader C)]
    delta_t = 45                                     # [(grader C)]

    # Initierer Vz, Vy, Mz, My, T = 0 av hensyn til Python
    V_z = 0
    V_y = 0
    M_z = 0
    M_y = 0
    T = 0

    if not i.fixpunktmast and not i.fixavspenningsmast:
        if i.strekkutligger:
            # Strekkraft virker i positiv z-retning [N]
            V_z += S * ((a / r) + 2 * ((B2 - B1) / a))

            # Tilleggskraft dersom siste seksjonsmast før avspenning.
            # Neste mast på den andre siden av sporet.
            if i.siste_for_avspenning and i.master_bytter_side:
                V_z += S * (a_T / a)
                # Neste mast på samme side av sporet.
            elif i.siste_for_avspenning and not i.master_bytter_side:
                V_z -= S * (a_T / a)
            # Momentet gir strekk på baksiden av mast ift. spor [Nm]
            M_y += V_z * FH
        else:
            # Trykkraft virker i negativ z-retning [N]
            V_z -= - S * ((a / r) + 2 * ((B2 - B1) / a))

            # Tilleggskraft dersom siste seksjonsmast før avspenning [N].
            # Neste mast på den andre siden av sporet.
            if i.siste_for_avspenning and i.master_bytter_side:
                V_z += S * (a_T_dot / a)
                # Neste mast på den samme siden av sporet.
            elif i.siste_for_avspenning and not i.master_bytter_side:
                V_z -= S * (a_T_dot / a)
            # Momentet gir strekk på sporsiden av masten [Nm].
            M_y -= - V_z * FH

    # Forskyvning dz [mm] pga. V_z
    Iy_13 = mast.Iy(mast.h*(2/3))  # Iy i tredjedelspunktet
    dz_kl = (V_z / (2 * E * Iy_13)) * ((2 / 3) * FH ** 3)

    # Ved temperaturendring vil KL vandre og utligger følge med.
    # Beregner maksimal skråstilling av utligger [m]
    dl = alpha * delta_t * i.avstand_fixpunkt

    if not i.siste_for_avspenning and not i.avspenningsmast\
            and not i.linjemast_utliggere == 2:
        # Kraft parallelt spor i primærfelt (én utligger)
        V_y = V_z * (dl / a_T)      # [N]
        M_z = V_y * FH              # [Nm]
        T = V_y * b_mast   # [Nm]

    # Forskyvning dy [mm] pga vandringskraften V_y
    Iz_13 = mast.Iz(mast.h*(2/3))  # Iz i tredjedelspunktet
    dy_vandre = (V_y / (2 * E * Iz_13)) * ((2 / 3) * FH ** 3)

    R = numpy.zeros((15, 9))
    R[1][0] = M_y
    R[1][1] = V_y
    R[1][2] = M_z
    R[1][3] = V_z
    R[1][5] = T
    R[1][7] = dy_vandre
    R[1][8] = dz_kl

    return R
