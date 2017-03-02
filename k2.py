# ====================================================================#
# Dette skriptet beregner krefter fra fix- og fastavspente ledninger.
#   (1) Fixpunktmast
#   (2) Fixavspenningsmast
#   (3) Avspenningsmast
#   (4) Master bytter side (sidekraft bidrag fra fasavspente ledninger)
# 01.03.17
# ====================================================================#

import numpy
import math


def beregn_fixpunkt(sys, i, mast, a_T, a_T_dot, a):
    """Beregner birag til Vz [kN], My [kNm] og dz [mm] fra
    fixpunktmast."""

    S = sys.fixline["Strekk i ledning"]  # [kN]
    r = i.radius
    E = mast.E
    FH = i.fh
    SH = i.sh
    # Initierer dz_fixpunkt, Vz, My = 0 av hensyn til Python
    V_z = 0
    M_y = 0
    dz_fixpunkt = 0

    if i.fixpunktmast:
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
    if mast.type == "B" or mast.type == "H":
        Iy_steg = mast.Iy
        A_steg = mast.Asteg
        b_13 = mast.b_13
        Iy_13 = 0

        if mast.type == "B":
            Iy_13 = (Iy_steg + A_steg * (b_13 / 2) ** 2) * 2
        elif mast.type == "H":
            Iy_13 = ((Iy_steg + A_steg * (b_13 / 2) ** 2) * 2) * 2

        dz_fixpunkt = (V_z / (2 * E * Iy_13)) * (((FH + SH) * FH ** 2) - (1 / 3) * FH ** 3)
    elif mast.type == "bjelke":
        Iy = mast.Iy

        dz_fixpunkt = (V_z / (2 * E * Iy)) * (((FH + SH) * FH ** 2) - (1 / 3) * FH ** 3)

    R = numpy.zeros((15, 9))
    R[2][3] = V_z
    R[2][0] = M_y
    R[2][8] = dz_fixpunkt

    return R


def beregn_fixavspenning(sys, i, mast, a_T, a, B1, B2):
    """Beregner bidrag til Vz [kN], My [kNm] og dz [mm] fra
    fixavspenningsmast."""

    S = sys.fixline["Strekk i ledning"]  # [kN]
    r = i.radius
    FH = i.fh
    SH = i.sh
    E = mast.E
    # Sum av sideforskyvn. for to påfølgende opphengningspunkter.
    z = a_T + (B1 + B2)
    # Initierer N, Vz, My,dz_fixavspenning = 0 av hensyn til Python.
    N = 0
    V_z = 0
    M_y = 0
    dz_fixavspenning = 0

    if i.fixavspenningsmast:
        if r <= 1200:
            # Programmet bruker da (+) for strekkutligger (ytterkurve).
            if i.strekkutligger:
                # Sidekraft fra avspenningsbardun.
                V_z = S * (0.5 * (a / r) + (z / a))
                M_y = V_z * FH
            else:
                # Sidekraft fra avspenningsbardun.
                V_z = S * (- 0.5 * (a / r) + (z / a))
                M_y = V_z * FH
        elif r > 1200:
            # Konservativ antagelse om (+) i begge uttrykk.
            V_z = S * (0.5 * (a / r) + (z / a))
            M_y = V_z * FH

    # Fixavspenningsbardun står normalt på utligger med 45 grader.
    # Dette gir et bidrag til normalkraften N [kN].
    N = (math.sqrt(2) / 2) * S

    # Forskyvning dz [mm] i høyde FH pga. V_z fra fixavspenning
    if mast.type == "B" or mast.type == "H":
        Iy_steg = mast.Iy
        A_steg = mast.Asteg
        b_13 = mast.b_13
        Iy_13 = 0

        if mast.type == "B":
            Iy_13 = (Iy_steg + A_steg * (b_13 / 2) ** 2) * 2
        elif mast.type == "H":
            Iy_13 = ((Iy_steg + A_steg * (b_13 / 2) ** 2) * 2) * 2

        dz_fixavspenning = (V_z / (2 * E * Iy_13)) * (((FH + SH) * FH ** 2) - (1 / 3) * FH ** 3)
    elif mast.type == "bjelke":
        Iy = mast.Iy

        dz_fixavspenning = (V_z / (2 * E * Iy)) * (((FH + SH) * FH ** 2) - (1 / 3) * FH ** 3)

    R = numpy.zeros((15, 9))
    R[3][3] = V_z
    R[3][0] = M_y
    R[3][4] = N
    R[3][8] = dz_fixavspenning

    return R


