import math

def beregn_sikksakk(sys, i):
    """Beregning av KL sikksakk, B1 og B2, samt max forskyvning, e."""

    r = i.radius

    # Systemavhengige sikksakk-verdier til input i max masteavstand.
    # struktur i sikksakk-ordbøker under: { "radius": [B1, B2] } i [m]
    # max tillatt overhøyde, overhøyde UE [m], bestemmes i indre if-setning.
    if sys.navn == "20a" or sys.navn == "20b":
        sikksakk = {"180": [-0.30, -0.30], "250": [-0.30, -0.30],
                    "300": [-0.30, -0.30], "400": [-0.30, -0.30],
                    "500": [-0.30, -0.30], "600": [-0.30, -0.30],
                    "700": [-0.30, -0.30], "800": [-0.30, -0.30],
                    "900": [-0.30, -0.30], "1000": [-0.30, -0.30],
                    "1100": [-0.30, -0.30], "1200": [-0.30, -0.30],
                    "1300": [-0.30, -0.30], "1400": [-0.30, -0.25],
                    "1500": [-0.30, -0.20], "1600": [-0.30, -0.20],
                    "1800": [-0.30, -0.15], "2000": [-0.30, -0.15],
                    "2400": [-0.30, -0.10], "2700": [-0.30, -0.10],
                    "3000": [-0.30, -0.10], "3500": [-0.30, -0.10],
                    "4000": [-0.30, -0.20], "5000": [-0.30, 0.30],
                    "7000": [-0.30, 0.30], "10000": [-0.30, 0.30],
                    "20000": [-0.30, 0.30], "10000000": [-0.30, 0.30]}
        if r <= 1000:
            UE = 0.42
        elif 1000 < r <= 2000:
            UE = 0.42 + (r - 1000) * ((0.50 - 0.42) / (2000 - 1000))
        elif 2000 < r <= 4000:
            UE = 0.50 + (r - 2000) * ((0.55 - 0.50) / (4000 - 2000))
        else:
            UE = 0.55
    elif sys.navn == "25":
        sikksakk = {"180": [-0.30, -0.30], "250": [-0.30, -0.30],
                    "300": [-0.30, -0.30], "400": [-0.30, -0.30],
                    "500": [-0.30, -0.30], "600": [-0.30, -0.30],
                    "700": [-0.30, -0.30], "800": [-0.30, -0.30],
                    "900": [-0.30, -0.30], "1000": [-0.30, -0.30],
                    "1100": [-0.30, -0.30], "1200": [-0.30, -0.30],
                    "1300": [-0.30, -0.30], "1400": [-0.30, -0.30],
                    "1500": [-0.30, -0.30], "1600": [-0.30, -0.30],
                    "1800": [-0.30, -0.29], "2000": [-0.30, -0.22],
                    "2400": [-0.30, -0.16], "2700": [-0.30, -0.13],
                    "3000": [-0.30, -0.13], "3500": [-0.30, -0.07],
                    "4000": [-0.30, -0.02], "5000": [-0.30, 0.28],
                    "7000": [-0.30, 0.19], "10000": [-0.30, 0.22],
                    "20000": [-0.30, 0.25], "10000000": [-0.30, 0.30]}
        if 180 <= r <= 300:
            UE = 0.40 + (r - 180) * ((0.43 - 0.40) / (300 - 180))
        elif 300 < r <= 600:
            UE = 0.43
        elif 600 < r <= 700:
            UE = 0.43  + (r - 600) * ((0.44 - 0.43) / (700 - 600))
        elif 700 < r <= 900:
            UE = 0.44
        elif 900 < r <= 1000:
            UE = 0.44 + (r - 900) * ((0.45 - 0.44) / (1000 - 900))
        elif 1000 < r <= 2000:
            UE = 0.45
        elif 2000 < r <= 3000:
            UE = 0.45  + (r - 2000) * ((0.50 - 0.45) / (3000 - 2000))
        else:
            UE = 0.50
    elif sys.navn == "35":
        sikksakk = {"180": [-0.4, -0.4], "250": [-0.4, -0.4],
                    "300": [-0.4, -0.4], "400": [-0.4, -0.4],
                    "500": [-0.4, -0.4], "600": [-0.4, -0.4],
                    "700": [-0.4, -0.4], "800": [-0.4, -0.4],
                    "900": [-0.4, -0.4], "1000": [-0.4, -0.4],
                    "1100": [-0.4, -0.4], "1200": [-0.4, -0.4],
                    "1300": [-0.4, -0.4], "1400": [-0.4, -0.4],
                    "1500": [-0.2, -0.2], "1600": [-0.2, -0.2],
                    "1800": [-0.2, -0.2], "2000": [-0.2, -0.2],
                    "2400": [-0.2, -0.2], "2700": [-0.2, -0.2],
                    "3000": [-0.2, -0.2], "3500": [-0.2, -0.2],
                    "4000": [-0.2, -0.2], "5000": [-0.4, 0.4],
                    "7000": [-0.4, 0.4], "10000": [-0.4, 0.4],
                    "20000": [-0.4, 0.4], "10000000": [-0.4, 0.4]}
        UE = 0.7

    B1 = sikksakk[str(r)][0]
    B2 = sikksakk[str(r)][1]
    return B1, B2, UE


