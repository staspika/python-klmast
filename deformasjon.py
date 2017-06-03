"""Funksjoner for å beregne deformasjonsbidrag fra et :class:`Kraft`-objekt."""

import numpy
import math
import scipy.integrate as integrate

def bjelkeformel_M(mast, j, fh):
    """
    .. warning::
        Denne funksjonen er for øyeblikket *ikke* aktiv ved
        deformasjonsberegninger da den ikke tar hensyn til forskjellige
        innspenningsbetingelser for eksentrisk plasserte vertikale laster.
        Mangler også implementasjon av midlere stivhetsberegning.

    Beregner deformasjoner i kontakttrådhøyde grunnet et rent moment.

    Dersom :math:`fh > x` interpoleres forskyvningen til høyde fh
    ved hjelp av :math:`tan(theta) * (fh-x)`,
    der :math:`theta` er mastens utbøyningsvinkel i høyde x.

    :param Mast mast: Aktuell mast som beregnes
    :param Kraft j: Last som skal påføres ``mast``
    :param float fh: Kontakttrådhøyde i :math:`m`
    :return: Matrise med forskyvningsbidrag i :math:`mm`
    :rtype: :class:`numpy.array`
    """
    E = mast.E
    I_y = mast.Iy(2/3 * mast.h)
    I_z = mast.Iz(2/3 * mast.h)
    f_x = j.f[0]
    e_y = j.e[1] * 1000 - mast.d/2
    e_z = j.e[2] * 1000 - mast.bredde(mast.h + j.e[0])/2
    M_y = f_x * e_z
    M_z = -f_x * e_y
    x = -j.e[0] * 1000
    fh *= 1000

    D = numpy.zeros((5, 8, 3))

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

    Dersom :math:`fh > x` interpoleres forskyvningen til høyde fh
    ved hjelp av :math:`tan(theta) * (fh-x)`,
    der :math:`theta` er mastens utbøyningsvinkel i høyde x.

    :param Mast mast: Aktuell mast som beregnes
    :param Kraft j: Last som skal påføres ``mast``
    :param float fh: Kontakttrådhøyde i :math:`m`
    :return: Matrise med forskyvningsbidrag i :math:`mm`
    :rtype: :class:`numpy.array`
    """

    D = numpy.zeros((5, 8, 3))

    if j.e[0] < 0:

        E = mast.E
        delta_topp = mast.h + j.e[0]
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
            theta_y = (f_y * x**2) / (2 * E * I_z)
            theta_z = (f_z * x**2) / (2 * E * I_y)
            D[j.type[1], j.type[0], 1] = (f_z / (3 * E * I_y)) * x ** 3 + numpy.tan(theta_y) * (fh - x)
            D[j.type[1], j.type[0], 0] = (f_y / (3 * E * I_z)) * x ** 3 + numpy.tan(theta_z) * (fh - x)
        else:
            D[j.type[1], j.type[0], 1] = (f_z / (2 * E * I_y)) * (x * fh ** 2 - ((1 / 3) * fh ** 3))
            D[j.type[1], j.type[0], 0] = (f_y / (2 * E * I_z)) * (x * fh ** 2 - ((1 / 3) * fh ** 3))

    return D


def bjelkeformel_q(mast, j, fh):
    """Beregner deformasjoner i kontakttrådhøyde grunnet en fordelt last.

    Lasten antas å være jevnet fordelt over hele mastens høyde ``h``,
    med resultant i høyde :math:`h/2`

    :param Mast mast: Aktuell mast som beregnes
    :param Kraft j: Last som skal påføres ``mast``
    :param float fh: Kontakttrådhøyde i :math:`m`
    :return: Matrise med forskyvningsbidrag i :math:`mm`
    :rtype: :class:`numpy.array`
    """

    D = numpy.zeros((5, 8, 3))

    if j.b > 0:

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

        D[j.type[1], j.type[0], 1] = ((q_z * fh ** 2) / (24 * E * I_y)) * (6 * b ** 2 - 4 * b * fh + fh ** 2)
        D[j.type[1], j.type[0], 0] = ((q_y * fh ** 2) / (24 * E * I_z)) * (6 * b ** 2 - 4 * b * fh + fh ** 2)

    return D


def torsjonsvinkel(mast, j, fh):
    """Beregner torsjonsvinkel i kontakttrådhøyde grunnet en eksentrisk horisontal last.

    :param Mast mast: Aktuell mast som beregnes
    :param Kraft j: Last som skal påføres ``mast``
    :param float fh: Kontakttrådhøyde i :math:`m`
    :return: Matrise med rotasjonsbidrag i grader
    :rtype: :class:`numpy.array`
    """

    T = (abs(j.f[1] * -j.e[2]) + abs(j.f[2] * j.e[1])) * 1000
    E = mast.E
    G = mast.G
    I_T = mast.It
    C_w = mast.Cw
    lam = math.sqrt(G * I_T / (E * C_w))
    fh = fh * 1000
    e_x = -j.e[0] * 1000

    D = numpy.zeros((5, 8, 3))

    D[j.type[1], j.type[0], 2] = (180/math.pi) * T/(E*C_w*lam**3) * ( (math.sinh(lam*(e_x-fh))
                                                 - math.sinh(lam*e_x))/math.cosh(lam*e_x) + lam*fh )
    return D


def utliggerbidrag(sys, sidekrefter, etasje):
    """Beregner deformasjonsbidrag fra utligger grunnet sidekrefter i KL.

    :param System sys: Data for ledninger og utligger
    :param list sidekrefter: Liste med :class:`Kraft`-objekter som gir sidekrefter
    :param int etasje: Angir riktig plassering av bidrag i forskyvningsmatrisen
    :return: Matrise med forskyvninger
    :rtype: :class:`numpy.array`
    """

    D = numpy.zeros((5, 8, 3))

    if sys.navn == "20a" or sys.navn == "20b":
        for s in sidekrefter:
            D[etasje, 0, 1] += 20/2500 * s
    elif sys.navn == "25":
        for s in sidekrefter:
            D[etasje, 0, 1] += 4/2500 * s

    return D

