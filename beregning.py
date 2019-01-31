# -*- coding: utf8 -*-
from __future__ import unicode_literals

"""Overordnet beregningsprosedyre for master.

Styrer beregning av reaksjonskrefter og forskyvninger for samtlige
master i systemet. Ut fra tredimensjonale ``numpy.array``-objekter
R og D for henholdsvis reaksjonskrefter ved masteinnspenning
og forskyvninger i kontakttrådhøyde utføres lastfaktoranalyse
for alle gyldige lastsituasjoner i valgt beregningsprosedyre.
Mastenes tredje dimensjon ikke gjengitt ved de plane figurene
nedenfor, refereres for enkelhets skyld til som etasjer.

::

    Indeksering av 3D-matriser:
    [etasje, rad, kolonne]


==
R
==
Reaksjonskrefter :math:`[N]` og momenter :math:`[Nm]` ved mastens innspenning
------------------------------------------------------------------------------

::

            Indekser:
       0   1   2   3   4   5
       My  Vy  Mz  Vz  N   T
     ________________________
    |                        | 0  Mast + utligger
    |                        | 1  Kontaktledning
    |                        | 2  Fixline
    |                        | 3  Avspenning
    |                        | 4  Bardunering
    |                        | 5  Fastavspente (sidemontert)
    |                        | 6  Fastavspente (toppmontert)
    |                        | 7  Brukerdefinert last
     ------------------------

    Etasjer: 0 = egenvekt, 1 = strekk,
             2 = temperatur, 3 = snø, 4 = vind


==
D
==
Forskyvning :math:`[mm]` og rotasjon :math:`[^{\\circ}]` av mast i kontakttrådhøyde
------------------------------------------------------------------------------------

::

      Indekser:
      0   1   2
      Dy  Dz  phi
     _____________
    |             | 0  Mast + utligger
    |             | 1  Kontaktledning
    |             | 2  Fixline
    |             | 3  Avspenning
    |             | 4  Bardunering
    |             | 5  Fastavspente (sidemontert)
    |             | 6  Fastavspente (toppmontert)
    |             | 7  Brukerdefinert last
     -------------

    Etasjer: 0 = egenvekt, 1 = strekk,
             2 = temperatur, 3 = snø, 4 = vind

"""

import numpy
import math
import scipy.integrate as integrate
import system
import lister
import laster
import tilstand
from kraft import Kraft
import mast


