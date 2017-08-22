# -*- coding: utf8 -*-
"""Funksjoner for beregning av laster ikke relatert til is/snø på systemet."""
from __future__ import unicode_literals

from kraft import Kraft
from system import Ledning, Loddavspent, Fix, Fastavspent
import math


def laster_mast(i, mast):
    """Beregner last grunnet mastens egenvekt og vindfang.

    :param Inndata i: Input fra bruker
    :param Mast mast: Aktuell mast
    :return: Liste med :class:`Kraft`-objekt for mastens egenvekt
    :rtype: :class:`list`
    """

    F = []

    # Egenvekt
    F.append(Kraft(navn="Egenvekt: Mast", type=(0, 0),
                   f=(mast.egenvekt * mast.h, 0, 0),
                   e=(0, 0, 0)))

    # Vindlast
    q_p = i.vindkasthastighetstrykk
    # 0: Vind fra mast mot spor
    # 1: Vind fra spor mot mast
    # 2: Vind parallelt sporet
    for vindretning in range(3):
        if vindretning < 2:
            if i.ec3:
                c_f = mast.c_f
                q_eff = c_f * q_p * mast.A_ref
            else:
                if mast.type=="bjelke" or mast.type=="B":
                    G = 1.0
                else:
                    G = 1.05
                C = mast.c_f
                q_eff = G * C * q_p * mast.A_ref

            if vindretning == 1:
                q_eff = -q_eff

            F.append(Kraft(navn="Vindlast: Mast", type=(0, 4),
                           q=(0, 0, q_eff), b=mast.h,
                           e=(-mast.h/2, 0, 0),
                           vindretning=vindretning))

        else:  # Vindretning 3
            if i.ec3:
                c_f_par = mast.c_f_par
                q_eff_par = c_f_par * q_p * mast.A_ref_par
            else:
                if mast.type == "bjelke":
                    G = 1.0
                else:
                    G = 1.05
                C = mast.c_f_par
                q_eff_par = G * C * q_p * mast.A_ref_par

            F.append(Kraft(navn="Vindlast: Mast", type=(0, 4),
                           q=(0, q_eff_par, 0), b=mast.h,
                           e=(-mast.h/2, 0, 0),
                           vindretning=vindretning))


    # Sorterer til klimauavhengig og klimaavhengig del
    F_statisk = [f for f in F if f.statisk]
    F_dynamisk = [f for f in F if not f.statisk]

    return F_statisk, F_dynamisk


