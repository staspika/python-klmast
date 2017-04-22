import numpy
import math


def _beregn_deformasjon_M(mast, M, x, fh):
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


def _beregn_deformasjon_Pz(mast, P, x, fh):
    """Beregner derformasjonen D_z i kontakttrådhøyde
    pga. punktlast P_z i angrepspunkt x."""

    E = mast.E                    # [N / mm^2] E-modul, stål
    Iy = mast.Iy(mast.h * (2/3))  # [mm^4]
    x = x * 1000                  # [mm]
    fh = fh * 1000                # [mm]

    delta = (P / (2 * E * Iy)) * (x * fh ** 2 - ((1 / 3) * fh ** 3))

    return delta


def _beregn_deformasjon_q(mast, q, x, fh):
    """Beregner deformasjonen D_z i kontakttråhøyde
    pga. vindlast q i angrepspunkt x."""

    E = mast.E                      # [N / mm^2] E-modul, stål
    Iy = mast.Iy(mast.h * (2 / 3))  # [mm^4] i mastens 3.delspunkt
    x = x * 1000                    # [mm]
    fh = fh * 1000                  # [mm]

    delta = ((q * fh ** 2) / (24 * E * Iy)) * (6 * x ** 2 - 4 * x * fh + fh ** 2)

    return delta


def _beregn_deformasjon_Py(mast, P, x, fh):
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


def beregn_deformasjoner(mast, F, i):
    """Beregner deformasjoner og plasserer bidragene
     i riktig rad og kolonne i D-matrisen.
    """

    # Initerer deformasjonsmatrisen, D
    D = numpy.zeros((15, 3))

    for j in F:
        D_0 = numpy.zeros((15, 3))

        # D_y
        D_0[j.type][0] = _beregn_deformasjon_Py(mast, j.f[1], -j.e[0], i.fh) \
                         + _beregn_deformasjon_q(mast, j.q[1], j.b, i.fh)
        # D_z
        D_0[j.type][1] = _beregn_deformasjon_Pz(mast, j.f[2], -j.e[0], i.fh) \
                         + _beregn_deformasjon_q(mast, j.q[2], j.b, i.fh) \
                         + _beregn_deformasjon_M(mast, (j.f[0] * j.e[2] + j.f[2] * -j.e[0]), -j.e[0], i.fh)
        # phi
        D_0[j.type][2] = 0
        if mast.type == "bjelke":
            D_0[j.type][2] = _beregn_phi(mast, (j.f[1] * -j.e[2] + j.f[2] * j.e[1]), -j.e[0], i.fh)

        D += D_0

    return D