def beregn_avspenning(sys, i, mast, a_T, a, B1, B2):
    """Beregner bidrag til Vz [kN], My [kNm] og dz [mm] fra
    avspenningsmast."""

    S = sys.kontakttraad["Strekk i ledning"]  # [kN]
    r = i.radius
    E = mast.E
    FH = i.fh
    SH = i.sh
    # Sum av sideforskyvn. for to påfølgende opphengningspunkter.
    z = a_T + (B1 + B2)
    # Initierer N, Vz, My, dz_fixavspenning = 0 av hensyn til Python.
    N = 0
    V_z = 0
    M_y = 0
    dz_avspenning = 0

    if i.avspenningsmast:
        if r <= 1200:
            # Programmet bruker da (+) for strekkutligger (ytterkurve).
            if i.strekkutligger:
                # Sidekraft fra avspenningsbardun.
                V_z = S * (0.5 * (a / r) + (z / a))
                M_y = V_z * FH
            else:
                # Sidekraft fra avspenningsbardun.
                V_z = S * (- 0.5 * (a / r) + (z / a))
                M_y = V_z * (FH + SH)
        elif r > 1200:
            # Konservativ antagelse om (+) i begge uttrykk.
            V_z = S * (0.5 * (a / r) + (z / a))
            M_y = V_z * (FH + SH)

    # Avspenningsbardun står normalt på utligger med 45 grader.
    # Dette gir et bidrag til normalkraften, N.
    N = (math.sqrt(2) / 2) * S

    # Forskyvning dz [mm] i høyde FH pga. V_z fra avspenning
    if mast.type == "B" or mast.type == "H":
        Iy_steg = mast.Iy
        A_steg = mast.Asteg
        b_13 = mast.b_13
        Iy_13 = 0

        if mast.type == "B":
            Iy_13 = (Iy_steg + A_steg * (b_13 / 2) ** 2) * 2
        elif mast.type == "H":
            Iy_13 = ((Iy_steg + A_steg * (b_13 / 2) ** 2) * 2) * 2

        dz_avspenning = (V_z / (2 * E * Iy_13)) * (((FH + SH) * FH ** 2) - (1 / 3) * FH ** 3)
    elif mast.type == "bjelke":
        Iy = mast.Iy

        dz_avspenning = (V_z / (2 * E * Iy)) * (((FH + SH) * FH ** 2) - (1 / 3) * FH ** 3)

    R = numpy.zeros((15, 9))
    R[4][3] = V_z
    R[4][0] = M_y
    R[4][4] = N
    R[4][8] = dz_avspenning

    return R


