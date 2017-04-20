from kraft import *


def beregn_fastavspent(i, a_T, a_T_dot, sys):

    f_diff = i.differansestrekk * 1000  # Differansestrekk [N]
    a = (i.a1 + i.a2) / 2

    # F = liste over krefter som skal returneres
    F = []

    if i.forbigang_ledn:
        hf = i.hf
        s = (sys.forbigangsledning["Max tillatt spenning"] *
             sys.forbigangsledning["Tverrsnitt"])
        e_z = -0.3
        if not i.matefjern_ledn and not i.at_ledn and not i.jord_ledn:
            e_z = 0
        f_z = s * ((a_T + a_T_dot + 2 * e_z) / a) if i.master_bytter_side else 0
        F.append(Kraft(navn="Fastavspent: Forbigangsledning", type=5,
                       f=[0, f_diff, f_z], e=[-hf, 0, e_z]))

    if i.retur_ledn:
        hr = i.hr
        s = 2 * (sys.returledning["Max tillatt spenning"] *
                 sys.returledning["Tverrsnitt"])
        e_z = -0.5
        f_z = s * ((a_T + a_T_dot + 2 * e_z) / a) if i.master_bytter_side else 0
        F.append(Kraft(navn="Fastavspent: Returledninger", type=6,
                       f=[0, 2 * f_diff, f_z], e=[-hr, 0, e_z]))

    if i.fiberoptisk_ledn:
        hf = i.hf
        s = (sys.fiberoptisk["Max tillatt spenning"] *
             sys.fiberoptisk["Tverrsnitt"])
        e_z = -0.3
        f_z = s * ((a_T + a_T_dot + 2 * e_z) / a) if i.master_bytter_side else 0
        F.append(Kraft(navn="Fastavspent: Fiberoptisk ledning", type=7,
                       f=[0, f_diff, f_z], e=[-hf, 0, e_z]))

    if i.matefjern_ledn:
        hfj = i.hfj
        n = i.matefjern_antall
        s = n * (sys.matefjernledning["Max tillatt spenning"] *
                 sys.matefjernledning["Tverrsnitt"])
        e_z = 0
        f_z = s * ((a_T + a_T_dot + 2 * e_z) / a) if i.master_bytter_side else 0
        er = "er" if n > 1 else ""
        F.append(Kraft(navn="Fastavspent: Mate-/fjernledning{}".format(er),
                       type=8, f=[0, n * f_diff, f_z], e=[-hfj, 0, e_z]))

    if i.at_ledn:
        hfj = i.hfj
        s = 2 * (sys.at_ledning["Max tillatt spenning"] *
                 sys.at_ledning["Tverrsnitt"])
        e_z = 0
        f_z = s * ((a_T + a_T_dot + 2 * e_z) / a) if i.master_bytter_side else 0
        F.append(Kraft(navn="Fastavspent: AT-ledninger", type=9,
                       f=[0, 2 * f_diff, f_z], e=[-hfj, 0, e_z]))

    if i.jord_ledn:
        hj = i.hj
        s = (sys.jordledning["Max tillatt spenning"] *
             sys.jordledning["Tverrsnitt"])
        e_z = -0.3
        if not i.matefjern_ledn and not i.at_ledn and not i.forbigang_ledn:
            e_z = 0
        f_z = s * ((a_T + a_T_dot + 2 * e_z) / a) if i.master_bytter_side else 0
        F.append(Kraft(navn="Fastavspent: Jordledning", type=10,
                       f=[0, f_diff, f_z], e=[-hj, 0, e_z]))

    return F


def beregn_fixpunkt(sys, i, arm):
    """Beregner kraftbidrag fra fixpunktmast"""

    s = 1000 * sys.fixline["Strekk i ledning"]  # [N]
    a = (i.a1 + i.a2) / 2                           # [m]
    r = i.radius                                    # [m]
    fh = i.fh
    sh = i.sh
    sms = i.sms

    # F = liste over krefter som skal returneres
    F = []

    f_z = s * ((a / r) + 2 * (arm / a))
    if i.strekkutligger and r <= 1200:
        f_z = s * (-(a / r) + 2 * (arm / a))
    F.append(Kraft(navn="Sidekraft: Fixpunktmast", type=2,
                   f=[0, 0, f_z], e=[-fh - sh, 0, sms]))

    return F


def beregn_fixavspenning(sys, i, mast, arm, B1, B2):
    """Beregner kraftbidrag fra fixavspenningsmast"""

    s = 1000 * sys.kontakttraad["Strekk i ledning"]  # [N]
    a = i.masteavstand  # [m]
    r = i.radius        # [m]
    fh = i.fh           # [m]
    sh = i.sh           # [m]
    z = arm + (B1 + B2)

    # F = liste over krefter som skal returneres
    F = []

    # Sidekraft fra fixavspenningsmast og bardun
    f_z = s * (0.5 * (a / r) + (z / a))
    if (not i.strekkutligger) and r <= 1200:
        f_z = s * (- 0.5 * (a / r) + (z / a))
    F.append(Kraft(navn="Sidekraft: Fixavspenningsmast", type=3,
                   f=[0, s, f_z], e=[-fh - sh, 0, 0]))

    if i.avspenningsbardun:
        F.append(Kraft(navn="Sidekraft: Avspenningsbardun", type=3,
                       f=[s, - s, 0], e=[-fh - sh, 0, 0]))

    return F


def beregn_avspenning(sys, i, mast, arm, B1, B2):
    """Beregner kraftbidrag fra avspenningsmast"""

    s_b = 1000 * (sys.baereline["Strekk i ledning"])      # [N]
    s_kl = 1000 * (sys.kontakttraad["Strekk i ledning"])  # [N]
    a = i.a1           # [m]
    r = i.radius        # [m]
    fh = i.fh           # [m]
    sh = i.sh           # [m]
    z_b = arm
    z_kl = arm + (B1 + B2)

    # F = liste over krefter som skal returneres
    F = []

    # Sidekraft fra avspenningsmast og bardun
    f_z_b = s_b * (0.5 * (a / r) + (z_b / a))
    f_z_kl = s_kl * (0.5 * (a / r) + (z_kl / a))
    if (not i.strekkutligger) and r <= 1200:
        f_z_b = s_b * (0.5 * (a / r) + (z_b / a))
        f_z_kl = s_kl * (0.5 * (a / r) + (z_kl / a))
    F.append(Kraft(navn="Sidekraft: Avspenning bæreline", type=4,
                   f=[0, s_b, f_z_b], e=[-fh - sh, 0, 0]))
    F.append(Kraft(navn="Sidekraft: Avspenning kontakttråd", type=4,
                   f=[0, s_kl, f_z_kl], e=[-fh, 0, 0]))

    if i.avspenningsbardun:
        F.append(Kraft(navn="Sidekraft: Avspenningsbardun", type=4,
                       f=[s_b + s_kl, - s_b - s_kl, 0], e=[-fh - sh, 0, 0]))

    return F
