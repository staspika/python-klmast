from kraft import *


def sidekraft(sys, i, arm, B1, B2):
    """Beregner sidekraft [kN] og moment [kNm] ved normal ledningsføring,
    samt forskyvning [mm]. Videre beregnes vandringskraften pga.
    temperatureffekter.
    """

    # Inngangsparametre
    s = 1000 * sys.kontakttraad["Strekk i ledning"]     # [N]
    r = i.radius                                        # [m]
    a1 = i.a1                                           # [m]
    a2 = i.a2                                           # [m]
    fh = i.fh                                           # [m]
    sh = i.sh                                           # [m]
    sms = i.sms
    alpha = 1.7 * 10 ** (-5)                            # [1/(grader C)]
    delta_t = 45                                        # [(grader C)]

    # F = liste over krefter som skal returneres
    F = []

    # Antall utliggere
    utliggere = 1
    if i.siste_for_avspenning or i.linjemast_utliggere == 2:
        utliggere = 2

    # Sidekrefter pga. ledningsføring
    f_z_kurvatur = - utliggere * s * (a1 + a2) / (2 * r)
    f_z_sikksakk = - utliggere * s * ((B2 - B1) / a1 + (B2 - B1) / a2)
    if i.strekkutligger:
        f_z_kurvatur = utliggere * s * (a1 + a2) / (2 * r)
        f_z_sikksakk = utliggere * s * 2 * ((B2 - B1) / a1)
    if i.siste_for_avspenning:
        f_z_avsp_b = - utliggere * s * (sms / a2)
        f_z_avsp_kl = - utliggere * s * (arm / a2)
        if i.master_bytter_side:
            f_z_avsp_b = utliggere * s * (sms / a2)
            f_z_avsp_kl = utliggere * s * (arm / a2)

    F.append(Kraft(navn="Sidekraft: Bæreline", type=1,
                   f=[0, 0, f_z_kurvatur + f_z_avsp_b],
                   e=[-fh-sh, 0, sms]))
    F.append(Kraft(navn="Sidekraft: Kontakttråd", type=1,
                   f=[0, 0, f_z_kurvatur + f_z_avsp_kl + f_z_sikksakk],
                   e=[-fh, 0, arm]))

    # Vandringskraft
    dl = alpha * delta_t * i.avstand_fixpunkt
    if not utliggere == 2:
        F.append(Kraft(navn="Vandringskraft: Bæreline", type=1,
                       f=[0, f_z_kurvatur * (dl / sms), 0],
                       e=[-fh - sh, 0, sms]))
        F.append(Kraft(navn="Vandringskraft: Kontakttråd", type=1,
                       f=[0, (f_z_kurvatur + f_z_sikksakk) * (dl / arm), 0],
                       e=[-fh - sh, 0, arm]))

    return F
