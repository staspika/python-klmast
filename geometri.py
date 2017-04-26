import math
import lister


def beregn_sikksakk(sys, i):
    """Beregning av KL sikksakk, B1 og B2, samt max forskyvning, e."""

    r = i.radius
    sikksakk, e_max = 0, 0

    # Systemavhengige sikksakk-verdier til input i max masteavstand.
    # struktur i sikksakk-ordbøker under: { "radius": [B1, B2] } i [m]
    # max tillatt utblåsning e_max i [m], bestemmes i indre if-setning.
    if sys.navn == "20a" or sys.navn == "20b":
        sikksakk = lister.sikksakk_20
        if r <= 1000:
            e_max = 0.42
        elif 1000 < r <= 2000:
            e_max = 0.42 + (r - 1000) * ((0.50 - 0.42) / (2000 - 1000))
        elif 2000 < r <= 4000:
            e_max = 0.50 + (r - 2000) * ((0.55 - 0.50) / (4000 - 2000))
        else:
            e_max = 0.55
    elif sys.navn == "25":
        sikksakk = lister.sikksakk_25
        if 180 <= r <= 300:
            e_max = 0.40 + (r - 180) * ((0.43 - 0.40) / (300 - 180))
        elif 300 < r <= 600:
            e_max = 0.43
        elif 600 < r <= 700:
            e_max = 0.43 + (r - 600) * ((0.44 - 0.43) / (700 - 600))
        elif 700 < r <= 900:
            e_max = 0.44
        elif 900 < r <= 1000:
            e_max = 0.44 + (r - 900) * ((0.45 - 0.44) / (1000 - 900))
        elif 1000 < r <= 2000:
            e_max = 0.45
        elif 2000 < r <= 3000:
            e_max = 0.45 + (r - 2000) * ((0.50 - 0.45) / (3000 - 2000))
        else:
            e_max = 0.50
    elif sys.navn == "35":
        sikksakk = lister.sikksakk_35
        e_max = 0.7

    B1 = sikksakk[str(r)][0]
    B2 = sikksakk[str(r)][1]
    return B1, B2, e_max


def beregn_masteavstand(sys, i, B1, B2, e_max, q):
    """Beregning av tillatt masteavstand, a, mht utblåsning av KL."""

    r = i.radius                                        # [m]
    s_kl = sys.kontakttraad["Strekk i ledning"] * 1000  # [N]

    # KL blåser UT fra kurven
    a1 = math.sqrt(((2 * s_kl) / (q - (s_kl / r))) * ((2 * e_max - B1 - B2)
                   + math.sqrt((2 * e_max - B1 - B2) ** 2 - (B1 - B2) ** 2)))

    # KL blåser INN i kurven
    a2 = math.sqrt(((2 * s_kl) / (q + (s_kl / r))) * ((2 * e_max + B1 + B2)
                   + math.sqrt((2 * e_max + B1 + B2) ** 2 - (B1 - B2) ** 2)))

    a = min(a1, a2)

    if a > 60 and sys.navn == "35":
        a = 60
        print(a)

    if a > 65 and (sys.navn == "25" or
                     sys.navn == "20a" or
                     sys.navn == "20b"):
        a = 65
        print(a)

    return a


def beregn_arm(i, B1):
    """Beregner momentarm a_T for strekkutligger og momentarm
    a_T_dot for trykkutligger."""

    r = i.radius
    b = abs(B1)

    # Overhøyde, UE i [m], pga kurveradius i [m]
    ue = lister.overhoyde

    # -----------------------!!NB!!-----------------------------------#
    #
    #   Hva skal velges av (+)0.3  eller (-)0.3 i uttrykkene under ??
    #       (+-)0.3 kan settes inn etter begge uttrykkene under
    #       for å ta hensyn til at bærelineholder kan justeres
    #
    # ----------------------------------------------------------------#

    # Momentarm [m] for strekkutligger.
    a_T = i.sms + i.fh * (ue[str(r)] / 1.435) - b

    # Momentarm [m] for trykkutligger.
    a_T_dot = i.sms - i.fh * (ue[str(r)] / 1.435) + b

    return a_T, a_T_dot