def laster_ledninger(i, sys, mastehoyde):
    """Beregner krefter på masten fra kontaktledningsanlegget.

    Krefter som beregnes inkluderer egenvekt av og strekk i samtlige ledninger,
    vekt av isolatorer, krefter grunnet ledningsføringens geometri,
    fix- og avspenningskrefter inkl. lodd, bardunering samt brukerdefinert last.
    Videre beregnes klimaavhengige laster fra snø og is samt
    strekk i fastavspente ledninger ved forskjellige temperaturer.

    Dersom fastavspent ledning foretas en sjekk av ledningens monteringshøyde
    i forhold til mastetopp for å avgjøre om ledningen er
    sidemontert (``rad`` = 5) eller toppmontert (``rad`` = 6).

    :param Inndata i: Input fra bruker
    :param System sys: Data for ledninger og utligger
    :param float mastehoyde: Mastehøyde :math:`[m]`
    :return: Liste med :class:`Kraft`-objekter
    :rtype: :class:`list`
    """

    r = i.radius
    sms = i.sms
    fh, sh = i.fh, i.sh
    a1, a2 = i.a1, i.a2
    a_mid = Ledning.a_mid

    B1, B2 = sys.B1, sys.B2
    arm, arm_sum = sys.arm, sys.arm_sum

    F = []

    e_x_kl = -(fh + sh/2)
    e_y_kl = 0

    # Sidekrefter KL pga. ledningsføring
    s_kl = sys.strekk_kl
    f_z_kl = s_kl * (a_mid/r + 0.5 * ((B2 - B1)/a1 + (B2 - B1)/a2))
    if not i.strekkutligger:
        f_z_kl = -f_z_kl

    # Bidrag dersom siste før avspenning
    if i.siste_for_avspenning:
        e_y_kl = i.traverslengde
        f_z_kl_avsp = s_kl * (arm/a2)
        if not i.master_bytter_side:
            f_z_kl_avsp = -f_z_kl_avsp
        F.append(Kraft(navn="Egenvekt: Utligger til avspenning", type=(0, 0),
                       f=(sys.utligger["Egenvekt"] * sms, 0, 0),
                       e=(e_x_kl, e_y_kl, sys.utligger["Momentarm"] * sms)))
        F.append(Kraft(navn="Sidekraft: KL til avspenning", type=(1, 1),
                       f=(0, 0, f_z_kl + f_z_kl_avsp),
                       e=(e_x_kl, e_y_kl, arm)))

    # Bidrag fra n stk. KL/utligger
    if i.linjemast_utliggere == 1:
        F.append(Kraft(navn="Egenvekt: Utligger", type=(0, 0),
                       f=(sys.utligger["Egenvekt"] * sms, 0, 0),
                       e=(e_x_kl, -e_y_kl, sys.utligger["Momentarm"] * sms)))
        F.append(Kraft(navn="Sidekraft: KL", type=(1, 1),
                       f=(0, 0, f_z_kl),
                       e=(e_x_kl, -e_y_kl, arm)))
    else:
        n = i.linjemast_utliggere
        F.append(Kraft(navn="Egenvekt: Utliggere", type=(0, 0),
                       f=(n * sys.utligger["Egenvekt"] * sms, 0, 0),
                       e=(e_x_kl, 0, sys.utligger["Momentarm"] * sms)))
        F.append(Kraft(navn="Sidekraft: KL", type=(1, 1),
                       f=(0, 0, n * f_z_kl),
                       e=(e_x_kl, 0, arm)))

    # Bidrag dersom fixpunktmast
    if i.fixpunktmast:
        s_fix = sys.strekk_fix
        f_z_fix = s_fix * ((a_mid/r) + 2*(arm/a_mid))
        if i.strekkutligger and r < 1200:
            f_z_fix = s_fix * (-(a_mid/r) + 2*(arm/a_mid))
        F.append(Kraft(navn="Strekk: Fixliner", type=(2, 1),
                       f=(0, 0, f_z_fix), e=(-(fh + sh), 0, sms)))

    # Bidrag dersom fixavspenningsmast
    if i.fixavspenningsmast:
        s_fix = sys.strekk_fix
        z = arm + B1 + B2
        f_z_fix = s_fix * (0.5 * (a_mid/r) + (z/a_mid))
        if not i.strekkutligger and r < 1200:
            f_z_fix = s_fix * (-0.5 * (a_mid/r) + (z/a_mid))
        F.append(Kraft(navn="Strekk: Fixline", type=(2, 1),
                       f=(0, s_fix, f_z_fix), e=(-(fh + sh), 0.1, 0)))
        # Avspenningsbardun
        if i.avspenningsbardun:
            F.append(Kraft(navn="Strekk: Avspenningsbardun", type=(4, 1),
                           f=(s_fix/math.tan(math.radians(40)), -s_fix, -f_z_fix), e=(-(fh + sh), -0.1, 0)))

    # Bidrag dersom avspenningsmast
    if i.avspenningsmast:
        z = arm + B1 + B2
        f_z_kl_avsp = s_kl * (0.5 * (a_mid/r) + (z/a_mid))
        if not i.strekkutligger and r < 1200:
            f_z_kl_avsp = s_kl * (-0.5 * (a_mid/r) + (z/a_mid))
        F.append(Kraft(navn="Strekk: Avspenning KL", type=(3, 1),
                       f=(0, s_kl, f_z_kl_avsp), e=(-(fh + sh), 0.1, 0)))
        # Avspenningsbardun
        if i.avspenningsbardun:
            F.append(Kraft(navn="Strekk: Avspenningsbardun", type=(4, 1),
                           f=(s_kl/math.tan(math.radians(40)), -s_kl, -f_z_kl_avsp), e=(-(fh + sh), -0.1, 0)))
        # Avspenningslodd
        utvekslingsforhold = 3
        if sys.navn == "35":
            utvekslingsforhold = 2
        s_avsp = (s_kl) / utvekslingsforhold
        F.append(Kraft(navn="Egenvekt: Avspenningslodd", type=(3, 0),
                       f=(s_avsp, 0, 0), e=(e_x_kl, 0, 0)))

    # Bidrag fra brukerdefinert last og vindfang
    if i.brukerdefinert_last:
        F.append(Kraft(navn="Egenvekt: Brukerdefinert lastvektor", type=(7, 0),
                       f=(i.f_x, i.f_y, i.f_z),
                       e=(-i.e_x, i.e_y, i.e_z)))
        # 0: Vind fra mast mot spor
        # 1: Vind fra spor mot mast
        # 2: Vind parallelt sporet
        for vindretning in range(3):
            q_p = i.vindkasthastighetstrykk
            if vindretning < 2:
                if vindretning == 1:
                    q_p = -q_p
                f_z_vind = q_p * i.a_vind
                F.append(Kraft(navn="Vindlast: Brukerdefinert vindfang", type=(7, 4),
                               f=(0, 0, f_z_vind),
                               e=(-i.e_x, i.e_y, i.e_z),
                               vindretning=vindretning))
            else:  # vindretning = 3
                f_y_vind = q_p * i.a_vind_par
                F.append(Kraft(navn="Vindlast: Brukerdefinert vindfang", type=(7, 4),
                               f=(0, f_y_vind, 0),
                               e=(-i.e_x, i.e_y, i.e_z),
                               vindretning=vindretning))


    for ledning in sys.ledninger:
        n = ledning.n
        L = ledning.L
        temperaturdata = ledning.temperaturdata

        if isinstance(ledning, Loddavspent):
            rad = 1
        elif isinstance(ledning, Fix):
            rad = 2
        elif isinstance(ledning, Fastavspent):
            rad = 5 if abs(ledning.e[0])<mastehoyde else 6


        # Egenvekt snøfri line inkl. bidrag til
        # normalkraft dersom ulik høyde mellom nabomaster
        f_x_ledn = n * (ledning.G_0 * L + ledning.isolatorvekt)
        f_x_ledn += n * ledning.s * (i.delta_h1/a1 + i.delta_h2/a2)
        egenvekt = Kraft(navn="Egenvekt: {}".format(ledning.type),
                         type=(rad, 0), f=(f_x_ledn, 0, 0),
                         e=ledning.e)
        F.append(egenvekt)

        # Klimaavhengige laster
        for temperatur in temperaturdata:

            T = int(temperatur[0:-1])

            # Egenvekt snø på ledning
            if T <= 0 and not ledning.type=="Hengetråd":
                if T == 0:
                    if i.ec3:
                        G_sno = 2 + 0.5 * 1000 * ledning.d
                    else:
                        G_sno = sys.G_sno_tung
                elif T == -25:
                    if i.ec3:
                        G_sno = 4 + 1000 * ledning.d
                    else:
                        G_sno = sys.G_sno_lett
                f_x_sno = n * G_sno * L
                snolast = Kraft(navn="Snølast: {}".format(ledning.type),
                                type=(rad, 3), f=(f_x_sno, 0, 0),
                                e=ledning.e, T=T)
                F.append(snolast)


            if ledning.type=="Kontakttråd":
                # Vandringskraft
                # Regnes kun dersom masten har én utligger
                # Det antas en forenklet verdi for momentarm lik 0.2m
                if not (i.linjemast_utliggere>1 or i.siste_for_avspenning or i.fixpunktmast):
                    delta_T = T - 5
                    delta_l = delta_T * sys.alpha_kl * i.avstand_fixpunkt
                    f_y_kl_vandre = f_z_kl * (delta_l/arm)
                    F.append(Kraft(navn="Vandringskraft: KL", type=(1, 2),
                                   f=(0, f_y_kl_vandre, 0),
                                   e=(e_x_kl, 0, 0.2),
                                   T=T))


            elif isinstance(ledning, Fastavspent):
                # Strekklast tagges som temperaturlast dersom ekstremtemperatur
                etasje = 1 if T > -40 else 2

                s = temperaturdata[temperatur]["s"]
                s_diff = temperaturdata[temperatur]["s_diff"]

                # Sidekraft
                f_z_side = n * s * L / r
                if not i.strekkutligger:
                    f_z_side = -f_z_side
                if i.master_bytter_side:
                    f_z_side += n * s * ((sys.arm + 2 * ledning.e[2]) / L)
                sidekraft = Kraft(navn="Sidekraft: {}".format(ledning.type),
                                  type=(rad, etasje), f=(0, 0, f_z_side),
                                  e=ledning.e, T=T, s=n*s)
                F.append(sidekraft)

                # Differansestrekk
                if abs(s_diff) > 0:
                    f_y_diff = n * s_diff
                    differansestrekk = Kraft(navn="Differansestrekk: {}".format(ledning.type),
                                             type=(rad, etasje), f=(0, f_y_diff, 0),
                                             e=ledning.e, T=T)
                    F.append(differansestrekk)


            # Vindlast
            q_p = i.vindkasthastighetstrykk
            D = ledning.temperaturdata[temperatur]["D"]
            if i.ec3:
                c_f = 1.1
                q_eff = c_f * q_p
            else:
                if isinstance(ledning, Loddavspent):
                    G_C = 0.75
                else:
                    G_C = 1.0
                C_C = 1.0
                q_eff = G_C * C_C * q_p

            # 0: Vind fra mast mot spor
            # 1: Vind fra spor mot mast
            # Ingen vindlast på ledninger ved vind parallelt spor
            for vindretning in range(2):
                if vindretning == 1:
                    q_eff = -q_eff
                f_z_vind = n * q_eff * D * ledning.L
                F.append(Kraft(navn="Vindlast: {}".format(ledning.type),
                               type=(rad, 4), f=(0, 0, f_z_vind), e=ledning.e,
                               T=T, vindretning=vindretning))


    # Sorterer til klimauavhengig og klimaavhengig del
    F_statisk = [f for f in F if f.statisk]
    F_dynamisk = [f for f in F if not f.statisk]

    return F_statisk, F_dynamisk

