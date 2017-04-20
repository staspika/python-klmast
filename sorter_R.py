import numpy


def beregn_reaksjonskrefter(F):
    """Beregner reaksjonskrefter og plasserer bidragene i riktig rad
    og kolonne i R-matrisen."""

    # Initierer R-matrisen for reaksjonskrefter
    R = numpy.zeros((15, 6))

    for j in range(F):
        f = j.f
        if numpy.count_nonzero(j.q) is not 0:
            f = [j.q[0] * j.b, j.q[1] * j.b, j.q[2] * j.b]

        # Sorterer bidrag til reaksjonskrefter
        R[type][0] += (f[0] * j.e[2]) + (f[2] * -j.e[0])
        R[type][1] += f[1]
        R[type][2] += (f[0] * -j.e[1]) + (f[1] * j.e[0])
        R[type][3] += f[2]
        R[type][4] += f[0]
        R[type][5] += (f[1] * -j.e[2]) + (f[2] * j.e[1])

    return R