def beregn(i):
    """Gjennomfører beregning og returnerer masteobjekter med resultater.

    :param Inndata i: Input fra bruker
    :return: Liste med master
    :rtype: :class:`list`
    """
    # Oppretter masteobjekt med brukerdefinert høyde
    master = mast.hent_master(
        i.h, i.s235, i.materialkoeff, i.avspenningsmast,
        i.fixavspenningsmast, i.avspenningsbardun)
    # Oppretter systemobjekt med data for ledninger, utliggere og geometri
    sys = system.hent_system(i)
    # F_statisk_ledn = laster uavhengige av temperatur, snø og vind
    # F_dynamisk_ledn = laster som varierer med én eller flere klimaforhold
    F_statisk_ledn, F_dynamisk_ledn = laster.laster_ledninger(i, sys, mastehoyde=i.h)
    iterasjon = 0
    for mast in master:
        F_statisk_mast, F_dynamisk_mast = laster.laster_mast(i, sys, mast)
        F_statisk = F_statisk_ledn + F_statisk_mast
        F_dynamisk = F_dynamisk_ledn + F_dynamisk_mast
        lastsituasjoner, lastfaktorer = lister.hent_lastkombinasjoner(i.ec3)
        for lastsituasjon in lastsituasjoner:
            psi_T = lastsituasjoner.get(lastsituasjon)["psi_T"]
            psi_S = lastsituasjoner.get(lastsituasjon)["psi_S"]
            psi_V = lastsituasjoner.get(lastsituasjon)["psi_V"]
            temp = lastsituasjoner.get(lastsituasjon)["T"]
            # F_T = klimaavhengige laster ved gitt temperatur
            F_T = []
            F_T.extend([f for f in F_dynamisk if f.T==temp or f.T==None])
            # 0: Vind fra mast mot spor
            # 1: Vind fra spor mot mast
            # 2: Vind parallelt sporet
            for vindretning in range(3):
                # F = alle dimensjonerende krefter ved gitte klimaforhold
                F = []
                F.extend(F_statisk)
                F.extend([f for f in F_T if f.vindretning==vindretning or f.vindretning==None])
                R_0 = _beregn_reaksjonskrefter(F)
                D_0 = _beregn_deformasjoner(i, mast, F)
                R = numpy.zeros((5, 8, 6))
                for G in lastfaktorer["G"]:
                    # Egenvekt
                    R[0, :, :] = R_0[0, :, :] * G
                    for L in lastfaktorer["L"]:
                        # Strekk
                        R[1, :, :] = R_0[1, :, :] * L
                        for T in lastfaktorer["T"]:
                            # Temperatur
                            R[2, :, :] = R_0[2, :, :] * psi_T * T
                            for S in lastfaktorer["S"]:
                                # Snø
                                R[3, :, :] = R_0[3, :, :] * psi_S * S
                                for V in lastfaktorer["V"]:
                                    # Vind
                                    R[4, :, :] = R_0[4, :, :] * psi_V * V

                                    t = tilstand.Tilstand(mast, i, lastsituasjon, vindretning,
                                                          grensetilstand=0, F=F, R=R, G=G, L=L,
                                                          T=T, S=S, V=V, psi_T=psi_T, psi_S=psi_S,
                                                          psi_V=psi_V, temp=temp, iterasjon=iterasjon)
                                    mast.lagre_tilstand(t)
                                    iterasjon += 1
                # Bruksgrense, forskyvning totalt
                R = numpy.zeros((5, 8, 6))
                R[0:2, :, :] = R_0[0:2, :, :]
                R[2, :, :] = R_0[2, :, :] * psi_T
                R[3, :, :] = R_0[3, :, :] * psi_S
                R[4, :, :] = R_0[4, :, :] * psi_V
                D = numpy.zeros((5, 8, 3))
                D[0:2, :, :] = D_0[0:2, :, :]
                D[2, :, :] = D_0[2, :, :] * psi_T
                D[3, :, :] = D_0[3, :, :] * psi_S
                D[4, :, :] = D_0[4, :, :] * psi_V
                D += _utliggerbidrag(sys, R)
                t = tilstand.Tilstand(mast, i, lastsituasjon, vindretning,
                                      grensetilstand=1, R=R, D=D, iterasjon=iterasjon)
                mast.lagre_tilstand(t)
                # Bruksgrense, forskyvning KL
                R[0:2, :, :], D[0:2, :, :] = 0, 0  # Nullstiller bidrag fra egenvekt og strekk
                t = tilstand.Tilstand(mast, i, lastsituasjon, vindretning,
                                      grensetilstand=2, R=R, D=D, iterasjon=iterasjon)
                mast.lagre_tilstand(t)
                iterasjon += 1
        # Ulykkeslast
        if i.siste_for_avspenning or i.linjemast_utliggere > 1:
            lastsituasjon = "Ulykkeslast"
            F_ulykke = []
            F_ulykke.extend([f for f in F_statisk if not f.navn.startswith("Sidekraft: KL")])
            R_ulykke = _beregn_reaksjonskrefter(F_ulykke)
            # Tilleggskraft ved ulykke
            ulykkeslast = laster.ulykkeslast(i, sys, numpy.sum(numpy.sum(R, axis=0), axis=0)[5])
            R_ulykke += _beregn_reaksjonskrefter(ulykkeslast)
            t = tilstand.Tilstand(mast, i, lastsituasjon, 0,
                                  grensetilstand=3, F=F_ulykke, R=R_ulykke, iterasjon=iterasjon)
            mast.lagre_tilstand(t)
            iterasjon += 1
    return master