def beregn_masteavstand(sys, i, B1, B2, q):
    """Beregning av tillatt masteavstand, a, mht utblåsning av KL."""

    e_per = 0.63                                        # [m]
    r = i.radius                                        # [m]
    s_kl = sys.kontakttraad["Strekk i ledning"] * 1000  # [N]

    # KL blåser UT fra kurven
    a1 = math.sqrt(((2 * s_kl) / (q - (s_kl / r))) * ((2 * e_per - B1 - B2)
                   + math.sqrt((2 * e_per - B1 - B2) ** 2 - (B1 - B2) ** 2)))

    # KL blåser INN i kurven
    a2 = math.sqrt(((2 * s_kl) / (q + (s_kl / r))) * ((2 * e_per + B1 + B2)
                   + math.sqrt((2 * e_per + B1 + B2) ** 2 - (B1 - B2) ** 2)))

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
    """Beregner momentarm a_T for strekk- eller trykkutligger."""

    r = i.radius
    b = abs(B1)
    a_T, a_T_dot = 0, 0  # Initialiserer momentarmvariabler

    # Overhøyde, UE i [m], pga kurveradius i [m]
    ue = {"180": 0.150, "250": 0.150, "300": 0.150, "400": 0.150,
          "500": 0.150, "600": 0.150, "700": 0.150, "800": 0.150,
          "900": 0.150, "1000": 0.135, "1100": 0.120, "1200": 0.120,
          "1300": 0.115, "1400": 0.110, "1500": 0.110, "1600": 0.110,
          "1800": 0.110, "2000": 0.100, "2400": 0.090, "2700": 0.080,
          "3000": 0.070, "3500": 0.060, "4000": 0.050, "5000": 0.040,
          "7000": 0.020, "10000": 0, "20000": 0, "10000000": 0}

    # -----------------------!!NB!!-----------------------------------#
    #
    #   Hva skal velges av (+)0.3  eller (-)0.3 i uttrykkene under ??
    #
    # ----------------------------------------------------------------#
    if i.strekkutligger:
        a_T = i.sms + i.fh * (ue[str(r)] / 1435) - b + 0.3

    # trykkutligger hvis ikke strekkutligger
    if not i.strekkutligger:
        a_T_dot = i.sms - i.fh * (ue[str(r)] / 1435) + b + 0.3

    return a_T, a_T_dot




