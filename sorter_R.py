import numpy


def beregn_reaksjonskrefter(F):
    """Beregner reaksjonskrefter og plasserer bidragene i riktig rad
    og kolonne i R-matrisen."""

    # Initierer R-matrisen for reaksjonskrefter
    R = numpy.zeros((15, 6))

    for j in range(F):
        R[type][0] += (j.f[0] * j.e[2]) + (j.f[2] * -j.e[0])
        R[type][1] += j.f[1]
        R[type][2] += (j.f[0] * -j.e[1]) + (j.f[1] * j.e[0])
        R[type][3] += j.f[2]
        R[type][4] += j.f[0]
        R[type][5] += (j.f[1] * -j.e[2]) + (j.f[2] * j.e[1])

    return R