def _beregn_reaksjonskrefter(F):
    """Beregner reaksjonskrefter ved masteinnspenning grunnet krefter i ``F``.

    :param list F: Liste med :class:`Kraft`-objekter påført systemet
    :return: Matrise med reaksjonskrefter
    :rtype: :class:`numpy.array`
    """

    # Initierer R-matrisen for reaksjonskrefter
    R = numpy.zeros((5, 8, 6))

    for j in F:
        R_0 = numpy.zeros((5, 8, 6))
        f = j.f
        if not numpy.count_nonzero(j.q) == 0:
            f = numpy.array([j.q[0] * j.b, j.q[1] * j.b, j.q[2] * j.b])

        # Sorterer bidrag til reaksjonskrefter
        R_0[j.type[1], j.type[0], 0] = f[0] * j.e[2] + f[2] * (-j.e[0])
        R_0[j.type[1], j.type[0], 1] = f[1]
        R_0[j.type[1], j.type[0], 2] = f[0] * (-j.e[1]) + f[1] * j.e[0]
        R_0[j.type[1], j.type[0], 3] = f[2]
        R_0[j.type[1], j.type[0], 4] = f[0]
        if j.navn.startswith("Sidekraft: KL"):
            R_0[j.type[1], j.type[0], 5] = f[1] * (-j.e[2]) + f[2] * j.e[1]
        else:
            sign = numpy.sign(numpy.sum(numpy.sum(R, axis=0), axis=0)[5])
            sign = 1 if sign == 0 else sign
            R_0[j.type[1], j.type[0], 5] = sign*(abs(f[1] * (-j.e[2])) + abs(f[2] * j.e[1]))

        R += R_0

    return R


def _beregn_deformasjoner(i, mast, F):
    """Beregner forskyvninger i kontakttrådhøyde grunnet krefter i ``F``.

    :param Inndata i: Input fra bruker
    :param Mast mast: Aktuell mast som beregnes
    :param list F: Liste med :class:`Kraft`-objekter påført systemet
    :return: Matrise med forskyvninger
    :rtype: :class:`numpy.array`
    """

    # Konverterer systemhøyde ``fh`` til mastens aksesystem
    fh_korrigert = i.fh + i.e

    # Initierer deformasjonsmatrisen, D
    D = numpy.zeros((5, 8, 3))

    for j in F:
        D_0 = numpy.zeros((5, 8, 3))

        D_0 += ( _bjelkeformel_P(mast, j, fh_korrigert)
                +_bjelkeformel_q(mast, j, fh_korrigert)
                +_bjelkeformel_M(mast, j, fh_korrigert) )

        if mast.type == "bjelke":
            sign = numpy.sign(numpy.sum(numpy.sum(D, axis=0), axis=0)[2])
            sign = 1 if sign == 0 else sign
            D_0 += _torsjonsvinkel(mast, j, fh_korrigert, sign)

        D += D_0

    return D


