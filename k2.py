# ====================================================================#
# Dette skriptet beregner krefter fra fix- og fastavspente ledninger.
#   (1) Fixpunktmast
#   (2) Fixavspenningsmast
#   (3) Avspenningsmast
#   (4) Master bytter side
# 01.03.17
# ====================================================================#

import numpy
import deformasjon


def _beregn_fastavspent(i, mast, s, a_T, a_T_dot, c, a, hoyde):
    """Definerer én funksjon til å beregne V [N] og M [Nm]
    for å beregne reaksjonskrefter fra differansestrekk og
    tilleggslast når master bytter side av sporet.
    Tar hensyn til ugunstig retning på differansestrekk
    ved sidebytte.
    """

    F_diff = i.differansestrekk * 1000  # Differansestrekk [N]

    # Deklarerer krefter og torsjonsmoment
    M_y, M_z, V_z, D_z = 0, 0, 0, 0
    V_y = F_diff
    T = F_diff * c

    # Tilleggslast dersom mast bytter side av spor.
    if i.master_bytter_side:
        V_y += s
        M_z += V_y * hoyde
        V_z += s * ((a_T + a_T_dot + 2 * c) / a)
        M_y += V_z * hoyde
        # Adderer bidrag fra strekk i fastavspent ledning.
        T += s * c

        # Forskyvning dz [mm] i høyde FH pga. V_z når mast bytter side.
        D_z = deformasjon._beregn_deformasjon_P(mast, V_z, hoyde, i.fh)

    return M_y, V_y, M_z, V_z, T, D_z


def beregn_fixpunkt(sys, i, mast, a_T, a_T_dot, a):
    """Beregner birag til Vz [N], My [Nm]
    og dz [mm] fra fixpunktmast.
    """

    S = 1000 * sys.fixline["Strekk i ledning"]  # [N]
    r = i.radius                                # [m]
    FH = i.fh                                   # [m]
    SH = i.sh                                   # [m]
    # Deklarerer My, Vz, Dz = 0.
    M_y, V_z, D_z = 0, 0, 0

    if r <= 1200:
        # (-) i første ledd for strekkutligger (ytterkurve).
        if i.strekkutligger:
            V_z = S * (-(a / r) + 2 * (a_T / a))
            M_y = V_z * (FH + SH)
        # (+) i første ledd for trykkutligger (innerkurve).
        else:
            V_z = S * ((a / r) + 2 * (a_T_dot / a))
            M_y = V_z * (FH + SH)
    elif r > 1200:
        # Konservativ antagelse om (+) i begge uttrykk.
        if i.strekkutligger:
            V_z = S * ((a / r) + 2 * (a_T / a))
            M_y = V_z * (FH + SH)
        else:
            V_z = S * ((a / r) + 2 * (a_T_dot / a))
            M_y = V_z * (FH + SH)

    # Forskyvning dz [mm] i høyde FH pga. V_z fra fixpunktmast
    D_z = deformasjon._beregn_deformasjon_P(mast, V_z, (FH + SH), FH)

    R = numpy.zeros((15, 9))
    R[2][0] = M_y
    R[2][3] = V_z
    R[2][8] = D_z

    return R


def beregn_fixavspenning(sys, i, mast, a_T, a, B1, B2):
    """Beregner bidrag til Vz [N], My [Nm] og dz [mm] fra
    fixavspenningsmast."""

    S = 1000 * sys.fixline["Strekk i ledning"]  # [N]
    r = i.radius
    FH = i.fh
    SH = i.sh
    # Sum av sideforskyvn. for to påfølgende opphengningspunkter.
    z = a_T + (B1 + B2)
    # Deklarerer My, Vy, Mz, Vz, Dz = 0.
    M_y, M_z, V_z, V_y, N, D_z = 0, 0, 0, 0, 0, 0

    if r <= 1200:
        # Programmet bruker da (+) for strekkutligger (ytterkurve).
        if i.strekkutligger:
            # Sidekraft fra avspenningsbardun.
            V_z += S * (0.5 * (a / r) + (z / a))
            M_y += V_z * (FH + SH)
        else:
            # Sidekraft fra avspenningsbardun.
            V_z += S * (- 0.5 * (a / r) + (z / a))
            M_y += V_z * (FH + SH)
    elif r > 1200:
        # Konservativ antagelse om (+) i begge uttrykk.
        V_z += S * (0.5 * (a / r) + (z / a))
        M_y += V_z * (FH + SH)

    V_y += - S
    M_z += S * (FH + SH)

    if i.avspenningsbardun:
        # Fixavspenningsbardun står normalt på utligger med 45 grader.
        # Dette gir et bidrag til normalkraften N [N].
        N += S

        # Differansen mellom den horisontale kraftkomponenten i bardunen
        # og strekket i KL gir Vy og Mz.
        V_y += S
        M_z += - V_y * (FH + SH)

    # Forskyvning dz [mm] i høyde FH pga. V_z fra fixavspenning
    D_z = deformasjon._beregn_deformasjon_P(mast, V_z, (FH + SH), FH)

    R = numpy.zeros((15, 9))
    R[3][0] = M_y
    R[3][1] = V_y
    R[3][2] = M_z
    R[3][3] = V_z
    R[3][4] = N
    R[3][8] = D_z

    return R


