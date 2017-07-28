# -*- coding: utf8 -*-
"""Beregning av vindlaster, funksjoner for påføring av krefter fra vind- og snølast."""
from __future__ import unicode_literals

import lister
import math
from kraft import *


def beregn_vindkasthastighetstrykk_EC(i, z):
    """Beregner dimensjonerende vindkasthastighetstrykk mhp. Eurokode 0.

    :param Inndata i: Input fra bruker
    :param float z: Høyde over bakken :math:`[m]`
    :return: Vindkasthastighetstrykk :math:`[\\frac{N}{m^2}]`
    :rtype: :class:`float`
    """

    # Inngangsparametre
    v_b_0 = i.referansevindhastighet  # [m/s] Referansevindhastighet for aktuell kommune
    c_dir = 1.0                       # [1] Retningsfaktor
    c_season = 1.0                    # [1] Årstidsfaktor
    c_alt = 1.0                       # [1] Nivåfaktor
    c_prob = 1.0                      # [1] Faktor dersom returperioden er mer enn 50 år
    c_0 = 1.0                         # [1] Terrengformfaktoren
    kategori = 2

    # Basisvindhastighet [m/s]
    v_b = c_dir * c_season * c_alt * c_prob * v_b_0

    k_r = lister.terrengkategorier[kategori]["k_r"]
    z_0 = lister.terrengkategorier[kategori]["z_0"]
    z_min = lister.terrengkategorier[kategori]["z_min"]
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
    q_m = 0.5 * rho * v_m ** 2  # [N / m^2]

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


def q_KL(i, sys):
    """Beregner vindlast på kontaktledningen.

    :param Inndata i: Input fra bruker
    :param sys: Data for ledninger og utligger
    :return: Vindlast på KL :math:`[\\frac{N}{m}]`
    :rtype: :class:`float`
    """

    # Inngangsparametre
    q_p = i.vindkasthasstighetstrykk
    cf = 1.1             # [1] Vindkraftfaktor ledning
    d_henge, d_Y = 0, 0  # [m] Diameter hengetraad, lengde Y-line
    q = 0                # [N/m] Brukes til å beregne masteavstand, a

    # Bidrag fra KL, bæreline, hengetråd og Y-line avhenger av utliggere
    utliggere = 1
    if i.siste_for_avspenning or i.linjemast_utliggere == 2:
        utliggere = 2

    # ALTERNATIV #1: q = 1.2 * q_kontakttråd
    q_kl = q_p * cf * sys.kontakttraad["Diameter"] / 1000  # [N / m]
    q += q_kl

    # ALTERNATIV #2: q = q_kontakttråd + q_bæreline + q_henge + q_Y
    # Kontakttråd.
    # q_kl = q_p * cf * sys.kontakttraad["Diameter"] / 1000  # [N / m]
    # q += q_kl

    # Bæreline.
    # q_b = q_p * cf * sys.baereline["Diameter"] / 1000  # [N / m]
    # q += q_b

    # Hengetråd.
    # for utligger in range(utliggere):
    #     d_henge += sys.hengetraad["Diameter"] / 1000   # [m]
    # q_henge = q_p * cf * d_henge  # [N/m]
    # q += q_henge

    # Y-line.
    # if not sys.y_line == None:  # Sjekker at systemet har Y-line
    #     d_Y += sys.y_line["Diameter"] / 1000  # [m]
    #     # L_Y = lengde Y-line
    # q_Y = q_p * cf * d_Y
    # q += q_Y

    return q