def sjekk_fh(i):
    """Kontrollerer FH: Høyde av kontakttråd."""
    if i.FH > 6.5 or i.FH < 4.8:
        print("Kontakttrådhøyden er ikke gyldig.")
        return False
    print("FH er OK.")
    return True


def sjekk_sh(i):
    """Kontrollerer SH: Systemhøyden."""
    if i.SH > 2.0 or i.SH < 0.2:
        print("Systemhøyden er ikke gyldig.")
        return False
    print("SH er OK.")
    return True


def sjekk_e(i):
    """Kontrollerer e: Avstanden SOK - toppmaal fundament."""
    if i.e > 3.0 or i.e < -(i.FH - 0.6):
        print("Ugyldig avstand til toppmaal fundament.")
        return False
    print("e er OK.")
    return True


def sjekk_sms(i):
    """Kontrollerer SMS: Avstanden s_mast - s_spor."""
    if i.SMS > 6.0 or i.SMS < 2.0:
        print("SMS avstanden er ugyldig.")
        return False
    print("SMS er OK.")
    return True


def valider_ledn(i):
    """Validerer gyldige kombinasjoner av ledninger."""

    if i.at_ledn and i.matefjern_ledn:
        print("Matefjern- OG AT-ledning kan ikke henges opp samtidig.")
        return False
    elif i.at_ledn and i.forbigang_ledn:
        print("Forbigang- OG AT-ledning kan ikke henges opp samtidig.")
        return False
    elif i.at_ledn and i.retur_ledn:
        print("Retur- OG AT-ledning kan ikke henges opp samtidig.")
        return False
    elif i.forbigang_ledn and i.fiberoptisk_ledn:
        print("Forbigangs- OG fiberoptisk ledning kan ikke henges opp samtidig.")
        return False
    else:
        print("Kombinasjonen av ledninger er OK.")
        return True


def hoyde_mast(i):
    """Høyde av KL-mast målt fra toppmaal fundament."""

    # Dersom mate-/fjern, AT- eller jordledning henger i masten.
    if i.matefjern_ledn or i.at_ledn or i.jord_ledn:
        H = i.FH + i.SH + i.e + 2.5
        if sjekk_h(H):
            return H
    # Dersom forbigangs- OG returledning henger i masten.
    elif i.forbigang_ledn and i.retur_ledn:
        H = i.FH + i.SH + i.e + 2.0
        if sjekk_h(H):
            return H
    # Hvis, og bare hvis, returledning henger alene i masten.
    elif i.retur_ledn and (not i.matefjern_ledn
                           and not i.at_ledn
                           and not i.forbigang_ledn
                           and not i.jord_ledn
                           and not i.fiberoptisk_ledn):
        H = i.FH + i.SH + i.e + 0.7
        if sjekk_h(H):
            return H
    # Mastehøyde dersom ingen fastavspente ledninger i masten.
    else:
        H = i.FH + i.SH + i.e + 0.7
        if sjekk_h(H):
            return H


def sjekk_h(H):
    """Kontrollerer S: Høyde av KL-mast."""
    if (H - 1.5) < H < (H + 5.0):
        return True
    return False


# ===============================!!NB!!=======================================#
#
#               sjekk ut formel for Hfj: les tilbakemelding fra Mirza !!
#
# ============================================================================#
def hoyde_fjernledn(i):
    """Høyde av mate-/fjern- eller AT-ledning målt fra SOK."""

    # Mate-/fjern- eller AT- og forbigangsledning i masten.
    if i.matefjern_ledn or (i.at_ledn and i.forbigang_ledn):
        return i.H - i.e + 0.5
    # Mate-/fjern- eller AT-ledning alene i masten
    elif (i.matefjern_ledn or i.at_ledn) and not i.forbigang_ledn:
        return i.FH + i.SH + 3.0
    else:
        print("Jordledningen henger i toppen av masten.")
        return False


