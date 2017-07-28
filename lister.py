# -*- coding: utf8 -*-
from __future__ import unicode_literals

def _hent_tall(str):
    """Henter ut tallverdi fra string for sortering."""

    tall = [int(s) for s in str.split() if s.isdigit()]
    return tall

# Kilometrering på dictionary-format, hentet fra gamle KL_fund
kilometer = {
			"0010 Oslo S": [0.0, 0.95],
			"0011 Oslo S fra spor 17 mot Gjøvikbanen": [0.0, 0.95],
			"0012 Gjøvikbanen inn i spor 16 Oslo S": [0.15, 0.95],
			"0013 Oslo S fra spor 9 mot Hovedbanen": [0.0, 0.95],
			"0014 Hovedbanen inn i spor 7 Oslo S": [0.0, 0.95],
			"0020 Lodalen": [0.0, 0.0],
			"0022 Oslo S fra spor 9 mot Østfoldbanen": [0.394, 2.18],
			"0023 Østfoldbanen inn i spor 7 Oslo S": [0.394, 2.18],
			"0030 Alnabru": [0.0, 0.0],
			"0040 Loenga": [0.0, 0.0],
			"0210 (Oslo S) - Alnabru/Alna": [0.95, 9.041],
			"0211 Alnabru/Alna - (Oslo S)": [0.95, 9.041],
			"0220 (Alnabru/Alna) - Lillestrøm": [9.041, 22.415],
			"0221 Lillestrøm - (Alnabru/Alna)": [9.041, 22.415],
			"0230 (Lillestrøm) - Eidsvoll": [22.415, 68.904],
			"0240 (Grefsen) - (Alnabru) g.spor": [0.0, 3.18],
			"0250 (Grefsen) - (Alnabru) g.spor": [3.18, 5.19],
			"0270 Etterstad - Gardermoen(GMB)": [2.4, 52.838],
			"0271 Gardermoen - Etterstad (GMB)": [2.4, 52.838],
			"0280 (Gardermoen)-(Eidsvoll)": [52.838, 69.3],
			"0281 Venjar - (Gardermoen)": [52.838, 65.74],
			"0300 (Lillestrøm) - Kongsvinger": [20.95, 101.692],
			"0310 (Kongsvinger) - Charlottenberg": [101.692, 136.27],
			"0510 (Loenga) - (Alnabru) g.spor": [0.0, 6.3],
			"0540 (Oslo S) - Ski": [0.39, 25.585],
			"0541 Ski - (Oslo S)": [0.39, 25.585],
			"0550 (Ski) - Moss": [25.585, 61.47],
			"0551 Sandbukta- (Ski)": [25.585, 57.187],
			"0560 (Moss) - Sarpsborg": [61.47, 111.853],
			"0561 Haug - Såstad": [67.82, 73.967],
			"0570 (Sarpsborg) - Kornsjø": [111.853, 170.123],
			"0580 (Ski) - (Sarpsborg) østre linje": [0.201, 78.9282],
			"0581 Hafslundsløyfa": [78.4366, 78.826],
			"0610 (Oslo S) - Grefsen": [0.95, 7.47],
			"0611 (Grefsen) - (Oslo S)": [0.95, 6.942],
			"0620 (Grefsen) - Roa": [7.47, 58.4],
			"0630 (Roa) - Eina": [58.4, 101.585],
			"0640 (Eina) - Gjøvik": [101.585, 124.3],
			"0670 (Roa) - Hønefoss": [57.74, 90.6],
			"0700 (Eidsvoll) - Hamar": [68.904, 127.21],
			"0710 (Hamar) - Lillehammer": [127.21, 185.174],
			"0720 (Lillehammer) - Vinstra": [185.174, 267.21],
			"0721 (Vinstra) - Dombås": [267.21, 343.596],
			"1100 (Dombås) - Hjerkinn": [343.596, 382.33],
			"1110 (Hjerkinn) - Oppdal": [382.33, 430.2],
			"1111 (Oppdal) - Støren": [430.2, 502.19],
			"1120 (Støren) - Trondheim": [502.19, 552.85],
			"1121 Trondheim": [0.0, 1.51],
			"1140 Marienborg": [548.5, 549.7],
			"1400 (Oslo S) - Lysaker": [0.0, 7.827],
			"1401 Lysaker - (Oslo S)": [0.0, 7.827],
			"1410 (Lysaker) - Asker": [7.827, 24.881],
			"1411 Asker - (Lysaker)": [7.827, 24.881],
			"1420 (Asker) - Drammen": [24.881, 53.88],
			"1421 Drammen - (Asker)": [24.881, 54.07],
			"1450 Fillipstad - (Skøyen)": [0.0, 3.0],
			"1460 (Asker) - Spikkestad": [24.03, 39.03],
			"1510 (Drammen) - Eidanger": [54.07, 192.603],
			"1511 (Larvik) - (Drammen)": [54.07, 159.173],
			"1550 (Skoppum) - Horten": [99.54, 106.51],
			"1600 (Drammen) - Hokksund": [53.88, 71.38],
			"1610 (Hokksund) - Hønefoss": [70.22, 125.3],
			"1650 (Hokksund) - Kongsberg": [71.38, 99.98],
			"1660 (Kongsberg) - Nordagutu": [99.98, 146.52],
			"1680 (Hønefoss) - Nesbyen": [90.6, 186.059],
			"1800 (Hjuksebø) - Tinnoset": [136.24, 175.3],
			"1820 (Nordagutu) - Skien": [145.95, 180.836],
			"1830 (Skien) - (Eidanger)": [180.836, 193.39],
			"2000 (Nordagutu) - Nelaug": [146.52, 282.0],
			"2120 (Nelaug) - Kristiansand": [282.0, 365.95],
			"2130 (Kristiansand) - Egersund": [365.95, 526.581],
			"2160 (Nelaug) - Arendal": [281.41, 317.64],
			"2220 (Egersund) - Stavanger": [526.581, 598.77],
			"2301 (Nesbyen) - Ål": [186.059, 228.811],
			"2310 (Ål) - (Haugastøl)": [228.811, 274.875],
			"2311 Haugastøl - Myrdal": [274.875, 336.7],
			"2312 (Myrdal) - Reimegrend": [336.7, 363.542],
			"2313 (Myrdal) - Flåm": [335.8, 356.0],
			"2320 (Reimegrend) - Voss": [363.542, 386.153],
			"2330 (Voss) - Dale": [386.153, 425.866],
			"2331 (Voss) - Palmafoss": [385.32, 389.4],
			"2340 (Dale) - Bergen": [425.866, 471.25],
			"2341 Minde - (Bergen)": [487.9, 491.3],
			"2400 Narvik havn - Vassijaure": [0.0, 42.99] }