def vindlast_mast(i, mast, vindretning):
    """Beregner krefter grunnet vindlast på mast.

    Lastens eksentrisitet i :math:`x`-retning justeres
    med :math:`e`-målet for å ta hensyn til at denne lasten
    måles fra masteinnspenning snarere enn SOK.
    Se også: :func:`kraft.Kraft.__init__`

    Funksjonen beregner også lastbidrag grunnet
    vindlast på brukerdefinert last.

    :param Inndata i: Input fra bruker
    :param Mast mast: Aktuell mast
    :param int vindretning: Aktuell vindretning
    :return: Liste med :class:`Kraft`-objekter
    :rtype: :class:`list`
    """

    # Liste over krefter som skal returneres
    F = []

    # Vind normalt spor
    if vindretning < 2:

        if i.ec3:
            q_p = i.vindkasthastighetstrykk    # [N/m^2]
            cf = mast.c_f                      # [1] Vindkraftfaktor mast
            q_normalt = q_p * cf * mast.A_ref  # [N/m] Normalt spor

            if vindretning == 1:
                q_normalt = -q_normalt

            F.append(Kraft(navn="Vindlast: Mast", type=(0, 4),
                           q=[0, 0, q_normalt],
                           b=mast.h,
                           e=[-mast.h / 2 + i.e, 0, 0]))

            if i.brukerdefinert_last:
                F.append(Kraft(navn="Vindlast: Brukerdefinert vindareal", type=(7, 4),
                               f=[0, 0, q_p * i.a_vind],
                               e=[- i.e_x + i.e, i.e_y, i.e_z]))

        else:
            q_K = _beregn_vindtrykk_NEK(i)

            if vindretning == 1:
                q_K = -q_K

            if mast.type == "H":
                G_lat = 1.05  # [1] Resonans faktor
                C_lat = 2.80  # [1] Drag faktor
                A_lat = mast.A_ref  # [m^2 / m] Mastens referanseareal
                q_normalt = q_K * G_lat * (1.0 + 0.2 * (math.sin(2 * (math.pi / 2)) ** 2)) * C_lat * A_lat

                F.append(Kraft(navn="Vindlast: Mast", type=(0, 4),
                               q=[0, 0, q_normalt],
                               b=mast.h,
                               e=[-mast.h / 2 + i.e, 0, 0]))
            else:
                C_str = 2.0
                if mast.type == "B":
                    C_str = 1.4
                q_normalt = q_K * C_str * mast.A_ref

                F.append(Kraft(navn="Vindlast: Mast", type=(0, 4),
                               q=[0, 0, q_normalt],
                               b=mast.h,
                               e=[-mast.h / 2 + i.e, 0, 0]))

            if i.brukerdefinert_last:
                F.append(Kraft(navn="Vindlast: Brukerdefinert vindareal", type=(7, 4),
                               f=[0, 0, q_K * i.a_vind],
                               e=[- i.e_x, i.e_y, i.e_z]))


    # Vind parallelt spor
    else:
        if i.ec3:
            q_p = i.vindkasthastighetstrykk        # [N/m^2]
            cf_par = mast.c_f_par                  # [1] Vindkraftfaktor mast
            q_par = q_p * cf_par * mast.A_ref_par  # [N/m] Parallelt spor

            F.append(Kraft(navn="Vindlast: Mast", type=(0, 4),
                           q=[0, q_par, 0],
                           b=mast.h,
                           e=[-mast.h / 2 + i.e, 0, 0]))

            if i.brukerdefinert_last:
                F.append(Kraft(navn="Vindlast: Brukerdefinert vindareal", type=(7, 4),
                               f=[0, q_p * i.a_vind, 0],
                               e=[- i.e_x, i.e_y, i.e_z]))

        else:
            q_K = _beregn_vindtrykk_NEK(i)

            if mast.type == "H":
                # Inngangsparametre
                G_lat = 1.05  # [1] Resonans faktor
                C_lat = 2.80  # [1] Drag faktor
                A_lat = mast.A_ref  # [m^2 / m] Mastens referanseareal
                q_par = q_K * G_lat * (1.0 + 0.2 * (math.sin(2 * (math.pi / 2)) ** 2)) * C_lat * A_lat

                F.append(Kraft(navn="Vindlast: Mast", type=(0, 4),
                               q=[0, q_par, 0],
                               b=mast.h,
                               e=[-mast.h / 2 + i.e, 0, 0]))
            else:
                # Inngangsparametre
                C_str = 1.4  # [1] Drag faktor
                q_par = q_K * C_str * mast.A_ref_par

                F.append(Kraft(navn="Vindlast: Mast", type=(0, 4),
                               q=[0, q_par, 0],
                               b=mast.h,
                               e=[-mast.h / 2 + i.e, 0, 0]))

            if i.brukerdefinert_last:
                F.append(Kraft(navn="Vindlast: Brukerdefinert vindareal", type=(7, 4),
                               f=[0, q_K * i.a_vind, 0],
                               e=[- i.e_x, i.e_y, i.e_z]))

    return F


