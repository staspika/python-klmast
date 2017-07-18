# -*- coding: utf8 -*-
"""Funksjoner for beregning av laster ikke relatert til is/snø på systemet."""
from __future__ import unicode_literals

from kraft import *

def _utliggerkrefter(i, sys, mast, e_t=0):
    """Beregner krefter fra utstyr montert på utligger.

    Kraftsett som påføres avhenger av traversens eksentrisitetsverdi ``e_t``:

    - ``e_t`` = 0: Beregner krefter for tilfelle med én utligger på systemet.

    - ``e_t`` > 0: Beregner krefter for en normalt konfigurert utligger
      dersom systemet har to utliggere.

    - ``e_t`` < 0: Beregner krefter for en normalt konfigurert utligger
      dersom systemet har to utliggere, eller utligger
      med KL til avspenning dersom masten er angitt å være
      siste seksjonsmast før avspenning.

    :param Inndata i: Input fra bruker
    :param System sys: Data for ledninger og utligger
    :param Mast mast: Aktuell mast
    :param e_t: Traversens eksentrisitet i y-retning :math:`[m]`
    :return: Liste med :class:`Kraft`-objekter
    :rtype: :class:`list`
    """

    r = i.radius
    a = (i.a1 + i.a2) / 2
    a1, a2 = i.a1, i.a2
    B1, B2 = sys.B1, sys.B2
    a_T, a_T_dot = sys.a_T, sys.a_T_dot
    sms = i.sms
    fh = i.fh
    sh = i.sh
    alpha = 1.7 * 10 ** (-5)
    delta_t = 45

    # Eksentrisitet i z-retning for KL.
    arm = a_T_dot
    if i.strekkutligger:
        arm = a_T

    # F = liste over krefter som skal returneres
    F = []

    # Utligger(e)
    F.append(Kraft(navn="Egenvekt: Utligger", type=(0, 0),
                   f=[sys.utligger["Egenvekt"] * sms, 0, 0],
                   e=[-fh - sh / 2, e_t, sys.utligger["Momentarm"] * sms]))

    # Bæreline(r)
    F.append(Kraft(navn="Egenvekt: Bæreline", type=(0, 0),
                   f=[sys.baereline["Egenvekt"] * a, 0, 0],
                   e=[-fh - sh, e_t, sms]))

    # Hengetråd(er)
    L = 8 * (a / 60)
    F.append(Kraft(navn="Egenvekt: Hengetråd", type=(0, 0),
                   f=[sys.hengetraad["Egenvekt"] * L, 0, 0],
                   e=[-fh - sh, e_t, arm]))

    # Kontakttråd(er)
    F.append(Kraft(navn="Egenvekt: Kontakttråd", type=(0, 0),
                   f=[sys.kontakttraad["Egenvekt"] * a, 0, 0],
                   e=[-fh, e_t, arm]))

    # Y-line(er)
    if not sys.y_line == None:
        L = 0
        if (sys.navn == "20A" or sys.navn == "35") and i.radius >= 800:
            L = 14
        elif sys.navn == "25" and i.radius >= 1200:
            L = 18
        F.append(Kraft(navn="Egenvekt: Y-line", type=(0, 0),
                       f=[sys.y_line["Egenvekt"] * L, 0, 0],
                       e=[-fh - sh, e_t, arm]))

    # Sidekrefter pga. ledningsføring
    s_b = 1000 * sys.baereline["Strekk i ledning"]
    s_kl = 1000 * sys.kontakttraad["Strekk i ledning"]
    f_z_b = - s_b * a / r
    f_z_kl = - s_kl * (a / r + ((B2 - B1) / a1 + (B2 - B1) / a2))
    if i.strekkutligger:
        f_z_b, f_z_kl = - f_z_b, - f_z_kl
    if i.siste_for_avspenning and e_t<0:
        f_z_avsp_b = - s_b * (sms / a2)
        f_z_avsp_kl = - s_kl * (arm / a2)
        if i.master_bytter_side:
            f_z_avsp_b, f_z_avsp_kl = - f_z_avsp_b, -f_z_avsp_kl
        F.append(Kraft(navn="Strekk: Bæreline til avspenning", type=(1, 1),
                       f=[0, 0, f_z_b + f_z_avsp_b],
                       e=[-fh - sh, 0, sms]))
        F.append(Kraft(navn="Strekk: Kontakttråd til avspenning", type=(1, 1),
                       f=[0, 0, f_z_kl + f_z_avsp_kl],
                       e=[-fh, 0, arm]))
        # Torsjonsresultant grunnet sidekreftenes eksentrisitet på travers
        f_z_res = f_z_avsp_b + f_z_avsp_kl
        F.append(Kraft(navn="Strekk: Torsjon, eksentrisitet utliggere", type=(1, 1),
                       f=[0, 0, f_z_res],
                       e=[-fh-sh/2, -e_t, (sms+arm)/2]))
    else:
        F.append(Kraft(navn="Strekk: Bæreline", type=(1, 1),
                       f=[0, 0, f_z_b],
                       e=[-fh - sh, 0, sms]))
        F.append(Kraft(navn="Strekk: Kontakttråd", type=(1, 1),
                       f=[0, 0, f_z_kl],
                       e=[-fh, 0, arm]))


    # Vandringskraft
    avstand_fixpunkt = i.avstand_fixpunkt if not i.fixavspenningsmast else a
    if i.fixpunktmast or i.siste_for_avspenning or i.linjemast_utliggere == 2:
        avstand_fixpunkt = 0
    dl = alpha * delta_t * avstand_fixpunkt
    F.append(Kraft(navn="Vandringskraft: Bæreline", type=(1, 2),
                   f=[0, f_z_b * (dl / i.sms), 0],
                   e=[-i.fh - i.sh, 0, mast.bredde(mast.h - (i.fh + i.sh))/2000]))
    F.append(Kraft(navn="Vandringskraft: Kontakttråd", type=(1, 2),
                   f=[0, (f_z_kl) * (dl / arm), 0],
                   e=[-i.fh, 0, mast.bredde(mast.h - i.fh)/2000]))


    # Bidrag til normalkraft dersom ulik høyde mellom nabomaster
    if not i.delta_h1 == 0 and not i.delta_h2 == 0:
        s = 1000 * (sys.baereline["Strekk i ledning"] + sys.kontakttraad["Strekk i ledning"])
        f_x = s * (i.delta_h1 / a1 + i.delta_h2 / a2)
        F.append(Kraft(navn="Geometri: Ulik høyde mellom master", type=(1, 1),
                       f=[f_x, 0, 0], e=[-fh - sh / 2, e_t, (sms + arm) / 2]))

    return F