# Kilometrering på listeformat
kilometer_list = []
for k in kilometer:
    kilometer_list.append(k)
kilometer_list.sort(key=_hent_tall)

# Liste over AT-ledninger
at_list = ["Al 400-37", "Al 240-19", "Al 150-19"]

# Liste over jordledninger
jord_list = ["KHF-70", "KHF-95"]

# Liste over strømavtakere
stromavtaker_list = ["1600", "1800", "1950"]

# Liste over systemer
system_list = ["System 20A", "System 20B", "System 25", "System 35"]


# Overhøyde D (= UE) avhengig av system
D_20B_35 = {"180": 0.150, "250": 0.150, "300": 0.150, "400": 0.140,
            "500": 0.130, "600": 0.120, "700": 0.110, "800": 0.100,
            "900": 0.090, "1000": 0.080, "1100": 0.070, "1200": 0.065,
            "1300": 0.060, "1400": 0.055, "1500": 0.055, "1600": 0.050,
            "1800": 0.045, "2000": 0.040, "2400": 0.035, "2700": 0.030,
            "3000": 0.025, "3500": 0.025, "4000": 0.020, "5000": 0.015,
            "7000": 0.015, "10000": 0.015, "20000": 0.010, "10000000": 0.0}
D_20A = {"180": 0.150, "250": 0.150, "300": 0.150, "400": 0.150,
         "500": 0.150, "600": 0.150, "700": 0.150, "800": 0.150,
         "900": 0.150, "1000": 0.150, "1100": 0.150, "1200": 0.150,
         "1300": 0.150, "1400": 0.150, "1500": 0.150, "1600": 0.150,
         "1800": 0.135, "2000": 0.110, "2400": 0.085, "2700": 0.080,
         "3000": 0.070, "3500": 0.060, "4000": 0.055, "5000": 0.045,
         "7000": 0.035, "10000": 0.025, "20000": 0.010, "10000000": 0.0}