def vindlast_ledninger(i, sys, vindretning):
    """Beregner krefter grunnet vindlast på ledninger.

    :param Inndata i: Input fra bruker
    :param System sys: Data for ledninger og utligger
    :param int vindretning: Aktuell vindretning
    :return: Liste med :class:`Kraft`-objekter
    :rtype: :class:`list`
    """

    # Liste over krefter som skal returneres
    F = []

    # Ingen vindlast på ledninger med vind parallelet spor
    if vindretning < 2:

        a = (i.a1 + i.a2) / 2  # [m] masteavstand
        a2 = i.a2  # [m] Avstand til neste mast

        if i.ec3:
            q_p = i.vindkasthastighetstrykk  # [N/m^2]
            cf = 1.1                         # [1] Vindkraftfaktor ledning
            q = q_p * cf

        else:
            q_K = _beregn_vindtrykk_NEK(i)
            G_C = 0.75  # [1] Respons faktor
            C_C = 1.0  # [1] Drag faktor
            q = q_K * G_C * C_C

        if vindretning == 1:
            q = -q

        # Antall utliggere
        n = 1
        if i.siste_for_avspenning or i.linjemast_utliggere == 2:
            n = 2

        # Kontakttråd
        g_sno = _g_sno(i.ec3, i.isklasse, sys.kontakttraad["Diameter"])
        D = _D_ledning(i.ec3, g_sno, sys.kontakttraad["Diameter"])
        f_z = n * a * q * sys.kontakttraad["Diameter"] / 1000
        F.append(Kraft(navn="Vindlast: Kontakttråd", type=(1, 4),
                       f=[0, 0, f_z], e=[-i.fh, 0, 0]))
        f_z = n * a * q * D
        F.append(Kraft(navn="Vindlast: Kontakttråd, økt diameter", type=(1, 3),
                       f=[0, 0, f_z], e=[-i.fh, 0, 0]))

        # Bæreline
        g_sno = _g_sno(i.ec3, i.isklasse, sys.baereline["Diameter"])
        D = _D_ledning(i.ec3, g_sno, sys.baereline["Diameter"])
        f_z = n * a * q * sys.baereline["Diameter"] / 1000
        F.append(Kraft(navn="Vindlast: Bæreline", type=(1, 4),
                       f=[0, 0, f_z], e=[-i.fh - i.sh, 0, 0]))
        f_z = n * a * q * D
        F.append(Kraft(navn="Vindlast: Bæreline, økt diameter", type=(1, 3),
                       f=[0, 0, f_z], e=[-i.fh - i.sh, 0, 0]))

        # Hengetråd
        d_henge = sys.hengetraad["Diameter"] / 1000  # [m]
        # Bruker lineær interpolasjon for å finne lengde av hengetråd
        L_henge = 8 * a / 60
        q_henge = q * d_henge  # [N/m]
        f_z = n * L_henge * q_henge
        F.append(Kraft(navn="Vindlast: Hengetråd", type=(1, 4),
                       f=[0, 0, f_z], e=[-i.fh - i.sh/2, 0, 0]))

        # Y-line
        if not sys.y_line == None:  # Sjekker at systemet har Y-line
            L = 0
            if (sys.navn == "20A" or sys.navn == "35") and i.radius > 800:
                L = 14
            elif sys.navn == "25" and i.radius > 1200:
                L = 18
            g_sno = _g_sno(i.ec3, i.isklasse, sys.y_line["Diameter"])
            D = _D_ledning(i.ec3, g_sno, sys.y_line["Diameter"])
            f_z = n * L * q * sys.y_line["Diameter"] / 1000
            F.append(Kraft(navn="Vindlast: Y-line", type=(1, 4),
                           f=[0, 0, f_z], e=[-i.fh - i.sh, 0, 0]))
            f_z = n * L * q * D
            F.append(Kraft(navn="Vindlast: Y-line, økt diameter", type=(1, 3),
                       f=[0, 0, f_z], e=[-i.fh - i.sh, 0, 0]))

        # Fikspunktmast
        if i.fixpunktmast:
            g_sno = _g_sno(i.ec3, i.isklasse, sys.fixline["Diameter"])
            D = _D_ledning(i.ec3, g_sno, sys.fixline["Diameter"])
            f_z = a * q * sys.fixline["Diameter"] / 1000
            F.append(Kraft(navn="Vindlast: Fixpunktmast", type=(2, 4),
                           f=[0, 0, f_z], e=[-i.fh - i.sh, 0, 0]))
            f_z = a * q * D
            F.append(Kraft(navn="Vindlast: Fixpunktmast, økt diameter", type=(2, 3),
                           f=[0, 0, f_z], e=[-i.fh - i.sh, 0, 0]))

        # Fiksavspenningsmast
        if i.fixavspenningsmast:
            g_sno = _g_sno(i.ec3, i.isklasse, sys.fixline["Diameter"])
            D = _D_ledning(i.ec3, g_sno, sys.fixline["Diameter"])
            f_z = (a2 / 2) * q * sys.fixline["Diameter"] / 1000
            F.append(Kraft(navn="Vindlast: Fixavspenningsmast", type=(2, 4),
                           f=[0, 0, f_z], e=[-i.fh - i.sh, 0, 0]))
            f_z = (a2 / 2) * q * D
            F.append(Kraft(navn="Vindlast: Fixavspenningsmast, økt diameter", type=(2, 3),
                           f=[0, 0, f_z], e=[-i.fh - i.sh, 0, 0]))

        # Avspenningsmast
        if i.avspenningsmast:
            g_sno_b = _g_sno(i.ec3, i.isklasse, sys.baereline["Diameter"])
            g_sno_kl = _g_sno(i.ec3, i.isklasse, sys.kontakttraad["Diameter"])
            D_b = _D_ledning(i.ec3, g_sno, sys.baereline["Diameter"])
            D_kl = _D_ledning(i.ec3, g_sno, sys.kontakttraad["Diameter"])
            f_z = (a2 / 2) * q * (sys.baereline["Diameter"] / 1000 + sys.kontakttraad["Diameter"] / 1000)
            F.append(Kraft(navn="Vindlast: Avspenningsmast", type=(3, 4),
                           f=[0, 0, f_z], e=[-i.fh - i.sh, 0, 0]))
            f_z = (a2 / 2) * q * (D_b + D_kl)
            F.append(Kraft(navn="Vindlast: Avspenningsmast, økt diameter", type=(3, 3),
                           f=[0, 0, f_z], e=[-i.fh - i.sh, 0, 0]))

        # Forbigangsledning
        if i.forbigang_ledn:
            g_sno = _g_sno(i.ec3, i.isklasse, sys.forbigangsledning["Diameter"])
            D = _D_ledning(i.ec3, g_sno, sys.forbigangsledning["Diameter"])
            f_z = a * q * sys.forbigangsledning["Diameter"] / 1000
            kategori = 5  # Fastavspent, side
            if not i.matefjern_ledn and not i.at_ledn and not i.jord_ledn:
                kategori = 6  # Fastavspent, topp
            F.append(Kraft(navn="Vindlast: Forbigangsledn", type=(kategori, 4),
                           f=[0, 0, f_z], e=[-i.hf, 0, 0]))
            f_z = a * q * D
            F.append(Kraft(navn="Vindlast: Forbigangsledn, økt diameter", type=(kategori, 3),
                           f=[0, 0, f_z], e=[-i.hf, 0, 0]))

        # Returledning (2 stk.)
        if i.retur_ledn:
            g_sno = _g_sno(i.ec3, i.isklasse, sys.returledning["Diameter"])
            D = 2 * _D_ledning(i.ec3, g_sno, sys.returledning["Diameter"])
            f_z = 2 * a * q * sys.returledning["Diameter"] / 1000
            F.append(Kraft(navn="Vindlast: Returledning", type=(5, 4),
                           f=[0, 0, f_z], e=[-i.hr, 0, 0]))
            f_z = a * q * D
            F.append(Kraft(navn="Vindlast: Returledning, økt diameter", type=(5, 3),
                           f=[0, 0, f_z], e=[-i.hr, 0, 0]))


        # Fiberoptisk ledning
        if i.fiberoptisk_ledn:
            g_sno = _g_sno(i.ec3, i.isklasse, sys.fiberoptisk["Diameter"])
            D = _D_ledning(i.ec3, g_sno, sys.fiberoptisk["Diameter"])
            f_z = a * q * sys.fiberoptisk["Diameter"] / 1000
            F.append(Kraft(navn="Vindlast: Fiberoptisk ledning", type=(5, 4),
                           f=[0, 0, f_z], e=[-i.fh, 0, 0]))
            f_z = a * q * D
            F.append(Kraft(navn="Vindlast: Fiberoptisk ledning, økt diameter", type=(5, 3),
                           f=[0, 0, f_z], e=[-i.fh, 0, 0]))

        # Mate-/fjernledning(er) (n stk.)
        if i.matefjern_ledn:
            n = i.matefjern_antall
            g_sno = _g_sno(i.ec3, i.isklasse, sys.matefjernledning["Diameter"])
            D = n * _D_ledning(i.ec3, g_sno, sys.matefjernledning["Diameter"])
            f_z = n * a * q * sys.matefjernledning["Diameter"] / 1000
            er = "er" if n > 1 else ""
            F.append(Kraft(navn="Vindlast: Mate-/fjernledning{}".format(er), type=(6, 4),
                           f=[0, 0, f_z], e=[-i.hfj, 0, 0]))
            f_z = a * q * D
            F.append(Kraft(navn="Vindlast: Mate-/fjernledning{}, økt diameter".format(er), type=(6, 3),
                           f=[0, 0, f_z], e=[-i.hfj, 0, 0]))

        # AT-ledning (2 stk.)
        if i.at_ledn:
            g_sno = _g_sno(i.ec3, i.isklasse, sys.at_ledning["Diameter"])
            D = 2 * _D_ledning(i.ec3, g_sno, sys.at_ledning["Diameter"])
            f_z = 2 * a * q * sys.at_ledning["Diameter"] / 1000
            F.append(Kraft(navn="Vindlast: AT-ledning", type=(6, 4),
                           f=[0, 0, f_z], e=[-i.hfj, 0, 0]))
            f_z = a * q * D
            F.append(Kraft(navn="Vindlast: AT-ledning, økt diameter", type=(6, 3),
                           f=[0, 0, f_z], e=[-i.hfj, 0, 0]))

        # Jordledning
        if i.jord_ledn:
            g_sno = _g_sno(i.ec3, i.isklasse, sys.jordledning["Diameter"])
            D = _D_ledning(i.ec3, g_sno, sys.jordledning["Diameter"])
            f_z = a * q * sys.jordledning["Diameter"] / 1000
            kategori = 5  # Fastavspent, side
            e_z = -0.3
            if not i.matefjern_ledn and not i.at_ledn and not i.forbigang_ledn:
                kategori = 6  # Fastavspent, topp
                e_z = 0
            F.append(Kraft(navn="Vindlast: AT-ledning", type=(kategori, 4),
                           f=[0, 0, f_z], e=[-i.hj, 0, e_z]))
            f_z = a * q * D
            F.append(Kraft(navn="Vindlast: AT-ledning, økt diameter", type=(kategori, 3),
                           f=[0, 0, f_z], e=[-i.hj, 0, e_z]))

    return F


