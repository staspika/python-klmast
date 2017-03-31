# ====================================================================#
# Dette skriptet beregner sidekrefter fra loddavspente ledninger (KL):
#   (1) Kurvekraft
#   (2) Sikksakk
#   (3) Siste seksjonsmast før avspenning
#   (4) Vandringskraft
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
    fh = i.fh                                           # [m]
    sh = i.sh                                           # [m]
    alpha = 1.7 * 10 ** (-5)                            # [1/(grader C)]
    delta_t = 45                                        # [(grader C)]

    # Deklarerer variablene V_kl, V_b, V_y_kl, M_z, T = 0
    V_kl, V_b = 0, 0
    V_y_kl = 0
    M_z, T = 0, 0

    # Antall utliggere
    if i.siste_for_avspenning or i.avspenningsmast or i.linjemast_utliggere == 2:
        utliggere = 2
    else:
        utliggere = 1

    # (1) Sidekraft pga. sporets kurvatur
    # NB! Antar LIKE spennlengder mellom master.
    # Strekkraft virker i positiv z-retning.
    if i.strekkutligger:
        V_kl += utliggere * s_kl * (a / r)  # [N]
        V_b += utliggere * s_b * (a / r)    # [N]
    # Trykkutligger: Trykkraft virker i negativ z-retning.
    else:
        # Bruker (-) da det antas at mast står i innerkurve.
        if r <= 1200:
            V_kl -= utliggere * s_kl * (a / r)
            V_b -= utliggere * s_b * (a / r)
        else:
            V_kl += utliggere * s_kl * (a / r)
            V_b += utliggere * s_b * (a / r)

    # (2) Sidekraft pga. kontakttrådens sikksakk
    # NB! Antar LIKE spennlengder mellom master.
    if i.strekkutligger:
        V_kl += utliggere * s_kl * 2 * ((B2 - B1) / a)
    # Trykkutligger: Trykkraft virker i negativ z-retning.
    else:
        V_kl -= utliggere * s_kl * 2 * ((B2 - B1) / a)

    # (3) Sidekraft dersom siste mast før avspenning
    # Strekkutligger --> a_T benyttes
    if i.siste_for_avspenning and i.strekkutligger:
        if i.master_bytter_side:
            V_kl += utliggere * s_kl * (a_T / a)
            V_b += utliggere * s_b * (a_T / a)
        # Bidraget er negativt når mastene står på samme side
        else:
            V_kl -= utliggere * s_kl * (a_T / a)
            V_b -= utliggere * s_b * (a_T / a)
    # Trykkutligger --> a_T_dot benyttes
    if i.siste_for_avspenning and not i.strekkutligger:
        if i.master_bytter_side:
            V_kl += utliggere * s_kl * (a_T_dot / a)
            V_b += utliggere * s_b * (a_T_dot / a)
        # Bidraget er negativt når mastene står på samme side
        else:
            V_kl -= utliggere * s_kl * (a_T_dot / a)
            V_b -= utliggere * s_b * (a_T_dot / a)

    # Bidrag til skjærkraft [N] og moment [Nm] på mast fra strekk i KL.
    V_z = V_kl + V_b
    M_y = V_kl * fh + V_b * (fh + sh)

    # Forskyvning dz [mm] i KL-høyde pga. V_kl og V_b
    dz_kl = deformasjon._beregn_deformasjon_P(mast, V_kl, fh, fh)
    dz_b = deformasjon._beregn_deformasjon_P(mast, V_b, (fh + sh), fh)

    # (4) Vandringskraft
    # Ved temperaturendring vil KL vandre og utligger følge med.
    # Beregner maksimal skråstilling av utligger [m]
    dl = alpha * delta_t * i.avstand_fixpunkt

    if not utliggere == 2:
        # Vandringskraft parallelt spor i primærfelt (én utligger)
        if i.strekkutligger:
            V_y_kl = V_z * (dl / a_T)      # [N]
        else:
            V_y_kl = V_z * (dl / a_T_dot)  # [N]
        M_z = V_y_kl * fh                  # [Nm]
        T = V_y_kl * b_mast                # [Nm]

    # Forskyvning dy [mm] pga vandringskraften V_y
    dy_kl = deformasjon._beregn_deformasjon_Py(mast, V_y_kl, fh, fh)

    R = numpy.zeros((15, 9))
    R[1][0] = M_y
    R[1][1] = V_y_kl
    R[1][2] = M_z
    R[1][3] = V_z
    R[1][5] = T
    R[1][7] = dy_kl
    R[1][8] = dz_kl + dz_b

    # print("\n")
    # print("M_KL = {} kNm     V_KL = {} kN".format(M_y / 1000, (V_kl + V_b) / 1000))
    # print("\n")

    return R
