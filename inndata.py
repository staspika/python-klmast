from __future__ import unicode_literals
import configparser

class OclSystem:
    def __init__(self, systemnavn="", radius=0, a1=0.0, a2=0.0, delta_h1=0.0, delta_h2=0.0, vindkasthastighetstrykk=0.0):
        """Class for OCL system"""
        self.systemnavn = systemnavn
        self.radius = radius
        self.a1 = a1
        self.a2 = a2
        self.delta_h1 = delta_h1
        self.delta_h2 = delta_h2
        self.vindkasthastighetstrykk = vindkasthastighetstrykk

class OclGeometry:
    def __init__(
            self, h=0.0, hfj=0.0, hf=0.0, hj=0.0, hr=0.0, fh=0.0,
            sh=0.0, e=0.0, sms=0.0):
        """Initialiserer :class:`OclGeometry`-objekt.

        :param h: Mastehøyde
        :param hfj: Høyde toppmonterte ledninger
        :param hf: Høyde forbigangsledning
        :param hj: Høyde jordledning
        :param hr: Høyde returledning
        :param fh: Kontakttrådhøyde
        :param sh: Utliggerens systemhøyde
        :param e: Avstand fra skinneoverkant til toppen av mastefundament
        :param sms: Avstand senter mast – senter spor
        """
        self.h = h
        self.hfj = hfj
        self.hf = hf
        self.hj = hj
        self.hr = hr
        self.fh = fh
        self.sh = sh
        self.e = e
        self.sms = sms

class OclLoad:
    def __init__(
            self, f_x=0.0, f_y=0.0, f_z=0.0, e_x=0.0, e_y=0.0, e_z=0.0,
            a_vind=0.0, a_vind_par=0.0):
        self.f_x = f_x
        self.f_y = f_y
        self.f_z = f_z
        self.e_x = e_x
        self.e_y = e_y
        self.e_z = e_z
        self.a_vind = a_vind
        self.a_vind_par = a_vind_par

class OclInfo:
    def __init__(
            self, banestrekning="", km=0.0, prosjektnr=0,
            mastenr = 0, signatur = "", dato = ""):
        self.banestrekning = banestrekning
        self.km = km
        self.prosjektnr = prosjektnr
        self.mastenr = mastenr
        self.signatur = signatur
        self.dato = dato

class OclMastAlt:
    def __init__(
            self, siste_for_avspenning=False, linjemast_utliggere=0,
            avstand_fixpunkt=0, fixpunktmast=False,
            fixavspenningsmast=False, avspenningsmast=False,
            strekkutligger=False, master_bytter_side=False,
            avspenningsbardun=False):
        # Mastealternativer
        self.siste_for_avspenning = siste_for_avspenning
        self.linjemast_utliggere = linjemast_utliggere
        self.avstand_fixpunkt = avstand_fixpunkt
        self.fixpunktmast = fixpunktmast
        self.fixavspenningsmast = fixavspenningsmast
        self.avspenningsmast = avspenningsmast
        self.strekkutligger = strekkutligger
        self.master_bytter_side = master_bytter_side
        self.avspenningsbardun = avspenningsbardun

class OclFastAvsp:
    """Fastavspente ledninger"""
    def __init__(
            self, matefjern_ledn=False, matefjern_antall=0,
            at_ledn=False, at_type="", forbigang_ledn=False,
            jord_ledn=False, jord_type="", fiberoptisk_ledn=False,
            retur_ledn=False, auto_differansestrekk=False,
            differansestrekk=0.0):
        self.matefjern_ledn = matefjern_ledn # Mate- eller fjernledning?
        self.matefjern_antall = matefjern_antall # Antall mate- og fjernledninger
        self.at_ledn = at_ledn # Autotransformatorledning?
        self.at_type = at_type # Type autotransformatorsystem
        self.forbigang_ledn = forbigang_ledn # Forbigangledning?
        self.jord_ledn = jord_ledn # Jordledning?
        self.jord_type = jord_type # Type jordledning
        self.fiberoptisk_ledn = fiberoptisk_ledn # Fiberoptisk ledning?
        self.retur_ledn = retur_ledn # Returledning
        self.auto_differansestrekk = auto_differansestrekk # 
        self.differansestrekk = differansestrekk