def beregn_avspenning(sys, i, mast, a_T, a, B1, B2):
    """Beregner bidrag til Vz [N], My [Nm] og dz [mm] fra
    avspenningsmast."""

    S = 1000 * (sys.kontakttraad["Strekk i ledning"]
                + sys.baereline["Strekk i ledning"])   # [N]
    r = i.radius
    FH = i.fh
    SH = i.sh
    # Sum av sideforskyvn. for to påfølgende opphengningspunkter.
    z = a_T + (B1 + B2)
    # Deklarerer My, Vy, Mz, Vz, N, Dz = 0.
    M_y, V_y, M_z, V_z, N, D_z = 0, 0, 0, 0, 0, 0

    if r <= 1200:
        # Programmet bruker (+) for strekkutligger (ytterkurve).
        if i.strekkutligger:
            # Sidekraft fra avspenningsbardun.
            V_z = S * (0.5 * (a / r) + (z / a))
            M_y = V_z * FH
        # Programmet bruker (-) for trykkutligger (innerkurve).
        else:
            # Sidekraft fra avspenningsbardun.
            V_z = S * (- 0.5 * (a / r) + (z / a))
            M_y = V_z * (FH + SH)
    elif r > 1200:
        # Konservativ antagelse om (+) i begge uttrykk.
        V_z = S * (0.5 * (a / r) + (z / a))
        M_y = V_z * (FH + SH)

    V_y += - S
    M_z += S * (FH + SH)

    if i.avspenningsbardun:
        # Fixavspenningsbarduner står normalt på utligger med 45 grader.
        # Dette gir et bidrag til normalkraften N [N].
        N += S

        # Differansen mellom den horisontale kraftkomponenten i bardunen
        # og strekket i KL gir Vy og Mz.
        V_y += S
        M_z += - V_y * (FH + SH)

    # Forskyvning dz [mm] i høyde FH pga. V_z fra avspenning
    D_z = deformasjon._beregn_deformasjon_P(mast, V_z, (FH + SH), FH)

    R = numpy.zeros((15, 9))
    R[4][0] = M_y
    R[4][1] = V_y
    R[4][2] = M_z
    R[4][3] = V_z
    R[4][4] = N
    R[4][8] = D_z

    return R


def sidekraft_forbi(sys, i, mast, a_T, a_T_dot, a):
    """Forbigangsledningen påfører masten sidekrefter [N] (og moment)
    [Nm] pga økt avbøyningsvinkel når master bytter side av sporet."""

    # Inngangsparametre
    s_forbi = (sys.forbigangsledning["Max tillatt spenning"] *
               sys.forbigangsledning["Tverrsnitt"])  # [N]
    Hf = i.hf  # [m] Høyde, forbigangsledning
    # Initierer My, Vy, Mz, Vz, N, Dz = 0.
    M_y, V_y, M_z, V_z, T, D_z = 0, 0, 0, 0, 0, 0

    # Master bytter side
    if not i.matefjern_ledn and not i.at_ledn and not i.jord_ledn:
        # Forbigangsledningen henger i toppen av masten.
        c = 0.0  # [m] Ingen momentarm
        # Krefter og forskyvn. pga. mast bytter side av sporet.
        M_y, V_y, M_z, V_z, T, D_z = _beregn_fastavspent(i, mast, s_forbi, a_T, a_T_dot, c, a, Hf)
    else:
        # Forbigangsledningen henger i bakkant av masten.
        c = 0.3  # [m]
        # Tilleggskraft da mast bytter side av sporet.
        M_y, V_y, M_z, V_z, T, D_z = _beregn_fastavspent(i, mast, s_forbi, a_T, a_T_dot, c, a, Hf)

    R = numpy.zeros((15, 9))
    R[5][0] = M_y
    R[5][1] = V_y
    R[5][2] = M_z
    R[5][3] = V_z
    R[5][5] = T
    R[5][8] = D_z

    return R


def sidekraft_retur(sys, i, mast, a_T, a_T_dot, a):
    """Returledninger påfører masten sidekrefter [N] og moment [Nm]
    pga. økt avbøyningsvinkel når masten bytter side av sporet."""

    # Inngangsparametre
    s_retur = (sys.returledning["Max tillatt spenning"] *
               sys.returledning["Tverrsnitt"])  # [N]
    c = -0.5    # [m] Returledningen henger alltid i bakkant av masten
    Hr = i.hr   # [m] Høyde, returledning

    # Krefter og forskyvn. pga. mast bytter side av sporet.
    M_y, V_y, M_z, V_z, T, D_z = _beregn_fastavspent(i, mast, s_retur, a_T, a_T_dot, c, a, Hr)

    R = numpy.zeros((15, 9))
    # 2 returledninger
    R[6][0] = 2 * M_y
    R[6][1] = 2 * V_y
    R[6][2] = 2 * M_z
    R[6][3] = 2 * V_z
    R[6][5] = 2 * T
    R[6][8] = 2 * D_z

    return R