def isogsno_last(i, sys):
    """Beregner krefter grunnet is- og snølast.

    :param Inndata i: Input fra bruker
    :param System sys: Data for ledninger og utligger
    :return: Liste med :class:`Kraft`-objekter
    :rtype: :class:`list`
    """

    a = (i.a2 + i.a1) / 2  # [m] Midlere masteavstand
    a2 = i.a2              # [m] Avstand til neste mast
    a_T, a_T_dot = sys.a_T, sys.a_T_dot


    arm = a_T_dot
    if i.strekkutligger:
        arm = a_T

    # F = liste over krefter som skal returneres
    F = []

    # Antall utliggere
    n = 1
    if i.siste_for_avspenning or i.linjemast_utliggere == 2:
        n = 2

    # Bæreline
    g_sno = _g_sno(i.ec3, i.isklasse, sys.baereline["Diameter"])
    F.append(Kraft(navn="Islast: Bæreline", type=(1, 3),
                   f=[n * a * g_sno, 0, 0],
                   e=[-i.fh - i.sh, 0, i.sms]))

    # Hengetråd: Ingen snølast.

    # Kontakttråd
    g_sno = _g_sno(i.ec3, i.isklasse, sys.kontakttraad["Diameter"])
    F.append(Kraft(navn="Islast: Kontakttråd", type=(1, 3),
                   f=[n * a * g_sno, 0, 0],
                   e=[-i.fh, 0, arm]))

    # Y-line
    if not sys.y_line == None:  # Sjekker at systemet har Y-line
        # L = lengde Y-line
        L = 0
        if (sys.navn == "20A" or sys.navn == "35") and i.radius >= 800:
            L = 14
        elif sys.navn == "25" and i.radius >= 1200:
            L = 18
        g_sno = _g_sno(i.ec3, i.isklasse, sys.y_line["Diameter"])
        F.append(Kraft(navn="Islast: Y-line", type=(1, 3),
                       f=[n * L * g_sno, 0, 0],
                       e=[-i.fh, 0, i.sms]))

    # Fikspunktmast
    if i.fixpunktmast:
        g_sno = _g_sno(i.ec3, i.isklasse, sys.fixline["Diameter"])
        F.append(Kraft(navn="Islast: Fixline", type=(2, 3),
                       f=[a * g_sno, 0, 0],
                       e=[-i.fh - i.sh, 0, i.sms]))

    # Fiksavspenningsmast
    if i.fixavspenningsmast:
        g_sno = _g_sno(i.ec3, i.isklasse, sys.fixline["Diameter"])
        F.append(Kraft(navn="Islast: Fixline", type=(2, 3),
                       f=[(a2/2) * g_sno, 0, 0],
                       e=[-i.fh - i.sh, 0, 0]))

    # Avspenningsmast
    if i.avspenningsmast:
        g_sno_b = _g_sno(i.ec3, i.isklasse, sys.baereline["Diameter"])
        g_sno_kl = _g_sno(i.ec3, i.isklasse, sys.kontakttraad["Diameter"])
        F.append(Kraft(navn="Islast: Avspenningsmast", type=(3, 3),
                       f=[(a2/2) * (g_sno_b + g_sno_kl), 0, 0],
                       e=[-i.fh - i.sh/2, 0, 0]))

    # Forbigangsledning
    if i.forbigang_ledn:
        e_z = -0.3
        kategori = 5
        if not i.matefjern_ledn and not i.at_ledn and not i.jord_ledn:
            # Forbigangsledning montert på baksiden av mast
            e_z = 0
            kategori = 6
        g_sno = _g_sno(i.ec3, i.isklasse, sys.forbigangsledning["Diameter"])
        F.append(Kraft(navn="Islast: Forbigangsledning", type=(kategori, 3),
                       f=[a * g_sno, 0, 0],
                       e=[-i.hf, 0, e_z]))

    # Returledninger (2 stk.)
    if i.retur_ledn:
        g_sno = 2 * _g_sno(i.ec3, i.isklasse, sys.returledning["Diameter"])
        F.append(Kraft(navn="Islast: Returledning", type=(5, 3),
                       f=[a * g_sno, 0, 0],
                       e=[-i.hr, 0, -0.5]))

    # Mate-/fjernledning(er) (n stk.)
    if i.matefjern_ledn:
        n = i.matefjern_antall
        er = "er" if n > 1 else ""
        g_sno = n * _g_sno(i.ec3, i.isklasse, sys.matefjernledning["Diameter"])
        F.append(Kraft(navn="Islast: Mate-/fjernledning{}".format(er), type=(6, 3),
                       f=[a * g_sno, 0, 0],
                       e=[-i.hfj, 0, 0]))

    # Fiberoptisk
    if i.fiberoptisk_ledn:
        g_sno = _g_sno(i.ec3, i.isklasse, sys.fiberoptisk["Diameter"])
        F.append(Kraft(navn="Islast: Fiberoptisk ledning", type=(5, 3),
                       f=[a * g_sno, 0, 0],
                       e=[-i.fh, 0, -0.3]))

    # AT-ledninger (2 stk.)
    if i.at_ledn:
        g_sno = 2 * _g_sno(i.ec3, i.isklasse, sys.at_ledning["Diameter"])
        F.append(Kraft(navn="Islast: AT-ledning", type=(6, 3),
                       f=[a * g_sno, 0, 0],
                       e=[-i.hfj, 0, 0]))

    # Jordledning
    if i.jord_ledn:
        e_z = -0.3
        kategori = 5
        if not i.matefjern_ledn and not i.at_ledn and not i.forbigang_ledn:
            e_z = 0
            kategori = 6
        g_sno = _g_sno(i.ec3, i.isklasse, sys.jordledning["Diameter"])
        F.append(Kraft(navn="Islast: Jordledning", type=(kategori, 3),
                       f=[a * g_sno, 0, 0],
                       e=[-i.hj, 0, e_z]))

    return F