def ulykkeslast(i, sys, T):
    """Beregner ulykkeslast (torsjon) dersom brudd i én av to KL.

    :param Inndata i: Input fra bruker
    :param System sys: Data for ledninger og utligger
    :param float T: Torsjonsmoment før påføring av ulykkeslast
    :return: Ulykkeslast
    :rtype: :class:`Kraft`
    """

    F = []

    r = i.radius
    fh, sh = i.fh, i.sh
    a1, a2 = i.a1, i.a2
    a_mid = (a1 + a2) / 2
    B1, B2 = sys.B1, sys.B2
    arm = sys.arm
    s_kl = sys.strekk_kl

    f_z_kl = s_kl * (a_mid / r + (B2 - B1) / a1 + (B2 - B1) / a2)
    if not i.strekkutligger:
        f_z_kl = -f_z_kl

    f_z_kl_avsp = 0
    if i.siste_for_avspenning:
        f_z_kl_avsp = s_kl * (arm / a2)
        if not i.master_bytter_side:
            f_z_kl_avsp = -f_z_kl_avsp

    f_z_ulykke = max(abs(T + f_z_kl), abs(T + f_z_kl + f_z_kl_avsp))

    F.append(Kraft(navn="Sidekraft: KL (ulykke)", type=(1, 1),
                   f=(0, 0, f_z_ulykke), e=(-(fh + sh / 2), i.traverslengde, arm)))

    return F