def beregn(i, sys, mast):
    """Beregner krefter grunnet statiske og temperaturavhengige forhold i systemet.

    Krefter som beregnes inkluderer egenvekt av og strekk i samtlige ledninger,
    vekt av isolatorer, krefter grunnet ledningsføringens geometri,
    fix- og avspenningskrefter samt tilhørende
    lodd og eventuell bardunering.

    :param Inndata i: Input fra bruker
    :param System sys: Data for ledninger og utligger
    :param Mast mast: Aktuell mast
    :return: Liste med :class:`Kraft`-objekter
    :rtype: :class:`list`
    """

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

    e_t = 0
    # Sjekker om mast har 2 utliggere
    if i.siste_for_avspenning or i.linjemast_utliggere == 2:
        # Ekstra bidrag fra traversens eksentrisitet i y-retning
        e_t = i.traverslengde / 2
        F.append(Kraft(navn="Egenvekt: Traverser", type=(0, 0),
                       f=[220, 0, 0], e=[-fh - sh/2, 0, 0]))
        F.extend(_utliggerkrefter(i, sys, mast, -e_t))
    F.extend(_utliggerkrefter(i, sys, mast, e_t))


    # Fixpunktmast
    if i.fixpunktmast:
        g = sys.fixline["Egenvekt"]
        s = 1000 * sys.fixline["Strekk i ledning"]
        f_z = s * ((a / r) + 2 * (arm / a))
        if i.strekkutligger and r <= 1200:
            f_z = s * (-(a / r) + 2 * (arm / a))
        F.append(Kraft(navn="Egenvekt: Fixliner", type=(2, 0),
                       f=[g * a, 0, 0], e=[-fh - sh, 0, sms]))
        F.append(Kraft(navn="Strekk: Fixliner", type=(2, 1),
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
                       f=[g * a / 2, 0, 0], e=[-fh - sh, 0, 0]))
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
            f_z_b = s_b * (-0.5 * (a / r) + (z_b / a))
            f_z_kl = s_kl * (-0.5 * (a / r) + (z_kl / a))
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
                       f=[s * (i.delta_h1 / a1 + i.delta_h2 / a2), 0, f_z],
                       e=[-i.hf, 0, e_z]))
        # Tilleggsbidrag grunnet temperatur -40C
        s = sys.forbigangsledning["Strekk -40C"] - sys.forbigangsledning["Strekk 5C"]
        f_z = s * ((a_T + a_T_dot + 2 * e_z) / a) if i.master_bytter_side else 0
        f_z += s * a / r
        f_diff = sys.forbigangsledning["Differansestrekk"] if i.auto_differansestrekk else i.differansestrekk
        if abs(f_diff) > 0:
            F.append(Kraft(navn="Differansestrekk: Forbigangsledning", type=(kategori, 1),
                           f=[0, f_diff, 0],
                           e=[-i.hf, 0, e_z]))
        F.append(Kraft(navn="Temperatur: Forbigangsledning", type=(kategori, 2),
                       f=[0, 0, f_z],
                       e=[-i.hf, 0, e_z]))
        # Tilleggsbidrag grunnet snølast
        s = sys.forbigangsledning["Strekk med snø -25C"] - sys.forbigangsledning["Strekk -40C"]
        f_z = s * ((a_T + a_T_dot + 2 * e_z) / a) if i.master_bytter_side else 0
        f_z += s * a / r
        F.append(Kraft(navn="Strekkbidrag fra snølast: Forbigangsledning", type=(kategori, 3),
                       f=[0, 0, f_z],
                       e=[-i.hf, 0, e_z]))

    # Returledninger (2 stk., inkl. 2 stk. isolatorer)
    if i.retur_ledn:
        g = 2 * sys.returledning["Egenvekt"]
        s = 2 * sys.returledning["Strekk 5C"]
        e_z = -0.5
        f_z = s * ((a_T + a_T_dot + 2 * e_z) / a) if i.master_bytter_side else 0
        f_z += s * a / r
        F.append(Kraft(navn="Egenvekt: Returledninger", type=(5, 0),
                       f=[g*a + 200, 0, 0], e=[-i.hr, 0, e_z]))
        F.append(Kraft(navn="Strekk: Returledninger", type=(5, 1),
                       f=[s * (i.delta_h1 / a1 + i.delta_h2 / a2), 0, f_z],
                       e=[-i.hr, 0, e_z]))
        # Tilleggsbidrag grunnet temperatur -40C
        s = 2 * (sys.returledning["Strekk -40C"] - sys.returledning["Strekk 5C"])
        f_z = s * ((a_T + a_T_dot + 2 * e_z) / a) if i.master_bytter_side else 0
        f_z += s * a / r
        f_diff = 2 * sys.returledning["Differansestrekk"] if i.auto_differansestrekk else 2 * i.differansestrekk
        if abs(f_diff) > 0:
            F.append(Kraft(navn="Differansestrekk: Returledninger", type=(5, 1),
                           f=[0, f_diff, 0],
                           e=[-i.hr, 0, e_z]))
        F.append(Kraft(navn="Temperatur: Returledninger", type=(5, 2),
                       f=[0, 0, f_z],
                       e=[-i.hr, 0, e_z]))
        # Tilleggsbidrag grunnet snølast
        s = 2 * (sys.returledning["Strekk med snø -25C"] - sys.returledning["Strekk -40C"])
        f_z = s * ((a_T + a_T_dot + 2 * e_z) / a) if i.master_bytter_side else 0
        f_z += s * a / r
        F.append(Kraft(navn="Strekkbidrag fra snølast: Returledning", type=(5, 3),
                       f=[0, 0, f_z],
                       e=[-i.hr, 0, e_z]))

    # Fiberoptisk ledning (1 stk.)
    if i.fiberoptisk_ledn:
        g = sys.fiberoptisk["Egenvekt"]
        s = sys.fiberoptisk["Strekk 5C"]
        e_z = -0.3
        f_z = s * ((a_T + a_T_dot + 2 * e_z) / a) if i.master_bytter_side else 0
        f_z += s * a / r
        F.append(Kraft(navn="Egenvekt: Fiberoptisk ledning", type=(5, 0),
                       f=[g * a, 0, 0], e=[-i.fh, 0, e_z]))
        F.append(Kraft(navn="Strekk: Fiberoptisk ledning", type=(5, 1),
                       f=[s * (i.delta_h1 / a1 + i.delta_h2 / a2), 0, f_z],
                       e=[-i.hf, 0, e_z]))
        # Tilleggsbidrag grunnet temperatur -40C
        s = sys.fiberoptisk["Strekk -40C"] - sys.fiberoptisk["Strekk 5C"]
        f_z = s * ((a_T + a_T_dot + 2 * e_z) / a) if i.master_bytter_side else 0
        f_z += s * a / r
        f_diff = sys.fiberoptisk["Differansestrekk"] if i.auto_differansestrekk else i.differansestrekk
        if abs(f_diff) > 0:
            F.append(Kraft(navn="Differansestrekk: Fiberoptisk ledning", type=(5, 1),
                           f=[0, f_diff, 0],
                           e=[-i.hf, 0, e_z]))
        F.append(Kraft(navn="Temperatur: Fiberoptisk ledning", type=(5, 2),
                       f=[0, 0, f_z],
                       e=[-i.hf, 0, e_z]))
        # Tilleggsbidrag grunnet snølast
        s = sys.fiberoptisk["Strekk med snø -25C"] - sys.fiberoptisk["Strekk -40C"]
        f_z = s * ((a_T + a_T_dot + 2 * e_z) / a) if i.master_bytter_side else 0
        f_z += s * a / r
        F.append(Kraft(navn="Strekkbidrag fra snølast: Fiberoptisk ledning", type=(5, 3),
                       f=[0, 0, f_z],
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
                       f=[s * (i.delta_h1 / a1 + i.delta_h2 / a2), 0, f_z],
                       e=[-i.hfj, 0, 0]))
        # Tilleggsbidrag grunnet temperatur -40C
        s = n * (sys.matefjernledning["Strekk -40C"] - sys.matefjernledning["Strekk 5C"])
        f_z = s * ((a_T + a_T_dot) / a) if i.master_bytter_side else 0
        f_z += s * a / r
        f_diff = n * sys.matefjernledning["Differansestrekk"] if i.auto_differansestrekk else n * i.differansestrekk
        if abs(f_diff) > 0:
            F.append(Kraft(navn="Differansestrekk: Mate-/fjernledning{}".format(er), type=(6, 1),
                           f=[0, f_diff, 0],
                           e=[-i.hfj, 0, 0]))
        F.append(Kraft(navn="Temperatur: Mate-/fjernledning{}".format(er), type=(6, 2),
                       f=[0, 0, f_z],
                       e=[-i.hfj, 0, 0]))
        # Tilleggsbidrag grunnet snølast
        s = n * (sys.matefjernledning["Strekk med snø -25C"] - sys.matefjernledning["Strekk -40C"])
        f_z = s * ((a_T + a_T_dot) / a) if i.master_bytter_side else 0
        f_z += s * a / r
        F.append(Kraft(navn="Strekkbidrag fra snølast: Mate-/fjernledning{}".format(er), type=(6, 3),
                       f=[0, 0, f_z],
                       e=[-i.hfj, 0, 0]))

    # AT-ledninger (2 stk.)
    if i.at_ledn:
        g = 2 * sys.at_ledning["Egenvekt"]
        s = 2 * sys.at_ledning["Strekk 5C"]
        f_z = s * ((a_T + a_T_dot) / a) if i.master_bytter_side else 0
        f_z += s * a / r
        F.append(Kraft(navn="Egenvekt: AT-ledninger", type=(6, 0),
                       f=[g * a, 0, 0], e=[-i.hfj, 0, 0]))
        F.append(Kraft(navn="Strekk: AT-ledninger", type=(6, 1),
                       f=[s * (i.delta_h1 / a1 + i.delta_h2 / a2), 0, f_z],
                       e=[-i.hfj, 0, 0]))
        # Tilleggsbidrag grunnet temperatur -40C
        s = 2 * (sys.at_ledning["Strekk -40C"] - sys.at_ledning["Strekk 5C"])
        f_z = s * ((a_T + a_T_dot) / a) if i.master_bytter_side else 0
        f_z += s * a / r
        f_diff = 2 * sys.at_ledning["Differansestrekk"] if i.auto_differansestrekk else 2 * i.differansestrekk
        if abs(f_diff) > 0:
            F.append(Kraft(navn="Differansestrekk: AT-ledninger", type=(6, 1),
                           f=[0, f_diff, 0],
                           e=[-i.hfj, 0, 0]))
        F.append(Kraft(navn="Temperatur: AT-ledninger", type=(6, 2),
                       f=[0, 0, f_z],
                       e=[-i.hfj, 0, 0]))
        # Tilleggsbidrag grunnet snølast
        s = 2 * (sys.at_ledning["Strekk med snø -25C"] - sys.at_ledning["Strekk -40C"])
        f_z = s * ((a_T + a_T_dot) / a) if i.master_bytter_side else 0
        f_z += s * a / r
        F.append(Kraft(navn="Strekkbidrag fra snølast: AT-ledninger", type=(6, 3),
                       f=[0, 0, f_z],
                       e=[-i.hfj, 0, 0]))

    # Jordledning (1 stk.)
    if i.jord_ledn:
        g = sys.jordledning["Egenvekt"]
        s = sys.jordledning["Strekk 5C"]
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
                       f=[s * (i.delta_h1 / a1 + i.delta_h2 / a2), 0, f_z],
                       e=[-i.hj, 0, e_z]))
        # Tilleggsbidrag grunnet temperatur -40C
        s = sys.jordledning["Strekk -40C"] - sys.jordledning["Strekk 5C"]
        f_z = s * ((a_T + a_T_dot) / a) if i.master_bytter_side else 0
        f_z += s * a / r
        f_diff = sys.jordledning["Differansestrekk"] if i.auto_differansestrekk else i.differansestrekk
        if abs(f_diff) > 0:
            F.append(Kraft(navn="Differansestrekk: Jordledning", type=(kategori, 1),
                           f=[0, f_diff, 0],
                           e=[-i.hj, 0, e_z]))
        F.append(Kraft(navn="Temperatur: Jordledning", type=(kategori, 2),
                       f=[0, 0, f_z],
                       e=[-i.hj, 0, e_z]))
        # Tilleggsbidrag grunnet snølast
        s = sys.jordledning["Strekk med snø -25C"] - sys.jordledning["Strekk -40C"]
        f_z = s * ((a_T + a_T_dot + 2 * e_z) / a) if i.master_bytter_side else 0
        f_z += s * a / r
        F.append(Kraft(navn="Strekkbidrag fra snølast: Jordledning", type=(kategori, 3),
                       f=[0, 0, f_z],
                       e=[-i.hj, 0, e_z]))

    return F