def _bjelkeformel_M(mast, j, fh):
    """Beregner deformasjoner i kontakttrådhøyde grunnet et rent moment.

    Funksjonen beregner horisontale forskyvninger basert på følgende bjelkeformel:
    :math:`\\delta = \\frac{M*fh^2}{2EI}`

    Dersom :math:`fh > x` interpoleres forskyvningen til høyde :math:`fh`
    ved hjelp av :math:`tan(\\theta) * (fh-x)`,
    der :math:`\\theta` er mastens utbøyningsvinkel i høyde :math:`x`.

    :param Mast mast: Aktuell mast som beregnes
    :param Kraft j: Last som skal påføres ``mast``
    :param float fh: Kontakttrådhøyde i :math:`[m]`
    :return: Matrise med forskyvningsbidrag i :math:`[mm]`
    :rtype: :class:`numpy.array`
    """

    D = numpy.zeros((5, 8, 3))

    if j.e[0] < 0:

        E = mast.E
        delta_topp = mast.h + j.e[0]
        delta_topp = 0 if delta_topp < 0 else delta_topp
        L = (mast.h - delta_topp) * 1000
        delta_y = integrate.quad(mast.Iy_int_M, 0, L, args=(delta_topp,))
        delta_z = integrate.quad(mast.Iz_int_M, 0, L, args=(delta_topp,))
        I_y = L ** 2 / (2 * delta_y[0])
        I_z = L ** 2 / (2 * delta_z[0])
        M_y = j.f[0] * j.e[2] * 1000
        M_z = - j.f[0] * j.e[1] * 1000
        x = -j.e[0] * 1000
        fh *= 1000

        if fh > x:
            theta_y = (M_y * x) / (E * I_y)
            theta_z = (M_z * x) / (E * I_z)
            D[j.type[1], j.type[0], 1] = (M_y * x ** 2) / (2 * E * I_y) + numpy.tan(theta_y) * (fh - x)
            D[j.type[1], j.type[0], 0] = (M_z * x ** 2) / (2 * E * I_z) + numpy.tan(theta_z) * (fh - x)
        else:
            D[j.type[1], j.type[0], 1] = (M_y * fh ** 2) / (2 * E * I_y)
            D[j.type[1], j.type[0], 0] = (M_z * fh ** 2) / (2 * E * I_z)


    return D


def _bjelkeformel_P(mast, j, fh):
    """Beregner deformasjoner i kontakttrådhøyde grunnet en punklast.

    Dersom lasten angriper under kontakttrådhøyde:
    :math:`\\delta = \\frac{P*x^2}{6EI}(3fh-x)`

    Dersom lasten angriper over kontakttrådhøyde:
    :math:`\\delta = \\frac{P*fh^2}{6EI}(3x-fh)`

    :param Mast mast: Aktuell mast som beregnes
    :param Kraft j: Last som skal påføres ``mast``
    :param float fh: Kontakttrådhøyde :math:`[m]`
    :return: Matrise med forskyvningsbidrag :math:`[mm]`
    :rtype: :class:`numpy.array`
    """

    D = numpy.zeros((5, 8, 3))

    if j.e[0] < 0:

        E = mast.E
        delta_topp = mast.h + j.e[0]
        delta_topp = 0 if delta_topp < 0 else delta_topp
        L = (mast.h - delta_topp) * 1000
        delta_y = integrate.quad(mast.Iy_int_P, 0, L, args=(delta_topp,))
        delta_z = integrate.quad(mast.Iz_int_P, 0, L, args=(delta_topp,))
        I_y = L ** 3 / (3 * delta_y[0])
        I_z = L ** 3 / (3 * delta_z[0])
        f_y = j.f[1]
        f_z = j.f[2]
        x = -j.e[0] * 1000
        fh *= 1000

        if fh > x:
            D[j.type[1], j.type[0], 1] = (f_z * x**2) / (6 * E * I_y) * (3 * fh - x)
            D[j.type[1], j.type[0], 0] = (f_y * x**2) / (6 * E * I_z) * (3 * fh - x)
        else:
            D[j.type[1], j.type[0], 1] = (f_z * fh ** 2) / (6 * E * I_y) * (3 * x - fh)
            D[j.type[1], j.type[0], 0] = (f_y * fh ** 2) / (6 * E * I_z) * (3 * x - fh)

    return D


