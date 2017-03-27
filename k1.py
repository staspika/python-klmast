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
import deformasjon


def sidekraft(sys, i, mast, a_T, a_T_dot, B1, B2):
    """Beregner sidekraft [kN] og moment [kNm] ved normal ledningsføring,
    samt forskyvning [mm]. Videre beregnes vandringskraften pga.
    temperatureffekter."""

    # Inngangsparametre
    s_kl = 1000 * sys.kontakttraad["Strekk i ledning"]  # [N]
    s_b = 1000 * sys.baereline["Strekk i ledning"]      # [N]
    b_mast = mast.bredde(i.h - i.fh) / 1000             # [m]
    r = i.radius                                        # [m]
    a = i.masteavstand                                  # [m]
    FH = i.fh                                           # [m]
    SH = i.sh                                           # [m]
    alpha = 1.7 * 10 ** (-5)                            # [1/(grader C)]
    delta_t = 45                                        # [(grader C)]

    # Deklarerer variablene Vz, Vy, Mz, My, T = 0
    V_kl, V_b = 0, 0
    V_y_kl = 0
    M_z, M_y, T = 0, 0, 0

    if not i.fixpunktmast and not i.fixavspenningsmast:
        if i.strekkutligger:
            # Strekkraft virker i positiv z-retning [N]
            V_kl += s_kl * ((a / r) + 2 * ((B2 - B1) / a))
            V_b += s_b * (a / r)

            # Tilleggskraft dersom siste mast før avspenning [N]
            # Neste mast på den andre siden av sporet.
            if i.siste_for_avspenning and i.master_bytter_side:
                V_kl += s_kl * (a_T / a)
                V_b += s_b * (a_T / a)
                # Neste mast på samme side av sporet.
            elif i.siste_for_avspenning and not i.master_bytter_side:
                V_kl -= s_kl * (a_T / a)
                V_b -= s_b * (a_T / a)
            # Momentet gir strekk på baksiden av mast ift. spor [Nm]
            M_y += V_kl * FH + (V_b * (FH + SH))
        else:
            # Trykkraft virker i negativ z-retning [N]
            V_kl -= s_kl * ((a / r) + 2 * ((B2 - B1) / a))
            if r < 1200:
                # Trykkutligger i innerkurve
                V_b -= s_b * (a / r)
            else:
                # Trykkutliggere både i inner og ytterkurve. Velger (+)
                V_b += s_b * (a / r)

            # Tilleggskraft dersom siste mast før avspenning [N]
            # Neste mast på den andre siden av sporet.
            if i.siste_for_avspenning and i.master_bytter_side:
                V_kl += s_kl * (a_T_dot / a)
                V_b += s_b * (a_T_dot / a)
                # Neste mast på den samme siden av sporet.
            elif i.siste_for_avspenning and not i.master_bytter_side:
                V_kl -= s_kl * (a_T_dot / a)
                V_b -= s_b * (a_T_dot / a)
            # Momentet gir strekk på sporsiden av masten [Nm].
            M_y -= - V_kl * FH - (V_b * (FH + SH))

    # Forskyvning dz [mm] pga. V_kl og V_b
    dz_kl = deformasjon._beregn_deformasjon_P(mast, V_kl, FH, FH)
    dz_b = deformasjon._beregn_deformasjon_P(mast, V_b, (FH + SH), FH)

    # Ved temperaturendring vil KL vandre og utligger følge med.
    # Beregner maksimal skråstilling av utligger [m]
    dl = alpha * delta_t * i.avstand_fixpunkt

    if not i.siste_for_avspenning and not i.avspenningsmast\
            and not i.linjemast_utliggere == 2:
        # Vandringskraft parallelt spor i primærfelt (én utligger)
        if i.strekkutligger:
            V_y_kl = V_kl * (dl / a_T)         # [N]
        else:
            V_y_kl = V_kl * (dl / a_T_dot)     # [N]
        M_z = V_y_kl * FH                      # [Nm]
        T = V_y_kl * b_mast                    # [Nm]

    # Forskyvning dy [mm] pga vandringskraften V_y
    dy_kl = deformasjon._beregn_deformasjon_Py(mast, V_y_kl, FH, FH)

    R = numpy.zeros((15, 9))
    R[1][0] = M_y
    R[1][1] = V_y_kl
    R[1][2] = M_z
    R[1][3] = V_kl + V_b
    R[1][5] = T
    R[1][7] = dy_kl
    R[1][8] = dz_kl + dz_b

    return R