D_25 = {"180": 0.150, "250": 0.150, "300": 0.150, "400": 0.150,
        "500": 0.150, "600": 0.150, "700": 0.150, "800": 0.150,
        "900": 0.150, "1000": 0.150, "1100": 0.150, "1200": 0.150,
        "1300": 0.150, "1400": 0.150, "1500": 0.150, "1600": 0.150,
        "1800": 0.150, "2000": 0.150, "2400": 0.150, "2700": 0.150,
        "3000": 0.120, "3500": 0.095, "4000": 0.080, "5000": 0.070,
        "7000": 0.050, "10000": 0.035, "20000": 0.025, "10000000": 0}

# Sammenheng mellom kurveradie og sikksakkverdier for forskjellige systemer
sikksakk_20 = {"180": [-0.30, -0.30], "250": [-0.30, -0.30],
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
sikksakk_25 = {"180": [-0.30, -0.30], "250": [-0.30, -0.30],
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
sikksakk_35 = {"180": [-0.4, -0.4], "250": [-0.4, -0.4],
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

# Kurveradier på listeformat
radius_list = []
for s in sikksakk_20:
    radius_list.append(s)
radius_list.sort(key=_hent_tall)

# Terrengkategorier etter EC1, NA.4.1
kat0 = {"k_r": 0.16, "z_0": 0.003, "z_min": 2.0}
kat1 = {"k_r": 0.17, "z_0": 0.01, "z_min": 2.0}
kat2 = {"k_r": 0.19, "z_0": 0.05, "z_min": 4.0}
kat3 = {"k_r": 0.22, "z_0": 0.3, "z_min": 8.0}
kat4 = {"k_r": 0.24, "z_0": 1.0, "z_min": 16.0}
terrengkategorier = ([kat0, kat1, kat2, kat3, kat4])

# Sidekrefter som gir bidrag til utliggerdeformasjon
sidekraftbidrag_strekk = ["Strekk: Bæreline", "Strekk: Kontakttråd"]
sidekraftbidrag_sno = ["Vindlast: Kontakttråd, økt diameter", "Vindlast: Bæreline, økt diameter",
					   "Vindlast: Hengetråd, økt diameter", "Vindlast: Y-line, økt diameter"]
sidekraftbidrag_vind = ["Vindlast: Kontakttråd", "Vindlast: Bæreline",
					    "Vindlast: Hengetråd", "Vindlast: Y-line"]

# Krefter som fjernes ved ulykkesberegning
ulykkeslaster_KL = ["Egenvekt: Bæreline", "Egenvekt: Hengetråd", "Egenvekt: Kontakttråd",
                    "Egenvekt: Y-line", "Strekk: Bæreline", "Strekk: Kontakttråd",
                    "Strekk: Bæreline til avspenning", "Strekk: Kontakttråd til avspenning",
                    "Strekk: Torsjon, eksentrisitet utliggere", "Vandringskraft: Bæreline",
                    "Vandringskraft: Kontakttråd", "Geometri: Ulik høyde mellom master"]


def hent_lastkombinasjoner(ec3):
    """Henter last- og kombinasjonsfaktorer til utregning av dimensjonerene laster.

    :param Boolean ec3: Brukerens valg av beregningsmetode
    :return: ``lastsituasjoner`` (kombinasjonsfaktorer), ``lastfaktorer``
    :rtype: :class:`dict`, :class:`dict`
    """
    if ec3:
        # Lastsituasjoner og faktorer ihht. EC3
        lastsituasjoner = {"Temperatur dominerende": {"psi_T": 1.0, "psi_S": 0.7, "psi_V": 0.6},
                           "Snølast dominerende": {"psi_T": 0.6, "psi_S": 1.0, "psi_V": 0.6},
                           "Vind dominerende": {"psi_T": 0.6, "psi_S": 0.7, "psi_V": 1.0}}
        lastfaktorer = {"G": (1.2, 1.0), "L": (1.2, 1.0), "T": (1.5, 0),
                        "S": (1.5, 0), "V": (1.5, 0)}
    else:
        # Lastsituasjoner og faktorer ihht. NEK (bransjestandard)
        lastsituasjoner = {"Maksimal temperaturlast": {"psi_T": 1.0, "psi_S": 0, "psi_V": 0},
                           "Maksimal vindlast": {"psi_T": 0, "psi_S": 0, "psi_V": 1.0},
                           "Maksimal snølast": {"psi_T": 0, "psi_S": 1.0, "psi_V": 0},
                           "Kombinert vind- og snølast": {"psi_T": 0, "psi_S": 1.0, "psi_V": 0.5}}
        lastfaktorer = {"G": (1.3, 1.0), "L": (1.3, 0), "T": (1.3, 0),
                        "S": (1.3, 0), "V": (1.3, 0)}

    return lastsituasjoner, lastfaktorer