def sidekraft_forbi(sys, i, mast, a_T, a_T_dot, a):
    """Forbigangsledningen påfører masten sidekrefter [kN] (og moment)
    [kNm] pga økt avbøyningsvinkel når master bytter side av sporet."""

    # Inngangsparametre
    s_forbi = (sys.forbigangsledning["Max tillatt spenning"] *
               sys.forbigangsledning["Tverrsnitt"]) / 1000  # [kN]
    FH = i.fh
    Hf = i.hf  # Høyde av forbigangsledning [m].
    E = mast.E
    # Initierer dz_forbi, Vz, My, T = 0 av hensyn til Python.
    V_z = 0
    M_y = 0
    T = 0
    dz_forbi = 0

    if i.master_bytter_side and i.forbigang_ledn:
        if not i.matefjern_ledn or not i.at_ledn or not i.jord_ledn:
            # Forbigangsledningen henger i toppen av masten.
            c = 0.0  # ingen momentarm
            # Tilleggskraft fra fastavspente ledninger pga. sidebytte
            V_z = s_forbi * ((a_T + a_T_dot + 2 * c) / a)
            M_y = V_z * Hf
        else:
            # Forbigangsledningen henger i bakkant av masten.
            c = 0.3  # [m]
            # Tilleggskraft da mast bytter side av sporet.
            V_z = s_forbi * ((a_T + a_T_dot + 2 * c) / a)
            M_y = V_z * Hf
            T = s_forbi * c

    # Forskyvning dz [mm] i høyde FH pga. V_z når mast bytter side.
    if mast.type == "B" or mast.type == "H":
        Iy_steg = mast.Iy
        A_steg = mast.Asteg
        b_13 = mast.b_13
        Iy_13 = 0

        if mast.type == "B":
            Iy_13 = (Iy_steg + A_steg * (b_13 / 2) ** 2) * 2
        elif mast.type == "H":
            Iy_13 = ((Iy_steg + A_steg * (b_13 / 2) ** 2) * 2) * 2

        dz_forbi = (V_z / (2 * E * Iy_13)) * ((Hf * FH ** 2) - (1 / 3) * FH ** 3)
    elif mast.type == "bjelke":
        Iy = mast.Iy

        dz_forbi= (V_z / (2 * E * Iy)) * ((Hf * FH ** 2) - (1 / 3) * FH ** 3)

    R = numpy.zeros((15, 9))
    R[5][3] = V_z
    R[5][0] = M_y
    R[5][5] = T
    R[5][8] = dz_forbi

    return R


def sidekraft_retur(sys, i, mast, a_T, a_T_dot, a):
    """Returledningen påfører masten sidekrefter [kN] og moment [kNm]
    pga. økt avbøyningsvinkel når masten bytter side av sporet."""

    # Inngangsparametre
    s_retur = (sys.returledning["Max tillatt spenning"] *
               sys.returledning["Tverrsnitt"]) / 1000  # [kN]
    c = 0.5    # Returledningen henger alltid i bakkant av masten [m].
    Hr = i.hr  # Høyde av returledning [m]
    FH = i.fh
    E = mast.E
    # Initierer Vz, My, T og dz_retur = 0 av hensyn til Python
    V_z = 0
    M_y = 0
    T = 0
    dz_retur = 0

    if i.master_bytter_side and i.retur_ledn:
        # Tilleggskraft da mast bytter side av sporet.
        V_z = s_retur * ((a_T + a_T_dot + 2 * c) / a)
        M_y = V_z * Hr
        T = s_retur * c

    # Forskyvning dz [mm] i høyde FH pga. V_z når mast bytter side.
    if mast.type == "B" or mast.type == "H":
        Iy_steg = mast.Iy
        A_steg = mast.Asteg
        b_13 = mast.b_13
        Iy_13 = 0

        if mast.type == "B":
            Iy_13 = (Iy_steg + A_steg * (b_13 / 2) ** 2) * 2
        elif mast.type == "H":
            Iy_13 = ((Iy_steg + A_steg * (b_13 / 2) ** 2) * 2) * 2

        dz_forbi = (V_z / (2 * E * Iy_13)) * ((Hr * FH ** 2) - (1 / 3) * FH ** 3)
    elif mast.type == "bjelke":
        Iy = mast.Iy

        dz_forbi = (V_z / (2 * E * Iy)) * ((Hr * FH ** 2) - (1 / 3) * FH ** 3)

    R = numpy.zeros((15, 9))
    R[6][3] = V_z
    R[6][0] = M_y
    R[6][5] = T
    R[6][8] = dz_retur

    return R