def sidekraft_fiber(sys, i, mast, a_T, a_T_dot, a):
    """Fiberoptisk ledning påfører masten sidekrefter [N] pga økt
    avbøyningsvinkel når masten bytter side av sporet."""

    # Inngangsparametre
    s_fiber = (sys.fiberoptisk["Max tillatt spenning"] *
               sys.fiberoptisk["Tverrsnitt"])  # [N]
    c = -0.3
    Hfi = i.hf  # Samme høyde som forbigangsledning i [m].
    # Initierer My, Vy, Mz, Vz, N, Dz = 0.
    M_y, V_y, M_z, V_z, T, D_z = 0, 0, 0, 0, 0, 0

    # Ingen fiberoptisk ledn. dersom forbigangsledn. er i masten.
    if i.forbigang_ledn:
        M_y, V_y, M_z, V_z, T, D_z = 0, 0, 0, 0, 0, 0
    else:
        # Krefter og forskyvn. pga. mast bytter side av sporet.
        M_y, V_y, M_z, V_z, T, D_z = _beregn_fastavspent(i, mast, s_fiber, a_T, a_T_dot, c, a, Hfi)

    R = numpy.zeros((15, 9))
    R[7][0] = M_y
    R[7][1] = V_y
    R[7][2] = M_z
    R[7][3] = V_z
    R[7][5] = T
    R[7][8] = D_z

    return R


def sidekraft_matefjern(sys, i, mast, a_T, a_T_dot, a):
    """Mate-/fjernledninger påfører masten sidekrefter [N] pga. økt
    avbøyningsvinkel når master bytter side av sporet."""

    # Inngangsprametre
    s_matefjern = (sys.matefjernledning["Max tillatt spenning"] *
                   sys.matefjernledning["Tverrsnitt"])  # [N]
    c = 0  # [m] Mate-/fjernledning henger ALLTID i toppen av masten
    n = i.matefjern_antall  # [1] antall mate-/fjernledninger
    Hfj = i.hfj

    # Tilleggskraft hvis mast bytter side av sporet.
    M_y, V_y, M_z, V_z, T, D_z = _beregn_fastavspent(i, mast, s_matefjern, a_T, a_T_dot, c, a, Hfj)

    R = numpy.zeros((15, 9))
    # n returledninger
    R[8][0] = n * M_y
    R[8][1] = n * V_y
    R[8][2] = n * M_z
    R[8][3] = n * V_z
    R[8][5] = n * T
    R[8][8] = n * D_z

    return R


def sidekraft_at(sys, i, mast, a_T, a_T_dot, a):
    """AT-ledninger påfører masten sidekrefter [kN] pga. økt
    avbøyningsvinkel når master bytter side av sporet."""

    # Inngangsprametre
    s_at = (sys.at_ledning["Max tillatt spenning"] *
            sys.at_ledning["Tverrsnitt"])  # [N]
    c = 0  # [m] AT-ledningen henger ALLTID i toppen av masten.
    Hfj = i.hfj  # [m] Høyde, AT-ledning

    # Tilleggskraft hvis mast bytter side av sporet.
    M_y, V_y, M_z, V_z, T, D_z = _beregn_fastavspent(i, mast, s_at, a_T, a_T_dot, c, a, Hfj)

    R = numpy.zeros((15, 9))
    # 2 AT-ledninger
    R[7][0] = 2 * M_y
    R[7][1] = 2 * V_y
    R[7][2] = 2 * M_z
    R[7][3] = 2 * V_z
    R[7][5] = 2 * T
    R[7][8] = 2 * D_z

    return R


def sidekraft_jord(sys, i, mast, a_T, a_T_dot, a):
    """Jordledningen påfører masten sidekrefter [kN] (og moment)[kNm]
     pga økt avbøyningsvinkel når master bytter side av sporet."""

    # Inngangsparametre
    s_jord = (sys.jordledning["Max tillatt spenning"] *
              sys.jordledning["Tverrsnitt"])  # [N]
    Hj = i.hj  # [m]
    # Deklarerer krefter og momenter
    M_y, V_y, M_z, V_z, T, D_z = 0, 0, 0, 0, 0, 0

    if not i.matefjern_ledn and not i.at_ledn and not i.forbigang_ledn:
        # Jordledningen henger i toppen av masten.
        c = 0.0
        M_y, V_y, M_z, V_z, T, D_z = _beregn_fastavspent(i, mast, s_jord, a_T, a_T_dot, c, a, Hj)
    else:
        # Jordledningen henger i bakkant av masten.
        c = -0.3
        M_y, V_y, M_z, V_z, T, D_z = _beregn_fastavspent(i, mast, s_jord, a_T, a_T_dot, c, a, Hj)

    R = numpy.zeros((15, 9))
    R[7][0] = M_y
    R[7][1] = V_y
    R[7][2] = M_z
    R[7][3] = V_z
    R[7][5] = T
    R[7][8] = D_z

    return R