def _bjelkeformel_q(mast, j, fh):
    """Beregner deformasjoner i kontakttrådhøyde grunnet en fordelt last.

    Funksjonen beregner horisontale forskyvninger basert på følgende bjelkeformel:
    :math:`\\delta = \\frac{q*fh^2}{24EI}(fh^2+6h^2-4h*fh)`

    Lasten antas å være jevnet fordelt over hele mastens høyde :math:`h`,
    med resultant i høyde :math:`h/2`

    :param Mast mast: Aktuell mast som beregnes
    :param Kraft j: Last som skal påføres ``mast``
    :param float fh: Kontakttrådhøyde :math:`[m]`
    :return: Matrise med forskyvningsbidrag :math:`[mm]`
    :rtype: :class:`numpy.array`
    """

    D = numpy.zeros((5, 8, 3))

    if j.b > 0 and j.e[0] < 0:

        E = mast.E
        delta_topp = mast.h - j.b
        L = (mast.h - delta_topp) * 1000
        delta_y = integrate.quad(mast.Iy_int_q, 0, L, args=(delta_topp,))
        delta_z = integrate.quad(mast.Iz_int_q, 0, L, args=(delta_topp,))
        I_y = L ** 4 / (4 * delta_y[0])
        I_z = L ** 4 / (4 * delta_z[0])
        q_y = j.q[1] / 1000
        q_z = j.q[2] / 1000
        b = j.b * 1000
        fh *= 1000

        D[j.type[1], j.type[0], 1] = ((q_z * fh ** 2) / (24 * E * I_y)) * (fh ** 2 + 6 * b ** 2 - 4 * b * fh)
        D[j.type[1], j.type[0], 0] = ((q_y * fh ** 2) / (24 * E * I_z)) * (fh ** 2 + 6 * b ** 2 - 4 * b * fh)

    return D


def _torsjonsvinkel(mast, j, fh, sign):
    """Beregner torsjonsvinkel i kontakttrådhøyde grunnet en eksentrisk horisontal last.

    Funksjonen beregner torsjonsvinkel i grader basert på følgende bjelkeformel:
    :math:`\\phi = \\frac{T}{2EC_w\\lambda}
    [\\frac{sinh(\\lambda(x-fh))-sinh(\\lambda x)}{cosh(\\lambda x)} + \\lambda*fh],
    \\ \\lambda = \\sqrt{\\frac{GI_T}{EC_w}}`

    :param Mast mast: Aktuell mast som beregnes
    :param Kraft j: Last som skal påføres ``mast``
    :param float fh: Kontakttrådhøyde :math:`[m]`
    :param float sign: Fortegn for torsjonsmoment
    :return: Matrise med rotasjonsbidrag :math:`[^{\\circ}]`
    :rtype: :class:`numpy.array`
    """

    D = numpy.zeros((5, 8, 3))

    if j.e[0] < 0:

        if j.navn.startswith("Sidekraft: KL"):
            T = (j.f[1] * -j.e[2] + j.f[2] * j.e[1]) * 1000
        else:
            T = sign*(abs(j.f[1] * -j.e[2]) + abs(j.f[2] * j.e[1])) * 1000

        E = mast.E
        G = mast.G
        I_T = mast.It
        C_w = mast.Cw
        lam = math.sqrt(G * I_T / (E * C_w))
        fh = fh * 1000
        x = -j.e[0] * 1000

        D[j.type[1], j.type[0], 2] = (180/math.pi) * T/(E*C_w*lam**3) * ((math.sinh(lam*(x-fh))
                                                 - math.sinh(lam*x))/math.cosh(lam*x) + lam*fh)
    return D


def _utliggerbidrag(sys, R):
    """Beregner deformasjonsbidrag fra utligger grunnet sidekrefter i KL.

    Sidekraften hentes ut fra R-matrisens celle korresponderende til
    skjærkraft Vz grunnet strekk i KL.

    Utregningen er basert på hjelpedokumentet til KL_fund,
    hvor utliggerstivheten er funnet via programmet GPROG-ramme.

    :param System sys: Data for ledninger og utligger
    :param numpy.array R: Reaksjonskraftmatrise
    :return: Matrise med forskyvningsbidrag :math:`[mm]`
    :rtype: :class:`numpy.array`
    """

    D = numpy.zeros((5, 8, 3))

    sidekraft = R[1, 1, 3]

    if sys.navn == "25":
        D[1, 0, 1] += 4/2500 * sidekraft * 0.5
    else:
        D[1, 0, 1] += 20/2500 * sidekraft * 0.5


    return D