class Inndata(object):
    """Container-klasse for enkel tilgang til inngangsparametre fra .ini-fil."""
    def __init__(self):
        # Info
        self.info = OclInfo()
        # Mastealternativer
        self.mast_alt = OclMastAlt()
        # Fastavspente ledninger
        self.fast_avsp = OclFastAvsp()
        # System
        self.system = OclSystem()
        # Geometri
        self.geometry = OclGeometry()
        # Diverse
        self.s235 = False
        self.materialkoeff = False
        self.traverslengde = False
        self.ec3 = False
        self.isklasse = ""
        # Brukerdefinert last
        self.brukerdefinert_last = False
        self.custom_load = OclLoad()
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
        banestrekning = cfg.get("Info", "banestrekning")
        km = cfg.getfloat("Info", "km")
        prosjektnr = cfg.getint("Info", "prosjektnr")
        mastenr = cfg.getint("Info", "mastenr")
        signatur = cfg.get("Info", "signatur")
        dato = cfg.get("Info", "dato")
        self.info = OclInfo(banestrekning, km, prosjektnr, mastenr, signatur, dato)
        # Mastealternativer
        siste_for_avspenning = cfg.getboolean("Mastealternativer", "siste_for_avspenning")
        linjemast_utliggere = cfg.getint("Mastealternativer", "linjemast_utliggere")
        avstand_fixpunkt = cfg.getint("Mastealternativer", "avstand_fixpunkt")
        fixpunktmast = cfg.getboolean("Mastealternativer", "fixpunktmast")
        fixavspenningsmast = cfg.getboolean("Mastealternativer", "fixavspenningsmast")
        avspenningsmast = cfg.getboolean("Mastealternativer", "avspenningsmast")
        strekkutligger = cfg.getboolean("Mastealternativer", "strekkutligger")
        master_bytter_side = cfg.getboolean("Mastealternativer", "master_bytter_side")
        avspenningsbardun = cfg.getboolean("Mastealternativer", "avspenningsbardun")
        mast_alt = OclMastAlt(siste_for_avspenning, linjemast_utliggere,
                              avstand_fixpunkt, fixpunktmast,
                              fixavspenningsmast, avspenningsmast,
                              strekkutligger, master_bytter_side,
                              avspenningsbardun)
        # Fastavspente ledninger
        matefjern_ledn = cfg.getboolean("Fastavspent", "matefjern_ledn")
        matefjern_antall = cfg.getint("Fastavspent", "matefjern_antall")
        at_ledn = cfg.getboolean("Fastavspent", "at_ledn")
        at_type = cfg.get("Fastavspent", "at_type")
        forbigang_ledn = cfg.getboolean("Fastavspent", "forbigang_ledn")
        jord_ledn = cfg.getboolean("Fastavspent", "jord_ledn")
        jord_type = cfg.get("Fastavspent", "jord_type")
        fiberoptisk_ledn = cfg.getboolean("Fastavspent", "fiberoptisk_ledn")
        retur_ledn = cfg.getboolean("Fastavspent", "retur_ledn")
        auto_differansestrekk = cfg.getboolean("Fastavspent", "auto_differansestrekk")
        differansestrekk = cfg.getfloat("Fastavspent", "differansestrekk")
        fast_avsp = OclFastAvsp(matefjern_ledn, matefjern_antall,
                                at_ledn, at_type, forbigang_ledn,
                                jord_ledn, jord_type, fiberoptisk_ledn,
                                retur_ledn, auto_differansestrekk,
                                differansestrekk)
        # System
        systemnavn = cfg.get("System", "systemnavn")
        radius = cfg.getint("System", "radius")
        a1 = cfg.getfloat("System", "a1")
        a2 = cfg.getfloat("System", "a2")
        delta_h1 = cfg.getfloat("System", "delta_h1")
        delta_h2 = cfg.getfloat("System", "delta_h2")
        vindkasthastighetstrykk = cfg.getfloat("System", "vindkasthastighetstrykk")
        self.system = OclSystem(systemnavn, radius, a1, a2, delta_h1, delta_h2, vindkasthastighetstrykk)
        # Geometri
        h = cfg.getfloat("Geometri", "h")
        hfj = cfg.getfloat("Geometri", "hfj")
        hf = cfg.getfloat("Geometri", "hf")
        hj = cfg.getfloat("Geometri", "hj")
        hr = cfg.getfloat("Geometri", "hr")
        fh = cfg.getfloat("Geometri", "fh")
        sh = cfg.getfloat("Geometri", "sh")
        e = cfg.getfloat("Geometri", "e")
        sms = cfg.getfloat("Geometri", "sms")
        self.geometry = OclGeometry(h, hfj, hf, hj, hr, fh, sh, e, sms)
        # Diverse
        self.s235 = cfg.getboolean("Div", "s235")
        self.materialkoeff = cfg.getfloat("Div", "materialkoeff")
        self.traverslengde = cfg.getfloat("Div", "traverslengde")
        self.ec3 = cfg.getboolean("Div", "ec3")
        self.isklasse = cfg.get("Div", "isklasse")
        # Brukerdefinert last
        self.brukerdefinert_last = cfg.getboolean("Brukerdefinert last", "brukerdefinert_last")
        f_x = cfg.getfloat("Brukerdefinert last", "f_x")
        f_y = cfg.getfloat("Brukerdefinert last", "f_y")
        f_z = cfg.getfloat("Brukerdefinert last", "f_z")
        e_x = cfg.getfloat("Brukerdefinert last", "e_x")
        e_y = cfg.getfloat("Brukerdefinert last", "e_y")
        e_z = cfg.getfloat("Brukerdefinert last", "e_z")
        a_vind = cfg.getfloat("Brukerdefinert last", "a_vind")
        a_vind_par = cfg.getfloat("Brukerdefinert last", "a_vind_par")
        self.custom_load = OclLoad(f_x, f_y, f_z, e_x, e_y, e_z, a_vind,
                                   a_vind_par)
        # Hjelpevariabler
        self.referansevindhastighet = cfg.getint("Hjelpevariabler", "referansevindhastighet")
        self.kastvindhastighet = cfg.getfloat("Hjelpevariabler", "kastvindhastighet")