def sidekraft_fiber(sys, i, mast, a_T, a_T_dot, a):
    """Fiberoptisk ledning påfører masten sidekrefter [kN] pga økt
    avbøyningsvinkel når masten bytter side av sporet."""

    # Inngangsparametre
    s_fiber = (sys.fiberoptisk["Max tillatt spenning"] *
               sys.fiberoptisk["Tverrsnitt"]) / 1000  # [kN]
    c = 0.3
    Hfi = 5.0  # ????????? Hva skal denne  høyden være ???????????
    FH = i.fh
    E = mast.E
    # Initierer Vz, My, T og dz_fiber = 0 av hensyn til Python.
    V_z = 0
    M_y = 0
    T = 0
    dz_fiber = 0

    if i.master_bytter_side and i.fiberoptisk_ledn:
        # Ingen fiberoptisk ledn dersom forbigangsledning er i masten.
        if i.forbigang_ledn:
            V_z = 0
            M_y = 0
        else:
            V_z = s_fiber * ((a_T + a_T_dot + 2 * c) / a)
            M_y = V_z * Hfi
            T = s_fiber * c

    # Forskyvning dz [mm] i høyde FH pga. V_z når mast bytter side.
    if mast.type == "B" or mast.type == "H":
        Iy_steg = mast.Iy
        A_steg = mast.Asteg
        b_13 = mast.b_13
        Iy_13 = 0

        if mast.type == "B":
            Iy_13 = (Iy_steg + A_steg * (b_13 / 2) ** 2) * 2
        elif mast.type == "H":
            Iy_13 = ((Iy_steg + A_steg * (b_13 / 2) ** 2) * 2) * 2

        dz_fiber = (V_z / (2 * E * Iy_13)) * ((Hfi * FH ** 2) - (1 / 3) * FH ** 3)
    elif mast.type == "bjelke":
        Iy = mast.Iy

        dz_fiber = (V_z / (2 * E * Iy)) * ((Hfi * FH ** 2) - (1 / 3) * FH ** 3)

    R = numpy.zeros((15, 9))
    R[7][3] = V_z
    R[7][0] = M_y
    R[7][5] = T
    R[7][8] = dz_fiber

    return R


def sidekraft_matefjern(sys, i, mast, a_T, a_T_dot, a):
    """Mate-/fjernledninger påfører masten sidekrefter [kN] pga. økt
    avbøyningsvinkel når master bytter side av sporet."""

    # Inngangsprametre
    s_matefjern = (sys.matefjernledning["Max tillatt spenning"] *
                   sys.matefjernledning["Tverrsnitt"]) / 1000  # [kN]
    c = 0  # Mate-/fjernledning henger alltid i toppen av masten.
    Hfj = i.hfj
    FH = i.fh
    E = mast.E
    # Initierer Vz, dz_matefjern = 0 av hensyn til Python
    V_z = 0
    dz_matefjern = 0

    if i.master_bytter_side and i.matefjern_ledn:
        # Tilleggskraft hvis mast bytter side av sporet.
        n = i.matefjern_antall
        V_z = n * s_matefjern * ((a_T + a_T_dot + 2 * c) / a)

    # Forskyvning dz [mm] i høyde FH pga. V_z når mast bytter side.
    if mast.type == "B" or mast.type == "H":
        Iy_steg = mast.Iy
        A_steg = mast.Asteg
        b_13 = mast.b_13
        Iy_13 = 0

        if mast.type == "B":
            Iy_13 = (Iy_steg + A_steg * (b_13 / 2) ** 2) * 2
        elif mast.type == "H":
            Iy_13 = ((Iy_steg + A_steg * (b_13 / 2) ** 2) * 2) * 2

        dz_matefjern = (V_z / (2 * E * Iy_13)) * ((Hfj * FH ** 2) - (1 / 3) * FH ** 3)
    elif mast.type == "bjelke":
        Iy = mast.Iy

        dz_matefjern = (V_z / (2 * E * Iy)) * ((Hfj * FH ** 2) - (1 / 3) * FH ** 3)

    R = numpy.zeros((15, 9))
    R[8][3] = V_z
    R[8][8] = dz_matefjern

    return R