def _beregn_vindtrykk_NEK(i):
    """Beregner dimensjonerende vindtrykk mhp. bransjestandard.

    :param Inndata i: Input fra bruker
    :return: Vindtrykk :math:`[\\frac{N}{m^2}]`
    :rtype: :class:`float`
    """

    """
    # Alternativ #1: NEK EN 50125-2
    # Inngangsparametre for referansehøyde 10m over bakkenivå
    z = 10              # [m] høyde over bakken
    v_10 = 24           # [m / s] 10-minste middelvindhastighet
    # Ruhetsparameteren for ulike terrengkategorier [1]
    alpha = [0.12, 0.16, 0.20, 0.28]

    # Vindhastigheten i høyden z over bakkenivå etter NEK EN 50125-2.
    v_z = v_10 * (z/10) ** alpha[3]
    """

    # Alternativ 2: EC1
    # Terrengkategori II velges
    v_b_0 = i.referansevindhastighet  # [m/s] Referansevindhastighet for aktuell kommune

    # Dynamisk vindtrykk [N / m^2]
    rho = 1.255  # [kg / m^3]
    G_q = 2.05   # [1] Gust-respons faktor
    G_t = 1.0    # [1] Terrengfaktor av typen åpent

    q_K = 0.5 * rho * G_q * G_t * v_b_0 ** 2

    return q_K


