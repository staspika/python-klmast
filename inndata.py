from __future__ import unicode_literals
import configparser

class Inndata(object):
    """Container-klasse for enkel tilgang til inngangsparametre fra .ini-fil."""

    def __init__(self, ini):
        """Initialiserer :class:`Inndata`-objekt.

        :param ini: .ini-fil for avlesing av inputparametre
        """

        cfg = configparser.ConfigParser()
        cfg.read("input.ini")

        # Oppretter variabler for data fra .ini-fil

        # Info
        self.banestrekning = cfg.get("Info", "banestrekning")
        self.km = cfg.getfloat("Info", "km")
        self.prosjektnr = cfg.getint("Info", "prosjektnr")
        self.mastenr = cfg.getint("Info", "mastenr")
        self.signatur = cfg.get("Info", "signatur")
        self.dato = cfg.get("Info", "dato")

        # Mastealternativer
        self.siste_for_avspenning = cfg.getboolean("Mastealternativer", "siste_for_avspenning")
        self.linjemast_utliggere = cfg.getint("Mastealternativer", "linjemast_utliggere")
        self.avstand_fixpunkt = cfg.getint("Mastealternativer", "avstand_fixpunkt")
        self.fixpunktmast = cfg.getboolean("Mastealternativer", "fixpunktmast")
        self.fixavspenningsmast = cfg.getboolean("Mastealternativer", "fixavspenningsmast")
        self.avspenningsmast = cfg.getboolean("Mastealternativer", "avspenningsmast")
        self.strekkutligger = cfg.getboolean("Mastealternativer", "strekkutligger")
        self.master_bytter_side = cfg.getboolean("Mastealternativer", "master_bytter_side")
        self.avspenningsbardun = cfg.getboolean("Mastealternativer", "avspenningsbardun")

        # Fastavspente ledninger
        self.matefjern_ledn = cfg.getboolean("Fastavspent", "matefjern_ledn")
        self.matefjern_antall = cfg.getint("Fastavspent", "matefjern_antall")
        self.at_ledn = cfg.getboolean("Fastavspent", "at_ledn")
        self.at_type = cfg.get("Fastavspent", "at_type")
        self.forbigang_ledn = cfg.getboolean("Fastavspent", "forbigang_ledn")
        self.jord_ledn = cfg.getboolean("Fastavspent", "jord_ledn")
        self.jord_type = cfg.get("Fastavspent", "jord_type")
        self.fiberoptisk_ledn = cfg.getboolean("Fastavspent", "fiberoptisk_ledn")
        self.retur_ledn = cfg.getboolean("Fastavspent", "retur_ledn")
        self.auto_differansestrekk = cfg.getboolean("Fastavspent", "auto_differansestrekk")
        self.differansestrekk = cfg.getfloat("Fastavspent", "differansestrekk")

        # System
        self.systemnavn = cfg.get("System", "systemnavn")
        self.radius = cfg.getint("System", "radius")
        self.a1 = cfg.getfloat("System", "a1")
        self.a2 = cfg.getfloat("System", "a2")
        self.delta_h1 = cfg.getfloat("System", "delta_h1")
        self.delta_h2 = cfg.getfloat("System", "delta_h2")
        self.vindkasthastighetstrykk = cfg.getfloat("System", "vindkasthastighetstrykk")

        # Geometri
        self.h = cfg.getfloat("Geometri", "h")
        self.hfj = cfg.getfloat("Geometri", "hfj")
        self.hf = cfg.getfloat("Geometri", "hf")
        self.hj = cfg.getfloat("Geometri", "hj")
        self.hr = cfg.getfloat("Geometri", "hr")
        self.fh = cfg.getfloat("Geometri", "fh")
        self.sh = cfg.getfloat("Geometri", "sh")
        self.e = cfg.getfloat("Geometri", "e")
        self.sms = cfg.getfloat("Geometri", "sms")

        # Diverse
        self.s235 = cfg.getboolean("Div", "s235")
        self.materialkoeff = cfg.getfloat("Div", "materialkoeff")
        self.traverslengde = cfg.getfloat("Div", "traverslengde")
        self.ec3 = cfg.getboolean("Div", "ec3")
        self.isklasse = cfg.get("Div", "isklasse")

        # Brukerdefinert last
        self.brukerdefinert_last = cfg.getboolean("Brukerdefinert last", "brukerdefinert_last")
        self.f_x = cfg.getfloat("Brukerdefinert last", "f_x")
        self.f_y = cfg.getfloat("Brukerdefinert last", "f_y")
        self.f_z = cfg.getfloat("Brukerdefinert last", "f_z")
        self.e_x = cfg.getfloat("Brukerdefinert last", "e_x")
        self.e_y = cfg.getfloat("Brukerdefinert last", "e_y")
        self.e_z = cfg.getfloat("Brukerdefinert last", "e_z")
        self.a_vind = cfg.getfloat("Brukerdefinert last", "a_vind")
        self.a_vind_par = cfg.getfloat("Brukerdefinert last", "a_vind_par")


