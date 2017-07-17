# -*- coding: utf8 -*-
"""Funksjoner for å beregne deformasjonsbidrag fra et :class:`Kraft`-objekt."""
from __future__ import unicode_literals

import numpy
import math
import scipy.integrate as integrate

def bjelkeformel_M(mast, j, fh):
    """Beregner deformasjoner i kontakttrådhøyde grunnet et rent moment.

    .. warning::
        Denne funksjonen er for øyeblikket *ikke* aktiv ved
        deformasjonsberegninger (se :func:`beregning._beregn_deformasjoner`)
        da den ikke tar hensyn til forskjellige innspenningsbetingelser
        for eksentrisk plasserte vertikale laster.

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


def bjelkeformel_P(mast, j, fh):
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


def bjelkeformel_q(mast, j, fh):
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


def torsjonsvinkel(mast, j, fh):
    """Beregner torsjonsvinkel i kontakttrådhøyde grunnet en eksentrisk horisontal last.

    Funksjonen beregner torsjonsvinkel i grader basert på følgende bjelkeformel:
    :math:`\\phi = \\frac{T}{2EC_w\\lambda}
    [\\frac{sinh(\\lambda(x-fh))-sinh(\\lambda x)}{cosh(\\lambda x)} + \\lambda*fh],
    \\ \\lambda = \\sqrt{\\frac{GI_T}{EC_w}}`

    :param Mast mast: Aktuell mast som beregnes
    :param Kraft j: Last som skal påføres ``mast``
    :param float fh: Kontakttrådhøyde :math:`[m]`
    :return: Matrise med rotasjonsbidrag :math:`[^{\\circ}]`
    :rtype: :class:`numpy.array`
    """

    D = numpy.zeros((5, 8, 3))

    if j.e[0] < 0:

        T = (abs(j.f[1] * -j.e[2]) + abs(j.f[2] * j.e[1])) * 1000
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


def utliggerbidrag(sys, sidekrefter, etasje):
    """Beregner deformasjonsbidrag fra utligger grunnet sidekrefter i KL.

    :param System sys: Data for ledninger og utligger
    :param list sidekrefter: Liste med :class:`Kraft`-objekter som gir sidekrefter på utligger
    :param int etasje: Angir riktig plassering av bidrag i forskyvningsmatrisen
    :return: Matrise med forskyvningsbidrag :math:`[mm]`
    :rtype: :class:`numpy.array`
    """

    D = numpy.zeros((5, 8, 3))

    if sys.navn == "20A" or sys.navn == "20B":
        for s in sidekrefter:
            D[etasje, 0, 1] += 20/2500 * s
    elif sys.navn == "25":
        for s in sidekrefter:
            D[etasje, 0, 1] += 4/2500 * s

    return D