def _g_sno(ec3, isklasse, d):
    """Beregner linjelast fra snø/is på en ledning.

    Linjelastene som hentes ut basert på isklasse ved
    NEK-beregning gjelder for ledninger med diametere mellom
    :math:`10` og :math:`20 mm`, derfor settes linjelasten
    for ledninger med større diametere til maksimalverdien
    :math:`[15 \\frac{N}{m}]`.

    :param Boolean ec3: Brukerens valg av beregningsmetode
    :param float d: Ledningens diameter :math:`[mm]`
    :return: Last på ledningen :math:`[\\frac{N}{m}]`
    :rtype: :class:`float`
    """

    if ec3:
        return 2 + 0.5 * d
    else:
        if d > 20:
            return 15
        else:
            if isklasse == 0:
                return 0
            elif isklasse == 1:
                return 3.5
            elif isklasse == 2:
                return 7.5
            else:
                return 15

def _D_ledning(ec3, g_sno, d):
    """Beregner effektiv økning av en lednings vindareal grunnet snø/is.

    :param Boolean ec3: Brukerens valg av beregningsmetode
    :param float g_sno: Linjelast fra snø/is :math:`[\\frac{N}{m}]`
    :param float d: Ledningens initielle diameter :math:`[mm]`
    :return: Ledningens tilleggsareal grunnet snø/is :math:`[m]`
    :rtype: :class:`float`
    """

    if ec3:
        return 0
    else:
        d /= 1000
        rho = 500 * 9.81
        return math.sqrt(d**2 + 4*g_sno/(math.pi*rho)) - d

