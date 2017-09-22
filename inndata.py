from __future__ import unicode_literals
import configparser

class Inndata(object):
    """Container-klasse for enkel tilgang til inngangsparametre fra .ini-fil."""
    def __init__(self):
        # Info
        self.banestrekning = ""
        self.km = 0.0
        self.prosjektnr = 0
        self.mastenr = 0
        self.signatur = ""
        self.dato = ""
        # Mastealternativer
        self.siste_for_avspenning = False
        self.linjemast_utliggere = 0
        self.avstand_fixpunkt = 0
        self.fixpunktmast = False
        self.fixavspenningsmast = False
        self.avspenningsmast = False
        self.strekkutligger = False
        self.master_bytter_side = False
        self.avspenningsbardun = False
        # Fastavspente ledninger
        self.matefjern_ledn = False # Mate- eller fjernledning?
        self.matefjern_antall = 0 # Antall mate- og fjernledninger
        self.at_ledn = False # Autotransformatorledning?
        self.at_type = "" # Type autotransformatorsystem
        self.forbigang_ledn = False # Forbigangledning?
        self.jord_ledn = False # Jordledning?
        self.jord_type = "" # Type jordledning
        self.fiberoptisk_ledn = False # Fiberoptisk ledning?
        self.retur_ledn = False # Returledning
        self.auto_differansestrekk = False # 
        self.differansestrekk = 0.0
        # System
        self.systemnavn = ""
        self.radius = 0
        self.a1 = 0.0
        self.a2 = 0.0
        self.delta_h1 = 0.0
        self.delta_h2 = 0.0
        self.vindkasthastighetstrykk = 0.0
        # Geometri
        self.h = 0.0 # Mastehøyde
        self.hfj = 0.0 # Høyde toppmonterte ledninger
        self.hf = 0.0 # Høyde forbigangsledning
        self.hj = 0.0 # Høyde jordledning
        self.hr = 0.0 # Høyde returledning
        self.fh = 0.0 # Kontakttrådhøyde
        self.sh = 0.0 # Utliggerens systemhøyde
        self.e = 0.0 # Avstand fra skinneoverkant til toppen av mastefundament
        self.sms = 0.0 # Avstand senter mast – senter spor
        # Diverse
        self.s235 = False
        self.materialkoeff = False
        self.traverslengde = False
        self.ec3 = False
        self.isklasse = ""
        # Brukerdefinert last
        self.brukerdefinert_last = False
        self.f_x = 0.0
        self.f_y = 0.0
        self.f_z = 0.0
        self.e_x = 0.0
        self.e_y = 0.0
        self.e_z = 0.0
        self.a_vind = 0.0
        self.a_vind_par = 0.0
        # Hjelpevariabler
        self.referansevindhastighet = 0
        self.kastvindhastighet = 0.0
    def from_ini_file(self, ini):
        """Initialiserer :class:`Inndata`-objekt.

        :param ini: .ini-fil for avlesing av inputparametre
        """
        cfg = configparser.ConfigParser()
        cfg.read(ini)
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
        # Hjelpevariabler
        self.referansevindhastighet = cfg.getint("Hjelpevariabler", "referansevindhastighet")
        self.kastvindhastighet = cfg.getfloat("Hjelpevariabler", "kastvindhastighet")
