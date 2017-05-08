import numpy
import math


def bjelkeformel_M(mast, j, fh, etasje):
    """Beregner deformasjon D_z i kontakttrådhøyde som følge av moment
    om  y-aksen med angrepspunkt i høyde x. Dersom FH > x interpoleres
    forskyvningen til høyde FH ved hjelp av tangens til vinkelen theta
    i høyde x ganget med høydedifferansen fh - x.
    """
    E = mast.E
    I_y = mast.Iy(2/3 * mast.h)
    I_z = mast.Iz(2/3 * mast.h)
    f_x = j.f[0]
    e_y = j.e[1] * 1000
    e_z = j.e[2] * 1000
    M_y = f_x * e_z
    M_z = f_x * e_y
    x = -j.e[0] * 1000
    fh = fh * 1000

    D = numpy.zeros((2, 8, 6))
    if fh > x:
        theta_y = (M_y * x) / (E * I_y)
        theta_z = (M_z * x) / (E * I_z)
        D[etasje, j.type[0], 1] = (M_y * x ** 2) / (2 * E * I_y) + numpy.tan(theta_y) * (fh - x)
        D[etasje, j.type[0], 0] = (M_z * x ** 2) / (2 * E * I_z) + numpy.tan(theta_z) * (fh - x)
    else:
        D[etasje, j.type[0], 1] = (M_y * fh ** 2) / (2 * E * I_y)
        D[etasje, j.type[0], 0] = (M_z * fh ** 2) / (2 * E * I_z)

    return D


def bjelkeformel_P(mast, j, fh, etasje):
    """Beregner derformasjon i kontakttrådhøyde
    pga. en generell horisontal last
    """

    E = mast.E
    I_y = mast.Iy(2/3 * mast.h)
    I_z = mast.Iz(2/3 * mast.h)
    f_y = j.f[1]
    f_z = j.f[2]
    e_x = -j.e[0] * 1000
    fh *= 1000

    D = numpy.zeros((2, 8, 6))
    D[etasje, j.type[0], 1] = (f_z / (2 * E * I_y)) * (e_x * fh ** 2 - ((1 / 3) * fh ** 3))
    D[etasje, j.type[0], 0] = (f_y / (2 * E * I_z)) * (e_x * fh ** 2 - ((1 / 3) * fh ** 3))

    return D


def bjelkeformel_q(mast, j, fh, etasje):
    """Beregner derformasjon i kontakttrådhøyde
    pga. en generell jevnt fordelt horisontal last
    """

    E = mast.E
    I_y = mast.Iy(2 / 3 * mast.h)  # [mm^4] 2. arealmoment i 2/3 ned fra mastetopp
    I_z = mast.Iz(2 / 3 * mast.h)  # [mm^4] 2. arealmoment i 2/3 ned fra mastetopp
    q_y = j.q[1] / 1000
    q_z = j.q[2] / 1000
    b = j.b * 1000
    fh *= 1000

    D = numpy.zeros((2, 8, 6))

    D[etasje, j.type[0], 1] = ((q_z * fh ** 2) / (24 * E * I_y)) * (6 * b ** 2 - 4 * b * fh + fh ** 2)
    D[etasje, j.type[0], 0] = ((q_y * fh ** 2) / (24 * E * I_z)) * (6 * b ** 2 - 4 * b * fh + fh ** 2)

    return D


def torsjonsvinkel(mast, j, i, etasje):
    """Beregner torsjonsvinkelen phi i radianer i kontakttrådhøyde FH
    for en fast innspent mast pga. tosjonsmoment i en avstand x fra
    fundamentet."""

    T = abs(j.f[1] * -j.e[2]) + abs(j.f[2] * j.e[1])
    E = mast.E
    G = mast.G
    I_T = mast.It
    C_w = mast.Cw
    alpha = math.sqrt((E * C_w) / (G * I_T))
    x = (i.fh + i.sh/2) * 1000
    e_x = -j.e[0] * 1000

    D = numpy.zeros((2, 8, 6))

    D[etasje, j.type[0], 2] = abs(alpha * (T / (G * I_T)) * \
                   ((math.tanh(e_x / alpha) * (math.cosh((x / alpha) - 1)) - math.sinh(x / alpha) + x / alpha)))

    return D

def utliggerbidrag(sys, sidekrefter):
    D = numpy.zeros((2, 8, 6))

    if sys.navn == "20a" or sys.navn == "20b":
        for s in sidekrefter:
            D[1, 0, 0] += 20/2500 * s
    elif sys.navn == "25":
        for s in sidekrefter:
            D[1, 0, 0] += 4/2500 * s

    return D