def egenvekt_mast(i, mast):
    """Beregner last grunnet mastens egenvekt.

    Lastens eksentrisitet i :math:`x`-retning justeres
    med :math:`e`-målet for å ta hensyn til at denne lasten
    måles fra masteinnspenning snarere enn SOK.
    Se også: :func:`kraft.Kraft.__init__`

    Funksjonen beregner også lastbidrag grunnet
    brukerdefinert last.

    :param Inndata i: Input fra bruker
    :param Mast mast: Aktuell mast
    :return: Liste med :class:`Kraft`-objekt for mastens egenvekt
    :rtype: :class:`list`
    """


    # F = liste over krefter som skal returneres
    F = []

    F.append(Kraft(navn="Egenvekt: Mast", type=(0, 0),
                   f=[mast.egenvekt * mast.h, 0, 0],
                   e=[i.e, 0, 0]))

    if i.brukerdefinert_last:
        F.append(Kraft(navn="Egenvekt: Brukerdefinert lastvektor", type=(7, 0),
                       f=[abs(i.f_x), abs(i.f_y), i.f_z],
                       e=[- i.e_x + i.e, i.e_y, i.e_z]))

    return F


def ulykkeslast_KL(i, sys, mast):
    """Beregner laster som skal påføres systemet ved ulykkessituasjon.

    :param Inndata i: Input fra bruker
    :param System sys: Data for ledninger og utligger
    :param Mast mast: Aktuell mast
    :return: Liste med :class:`Kraft`-objekter
    :rtype: :class:`list`
    """

    r = i.radius
    a = (i.a1 + i.a2) / 2
    a1, a2 = i.a1, i.a2
    B1, B2 = sys.B1, sys.B2
    a_T, a_T_dot = sys.a_T, sys.a_T_dot
    sms = i.sms
    fh = i.fh
    sh = i.sh
    alpha = 1.7 * 10 ** (-5)
    delta_t = 45

    # Eksentrisitet i z-retning for KL.
    arm = a_T_dot
    if i.strekkutligger:
        arm = a_T

    # F = liste over krefter som skal returneres
    F = []

    e_t = i.traverslengde
    # Sidekrefter pga. ledningsføring
    s_b = 1000 * sys.baereline["Strekk i ledning"]
    s_kl = 1000 * sys.kontakttraad["Strekk i ledning"]
    f_z_b = - s_b * a / r
    f_z_kl = - s_kl * (a / r + ((B2 - B1) / a1 + (B2 - B1) / a2))
    f_z_avsp_b, f_z_avsp_kl = 0, 0
    if i.strekkutligger:
        f_z_b, f_z_kl = - f_z_b, - f_z_kl
    if i.siste_for_avspenning:
        f_z_avsp_b = - s_b * (sms / a2)
        f_z_avsp_kl = - s_kl * (arm / a2)
        if i.master_bytter_side:
            f_z_avsp_b, f_z_avsp_kl = - f_z_avsp_b, -f_z_avsp_kl
    if abs(f_z_b + f_z_avsp_b + f_z_kl + f_z_avsp_kl) > abs(f_z_b + f_z_kl):
        F.append(Kraft(navn="Strekk: Bæreline", type=(1, 1),
                       f=[0, 0, f_z_b + f_z_avsp_b],
                       e=[-fh - sh, e_t, sms]))
        F.append(Kraft(navn="Strekk: Kontakttråd", type=(1, 1),
                       f=[0, 0, f_z_kl + f_z_avsp_kl],
                       e=[-fh, e_t, arm]))
    else:
        F.append(Kraft(navn="Strekk: Bæreline", type=(1, 1),
                       f=[0, 0, f_z_b],
                       e=[-fh - sh, e_t, sms]))
        F.append(Kraft(navn="Strekk: Kontakttråd", type=(1, 1),
                       f=[0, 0, f_z_kl],
                       e=[-fh, e_t, arm]))

    # Bæreline(r)
    F.append(Kraft(navn="Egenvekt: Bæreline", type=(0, 0),
                   f=[sys.baereline["Egenvekt"] * a, 0, 0],
                   e=[-fh - sh, e_t, sms]))

    # Hengetråd(er)
    L = 8 * (a / 60)
    F.append(Kraft(navn="Egenvekt: Hengetråd", type=(0, 0),
                   f=[sys.hengetraad["Egenvekt"] * L, 0, 0],
                   e=[-fh - sh, e_t, arm]))

    # Kontakttråd(er)
    F.append(Kraft(navn="Egenvekt: Kontakttråd", type=(0, 0),
                   f=[sys.kontakttraad["Egenvekt"] * a, 0, 0],
                   e=[-fh, e_t, arm]))

    # Y-line(er)
    if not sys.y_line == None:
        L = 0
        if (sys.navn == "20A" or sys.navn == "35") and i.radius >= 800:
            L = 14
        elif sys.navn == "25" and i.radius >= 1200:
            L = 18
        F.append(Kraft(navn="Egenvekt: Y-line", type=(0, 0),
                       f=[sys.y_line["Egenvekt"] * L, 0, 0],
                       e=[-fh - sh, e_t, arm]))

    # Vandringskraft
    avstand_fixpunkt = i.avstand_fixpunkt if not i.fixavspenningsmast else a
    if i.fixpunktmast:
        avstand_fixpunkt = 0
    dl = alpha * delta_t * avstand_fixpunkt
    F.append(Kraft(navn="Vandringskraft: Bæreline", type=(1, 2),
                   f=[0, f_z_b * (dl / i.sms), 0],
                   e=[-i.fh - i.sh, 0, mast.bredde(mast.h - (i.fh + i.sh)) / 2000]))
    F.append(Kraft(navn="Vandringskraft: Kontakttråd", type=(1, 2),
                   f=[0, (f_z_kl) * (dl / arm), 0],
                   e=[-i.fh, 0, mast.bredde(mast.h - i.fh) / 2000]))

    # Bidrag til normalkraft dersom ulik høyde mellom nabomaster
    if not i.delta_h1 == 0 and not i.delta_h2 == 0:
        s = 1000 * (sys.baereline["Strekk i ledning"] + sys.kontakttraad["Strekk i ledning"])
        f_x = s * (i.delta_h1 / a1 + i.delta_h2 / a2)
        F.append(Kraft(navn="Geometri: Ulik høyde mellom master", type=(1, 1),
                       f=[f_x, 0, 0], e=[-fh - sh / 2, e_t, (sms + arm) / 2]))

    return F

