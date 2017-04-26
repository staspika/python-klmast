# ====================================================================#
# Dette skriptet sjekker at data i .ini-fila er gyldig                #
# Det må kontrolleres at dette skriptet gir mening!                   #
# ====================================================================#


def sjekk_fh(i):
    """Kontrollerer FH: Høyde av kontakttråd."""

    if i.fh > 6.5 or i.fh < 4.8:
        print("Kontakttrådhøyden er ikke gyldig.")
        return False
    print("FH er OK.")
    return True


def sjekk_sh(i):
    """Kontrollerer SH: Systemhøyden."""

    if i.sh > 2.0 or i.sh < 0.2:
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

    if i.sms > 6.0 or i.sms < 2.0:
        print("SMS avstanden er ugyldig.")
        return False
    print("SMS er OK.")
    return True


def valider_ledn(i):
    """Validerer gyldige kombinasjoner av ledninger."""

    if i.at_ledn and i.matefjern_ledn:
        print("Mate-/fjern- og AT-ledning kan ikke henges opp samtidig.")
        return False
    elif i.at_ledn and i.forbigang_ledn:
        print("Forbigangs- og AT-ledning kan ikke henges opp samtidig.")
        return False
    elif i.at_ledn and i.retur_ledn:
        print("Retur- og AT-ledning kan ikke henges opp samtidig.")
        return False
    elif i.forbigang_ledn and i.fiberoptisk_ledn:
        print("Forbigangs- og fiberoptisk ledning kan ikke henges opp samtidig.")
        return False
    else:
        print("Kombinasjonen av ledninger er OK.")
        return True


def hoyde_mast(i):
    """Høyde av KL-mast målt fra toppmaal fundament."""

    # Dersom mate-/fjern, AT- eller jordledning henger i masten.
    if i.matefjern_ledn or i.at_ledn or i.jord_ledn:
        H = i.fh + i.sh + i.e + 2.5
        if sjekk_h(H):
            return H
    # Dersom forbigangs- OG returledning henger i masten.
    elif i.forbigang_ledn and i.retur_ledn:
        H = i.fh + i.sh + i.e + 2.0
        if sjekk_h(H):
            return H
    # Hvis, og bare hvis, returledning henger alene i masten.
    elif i.retur_ledn and (not i.matefjern_ledn
                           and not i.at_ledn
                           and not i.forbigang_ledn
                           and not i.jord_ledn
                           and not i.fiberoptisk_ledn):
        H = i.fh + i.sh + i.e + 0.7
        if sjekk_h(H):
            return H
    # Mastehøyde dersom ingen fastavspente ledninger i masten.
    else:
        H = i.fh + i.sh + i.e + 0.7
        if sjekk_h(H):
            return H


def sjekk_h(H):
    """Kontrollerer høyde av KL-mast."""
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
        return i.h - i.e + 0.5
    # Mate-/fjern- eller AT-ledning alene i masten
    elif (i.matefjern_ledn or i.at_ledn) and not i.forbigang_ledn:
        return i.fh + i.sh + 3.0
    else:
        print("Jordledningen henger i toppen av masten.")
        return False


def sjekk_atledn(i):
    """AT-ledningen kan ikke henge lavere enn Hfj = FH + SH + 3.3m."""
    if i.at_ledn:
        if i.hfj < (i.fh + i.sh + 3.3):
            print("Kritisk liten avstand mellom AT-ledning og KL-anlegget")
            return False


def sjekk_hfj(i):
    """Kontrollerer Hfj: Høyde av forbigangsledning."""
    if i.hfj > (i.max_hoyde + 2.0):
        print("Mate-/fjern- eller AT-ledningen henger for høyt.")
        return False
    elif i.hfj < (i.h - i.e):
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
        hf = i.fh + i.sh + 2.5
        if hf > (i.max_hoyde + 2.0):
            return False
        elif hf < (i.h - i.e):
            return False
        else:
            return i.fh + i.sh + 2.5
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
        hf = i.fh + i.sh + 0.5
        if hf > (i.hfj - 2.0):
            return False
        elif hf < (hf - 1.0):
            return False
        else:
            return i.fh + i.sh + 0.5


def hoyde_returledn(i):
    """Høyde, samt kontroll av høyde, for returledning målt fra SOK."""

    # Dersom mate-/fjern-, AT- eller jordledning i masten.
    hr = i.fh + i.sh
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