from kraft import *


def beregn(i, sys):
    """Beregner krefter fra egenvekt av og strekk i samtlige ledninger,
    vekt av isolatorer, krefter grunnet ledningsføringens geometri, 
    fix- og avspenningskrefter samt tilhørende
    lodd og eventuell bardunering.
    """

    f_diff = i.differansestrekk * 1000  # Differansestrekk [N]
    r = i.radius
    a = (i.a1 + i.a2) / 2
    a1, a2 = i.a1, i.a2
    B1, B2 = sys.B1, sys.B2
    a_T, a_T_dot = sys.a_T, sys.a_T_dot
    sms = i.sms
    fh = i.fh
    sh = i.sh

    # Eksentrisitet i z-retning for KL.
    arm = a_T_dot
    if i.strekkutligger:
        arm = a_T

    # F = liste over krefter som skal returneres
    F = []

    # Antall utliggere
    n = 1
    if i.siste_for_avspenning or i.linjemast_utliggere == 2:
        n = 2
        F.append(Kraft(navn="Egenvekt: Traverser", type=(0, 0),
                       f=[220, 0, 0], e=[-fh - sh/2, 0, 0]))

    # Utligger(e)
    F.append(Kraft(navn="Egenvekt: Utligger", type=(0, 0),
                   f=[n * sys.utligger["Egenvekt"] * sms, 0, 0],
                   e=[-fh - sh/2, 0, sys.utligger["Momentarm"] * sms]))

    # Bæreline(r)
    F.append(Kraft(navn="Egenvekt: Bæreline", type=(0, 0),
                   f=[n * sys.baereline["Egenvekt"] * a, 0, 0],
                   e=[-fh - sh, 0, sms]))

    # Hengetråd(er)
    L = 8 * (a / 60)
    F.append(Kraft(navn="Egenvekt: Hengetråd", type=(0, 0),
                   f=[n * sys.hengetraad["Egenvekt"] * L, 0, 0],
                   e=[-fh - sh, 0, arm]))

    # Kontakttråd(er)
    F.append(Kraft(navn="Egenvekt: Kontakttråd", type=(0, 0),
                   f=[n * sys.kontakttraad["Egenvekt"] * a, 0, 0],
                   e=[-fh, 0, arm]))

    # Y-line(er)
    if not sys.y_line == None:
        L = 0
        if (sys.navn == "20a" or sys.navn == "35") and i.radius >= 800:
            L = 14
        elif sys.navn == "25" and i.radius >= 1200:
            L = 18
        F.append(Kraft(navn="Egenvekt: Y-line", type=(0, 0),
                       f=[n * sys.y_line["Egenvekt"] * L, 0, 0],
                       e=[-fh - sh, 0, arm]))

    # Sidekrefter pga. ledningsføring
    s = 1000 * sys.kontakttraad["Strekk i ledning"]
    f_z_kurvatur = - n * s * (a1 + a2) / (2 * r)
    f_z_sikksakk = - n * s * ((B2 - B1) / a1 + (B2 - B1) / a2)
    if i.strekkutligger:
        f_z_kurvatur, f_z_sikksakk = - f_z_kurvatur, - f_z_sikksakk
    f_z_avsp_b, f_z_avsp_kl = 0, 0
    if i.siste_for_avspenning:
        f_z_avsp_b = - s * (sms / a2)
        f_z_avsp_kl = - s * (arm / a2)
        if i.master_bytter_side:
            f_z_avsp_b, f_z_avsp_kl = - f_z_avsp_b, -f_z_avsp_kl
    F.append(Kraft(navn="Strekk: Bæreline", type=(1, 1),
                   f=[0, 0, f_z_kurvatur + f_z_avsp_b],
                   e=[-fh - sh, 0, sms]))
    F.append(Kraft(navn="Strekk: Kontakttråd", type=(1, 1),
                   f=[0, 0, f_z_kurvatur + f_z_avsp_kl + f_z_sikksakk],
                   e=[-fh, 0, arm]))

    # Bidrag til normalkraft dersom ulik høyde mellom nabomaster
    if not i.delta_h1 == 0 and not i.delta_h2 == 0:
        s = 1000 * (sys.baereline["Strekk i ledning"] + sys.kontakttraad["Strekk i ledning"])
        f_x = s * (i.delta_h1 / a1 + i.delta_h2 / a2)
        F.append(Kraft(navn="Geometri: Ulik høyde mellom master", type=(1, 1),
                       f=[f_x, 0, 0], e=[-fh - sh / 2, 0, (sms + arm) / 2]))

    # Fixpunktmast
    if i.fixpunktmast:
        g = sys.fixline["Egenvekt"]
        s = 1000 * sys.fixline["Strekk i ledning"]
        f_z = s * ((a / r) + 2 * (arm / a))
        if i.strekkutligger and r <= 1200:
            f_z = s * (-(a / r) + 2 * (arm / a))
        F.append(Kraft(navn="Egenvekt: Fixline", type=(2, 0),
                       f=[g * a, 0, 0], e=[-fh - sh, 0, sms]))
        F.append(Kraft(navn="Strekk: Fixline", type=(2, 1),
                       f=[0, 0, f_z], e=[-fh - sh, 0, sms]))

    # Fixavspenningsmast
    if i.fixavspenningsmast:
        g = sys.fixline["Egenvekt"]
        s = 1000 * sys.fixline["Strekk i ledning"]
        z = arm + (B1 + B2)
        f_z = s * (0.5 * (a / r) + (z / a))
        if (not i.strekkutligger) and r <= 1200:
            f_z = s * (- 0.5 * (a / r) + (z / a))
        F.append(Kraft(navn="Egenvekt: Fixline", type=(2, 0),
                       f=[g * a1 / 2, 0, 0], e=[-fh - sh, 0, 0]))
        F.append(Kraft(navn="Strekk: Fixline", type=(2, 1),
                       f=[0, s, f_z], e=[-fh - sh, 0, 0]))
        # Avspenningsbardun
        if i.avspenningsbardun:
            F.append(Kraft(navn="Strekk: Avspenningsbardun", type=(4, 1),
                           f=[s, - s, -f_z], e=[-fh - sh, 0, 0]))

    # Avspenningsmast
    if i.avspenningsmast:
        g_b = sys.baereline["Egenvekt"]
        g_kl = sys.kontakttraad["Egenvekt"]
        s_b = 1000 * sys.baereline["Strekk i ledning"]
        s_kl = 1000 * sys.kontakttraad["Strekk i ledning"]
        z_b = arm
        z_kl = arm + (B1 + B2)
        f_z_b = s_b * (0.5 * (a / r) + (z_b / a))
        f_z_kl = s_kl * (0.5 * (a / r) + (z_kl / a))
        if (not i.strekkutligger) and r <= 1200:
            f_z_b = s_b * (0.5 * (a / r) + (z_b / a))
            f_z_kl = s_kl * (0.5 * (a / r) + (z_kl / a))
        F.append(Kraft(navn="Egenvekt: Bæreline til avspenning", type=(3, 0),
                       f=[g_b * a1 / 2, 0, 0], e=[-fh - sh, 0, 0]))
        F.append(Kraft(navn="Egenvekt: Kontakttråd til avspenning", type=(3, 0),
                       f=[g_kl * a1 / 2, 0, 0], e=[-fh, 0, 0]))
        F.append(Kraft(navn="Strekk: Avspenning bæreline", type=(3, 1),
                       f=[0, s_b, f_z_b], e=[-fh - sh, 0, 0]))
        F.append(Kraft(navn="Strekk: Avspenning kontakttråd", type=(3, 1),
                       f=[0, s_kl, f_z_kl], e=[-fh, 0, 0]))
        # Avspenningsbardun
        if i.avspenningsbardun:
            F.append(Kraft(navn="Strekk: Avspenningsbardun", type=(4, 1),
                           f=[s_b + s_kl, - s_b - s_kl, -f_z_b -f_z_kl], e=[-fh - sh/2, 0, 0]))
        # Avspenningslodd
        utvekslingsforhold = 3
        if sys.navn == "35":
            utvekslingsforhold = 2
        s_avsp = (s_b + s_kl) / utvekslingsforhold
        F.append(Kraft(navn="Egenvekt: Avspenningslodd", type=(3, 0),
                       f=[s_avsp, 0, 0], e=[-fh - sh/2, 0, 0]))

    # Forbigangsledning (1 stk., inkl. isolator)
    if i.forbigang_ledn:
        g = sys.forbigangsledning["Egenvekt"]
        s = sys.forbigangsledning["Strekk 5C"]
        e_z = -0.3
        kategori = 5  # Fastavspent, side
        if not i.matefjern_ledn and not i.at_ledn and not i.jord_ledn:
            e_z = 0
            kategori = 6  # Fastavspent, topp
        f_z = s * ((a_T + a_T_dot + 2 * e_z) / a) if i.master_bytter_side else 0
        f_z += s * a / r
        F.append(Kraft(navn="Egenvekt: Forbigangsledning", type=(kategori, 0),
                       f=[g * a + 150, 0, 0], e=[-i.hf, 0, e_z]))
        F.append(Kraft(navn="Strekk: Forbigangsledning", type=(kategori, 1),
                       f=[s * (i.delta_h1 / a1 + i.delta_h2 / a2), f_diff, f_z],
                       e=[-i.hf, 0, e_z]))
        # Tilleggsbidrag grunnet temperatur -40C
        s = sys.forbigangsledning["Strekk -40C"] - sys.forbigangsledning["Strekk 5C"]
        f_z = s * ((a_T + a_T_dot + 2 * e_z) / a) if i.master_bytter_side else 0
        f_z += s * a / r
        F.append(Kraft(navn="Temperatur: Forbigangsledning", type=(kategori, 2),
                       f=[s * (i.delta_h1 / a1 + i.delta_h2 / a2), 0, f_z],
                       e=[-i.hf, 0, e_z]))

    # Returledninger (2 stk., inkl. 2 stk. isolatorer)
    if i.retur_ledn:
        g = sys.returledning["Egenvekt"]
        s = 2 * sys.returledning["Strekk 5C"]
        e_z = -0.5
        f_z = s * ((a_T + a_T_dot + 2 * e_z) / a) if i.master_bytter_side else 0
        f_z += s * a / r
        F.append(Kraft(navn="Egenvekt: Returledninger", type=(5, 0),
                       f=[2 * (g * a + 100), 0, 0], e=[-i.hr, 0, e_z]))
        F.append(Kraft(navn="Strekk: Returledninger", type=(5, 1),
                       f=[s * (i.delta_h1 / a1 + i.delta_h2 / a2), 2 * f_diff, f_z],
                       e=[-i.hr, 0, e_z]))
        # Tilleggsbidrag grunnet temperatur -40C
        s = 2 * (sys.returledning["Strekk -40C"] - sys.returledning["Strekk 5C"])
        f_z = s * ((a_T + a_T_dot + 2 * e_z) / a) if i.master_bytter_side else 0
        f_z += s * a / r
        F.append(Kraft(navn="Temperatur: Returledninger", type=(5, 2),
                       f=[s * (i.delta_h1 / a1 + i.delta_h2 / a2), 0, f_z],
                       e=[-i.hr, 0, e_z]))

    # Fiberoptisk ledning (1 stk.)
    if i.fiberoptisk_ledn:
        g = sys.fiberoptisk["Egenvekt"]
        s = (sys.fiberoptisk["Max tillatt spenning"] *
             sys.fiberoptisk["Tverrsnitt"])
        e_z = -0.3
        f_z = s * ((a_T + a_T_dot + 2 * e_z) / a) if i.master_bytter_side else 0
        f_z += s * a / r
        F.append(Kraft(navn="Egenvekt: Fiberoptisk", type=(5, 0),
                       f=[g * a, 0, 0], e=[-i.fh, 0, e_z]))
        F.append(Kraft(navn="Strekk: Fiberoptisk ledning", type=(5, 1),
                       f=[s * (i.delta_h1 / a1 + i.delta_h2 / a2), f_diff, f_z],
                       e=[-i.hf, 0, e_z]))

    # Mate-/fjernledning(er) (n stk., inkl. isolatorer)
    if i.matefjern_ledn:
        n = i.matefjern_antall
        g = n * sys.matefjernledning["Egenvekt"]
        s = n * sys.matefjernledning["Strekk 5C"]
        f_z = s * ((a_T + a_T_dot) / a) if i.master_bytter_side else 0
        f_z += s * a / r
        er = "er" if n > 1 else ""
        F.append(Kraft(navn="Egenvekt: Mate-/fjernledning{}".format(er),
                       type=(6, 0), f=[g * a + 220, 0, 0], e=[-i.hfj, 0, 0]))
        F.append(Kraft(navn="Strekk: Mate-/fjernledning{}".format(er), type=(6, 1),
                       f=[s * (i.delta_h1 / a1 + i.delta_h2 / a2), n * f_diff, f_z],
                       e=[-i.hfj, 0, 0]))
        # Tilleggsbidrag grunnet temperatur -40C
        s = n * (sys.matefjernledning["Strekk -40C"] - sys.matefjernledning["Strekk 5C"])
        f_z = s * ((a_T + a_T_dot) / a) if i.master_bytter_side else 0
        f_z += s * a / r
        F.append(Kraft(navn="Temperatur: Mate-/fjernledning{}".format(er), type=(6, 2),
                       f=[s * (i.delta_h1 / a1 + i.delta_h2 / a2), 0, f_z],
                       e=[-i.hfj, 0, 0]))

    # AT-ledninger (2 stk.)
    if i.at_ledn:
        g = 2 * sys.at_ledning["Egenvekt"]
        s = 2 * (sys.at_ledning["Max tillatt spenning"] *
                 sys.at_ledning["Tverrsnitt"])
        f_z = s * ((a_T + a_T_dot) / a) if i.master_bytter_side else 0
        f_z += s * a / r
        F.append(Kraft(navn="Egenvekt: AT-ledning", type=(6, 0),
                       f=[g * a, 0, 0], e=[-i.hfj, 0, 0]))
        F.append(Kraft(navn="Strekk: AT-ledninger", type=(6, 1),
                       f=[s * (i.delta_h1 / a1 + i.delta_h2 / a2), 2 * f_diff, f_z],
                       e=[-i.hfj, 0, 0]))

    # Jordledning (1 stk.)
    if i.jord_ledn:
        g = sys.jordledning["Egenvekt"]
        s = (sys.jordledning["Max tillatt spenning"] *
             sys.jordledning["Tverrsnitt"])
        e_z = -0.3
        kategori = 5  # Fastavspent, side
        if not i.matefjern_ledn and not i.at_ledn and not i.forbigang_ledn:
            e_z = 0
            kategori = 6  # Fastavspent, topp
        f_z = s * ((a_T + a_T_dot + 2 * e_z) / a) if i.master_bytter_side else 0
        f_z += s * a / r
        F.append(Kraft(navn="Egenvekt: Jordledning", type=(kategori, 0),
                       f=[g * a, 0, 0], e=[-i.hj, 0, e_z]))
        F.append(Kraft(navn="Strekk: Jordledning", type=(kategori, 1),
                       f=[s * (i.delta_h1 / a1 + i.delta_h2 / a2), f_diff, f_z],
                       e=[-i.hj, 0, e_z]))

    return F


def egenvekt_mast(mast):
    """Mastens egenvekt"""
    # F = liste over krefter som skal returneres
    F = []

    F.append(Kraft(navn="Egenvekt: Mast", type=(0, 0),
                   f=[mast.egenvekt * mast.h, 0, 0]))
    return F