def sjekk_atledn(i, Hfj):
    """AT-ledningen kan ikke henge lavere enn Hfj = FH + SH + 3.3m."""
    if i.at_ledn:
        if Hfj < (i.FH + i.SH + 3.3):
            print("Kritisk liten avstand mellom AT-ledning og KL-anlegget")
            return False


def sjekk_hfj(i, Hfj):
    """Kontrollerer Hfj: Høyde av forbigangsledning."""
    if Hfj > (i.max_hoyde + 2.0):
        print("Mate-/fjern- eller AT-ledningen henger for høyt.")
        return False
    elif Hfj < (i.h - i.e):
        print("Mate-/fjern- eller AT-ledningen henger for lavt.")
        return False
    else:
        print("Hfj er OK.")
        return True


def hoyde_forbigangledn(i):
    """Høyde, samt kontroll av høyde, for forbigangsledning målt fra SOK."""

    # Forbigangsledning alene i masten => Hf i toppen.
    if i.forbigang_ledn and (not i.matefjern_ledn
                             and not i.at_ledn
                             and not i.jord_ledn):
        print("Forbigangsledningen henger i toppen av masten.")
        hf = i.FH + i.SH + 2.5
        if hf > (i.max_hoyde + 2.0):
            return False
        elif hf < (i.h - i.e):
            return False
        else:
            return i.FH + i.SH + 2.5
    # Mate-/fjern- i tillegg til forbigangsledning i masten, Hf i topp.
    elif i.forbigang_ledn and (i.matefjern_ledn or i.at_ledn):
        hf = i.h - i.e + 0.5
        if hf > (i.max_hoyde + 2.0):
            return False
        elif hf < (i.h - i.e):
            return False
        else:
            return True
    # Mate-/fjern, AT- eller jordledning i masten => Hf i bakkant.
    else:
        print("Forbigangsledningen henger 0.5 m over returledningen.")
        hf = i.FH + i.SH + 0.5
        if hf > (i.hfj - 2.0):
            return False
        elif hf < (hf - 1.0):
            return False
        else:
            return i.FH + i.SH + 0.5


def hoyde_returledn(i):
    """Høyde, samt kontroll av høyde, for returledning målt fra SOK."""

    # Dersom mate-/fjern-, AT- eller jordledning i masten.
    hr = i.FH + i.SH
    if i.retur_ledn and (i.matefjern_ledn
                         or i.at_ledn
                         or i.jord_ledn):
        if hr > (i.hfj - 0.5):
            return False
        elif hr < (hr - 1.0):
            return False
    # Dersom forbigangsledning er i masten.
    if i.retur_ledn and i.forbigang_ledn:
        if hr > (i.hf - 0.5):
            return False
        elif hr < (hr - 1.0):
            return False
    # Hvis, og bare hvis, returledningen henger alene i masten.
    elif i.retur_ledn and (not i.matefjern_ledn
                           and not i.at_ledn
                           and not i.jord_ledn
                           and not i.fiberoptisk_ledn
                           and not i.forbigang_ledn):
        if hr > (i.h - i.e - 0.1):
            return False
        elif hr < (hr - 1.0):
            return False



# ================================NB!!================================#
#
# Få svar fra Mirza på gyldige intervaller for jordledningen
# Runde av delsvar til nærmeste 0.5m. Master produseres pr. 0.5m
#
# ====================================================================#
"""
# høyde for jordledning målt fra SOK.
def hoyde_jordledn (FH, SH):
    # forbigangsledning og returledning i masten.
    if forbigang_ledn and retur_ledn:
        return (0.5*(Hf + Hr))
    # mate-/fjern- eller AT-ledning i toppen av mast => Hj i bakkant.
    elif matefjern_ledn or at_ledn:
        return ()
    # ingen andre ledninger enn jord- og kontakledning i masten.
    else:
        return ()
"""

"""Master produseres i intervall-lengder på 0.5m.
   Mastehøyde forhøyes ALLTID opp til nærmeste 0.5m.
   """