def sidekraft_at(sys, i, mast, a_T, a_T_dot, a):
    """AT - ledninger påfører masten sidekrefter [kN] pga. økt
    avbøyningsvinkel når master bytter side av sporet."""

    # Inngangsprametre
    s_at = (sys.at_ledning["Max tillatt spenning"] *
            sys.at_ledning["Tverrsnitt"]) / 1000  # [kN]
    c = 0  # AT-ledningen henger alltid i toppen [m].
    Hfj = i.hfj
    FH = i.fh
    E = mast.E
    # Initerer Vz, dz_at = 0 av hensyn til Python
    V_z = 0
    dz_at = 0

    if i.master_bytter_side:
        # Tilleggskraft hvis mast bytter side av sporet.
        V_z = s_at * ((a_T + a_T_dot + 2 * c) / a)

    # Forskyvning dz [mm] i høyde FH pga. V_z når mast bytter side.
    if mast.type == "B" or mast.type == "H":
        Iy_steg = mast.Iy
        A_steg = mast.Asteg
        b_13 = mast.b_13
        Iy_13 = 0

        if mast.type == "B":
            Iy_13 = (Iy_steg + A_steg * (b_13 / 2) ** 2) * 2
        elif mast.type == "H":
            Iy_13 = ((Iy_steg + A_steg * (b_13 / 2) ** 2) * 2) * 2

        dz_at = (V_z / (2 * E * Iy_13)) * ((Hfj * FH ** 2) - (1 / 3) * FH ** 3)
    elif mast.type == "bjelke":
        Iy = mast.Iy

        dz_at = (V_z / (2 * E * Iy)) * ((Hfj * FH ** 2) - (1 / 3) * FH ** 3)

    R = numpy.zeros((15, 9))
    R[9][3] = V_z
    R[9][8] = dz_at

    return R


def sidekraft_jord(sys, i, mast, a_T, a_T_dot, a):
    """Jordledningen påfører masten sidekrefter [kN] (og moment)[kNm]
     pga økt avbøyningsvinkel når master bytter side av sporet."""

    # Inngangsparametre
    s_jord = (sys.jordledning["Max tillatt spenning"] *
              sys.jordledning["Tverrsnitt"]) / 1000  # [kN]
    Hj = i.hj
    FH = i.fh
    E = mast.E
    # Initerer Vz, My, T, dz_jord = 0 av hensyn til Python
    V_z = 0
    M_y = 0
    T = 0
    dz_jord = 0

    if i.master_bytter_side and i.jord_ledn:
        if not i.matefjern_ledn or not i.at_ledn or not i.forbigang_ledn:
            # Jordledningen henger i toppen av masten.
            c = 0.0
            V_z = s_jord * ((a_T + a_T_dot + 2 * c) / a)
            M_y = 0
            T = 0
        else:
            # Jordledningen henger i bakkant av masten.
            c = 0.3
            V_z = s_jord * ((a_T + a_T_dot + 2 * c) / a)
            M_y = V_z * Hj
            T = s_jord * c

    # Forskyvning dz [mm] i høyde FH pga. V_z når mast bytter side.
    if mast.type == "B" or mast.type == "H":
        Iy_steg = mast.Iy
        A_steg = mast.Asteg
        b_13 = mast.b_13
        Iy_13 = 0

        if mast.type == "B":
            Iy_13 = (Iy_steg + A_steg * (b_13 / 2) ** 2) * 2
        elif mast.type == "H":
            Iy_13 = ((Iy_steg + A_steg * (b_13 / 2) ** 2) * 2) * 2

        dz_jord = (V_z / (2 * E * Iy_13)) * ((Hj * FH ** 2) - (1 / 3) * FH ** 3)
    elif mast.type == "bjelke":
        Iy = mast.Iy

        dz_jord = (V_z / (2 * E * Iy)) * ((Hj * FH ** 2) - (1 / 3) * FH ** 3)

    R = numpy.zeros((15, 9))
    R[10][3] = V_z
    R[10][0] = M_y
    R[10][5] = T
    R[10][8] = dz_jord

    return R
