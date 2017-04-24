import numpy
import math


def bjelkeformel_M(mast, j, fh):
    """Beregner deformasjon D_z i kontakttrådhøyde som følge av moment
    om  y-aksen med angrepspunkt i høyde x. Dersom FH > x interpoleres
    forskyvningen til høyde FH ved hjelp av tangens til vinkelen theta
    i høyde x ganget med høydedifferansen fh - x.
    """
    E = mast.E
    I_y = mast.Iy(mast.h)
    I_z = mast.Iz(mast.h)
    f_x = j.f[0]
    e_y = j.e[1] * 1000
    e_z = j.e[2] * 1000
    M_y = f_x * e_z
    M_z = f_x * e_y
    x = -j.e[0] * 1000
    fh = fh * 1000

    D = numpy.zeros((15, 3))
    if fh > x:
        theta_y = (M_y * x) / (E * I_y)
        theta_z = (M_z * x) / (E * I_z)
        D[j.type][1] = (M_y * x ** 2) / (2 * E * I_y) + numpy.tan(theta_y) * (fh - x)
        D[j.type][0] = (M_z * x ** 2) / (2 * E * I_z) + numpy.tan(theta_z) * (fh - x)
    else:
        D[j.type][1] = (M_y * fh ** 2) / (2 * E * I_y)
        D[j.type][0] = (M_z * fh ** 2) / (2 * E * I_z)

    return D


def _beregn_Dz_Pz(mast, P, x, fh):
    """Beregner derformasjonen D_z i kontakttrådhøyde
    pga. punktlast P_z i angrepspunkt x."""

    E = mast.E                    # [N / mm^2] E-modul, stål
    Iy = mast.Iy(mast.h * (2/3))  # [mm^4]
    x = x * 1000                  # [mm]
    fh = fh * 1000                # [mm]

    delta = (P / (2 * E * Iy)) * (x * fh ** 2 - ((1 / 3) * fh ** 3))

    return delta


def _beregn_Dz_q(mast, q, x, fh):
    """Beregner deformasjonen D_z i kontakttråhøyde
    pga. vindlast q i angrepspunkt x."""

    E = mast.E                      # [N / mm^2] E-modul, stål
    Iy = mast.Iy(mast.h * (2 / 3))  # [mm^4] i mastens 3.delspunkt
    x = x * 1000                    # [mm]
    fh = fh * 1000                  # [mm]

    delta = ((q * fh ** 2) / (24 * E * Iy)) * (6 * x ** 2 - 4 * x * fh + fh ** 2)

    return delta


def _beregn_Dy_q(mast, q, x, fh):
    """Beregner deformasjonen D_y i kontakttråhøyde fh
    pga. vindlast q i angrepspunkt x."""

    E = mast.E                      # [N / mm^2] E-modul, stål
    Iz = mast.Iz(mast.h * (2 / 3))  # [mm^4] i mastens 3.delspunkt
    x = x * 1000                    # [mm]
    fh = fh * 1000                  # [mm]

    delta = ((q * fh ** 2) / (24 * E * Iz)) * (6 * x ** 2 - 4 * x * fh + fh ** 2)

    return delta


def _beregn_Dy_Py(mast, P, x, fh):
    """Beregner derformasjonen D_y i kontakttrådhøyde
    pga. punktlast P_y i angrepspunkt x."""

    E = mast.E                      # [N / mm^2] E-modul, stål
    Iz = mast.Iz(mast.h * (2 / 3))  # [mm^4]
    x = x * 1000                    # [mm]
    fh = fh * 1000                  # [mm]

    delta = (P / (2 * E * Iz)) * (x * fh ** 2 - ((1 / 3) * fh ** 3))

    return delta


def _beregn_phi(mast, T, x, fh):
    """Beregner torsjonsvinkelen phi i radianer i kontakttrådhøyde FH
    for en fast innspent mast pga. tosjonsmoment i en avstand x fra
    fundamentet."""

    E = mast.E
    G = mast.G
    I_T = mast.It
    C_w = mast.Cw
    K = math.sqrt((E * C_w) / (G * I_T))

    phi = K * (T / (G * I_T)) * (math.tanh(x / K) * (math.cosh((fh / K) - 1)) - math.sinh(fh / K) + fh / K)

    return phi
