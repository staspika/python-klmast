import numpy
import math


def _beregn_Dz_M(mast, M, x, fh):
    """Beregner deformasjon D_z i kontakttrådhøyde som følge av moment
    om  y-aksen med angrepspunkt i høyde x. Dersom FH > x interpoleres
    forskyvningen til høyde FH ved hjelp av tangens til vinkelen theta
    i høyde x ganget med høydedifferansen fh - x.
    """
    E = mast.E              # [N / mm^2] E-modul, stål
    Iy = mast.Iy(mast.h)    # [mm^4]
    M = M * 1000            # Konverterer til [Nmm]
    x = x * 1000            # Konverterer til [mm]
    fh = fh * 1000          # Konverterer til [mm]

    if fh > x:
        theta = (M * x) / (E * Iy)
        D_z = (M * x ** 2) / (2 * E * Iy) + numpy.tan(theta) * (fh - x)
    else:
        D_z = (M * fh ** 2) / (2 * E * Iy)
    return D_z


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
