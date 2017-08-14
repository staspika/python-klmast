# -*- coding: utf8 -*-
"""Grafisk brukergrensesnitt, avlesing/skriving av input til .ini-fil."""

import tkinter as tk
import configparser
import lister
import math
from collections import OrderedDict
from datetime import date
import main
import numpy
import hjelpefunksjoner


# Fonter
skrifttype = "Helvetica"
skriftstr = 11
banner = (skrifttype, int(math.floor(skriftstr*1.3)))
plain = (skrifttype, skriftstr)
bold = (skrifttype, skriftstr, "bold")
italic = (skrifttype, skriftstr, "italic")

class KL_mast(tk.Tk):
    """Hovedprogram."""

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("KL-mast")

        self.x, self.y = 1600, 900
        self.geometry("{}x{}".format(self.x, self.y))


        # Range = [default, minste, storste]
        self.masteavstand_range = [63.0, 30.0, 75.0]
        self.fh_range = [5.6, 4.8, 6.5]
        self.sh_range = [1.6, 0.2, 2.0]
        self.e_range = [0.0, -5.9, 3.0]
        self.sms_range = [3.5, 2.0, 6.0]
        self.h_range = [8.0, 1.5, 17.0]
        self.hfj_type = "fjern-/AT-ledning"
        self.hfj_range = [8.5, 4.8, 19.0]
        self.hf_type = "forbigangs-/fiberoptisk ledning"
        self.hf_range = [7.8, 4.8, 15.5]
        self.hj_range = [7.0, 4.8, 15.5]
        self.hr_range = [7.3, 4.8, 15.5]



        # --- Variabeloversikt ---

        # Info
        self.banestrekning = tk.StringVar()
        self.km = tk.DoubleVar()
        self.prosjektnr = tk.IntVar()
        self.mastenr = tk.IntVar()
        self.signatur = tk.StringVar()
        self.dato = tk.StringVar()

        # Mastealternativer
        self.siste_for_avspenning = tk.BooleanVar()
        self.linjemast_utliggere = tk.IntVar()
        self.avstand_fixpunkt = tk.IntVar()
        self.fixpunktmast = tk.BooleanVar()
        self.fixavspenningsmast = tk.BooleanVar()
        self.avspenningsmast = tk.BooleanVar()
        self.strekkutligger = tk.BooleanVar()
        self.master_bytter_side = tk.BooleanVar()
        self.avspenningsbardun = tk.BooleanVar()

        # Fastavspente ledninger
        self.matefjern_ledn = tk.BooleanVar()
        self.matefjern_antall = tk.IntVar()
        self.at_ledn = tk.BooleanVar()
        self.at_type = tk.StringVar()
        self.forbigang_ledn = tk.BooleanVar()
        self.jord_ledn = tk.BooleanVar()
        self.jord_type = tk.StringVar()
        self.fiberoptisk_ledn = tk.BooleanVar()
        self.retur_ledn = tk.BooleanVar()
        self.auto_differansestrekk = tk.BooleanVar()
        self.differansestrekk = tk.DoubleVar()

        # System
        self.systemnavn = tk.StringVar()
        self.radius = tk.IntVar()
        self.hogfjellsgrense = tk.BooleanVar()
        self.a1 = tk.DoubleVar()
        self.a2 = tk.DoubleVar()
        self.delta_h1 = tk.DoubleVar()
        self.delta_h2 = tk.DoubleVar()
        self.referansevindhastighet = tk.DoubleVar()
        self.kastvindhastighet = tk.DoubleVar()
        self.vindkasthastighetstrykk = tk.DoubleVar()

        # Geometri
        self.h = tk.DoubleVar()
        self.hfj = tk.DoubleVar()
        self.hf = tk.DoubleVar()
        self.hj = tk.DoubleVar()
        self.hr = tk.DoubleVar()
        self.fh = tk.DoubleVar()
        self.sh = tk.DoubleVar()
        self.e = tk.DoubleVar()
        self.sms = tk.DoubleVar()

        # Diverse
        self.s235 = tk.BooleanVar()
        self.materialkoeff = tk.DoubleVar()
        self.traverslengde = tk.DoubleVar()
        self.stromavtaker_type = tk.StringVar()
        self.ec3 = tk.BooleanVar()
        self.isklasse = tk.StringVar()

        # Brukerdefinert last
        self.brukerdefinert_last = tk.BooleanVar()
        self.f_x = tk.DoubleVar()
        self.f_y = tk.DoubleVar()
        self.f_z = tk.DoubleVar()
        self.e_x = tk.DoubleVar()
        self.e_y = tk.DoubleVar()
        self.e_z = tk.DoubleVar()
        self.a_vind = tk.DoubleVar()
        self.a_vind_par = tk.DoubleVar()


    def skriv_ini(self):
        """Skriver varibelverdier fra hovedprogram til .ini-fil."""

        cfg = configparser.ConfigParser(dict_type=OrderedDict)
        cfg["Info"] = OrderedDict([("banestrekning", self.banestrekning.get()),
                                   ("km", self.km.get()),
                                   ("prosjektnr", self.prosjektnr.get()),
                                   ("mastenr", self.mastenr.get()),
                                   ("signatur", self.signatur.get()),
                                   ("dato", self.dato.get())])
        cfg["Mastealternativer"] = OrderedDict([("siste_for_avspenning", self.siste_for_avspenning.get()),
                                                ("linjemast_utliggere", self.linjemast_utliggere.get()),
                                                ("avstand_fixpunkt", self.avstand_fixpunkt.get()),
                                                ("fixpunktmast", self.fixpunktmast.get()),
                                                ("fixavspenningsmast", self.fixavspenningsmast.get()),
                                                ("avspenningsmast", self.avspenningsmast.get()),
                                                ("strekkutligger", self.strekkutligger.get()),
                                                ("master_bytter_side", self.master_bytter_side.get()),
                                                ("avspenningsbardun", self.avspenningsbardun.get())])
        cfg["Fastavspent"] = OrderedDict([("matefjern_ledn", self.matefjern_ledn.get()),
                                          ("matefjern_antall", self.matefjern_antall.get()),
                                          ("at_ledn", self.at_ledn.get()),
                                          ("at_type", self.at_type.get()),
                                          ("forbigang_ledn", self.forbigang_ledn.get()),
                                          ("jord_ledn", self.jord_ledn.get()),
                                          ("jord_type", self.jord_type.get()),
                                          ("fiberoptisk_ledn", self.fiberoptisk_ledn.get()),
                                          ("retur_ledn", self.retur_ledn.get()),
                                          ("auto_differansestrekk", self.auto_differansestrekk.get()),
                                          ("differansestrekk", self.differansestrekk.get()*1000)])
        cfg["System"] = OrderedDict([("systemnavn", self.systemnavn.get()),
                                     ("radius", self.radius.get()),
                                     ("hogfjellsgrense", self.hogfjellsgrense.get()),
                                     ("a1", self.a1.get()), ("a2", self.a2.get()),
                                     ("delta_h1", self.delta_h1.get()), ("delta_h2", self.delta_h2.get()),
                                     ("referansevindhastighet", self.referansevindhastighet.get()),
                                     ("kastvindhastighet", self.kastvindhastighet.get()),
                                     ("vindkasthastighetstrykk", self.vindkasthastighetstrykk.get()*1000)])
        cfg["Geometri"] = OrderedDict([("h", self.h.get()), ("hfj", self.hfj.get()),
                                       ("hf", self.hf.get()), ("hj", self.hj.get()),
                                       ("hr", self.hr.get()), ("fh", self.fh.get()),
                                       ("sh", self.sh.get()), ("e", self.e.get()),
                                       ("sms", self.sms.get())])
        cfg["Div"] = OrderedDict([("s235", self.s235.get()), ("materialkoeff", self.materialkoeff.get()),
                                  ("traverslengde", self.traverslengde.get()),
                                  ("stromavtaker_type", self.stromavtaker_type.get()),
                                  ("ec3", self.ec3.get()), ("isklasse", self.isklasse.get())])
        cfg["Brukerdefinert last"] = OrderedDict([("brukerdefinert_last", self.brukerdefinert_last.get()),
                                                  ("f_x", self.f_x.get()), ("f_y", self.f_y.get()),
                                                  ("f_z", self.f_z.get()), ("e_x", self.e_x.get()),
                                                  ("e_y", self.e_y.get()), ("e_z", self.e_z.get()),
                                                  ("a_vind", self.a_vind.get()),
                                                  ("a_vind_par", self.a_vind_par.get())])

        with open("input.ini", "w+") as ini:
            cfg.write(ini)




class Hovedvindu(tk.Frame):
    """Vindu for hovedprogram."""

    def __init__(self, *args, **kwargs):
        """Initialiserer vindu for hovedprogram."""

        tk.Frame.__init__(self, *args, **kwargs)
        self.pack(fill="both")

        # Hjelpevariabler, hovedvindu
        self._mastefelt = tk.IntVar()
        self._alternative_mastefunksjoner = tk.BooleanVar()
        self._alternativ_funksjon = tk.IntVar()

        # Hjelpevariabler, vind
        self.refvindhastighet = tk.IntVar()
        self.c_dir = tk.DoubleVar()
        self.c_season = tk.DoubleVar()
        self.c_alt = tk.DoubleVar()
        self.tregrense = tk.IntVar()
        self.c_prob = tk.DoubleVar()
        self.overgangssoner = tk.BooleanVar()
        self.terrengruhetskategori = tk.IntVar()
        self.z = tk.IntVar()
        self.Iv = tk.DoubleVar()
        self.k_l = tk.DoubleVar()
        self.C_0 = tk.DoubleVar()

        # Hjelpevariabel, resultater
        self.mast_resultater = tk.StringVar()
        self.gittermast = tk.BooleanVar()


        # initierer
        self._mastefelt.set(0)
        self._alternative_mastefunksjoner.set(False)
        self._alternativ_funksjon.set(0)
        self.refvindhastighet.set(22)
        self.c_dir.set(1.0)
        self.c_season.set(1.0)
        self.c_alt.set(1.0)
        self.tregrense.set(900)
        self.c_prob.set(1.00)
        self.overgangssoner.set(False)
        self.terrengruhetskategori.set(2)
        self.z.set(10)
        self.Iv.set(0.19)
        self.k_l.set(1)
        self.C_0.set(1)
        self.mast_resultater.set(lister.master_list[5])
        self.gittermast.set(True)

        # Ferdig beregnede master
        self.alle_master = []
        self.gittermaster = []
        self.bjelkemaster = []

        # Kopi av inndataobjekt fra beregning
        self.i = None





        #--------------------------------------Info--------------------------------------
        info = tk.Frame(self, width=self.master.x, height=0.10*self.master.y, bd=3, relief="ridge")
        info.pack(fill="both")

        tk.Label(info, text="KONTAKTLEDNINGSMASTER OG KREFTER I TOPP FUNDAMENT",
                 font=banner, fg="blue").grid(row=0, column=0, sticky="W", columnspan=4)

        # banestrekning
        self.master.banestrekning.set(lister.kilometer_list[0])
        tk.Label(info, text="Banestrekning:", font=plain).grid(row=1, column=0, sticky="E")
        strekning_menu = tk.OptionMenu(info, self.master.banestrekning, *lister.kilometer_list)
        strekning_menu.config(font=plain)
        strekning_menu.grid(row=1, column=1, sticky="EW")

        # km
        self.master.km.set(lister.kilometer[lister.kilometer_list[0]][0])
        tk.Label(info, text="Km:", font=plain).grid(row=1, column=2, sticky="E")
        km_entry = tk.Entry(info, textvariable=self.master.km, bg="red")
        km_entry.config(font=plain)
        km_entry.grid(row=1, column=3, sticky="W")
        createToolTip(self.master, km_entry, "km")

        # prosjektnr
        self.master.prosjektnr.set(0)
        tk.Label(info, text="Prosj.nr:", font=plain).grid(row=0, column=4, sticky="E")
        prosj_entry = tk.Entry(info, textvariable=self.master.prosjektnr, bg="red")
        prosj_entry.config(font=plain)
        prosj_entry.grid(row=0, column=5, sticky="W")

        # mastenr
        self.master.mastenr.set(0)
        tk.Label(info, text="Mastenr:", font=plain).grid(row=1, column=4, sticky="E")
        mastenr_entry = tk.Entry(info, textvariable=self.master.mastenr, bg="red")
        mastenr_entry.config(font=plain)
        mastenr_entry.grid(row=1, column=5, sticky="W")

        # signatur
        self.master.signatur.set("ANONYM")
        tk.Label(info, text="Sign.:", font=plain).grid(row=0, column=6, sticky="E")
        tk.Entry(info, textvariable=self.master.signatur, bg="red").grid(row=0, column=7, sticky="W")

        # dato
        today = date.today()
        self.master.dato.set("{}.{}.{}".format(today.day, today.month, today.year))
        tk.Label(info, text="Dato:", font=plain).grid(row=0, column=8, sticky="E")
        dato_entry = tk.Entry(info, textvariable=self.master.dato, state="readonly")
        dato_entry.config(font=plain)
        dato_entry.grid(row=0, column=9, sticky="W")

        # kontroll
        tk.Label(info, text="Kontroll:", font=plain).grid(row=1, column=6, sticky="E")
        tk.Label(info, text="_______________________", font=plain).grid(row=1, column=7, sticky="W")

        # kontrolldato
        tk.Label(info, text="Dato for kontroll:", font=plain).grid(row=1, column=8, sticky="E")
        tk.Label(info, text="_______________________", font=plain).grid(row=1, column=9, sticky="W")


        # ----------------------------------Inngangsdata----------------------------------
        inngangsdata = tk.Frame(self, width=0.48 * self.master.x,
                                     height=0.78 * self.master.y,
                                    bd=3, relief="ridge")
        inngangsdata.pack(side="left")
        inngangsdata.columnconfigure(0, weight=1)
        inngangsdata.columnconfigure(1, weight=1)
        venstre = tk.Frame(inngangsdata)
        venstre.pack(side="left")
        hoyre = tk.Frame(inngangsdata)
        hoyre.pack(side="right")

        # ------------------------------------Mastefelt------------------------------------
        mastefelt = tk.LabelFrame(venstre, text="Mastefelt", font=bold)
        mastefelt.pack(fill="both")
        tk.Radiobutton(mastefelt, text="Linjemast med enkel utligger", font=plain,
                       variable=self._mastefelt, value=0).pack(anchor="w")
        tk.Radiobutton(mastefelt, text="Linjemast med dobbel utligger", font=plain,
                       variable=self._mastefelt, value=1).pack(anchor="w")
        tk.Radiobutton(mastefelt, text="Siste seksjonsmast før avspenning", font=plain,
                       variable=self._mastefelt, value=2).pack(anchor="w")
        tk.Label(mastefelt, text="Avstand til fixpunkt:", font=plain).pack(anchor="w", side="left")
        self.master.avstand_fixpunkt.set(700)
        self.fixavstand_spinbox = tk.Spinbox(mastefelt, from_=0.0, to=800, increment=25,
                                               width=10, repeatinterval=100)
        self.fixavstand_spinbox.delete(0,"end")
        self.fixavstand_spinbox.insert(0, self.master.avstand_fixpunkt.get())
        self.fixavstand_spinbox.config(font=plain, state="readonly")
        self.fixavstand_spinbox.pack(anchor="e", side="left", padx=5, pady=8)
        tk.Label(mastefelt, text="[m]", font=plain).pack(anchor="e", side="left")

        # ----------------------------------Mastefunksjoner----------------------------------
        mastefunksjoner = tk.LabelFrame(venstre, text="Mastefunksjoner", font=bold)
        mastefunksjoner.pack(fill="both")
        alternative_funksjoner = tk.Checkbutton(mastefunksjoner, text="Alternative mastefunksjoner",
                                                font=plain, variable=self._alternative_mastefunksjoner,
                                                onvalue=True, offvalue=False)
        alternative_funksjoner.pack(anchor="w")
        tk.Radiobutton(mastefunksjoner, text="Fixpunktmast", font=plain,
                       variable=self._alternativ_funksjon, value=0)\
                       .pack(anchor="w", padx=15)
        tk.Radiobutton(mastefunksjoner, text="Fixavspenningsmast", font=plain,
                       variable=self._alternativ_funksjon, value=1)\
                       .pack(anchor="w", padx=15)
        tk.Radiobutton(mastefunksjoner, text="Avspenningsmast", font=plain,
                       variable=self._alternativ_funksjon, value=2)\
                       .pack(anchor="w", padx=15)
        mastefunksjoner_2 = tk.Frame(mastefunksjoner, relief="groove", bd=1)
        mastefunksjoner_2.pack(pady=(10,0))
        self.master.strekkutligger.set(True)
        tk.Radiobutton(mastefunksjoner_2, text="Strekkutligger", font=plain,
                       variable=self.master.strekkutligger, value=True)\
                       .grid(row=0, column=0, sticky="W", pady=2)
        tk.Radiobutton(mastefunksjoner_2, text="Trykkutligger", font=plain,
                       variable=self.master.strekkutligger, value=False)\
                       .grid(row=0, column=1, sticky="W", pady=2)
        tk.Checkbutton(mastefunksjoner_2, text="Neste mast på andre siden av sporet", font=plain,
                       variable=self.master.master_bytter_side, onvalue=True, offvalue=False)\
                       .grid(row=1, column=0, sticky="W", columnspan=2, pady=(0,2))

        # -------------------------------Fastavspente ledninger-------------------------------
        fastavspente = tk.LabelFrame(venstre, text="Fastavspente ledninger", font=bold)
        fastavspente.pack(fill="both")

        # mate-/fjernledninger
        tk.Checkbutton(fastavspente, text="Mate-/fjernledninger", font=plain,
                       variable=self.master.matefjern_ledn, onvalue=True,
                       offvalue=False).grid(row=0, column=0, sticky="W")
        tk.Label(fastavspente, text="Antall:", font=plain).grid(row=0, column=1, sticky="E")
        self.master.matefjern_antall.set(1)
        self.matefjern_spinbox = tk.Spinbox(fastavspente, values=(1, 2), width=10)
        self.matefjern_spinbox.config(font=plain, state="readonly")
        self.matefjern_spinbox.grid(row=0, column=2, sticky="W")

        # at-ledninger
        tk.Checkbutton(fastavspente, text="AT-ledninger (2 stk.)", font=plain,
                       variable=self.master.at_ledn, onvalue=True,
                       offvalue=False).grid(row=1, column=0, sticky="W")
        self.master.at_type.set(lister.at_list[0])
        tk.Label(fastavspente, text="Type:", font=plain).grid(row=1, column=1, sticky="E")
        at_menu = tk.OptionMenu(fastavspente, self.master.at_type, *lister.at_list)
        at_menu.config(font=plain)
        at_menu.grid(row=1, column=2, sticky="W")

        # forbigangsledning
        tk.Checkbutton(fastavspente, text="Forbigangsledning (1 stk.)", font=plain,
                       variable=self.master.forbigang_ledn, onvalue=True,
                       offvalue=False).grid(row=2, column=0, sticky="W")

        # jordledning
        tk.Checkbutton(fastavspente, text="Jordledning (1 stk.)", font=plain,
                       variable=self.master.jord_ledn, onvalue=True,
                       offvalue=False).grid(row=3, column=0, sticky="W")
        self.master.jord_type.set(lister.jord_list[0])
        tk.Label(fastavspente, text="Type:", font=plain).grid(row=3, column=1, sticky="E")
        jord_menu = tk.OptionMenu(fastavspente, self.master.jord_type, *lister.jord_list)
        jord_menu.config(font=plain)
        jord_menu.grid(row=3, column=2, sticky="W")

        # returledninger
        tk.Checkbutton(fastavspente, text="Returledninger (2 stk.)", font=plain,
                       variable=self.master.retur_ledn, onvalue=True,
                       offvalue=False).grid(row=4, column=0, sticky="W")

        # fiberoptisk ledning
        tk.Checkbutton(fastavspente, text="Fiberoptisk ledning (1 stk.)", font=plain,
                       variable=self.master.fiberoptisk_ledn, onvalue=True,
                       offvalue=False).grid(row=5, column=0, sticky="W")


        # ------------------------------------System------------------------------------
        system = tk.LabelFrame(hoyre, text="System", font=bold)
        system.pack(fill="both")

        # system
        self.master.systemnavn.set(lister.system_list[0])
        system_menu = tk.OptionMenu(system, self.master.systemnavn, *lister.system_list)
        system_menu.config(font=plain)
        system_menu.grid(row=0, column=0, sticky="W", columnspan=2)

        # radius
        tk.Label(system, text="Radius:", font=plain).grid(row=1, column=0)
        self.master.radius.set(lister.radius_list[11])
        radius_menu = tk.OptionMenu(system, self.master.radius, *lister.radius_list)
        radius_menu.config(font=plain, width=7)
        radius_menu.grid(row=1, column=0, sticky="E")
        tk.Label(system, text="[m]", font=plain).grid(row=1, column=1, sticky="W")

        # høgfjellsgrense
        hogfjellsgrense = tk.Checkbutton(system, text="Vindutsatt strekning (høyfjell)",
                                        font=plain, variable=self.master.hogfjellsgrense,
                                        onvalue=True, offvalue=False)
        hogfjellsgrense.grid(row=2, column=0, sticky="W")

        # masteavstander
        tk.Label(system, text="Avstand til forrige mast:", font=plain) \
            .grid(row=3, column=0, sticky="W")
        self.master.a1.set(self.master.masteavstand_range[0])
        self.master.a2.set(self.master.masteavstand_range[0])

        # avstand forrige mast
        self.a1_spinbox = tk.Spinbox(system, from_=self.master.masteavstand_range[1],
                                               to=self.master.masteavstand_range[2], increment=0.1,
                                               width=10, repeatinterval=25)
        self.a1_spinbox.delete(0, "end")
        self.a1_spinbox.insert(0, self.master.a1.get())
        self.a1_spinbox.config(font=plain)
        self.a1_spinbox.grid(row=3, column=0, sticky="E")
        tk.Label(system, text="[m]", font=plain).grid(row=3, column=1, sticky="W")

        # avstand neste mast
        tk.Label(system, text="Avstand til neste mast:", font=plain) \
            .grid(row=4, column=0, sticky="W")
        self.a2_spinbox = tk.Spinbox(system, from_=self.master.masteavstand_range[1],
                                               to=self.master.masteavstand_range[2], increment=0.1,
                                               width=10, repeatinterval=25)
        self.a2_spinbox.delete(0, "end")
        self.a2_spinbox.insert(0, self.master.a2.get())
        self.a2_spinbox.config(font=plain)
        self.a2_spinbox.grid(row=4, column=0, sticky="E")
        tk.Label(system, text="[m]", font=plain).grid(row=4, column=1, sticky="W")

        tk.Label(system, text="(Max. masteavstand = {} m)"
                 .format(self.master.masteavstand_range[2]), font=italic)\
                 .grid(row=5, column=0, sticky="W", columnspan=2)

        # vind
        self.master.referansevindhastighet.set(22.0)
        self.master.kastvindhastighet.set(33.7)
        self.master.vindkasthastighetstrykk.set(0.71)
        klima_btn = tk.Button(system, text="Klima", font=bold, width=12,
                             command=self._klima)
        klima_btn.grid(row=6, column=0, sticky="W")
        self.master.vindkasthastighetstrykk.set(0.71)
        tk.Label(system, text="(Vindkasthastighetstrykk = {} kN/m^2)"
                 .format(self.master.vindkasthastighetstrykk.get()), font=italic) \
            .grid(row=7, column=0, columnspan=1, sticky="W")

        # --------------------------------Geometriske data--------------------------------
        geom_data = tk.LabelFrame(hoyre, text="System", font=bold)
        geom_data.pack(fill="both")
        g_1 = tk.Frame(geom_data, relief="groove", bd=1)
        g_1.pack(fill="both")

        # h
        tk.Label(g_1, text="    (mastehøyde):", font=plain).grid(row=0, column=0, sticky="W")
        tk.Label(g_1, text="H", font=bold) \
            .grid(row=0, column=0, sticky="W")
        self.master.h.set(self.master.h_range[0])
        self.h_spinbox = tk.Spinbox(g_1, from_=self.master.h_range[1], to=self.master.h_range[2],
                                    increment=0.5, repeatinterval=120, width=10)
        self.h_spinbox.delete(0, "end")
        self.h_spinbox.insert(0, self.master.h.get())
        self.h_spinbox.config(font=plain, state="readonly")
        self.h_spinbox.grid(row=0, column=1, sticky="E")
        tk.Label(g_1, text="[m]", font=plain).grid(row=0, column=2, sticky="W")

        # hfj
        tk.Label(g_1, text="      ({}):".format(self.master.hfj_type), font=plain) \
            .grid(row=1, column=0, sticky="W")
        tk.Label(g_1, text="Hfj", font=bold) \
            .grid(row=1, column=0, sticky="W")
        self.master.hfj.set(self.master.hfj_range[0])
        self.hfj_spinbox = tk.Spinbox(g_1, from_=self.master.hfj_range[1], to=self.master.hfj_range[2],
                                    increment=0.1, repeatinterval=60, width=10)
        self.hfj_spinbox.delete(0, "end")
        self.hfj_spinbox.insert(0, self.master.hfj.get())
        self.hfj_spinbox.config(font=plain, state="readonly")
        self.hfj_spinbox.grid(row=1, column=1, sticky="E")
        tk.Label(g_1, text="[m]", font=plain).grid(row=1, column=2, sticky="W")

        # hf
        tk.Label(g_1, text="     ({}):".format(self.master.hf_type), font=plain) \
            .grid(row=2, column=0, sticky="W")
        tk.Label(g_1, text="Hf", font=bold) \
            .grid(row=2, column=0, sticky="W")
        self.master.hf.set(self.master.hf_range[0])
        self.hf_spinbox = tk.Spinbox(g_1, from_=self.master.hf_range[1], to=self.master.hf_range[2],
                                      increment=0.1, repeatinterval=60, width=10)
        self.hf_spinbox.delete(0, "end")
        self.hf_spinbox.insert(0, self.master.hf.get())
        self.hf_spinbox.config(font=plain, state="readonly")
        self.hf_spinbox.grid(row=2, column=1, sticky="E")
        tk.Label(g_1, text="[m]", font=plain).grid(row=2, column=2, sticky="W")

        # hj
        tk.Label(g_1, text="     (jordledning):", font=plain) \
            .grid(row=3, column=0, sticky="W")
        tk.Label(g_1, text="Hj", font=bold) \
            .grid(row=3, column=0, sticky="W")
        self.master.hj.set(self.master.hj_range[0])
        self.hj_spinbox = tk.Spinbox(g_1, from_=self.master.hj_range[1], to=self.master.hj_range[2],
                                     increment=0.1, repeatinterval=60, width=10)
        self.hj_spinbox.delete(0, "end")
        self.hj_spinbox.insert(0, self.master.hj.get())
        self.hj_spinbox.config(font=plain, state="readonly")
        self.hj_spinbox.grid(row=3, column=1, sticky="E")
        tk.Label(g_1, text="[m]", font=plain).grid(row=3, column=2, sticky="W")

        # hr
        tk.Label(g_1, text="     (returledning):", font=plain) \
            .grid(row=4, column=0, sticky="W")
        tk.Label(g_1, text="Hr", font=bold) \
            .grid(row=4, column=0, sticky="W")
        self.master.hr.set(self.master.hr_range[0])
        self.hr_spinbox = tk.Spinbox(g_1, from_=self.master.hr_range[1], to=self.master.hr_range[2],
                                     increment=0.1, repeatinterval=60, width=10)
        self.hr_spinbox.delete(0, "end")
        self.hr_spinbox.insert(0, self.master.hr.get())
        self.hr_spinbox.config(font=plain, state="readonly")
        self.hr_spinbox.grid(row=4, column=1, sticky="E")
        tk.Label(g_1, text="[m]", font=plain).grid(row=4, column=2, sticky="W")


        g_2 = tk.Frame(geom_data, relief="groove", bd=1)
        g_2.pack(fill="both")

        # fh
        tk.Label(g_2, text="      (kontakttråd):", font=plain) \
            .grid(row=0, column=0, sticky="W")
        tk.Label(g_2, text="FH", font=bold) \
            .grid(row=0, column=0, sticky="W")
        self.master.fh.set(self.master.fh_range[0])
        self.fh_spinbox = tk.Spinbox(g_2, from_=self.master.fh_range[1], to=self.master.fh_range[2],
                                     increment=0.1, repeatinterval=60, width=10)
        self.fh_spinbox.delete(0, "end")
        self.fh_spinbox.insert(0, self.master.fh.get())
        self.fh_spinbox.config(font=plain, state="readonly")
        self.fh_spinbox.grid(row=0, column=1, sticky="E")
        tk.Label(g_2, text="[m]", font=plain).grid(row=0, column=2, sticky="W")

        # sh
        tk.Label(g_2, text="      (systemhøyde):", font=plain) \
            .grid(row=1, column=0, sticky="W")
        tk.Label(g_2, text="SH", font=bold) \
            .grid(row=1, column=0, sticky="W")
        self.master.sh.set(self.master.sh_range[0])
        self.sh_spinbox = tk.Spinbox(g_2, from_=self.master.sh_range[1], to=self.master.sh_range[2],
                                     increment=0.1, repeatinterval=60, width=10)
        self.sh_spinbox.delete(0, "end")
        self.sh_spinbox.insert(0, self.master.sh.get())
        self.sh_spinbox.config(font=plain, state="readonly")
        self.sh_spinbox.grid(row=1, column=1, sticky="E")
        tk.Label(g_2, text="[m]", font=plain).grid(row=1, column=2, sticky="W")

        # e
        tk.Label(g_2, text="    (SOK - top fundament):", font=plain) \
            .grid(row=2, column=0, sticky="W")
        tk.Label(g_2, text="e", font=bold) \
            .grid(row=2, column=0, sticky="W")
        self.master.e.set(self.master.e_range[0])
        self.e_spinbox = tk.Spinbox(g_2, from_=self.master.e_range[1], to=self.master.e_range[2],
                                     increment=0.1, repeatinterval=60, width=10)
        self.e_spinbox.delete(0, "end")
        self.e_spinbox.insert(0, self.master.e.get())
        self.e_spinbox.config(font=plain, state="readonly")
        self.e_spinbox.grid(row=2, column=1, sticky="E")
        tk.Label(g_2, text="[m]", font=plain).grid(row=2, column=2, sticky="W")

        # sms
        tk.Label(g_2, text="      (s mast - s spor):", font=plain) \
            .grid(row=3, column=0, sticky="W")
        tk.Label(g_2, text="SMS", font=bold) \
            .grid(row=3, column=0, sticky="W")
        self.master.sms.set(self.master.sms_range[0])
        self.sms_spinbox = tk.Spinbox(g_2, from_=self.master.sms_range[1], to=self.master.sms_range[2],
                                    increment=0.1, repeatinterval=60, width=10)
        self.sms_spinbox.delete(0, "end")
        self.sms_spinbox.insert(0, self.master.sms.get())
        self.sms_spinbox.config(font=plain, state="readonly")
        self.sms_spinbox.grid(row=3, column=1, sticky="E")
        tk.Label(g_2, text="[m]", font=plain).grid(row=3, column=2, sticky="W")

        # mast
        mast = tk.LabelFrame(hoyre, text="Mast", font=bold)
        mast.pack(fill="both")
        tk.Label(mast, text="Stålkvalitet:", font=plain).grid(row=0, column=0)
        tk.Radiobutton(mast, text="S235", font=plain,
                       variable=self.master.s235, value=True).grid(row=0, column=1)
        tk.Radiobutton(mast, text="S355", font=plain,
                       variable=self.master.s235, value=False).grid(row=0, column=2)

        # -------------------------------Avansert/beregn-------------------------------
        av_beregn = tk.LabelFrame(hoyre)
        av_beregn.pack(fill="both")
        self.master.avspenningsbardun.set(True)
        self.master.auto_differansestrekk.set(True)
        self.master.delta_h1.set(0.0)
        self.master.delta_h2.set(0.0)
        self.master.materialkoeff.set(1.05)
        self.master.traverslengde.set(0.6)
        self.master.ec3.set(True)
        self.master.isklasse.set(lister.isklasse_list[2])
        self.master.stromavtaker_type.set(lister.stromavtaker_list[2])
        self.master.brukerdefinert_last.set(False)
        avansert_btn = tk.Button(av_beregn, text="Avansert", font=bold,
                                 command=self._avansert)
        avansert_btn.grid(row=0, column=0, padx=12)
        beregn_btn = tk.Button(av_beregn, text="Kjør beregning", font=bold,
                               command=self._beregn)
        beregn_btn.grid(row=0, column=1, padx=12)
        self.resultater_btn = tk.Button(av_beregn, text="Resultater", font=bold,
                                   fg="blue", command=self._resultater)
        self.resultater_btn.grid(row=0, column=2, padx=12)
        self.resultater_btn.grid_remove()



    def _klima(self):
        """Oppretter vindu for klima."""

        klima_root = tk.Toplevel(self)
        klima_vindu = Klima(klima_root)

    def _avansert(self):
        """Oppretter vindu for avansert."""

        avansert_root = tk.Toplevel(self)
        avansert_vindu = Avansert(avansert_root)

    def _resultater(self):
        """Oppretter vindu for resultater."""

        resultater_root = tk.Toplevel(self)
        resultater_vindu = Resultater(resultater_root)

    def _bidrag(self):
        """Oppretter vindu for bidrag."""

        bidrag_root = tk.Toplevel(self)
        bidrag_vindu = Bidrag(bidrag_root)

    def _beregn(self):
        """Setter manglende inputparametre og kaller skriving av .ini-fil."""

        self.master.siste_for_avspenning.set(False)
        if self._mastefelt.get() == 0:
            self.master.linjemast_utliggere.set(1)
        elif self._mastefelt.get() == 1:
            self.master.linjemast_utliggere.set(2)
        elif self._mastefelt.get() == 2:
            self.master.linjemast_utliggere.set(1)
            self.master.siste_for_avspenning.set(True)

        self.master.fixpunktmast.set(False)
        self.master.fixavspenningsmast.set(False)
        self.master.avspenningsmast.set(False)
        if self._alternative_mastefunksjoner.get():
            if self._alternativ_funksjon.get() == 0:
                self.master.fixpunktmast.set(True)
            elif self._alternativ_funksjon.get() == 1:
                self.master.fixavspenningsmast.set(True)
            elif self._alternativ_funksjon.get() == 2:
                self.master.avspenningsmast.set(True)

        # lagrer verdier fra spinboxer
        self.master.avstand_fixpunkt.set(self.fixavstand_spinbox.get())
        self.master.matefjern_antall.set(self.matefjern_spinbox.get())
        self.master.a1.set(self.a1_spinbox.get())
        self.master.a2.set(self.a2_spinbox.get())
        self.master.h.set(self.h_spinbox.get())
        self.master.hfj.set(self.hfj_spinbox.get())
        self.master.hf.set(self.hf_spinbox.get())
        self.master.hj.set(self.hj_spinbox.get())
        self.master.hr.set(self.hr_spinbox.get())
        self.master.fh.set(self.fh_spinbox.get())
        self.master.sh.set(self.sh_spinbox.get())
        self.master.e.set(self.e_spinbox.get())
        self.master.sms.set(self.sms_spinbox.get())

        self.master.skriv_ini()

        self.alle_master, self.gittermaster, self.bjelkemaster = [], [], []
        self.i = None
        with open("input.ini", "r") as ini:
            g, b, i = main.beregn_master(ini)
            self.alle_master.extend(g)
            self.alle_master.extend(b)
            self.gittermaster.extend(g)
            self.bjelkemaster.extend(b)
            self.i = i

        self.resultater_btn.grid()


class Klima(tk.Frame):
    """Vindu for klimaegenskaper."""

    def __init__(self, *args, **kwargs):
        """Initialiserer vindu."""
        tk.Frame.__init__(self, *args, **kwargs)
        self.pack(fill="both")

        self.M = self.master.master

        # --------------------------------Referansevindhastighet--------------------------------
        refvind_frame = tk.LabelFrame(self, text="Referansevindhastighet", font=bold)
        refvind_frame.grid(row=0, column=0, sticky="W")

        # v_b,0
        tk.Label(refvind_frame, text="v_b,0:",
                 font=plain).grid(row=0, column=0, sticky="W")
        self.refvind_spinbox = tk.Spinbox(refvind_frame, from_=22, to=30, width=10)
        self.refvind_spinbox.delete(0, "end")
        self.refvind_spinbox.insert(0, int(self.M.refvindhastighet.get()))
        self.refvind_spinbox.config(font=plain, state="readonly")
        self.refvind_spinbox.grid(row=0, column=1, sticky="W")
        tk.Label(refvind_frame, text="[m/s]", font=plain).grid(row=0, column=2, sticky="W")

        # --------------------------------c-faktorer--------------------------------
        c_faktorer = tk.LabelFrame(self, text="Faktorer som påvirker basisvindhastigheten", font=bold)
        c_faktorer.grid(row=1, column=0, sticky="W")

        # c_dir
        tk.Label(c_faktorer, text="c_dir:",
                 font=plain).grid(row=0, column=0, sticky="W")
        self.c_dir_spinbox = tk.Spinbox(c_faktorer, values=(0.8, 0.9, 1.0), width=10)
        self.c_dir_spinbox.delete(0, "end")
        self.c_dir_spinbox.insert(0, float(self.M.c_dir.get()))
        self.c_dir_spinbox.config(font=plain, state="readonly")
        self.c_dir_spinbox.grid(row=0, column=1, sticky="W")

        # c_season
        tk.Label(c_faktorer, text="c_season:",
                 font=plain).grid(row=1, column=0, sticky="W")
        self.c_season_spinbox = tk.Spinbox(c_faktorer, values=(0.8, 0.9, 1.0), width=10)
        self.c_season_spinbox.delete(0, "end")
        self.c_season_spinbox.insert(0, float(self.M.c_season.get()))
        self.c_season_spinbox.config(font=plain, state="readonly")
        self.c_season_spinbox.grid(row=1, column=1, sticky="W")

        # c_alt
        tk.Label(c_faktorer, text="c_alt:",
                 font=plain).grid(row=2, column=0, sticky="W")
        self.M.c_alt.set(1.0)
        c_alt_entry = tk.Entry(c_faktorer, textvariable=self.M.c_alt, width=10, state="readonly")
        c_alt_entry.config(font=plain)
        c_alt_entry.grid(row=2, column=1, sticky="W")

        # c_prob
        tk.Label(c_faktorer, text="c_prob:",
                 font=plain).grid(row=3, column=0, sticky="W")
        self.c_prob_spinbox = tk.Spinbox(c_faktorer, from_=0.8, to=1.0, increment=0.01,
                                        repeatinterval=50, width=10)
        self.c_prob_spinbox.delete(0,"end")
        self.c_prob_spinbox.insert(0, float(self.M.c_prob.get()))
        self.c_prob_spinbox.config(font=plain, state="readonly")
        self.c_prob_spinbox.grid(row=3, column=1, sticky="W")

        # -------------------------------Terrengfaktorer-------------------------------
        terrengfaktorer = tk.LabelFrame(self, text="Faktorer (terrengfaktorer) som påvirker"
                                                   " stedets vindhastighet", font=bold)
        terrengfaktorer.grid(row=1, column=1, sticky="W")

        # overgangssoner
        overgangssoner = tk.Checkbutton(terrengfaktorer, text="Overgangssoner",
                                                font=plain, variable=self.M.overgangssoner,
                                                onvalue=True, offvalue=False)
        overgangssoner.grid(row=0, column=0, sticky="W")

        # terrengruhetskategori
        tk.Label(terrengfaktorer, text="Terrengruhetskategori:",
                 font=plain).grid(row=1, column=0, sticky="W")
        terrengruhetskategori_menu = tk.OptionMenu(terrengfaktorer,
                                                   self.M.terrengruhetskategori,
                                                   *[0,1,2,3,4])
        terrengruhetskategori_menu.config(font=plain, width=3)
        terrengruhetskategori_menu.grid(row=2, column=0)

        # høgde over terrenget z
        tk.Label(terrengfaktorer, text="Høgde over terrenget z [m]:",
                 font=plain).grid(row=1, column=1, sticky="W")
        self.z_spinbox = tk.Spinbox(terrengfaktorer, from_=1, to=50,
                                    repeatinterval=50, width=10)
        self.z_spinbox.delete(0, "end")
        self.z_spinbox.insert(0, int(self.M.z.get()))
        self.z_spinbox.config(font=plain, state="readonly")
        self.z_spinbox.grid(row=2, column=1)

        # turbulensintensitet Iv
        tk.Label(terrengfaktorer, text="Turbulensintensitet Iv:",
                 font=plain).grid(row=3, column=0, sticky="W")
        self.M.Iv.set(0.19)
        Iv_entry = tk.Entry(terrengfaktorer, textvariable=self.M.Iv, width=10, state="readonly")
        Iv_entry.config(font=plain)
        Iv_entry.grid(row=4, column=0)

        # turbulensfaktor k_l
        tk.Label(terrengfaktorer, text="Turbulensfaktor k_l:",
                 font=plain).grid(row=3, column=1)
        self.M.k_l.set(1)
        Iv_entry = tk.Entry(terrengfaktorer, textvariable=self.M.k_l, width=10, state="readonly")
        Iv_entry.config(font=plain)
        Iv_entry.grid(row=4, column=1)

        # terrengformfaktor C_0
        tk.Label(terrengfaktorer, text="Terrengformfaktor C_0:",
                 font=plain).grid(row=3, column=2, sticky="W")
        self.C_0_spinbox = tk.Spinbox(terrengfaktorer, from_=0.5, to=1.5,
                                      increment=0.1, repeatinterval=100, width=10)
        self.C_0_spinbox.delete(0, "end")
        self.C_0_spinbox.insert(0, float(self.M.C_0.get()))
        self.C_0_spinbox.config(font=plain, state="readonly")
        self.C_0_spinbox.grid(row=4, column=2)

        # -------------------------------MANUELLE VERDIER-------------------------------
        # Midlertidig implementasjon for å kunne endre vindlast ved beregninger
        manuelle_verdier = tk.LabelFrame(self, text="MANUELLE VERDIER", font=bold)
        manuelle_verdier.grid(row=2, column=0, columnspan=2, sticky="W")

        # referansevindhastighet v_b,0
        tk.Label(manuelle_verdier, text="Referansevindhastighet v_b,0:",
                 font=plain).grid(row=0, column=0, sticky="W")
        refvind_entry = tk.Entry(manuelle_verdier, textvariable=self.M.master.referansevindhastighet, width=10)
        refvind_entry.config(font=plain)
        refvind_entry.grid(row=0, column=1, sticky="E")
        tk.Label(manuelle_verdier, text="[m/s]",
                 font=plain).grid(row=0, column=2, sticky="W")

        # kastvindhastighet
        tk.Label(manuelle_verdier, text="Kastvindhastighet:",
                 font=plain).grid(row=1, column=0, sticky="W")
        kastvind_entry = tk.Entry(manuelle_verdier, textvariable=self.M.master.kastvindhastighet, width=10)
        kastvind_entry.config(font=plain)
        kastvind_entry.grid(row=1, column=1, sticky="E")
        tk.Label(manuelle_verdier, text="[m/s]",
                 font=plain).grid(row=1, column=2, sticky="W")

        # vindkasthastighetstrykk
        tk.Label(manuelle_verdier, text="Vindkasthastighetstrykk:",
                 font=plain).grid(row=2, column=0, sticky="W")
        vindkast_entry = tk.Entry(manuelle_verdier, textvariable=self.M.master.vindkasthastighetstrykk, width=10)
        vindkast_entry.config(font=plain)
        vindkast_entry.grid(row=2, column=1, sticky="E")
        tk.Label(manuelle_verdier, text="[kN/m^2]",
                 font=plain).grid(row=2, column=2, sticky="W")

        # isklasse
        tk.Label(manuelle_verdier, text="Isklasse:",
                 font=plain).grid(row=3, column=0)
        self.isklasse_menu = tk.OptionMenu(manuelle_verdier, self.M.master.isklasse,
                                                   *lister.isklasse_list)
        self.isklasse_menu.config(font=plain, width=12)
        self.isklasse_menu.grid(row=3, column=1)
        tk.Label(manuelle_verdier, text="(Kun gjeldende ved NEK-beregning)",
                 font=italic).grid(row=4, column=0, columnspan=2, sticky="E")

        # -------------------------------Lukk vindu------------------------------
        lukk = tk.Frame(self)
        lukk.grid(row=2, column=1, sticky="SE")
        lukk_btn = tk.Button(lukk, text="Lukk vindu", font=bold, command=self._lukk_vindu)
        lukk_btn.pack(padx=5, pady=5)

    def _lukk_vindu(self):
        """Lagrer verdier fra spinboxer og lukker vindu."""

        self.M.refvindhastighet.set(self.refvind_spinbox.get())
        self.M.c_dir.set(self.c_dir_spinbox.get())
        self.M.c_season.set(self.c_season_spinbox.get())
        self.M.c_prob.set(self.c_prob_spinbox.get())
        self.M.z.set(self.z_spinbox.get())
        self.M.C_0.set(self.C_0_spinbox.get())

        # lukker vindu
        self.master.destroy()



class Avansert(tk.Frame):
    """Vindu for avanserte funksjoner."""

    def __init__(self, *args, **kwargs):
        """Initialiserer vindu."""
        tk.Frame.__init__(self, *args, **kwargs)
        self.pack(fill="both")

        self.M = self.master.master

        # -------------------------------Alternativer-------------------------------
        alternativer = tk.LabelFrame(self, text="Avanserte alternativer", font=bold)
        alternativer.pack(fill="both")

        # beregningsprosedyre
        tk.Label(alternativer, text="Beregningsprosedyre:",
                 font=plain).grid(row=0, column=0, sticky="W")
        tk.Radiobutton(alternativer, text="Eurokode (EC3)", font=plain,
                       variable=self.M.master.ec3, value=True).grid(row=0, column=1)
        tk.Radiobutton(alternativer, text="Bransjestandard (NEK)", font=plain,
                       variable=self.M.master.ec3, value=False).grid(row=0, column=2)

        # materialkoeffisient
        tk.Label(alternativer, text="Materialkoeffisient:",
                 font=plain).grid(row=1, column=0, sticky="W")
        self.materialkoeff_spinbox = tk.Spinbox(alternativer, from_=1.0, to=1.15,
                                                increment=0.05, width=10)
        self.materialkoeff_spinbox.delete(0, "end")
        self.materialkoeff_spinbox.insert(0, float(self.M.master.materialkoeff.get()))
        self.materialkoeff_spinbox.config(font=plain, state="readonly")
        self.materialkoeff_spinbox.grid(row=1, column=1, sticky="E")
        tk.Label(alternativer, text="Anbefalt: 1.05 (EC3), 1.10 (NEK)",
                 font=italic).grid(row=1, column=2, columnspan=2, sticky="W")

        # traverslengde
        tk.Label(alternativer, text="Traverslengde hver side:",
                 font=plain).grid(row=2, column=0, sticky="W")
        self.traverslengde_spinbox = tk.Spinbox(alternativer, from_=0.3, to=1.0,
                                           increment=0.1, width=10)
        self.traverslengde_spinbox.delete(0, "end")
        self.traverslengde_spinbox.insert(0, float(self.M.master.traverslengde.get()))
        self.traverslengde_spinbox.config(font=plain, state="readonly")
        self.traverslengde_spinbox.grid(row=2, column=1, sticky="E")
        tk.Label(alternativer, text="[m]",
                 font=plain).grid(row=2, column=2, sticky="W")

        # strømavtaker
        tk.Label(alternativer, text="Strømavtakerbredde:",
                 font=plain).grid(row=3, column=0, sticky="W")
        system_menu = tk.OptionMenu(alternativer, self.M.master.stromavtaker_type,
                                    *lister.stromavtaker_list)
        system_menu.config(font=plain, width=7)
        system_menu.grid(row=3, column=1, sticky="E")
        tk.Label(alternativer, text="[mm]",
                 font=plain).grid(row=3, column=2, sticky="W")


        # avspenningsbardun
        bardun_checkbtn = tk.Checkbutton(alternativer, text="Avspenningsbardun (dersom fixavsp.- eller avsp.mast)",
                                           font=plain, variable=self.M.master.avspenningsbardun,
                                           onvalue=True, offvalue=False)
        bardun_checkbtn.grid(row=4, column=0, columnspan=3, sticky="W")

        # differansestrekk
        autodiff_checkbtn = tk.Checkbutton(alternativer, text="Automatisk beregning av differansestrekk",
                                         font=plain, variable=self.M.master.auto_differansestrekk,
                                         onvalue=True, offvalue=False)
        autodiff_checkbtn.grid(row=5, column=0, columnspan=3, sticky="W")
        tk.Label(alternativer, text="   Differansestrekk:",
                 font=plain).grid(row=6, column=0, sticky="E")
        self.differansestrekk_spinbox = tk.Spinbox(alternativer, from_=0.0, to=2.0,
                                                   increment=0.05, width=10)
        self.differansestrekk_spinbox.delete(0, "end")
        self.differansestrekk_spinbox.insert(0, float(self.M.master.differansestrekk.get()))
        self.differansestrekk_spinbox.config(font=plain, state="readonly")
        self.differansestrekk_spinbox.grid(row=6, column=1, sticky="E")
        tk.Label(alternativer, text="[kN]",
                 font=plain).grid(row=6, column=2, sticky="W")

        # høydedifferanse
        alternativer_2 = tk.Frame(alternativer, relief="groove", bd=1)
        alternativer_2.grid(row=7, column=0, columnspan=3)
        tk.Label(alternativer_2, text="Ledningers midlere innfestingshøyde i \n"
                                      "aktuell mast i forhold til...",
                font=plain).grid(row=0, column=0, columnspan=3)
        tk.Label(alternativer_2, text="forrige mast:",
                 font=plain).grid(row=1, column=0, sticky="E")
        tk.Entry(alternativer_2, textvariable=self.M.master.delta_h1,
                 font=plain, width=10).grid(row=1, column=1)
        tk.Label(alternativer_2, text="[m]",
                 font=plain).grid(row=1, column=2, sticky="W")
        tk.Label(alternativer_2, text="neste mast:",
                 font=plain).grid(row=2, column=0, sticky="E")
        tk.Entry(alternativer_2, textvariable=self.M.master.delta_h2,
                 font=plain, width=10).grid(row=2, column=1)
        tk.Label(alternativer_2, text="[m]",
                 font=plain).grid(row=2, column=2, sticky="W")
        tk.Label(alternativer_2, text="(Positiv verdi = aktuell mast høyere)",
                 font=italic).grid(row=3, column=0, columnspan=3)

        # -----------------------------Brukerdefinert last-----------------------------
        brukerdef_frame = tk.LabelFrame(self, text="Egendefinert last", font=bold)
        brukerdef_frame.pack(fill="both")

        brukerdef_checkbtn = tk.Checkbutton(brukerdef_frame, text="Aktiver egendefinert kraftvektor og vindareal",
                                           font=plain, variable=self.M.master.brukerdefinert_last,
                                           onvalue=True, offvalue=False)
        brukerdef_checkbtn.grid(row=0, column=0, columnspan=2, sticky="W")

        # lastvektor
        lastvektor_frame = tk.LabelFrame(brukerdef_frame, text="Lastvektor", font=bold)
        lastvektor_frame.grid(row=1, column=0, sticky="W")
        tk.Label(lastvektor_frame, text="f_x = positiv nedover",
                 font=italic).grid(row=4, column=0, columnspan=3, sticky="E")

        tk.Label(lastvektor_frame, text="f_x:",
                 font=plain).grid(row=1, column=0, sticky="E")
        tk.Entry(lastvektor_frame, textvariable=self.M.master.f_x,
                 font=plain, width=10).grid(row=1, column=1)
        tk.Label(lastvektor_frame, text="[N]",
                 font=plain).grid(row=1, column=2, sticky="W")
        tk.Label(lastvektor_frame, text="f_y:",
                 font=plain).grid(row=2, column=0, sticky="E")
        tk.Entry(lastvektor_frame, textvariable=self.M.master.f_y,
                 font=plain, width=10).grid(row=2, column=1)
        tk.Label(lastvektor_frame, text="[N]",
                 font=plain).grid(row=2, column=2, sticky="W")
        tk.Label(lastvektor_frame, text="f_z:",
                 font=plain).grid(row=3, column=0, sticky="E")
        tk.Entry(lastvektor_frame, textvariable=self.M.master.f_z,
                 font=plain, width=10).grid(row=3, column=1)
        tk.Label(lastvektor_frame, text="[N]",
                 font=plain).grid(row=3, column=2, sticky="W")

        # eksentrisitet
        eksentrisitet_frame = tk.LabelFrame(brukerdef_frame, text="Eksentrisitet fra masteinnspenning", font=bold)
        eksentrisitet_frame.grid(row=1, column=1, sticky="W")
        tk.Label(eksentrisitet_frame, text="e_x = positiv oppover",
                 font=italic).grid(row=4, column=0, columnspan=3, sticky="E")

        tk.Label(eksentrisitet_frame, text="e_x:",
                 font=plain).grid(row=1, column=0, sticky="E")
        tk.Entry(eksentrisitet_frame, textvariable=self.M.master.e_x,
                 font=plain, width=10).grid(row=1, column=1)
        tk.Label(eksentrisitet_frame, text="[m]",
                 font=plain).grid(row=1, column=2, sticky="W")
        tk.Label(eksentrisitet_frame, text="e_y:",
                 font=plain).grid(row=2, column=0, sticky="E")
        tk.Entry(eksentrisitet_frame, textvariable=self.M.master.e_y,
                 font=plain, width=10).grid(row=2, column=1)
        tk.Label(eksentrisitet_frame, text="[m]",
                 font=plain).grid(row=2, column=2, sticky="W")
        tk.Label(eksentrisitet_frame, text="e_z:",
                 font=plain).grid(row=3, column=0, sticky="E")
        tk.Entry(eksentrisitet_frame, textvariable=self.M.master.e_z,
                 font=plain, width=10).grid(row=3, column=1)
        tk.Label(eksentrisitet_frame, text="[m]",
                 font=plain).grid(row=3, column=2, sticky="W")

        # vindareal
        areal_frame = tk.LabelFrame(brukerdef_frame, text="Vindfang", font=bold)
        areal_frame.grid(row=2, column=0, columnspan=2, sticky="W")
        tk.Label(areal_frame, text="Effektivt areal for vind...",
                 font=plain).grid(row=0, column=0, columnspan=3)

        tk.Label(areal_frame, text="normalt sporet (A_xy):",
                 font=plain).grid(row=1, column=0, sticky="E")
        tk.Entry(areal_frame, textvariable=self.M.master.a_vind,
                 font=plain, width=10).grid(row=1, column=1)
        tk.Label(areal_frame, text="[m^2]",
                 font=plain).grid(row=1, column=2, sticky="W")
        tk.Label(areal_frame, text="parallelt sporet (A_xz):",
                 font=plain).grid(row=2, column=0, sticky="E")
        tk.Entry(areal_frame, textvariable=self.M.master.a_vind_par,
                 font=plain, width=10).grid(row=2, column=1)
        tk.Label(areal_frame, text="[m^2]",
                 font=plain).grid(row=2, column=2, sticky="W")

        # -------------------------------Lukk vindu-------------------------------
        lukk = tk.Frame(self)
        lukk.pack()
        lukk_btn = tk.Button(lukk, text="Lukk vindu", font=bold, command=self._lukk_vindu)
        lukk_btn.pack(padx=5, pady=5)

    def _lukk_vindu(self):
        """Lagrer verdier fra spinboxer og lukker vindu."""

        self.M.master.materialkoeff.set(self.materialkoeff_spinbox.get())
        self.M.master.traverslengde.set(self.traverslengde_spinbox.get())
        self.M.master.differansestrekk.set(self.differansestrekk_spinbox.get())

        # lukker vindu
        self.master.destroy()


class Resultater(tk.Frame):
    """Vindu for resultater."""

    def __init__(self, *args, **kwargs):
        """Initialiserer vindu."""
        tk.Frame.__init__(self, *args, **kwargs)
        self.pack(fill="both")

        self.M = self.master.master

        hovedvindu = tk.LabelFrame(self, text="Resultater", font=bold)
        hovedvindu.pack()

        tk.Label(hovedvindu, text="Krefter i bruddgrensetilstand",
                 font=plain).grid(row=0, column=0)
        tk.Label(hovedvindu, text="M, T = [kNm]    V, N = [kN]",
                 font=italic).grid(row=1, column=0)
        tk.Label(hovedvindu, text="Mast:",
                 font=plain).grid(row=1, column=1, sticky="E")
        system_menu = tk.OptionMenu(hovedvindu, self.M.mast_resultater,
                                    *lister.master_list)
        system_menu.config(font=plain, width=7)
        system_menu.grid(row=1, column=2, sticky="W")

        self.tracer = self.M.mast_resultater.trace("w", self.callback_krefter)


        self.kraftboks = tk.Text(hovedvindu, width=100, height=16)
        self.kraftboks.grid(row=2, column=0, columnspan=3)
        self._skriv_krefter()


        tk.Label(hovedvindu, text="Velg mastetype:",
                 font=plain).grid(row=3, column=0)
        tk.Radiobutton(hovedvindu, text="Gittermast", font=plain,
                       variable=self.M.gittermast, value=True,
                       command=self._skriv_master).grid(row=3, column=1)
        tk.Radiobutton(hovedvindu, text="Bjelkemast", font=plain,
                       variable=self.M.gittermast, value=False,
                       command=self._skriv_master).grid(row=3, column=2)

        tk.Label(hovedvindu, text="D = [mm]    phi = [grader]",
                 font=italic).grid(row=4, column=0)

        self.masteboks = tk.Text(hovedvindu, width=100, height=18)
        self.masteboks.grid(row=5, column=0, columnspan=3)
        self._skriv_master()


        # -------------------------------Knapper-------------------------------
        knapper_frame = tk.Frame(self)
        knapper_frame.pack()
        bidrag_btn = tk.Button(knapper_frame, text="Vis kraftbidrag", font=bold,
                               command=self.M._bidrag)
        bidrag_btn.pack(padx=20, pady=5, side="left")
        self.eksporter_btn = tk.Button(knapper_frame, text="Eksporter til Fundamast",
                                  font=bold, command=self._eksporter_fundamast)
        self.eksporter_btn.pack(padx=20, pady=5, side="left")
        lukk_btn = tk.Button(knapper_frame, text="Lukk vindu",
                             font=bold, command=self.lukk_resultater)
        lukk_btn.pack(padx=20, pady=5, side="left")

    def callback_krefter(self, *args):
        self._skriv_krefter()

    def lukk_resultater(self):
        self.M.mast_resultater.trace_vdelete("w", self.tracer)
        self.master.destroy()

    def _skriv_krefter(self):
        """Skriver krefter til tekstboks."""

        if self.kraftboks.get(0.0) is not None:
            self.kraftboks.delete(1.0, "end")

        mast = None
        for m in self.M.alle_master:
            if m.navn==self.M.mast_resultater.get():
                mast = m
                break

        grensetilstander = ("(1) Bruddgrensetilstand",
                            "(2) Bruksgrense (forskyvning KL)",
                            "(3) Bruksgrense (forskyvning totalt)")
        max_bredde_tilstand = 0
        for g in grensetilstander:
            max_bredde_tilstand = len(g) if len(g)>max_bredde_tilstand else max_bredde_tilstand

        kolonnebredde = 8

        s = "Grensetilstand:".ljust(max_bredde_tilstand + 1)
        kolonner = ("My", "Vy", "Mz", "Vz", "N", "T")
        for k in kolonner:
            s += k.rjust(kolonnebredde)
        s += "\n{}\n".format("-"*(max_bredde_tilstand+1+kolonnebredde*len(kolonner)))

        # (1) Bruddgrensetilstand
        s += grensetilstander[0].ljust(max_bredde_tilstand + 1)
        K = mast.tilstand_My_max.K / 1000
        for n in range(6):
            if n==5:
                k = str(round(K[n],2))
            else:
                k = str(round(K[n],1))
            k = "0" if (k == "0.0" or k == "-0.0") else k
            s += k.rjust(kolonnebredde)
        s += "\n"

        # (2) Bruksgrense (forskyvning KL)
        s += grensetilstander[1].ljust(max_bredde_tilstand + 1)
        K = mast.tilstand_Dz_kl_max.K / 1000
        for n in range(6):
            if n==5:
                k = str(round(K[n], 2))
            else:
                k = str(round(K[n], 1))
            k = "0" if (k == "0.0" or k == "-0.0") else k
            s += k.rjust(kolonnebredde)
        s += "\n"

        # (3) Bruksgrense (forskyvning totalt)
        s += grensetilstander[2].ljust(max_bredde_tilstand + 1)
        K = mast.tilstand_Dz_tot_max.K / 1000
        for n in range(6):
            if n==5:
                k = str(round(K[n],2))
            else:
                k = str(round(K[n],1))
            k = "0" if (k == "0.0" or k == "-0.0") else k
            s += k.rjust(kolonnebredde)
        s += "\n\n"

        lastsituasjon = mast.tilstand_My_max.lastsituasjon
        vindretning = "vind fra mast mot spor"
        if mast.tilstand_My_max.vindretning == 1:
            vindretning = "vind fra spor mot mast"
        elif mast.tilstand_My_max.vindretning == 2:
            vindretning = "vind parallelt spor"

        s += "Dimensjonerende lastsituasjon:  {}, ".format(lastsituasjon)
        s += "{}\n\n".format(vindretning)

        T = round(mast.tilstand_T_max.K[5] / 1000, 2)
        s += "Maksimal T ved -40C:  {} kNm\n".format(T)

        if mast.tilstand_T_max_ulykke is not None:
            T = round(mast.tilstand_T_max_ulykke.K[5] / 1000, 2)
            s += "Maksimal T ved brudd i KL (ulykkeslast):  {} kNm\n".format(T)

        t =  mast.tilstand_My_max
        s += "\nLastfaktorer:\nEgenvekt: {}    Kabelstrekk: {}\n".format(t.faktorer["G"],
                                                                       t.faktorer["L"])
        s += "Temperatur: {:.4g}    Snø/is: {:.4g}    " \
             "Vind: {:.4g}\n\n".format(t.faktorer["T"]*t.faktorer["psi_T"],
                                       t.faktorer["S"]*t.faktorer["psi_S"],
                                       t.faktorer["V"]*t.faktorer["psi_V"])

        self.kraftboks.insert("end", s)

    def _skriv_master(self):
        self.masteboks.delete(1.0, "end")
        masteliste = self.M.gittermaster if self.M.gittermast.get() else self.M.bjelkemaster

        anbefalt_mast = None
        for mast in masteliste:
            if mast.h_max>=self.M.master.h.get() and mast.tilstand_UR_max.utnyttelsesgrad<=1.0:
                anbefalt_mast = mast
                break

        s = "\n\n"
        if anbefalt_mast:
            s += "Anbefalt mast:  {}   ".format(anbefalt_mast.navn)
            UR = round(anbefalt_mast.tilstand_UR_max.utnyttelsesgrad * 100, 1)
            s += "({:.1f}% utnyttelsesgrad, høydekrav OK)\n\n\n".format(UR)
        else:
            s += "Ingen master oppfyller kravene til utnyttelsesgrad og høyde.\n\n\n"

        max_bredde_navn = len("Navn:")
        for mast in masteliste:
            max_bredde_navn = len(mast.navn) if len(mast.navn)>max_bredde_navn else max_bredde_navn

        kolonnebredde = 10

        s += "Navn:".ljust(max_bredde_navn + 1)
        kolonner = ("UR", "Dz(tot)", "Dz(KL)", "phi(tot)", "phi(KL)", "Max.høyde")
        for k in kolonner:
            if k=="Max.høyde":
                s += k.rjust(kolonnebredde+1)
            else:
                s += k.rjust(kolonnebredde)
        s += "\n{}\n".format("-"*(max_bredde_navn+2+kolonnebredde*len(kolonner)))

        for mast in masteliste:
            if mast.navn=="H6" and self.M.master.s235.get():
                s += "H6-mast kan ikke velges da stålkvaliteten er S235.\n"
            else:
                s += mast.navn.ljust(max_bredde_navn+1)

                # Utnyttelsesgrad
                UR = round(mast.tilstand_UR_max.utnyttelsesgrad*100, 1)
                s += "{}%".format(UR).rjust(kolonnebredde)

                # Forskyvning tot
                d = str(round(mast.tilstand_Dz_tot_max.K_D[1], 1))
                d = "0" if (d == "0.0" or d == "-0.0") else d
                s += d.rjust(kolonnebredde)

                # Forskyvning kl
                d = str(round(mast.tilstand_Dz_kl_max.K_D[1], 1))
                d = "0" if (d == "0.0" or d == "-0.0") else d
                s += d.rjust(kolonnebredde)

                # Torsjonsvinkel tot
                d = str(round(mast.tilstand_phi_tot_max.K_D[2], 2))
                d = "0" if (d == "0.0" or d == "-0.0") else d
                s += d.rjust(kolonnebredde)

                # Torsjonsvinkel kl
                d = str(round(mast.tilstand_phi_kl_max.K_D[2], 2))
                d = "0" if (d == "0.0" or d == "-0.0") else d
                s += d.rjust(kolonnebredde)

                # Maksimal tillatt høyde
                h_max = round(mast.h_max, 1)
                s += (str(h_max)+"m").rjust(kolonnebredde+1)

                s += "\n"

        s += "\n"
        s += "Dz = forskyvning av kontakttråd normalt sporretningen\n"
        s += "phi = mastens torsjonsvinkel i kontakttrådhøyde\n"

        self.masteboks.insert("end", s)

    def _eksporter_fundamast(self):
        """Eksporterer krefter til FUNDAMAST.DAT."""

        mast = None
        for m in self.M.alle_master:
            if m.navn==self.M.mast_resultater.get():
                mast = m
                break

        s = "*** Reaksjonskrefter for {}  (KL_mast, {})\n".format(mast.navn, self.M.i.dato)
        s += "Banestrekning {}, Mast nr. {}, ".format(self.M.master.banestrekning.get(),
                                                      self.M.master.mastenr.get())
        # Hvor finnes fundamentnr.?
        s += "Fundament nr. {}, Prosjektnummer {}\n".format(self.M.master.prosjektnr.get(),
                                                      self.M.master.prosjektnr.get())
        s += "*** Systemkonfigurasjon SMS  - FH  - e-mål\n"
        s += "{:.1f}\n{:.1f}\n{:.1f}\n".format(self.M.master.sms.get(),
                                               self.M.master.fh.get(),
                                               self.M.master.e.get())
        s += "*** Bruddgrense    N (kN) - V (kN) - M (kNm)\n"
        s += "{:.1f}\n{:.1f}\n{:.1f}\n".format(abs(mast.tilstand_My_max.K[4] / 1000),
                                               abs(mast.tilstand_My_max.K[3] / 1000),
                                               abs(mast.tilstand_My_max.K[0] / 1000))
        s += "*** Bruksgrense 2  N (kN) - V (kN) - M (kNm)\n"
        s += "{:.1f}\n{:.1f}\n{:.1f}\n".format(abs(mast.tilstand_Dz_kl_max.K[4] / 1000),
                                               abs(mast.tilstand_Dz_kl_max.K[3] / 1000),
                                               abs(mast.tilstand_Dz_kl_max.K[0] / 1000))
        s += "*** Bruksgrense 3  N (kN) - V (kN) - M (kNm)\n"
        s += "{:.1f}\n{:.1f}\n{:.1f}\n".format(abs(mast.tilstand_Dz_tot_max.K[4] / 1000),
                                               abs(mast.tilstand_Dz_tot_max.K[3] / 1000),
                                               abs(mast.tilstand_Dz_tot_max.K[0] / 1000))

        with open("FUNDAMAST.DAT", "w+") as fil:
            fil.write(s)

        self.eksporter_btn.config(text="Eksport av {} fullført".format(mast.navn), font=plain)



class Bidrag(tk.Frame):
    """Vindu for kraftbidrag."""

    def __init__(self, *args, **kwargs):
        """Initialiserer vindu."""
        tk.Frame.__init__(self, *args, **kwargs)
        self.pack(fill="both")

        self.M = self.master.master

        hovedvindu = tk.LabelFrame(self, text="Bidragsliste", font=bold)
        hovedvindu.pack()

        tk.Label(hovedvindu, text="Reaksjonskraftbidrag ved masteinnspenning fra individuelle krefter",
                 font=plain).grid(row=0, column=0)
        tk.Label(hovedvindu, text="M, T = [kNm]    V, N = [kN]",
                 font=italic).grid(row=1, column=0)
        tk.Label(hovedvindu, text="Mast:",
                 font=plain).grid(row=1, column=1, sticky="E")
        system_menu = tk.OptionMenu(hovedvindu, self.M.mast_resultater,
                                    *lister.master_list)
        system_menu.config(font=plain, width=7)
        system_menu.grid(row=1, column=2, sticky="W")

        self.tracer = self.M.mast_resultater.trace("w", self.callback_bidrag)

        self.bidragsboks = tk.Text(hovedvindu, width=100, height=50)
        self.bidragsboks.grid(row=2, column=0, columnspan=3)

        self._skriv_bidrag()

        lukk_btn = tk.Button(self, text="Lukk vindu",
                             font=bold, command=self.lukk_bidrag)
        lukk_btn.pack(padx=5, pady=5, side="right")

    def callback_bidrag(self, *args):
        self._skriv_bidrag()

    def lukk_bidrag(self):
        self.M.mast_resultater.trace_vdelete("w", self.tracer)
        self.master.destroy()

    def _skriv_bidrag(self):
        """Skriver bidrag inkl. alle lastfaktorer."""

        if self.bidragsboks.get(0.0) is not None:
            self.bidragsboks.delete(1.0, "end")

        mast = None
        for m in self.M.alle_master:
            if m.navn==self.M.mast_resultater.get():
                mast = m
                break

        krefter_alfabetisk = sorted(mast.tilstand_My_max.F,
                                 key=lambda j: j.navn)

        max_bredde_navn = 0
        for j in krefter_alfabetisk:
            max_bredde_navn = len(j.navn) if len(j.navn)>max_bredde_navn else max_bredde_navn

        kolonnebredde = 8

        s = "Navn:".ljust(max_bredde_navn+1)
        kolonner = ("My", "Vy", "Mz", "Vz", "N", "T")
        for k in kolonner:
            s += k.rjust(kolonnebredde)
        s += "\n{}\n".format("-"*(max_bredde_navn+1+kolonnebredde*len(kolonner)))

        strekk_ledninger = {}

        for j in krefter_alfabetisk:
            s += j.navn.ljust(max_bredde_navn+1)

            if j.s is not None:
                strekk_ledninger[j.navn.split(": ")[1]] = j.s

            faktor = 1.0
            if j.type[1] == 0:
                faktor = mast.tilstand_My_max.faktorer["G"]
            elif j.type[1] == 1:
                faktor = mast.tilstand_My_max.faktorer["L"]
            elif j.type[1] == 2:
                faktor = mast.tilstand_My_max.faktorer["T"] * mast.tilstand_My_max.faktorer["psi_T"]
            elif j.type[1] == 3:
                faktor = mast.tilstand_My_max.faktorer["S"] * mast.tilstand_My_max.faktorer["psi_S"]
            elif j.type[1] == 4:
                faktor = mast.tilstand_My_max.faktorer["V"] * mast.tilstand_My_max.faktorer["psi_V"]

            R = self._beregn_reaksjonskrefter_enkeltvis(j, numpy.sign(mast.tilstand_My_max.K[5]))
            K = faktor * numpy.sum(numpy.sum(R, axis=0), axis=0) / 1000

            for n in range (6):
                if n==5:
                    k = str(round(K[n],2))
                else:
                    k = str(round(K[n],1))
                k = "0" if (k == "0.0" or k == "-0.0") else k
                s += k.rjust(kolonnebredde)
            s += "\n"

        if strekk_ledninger:
            s += "\n\nStrekk i fastavspente ledninger (uten lastfaktor):"
            max_bredde_navn = 0
            for navn in strekk_ledninger:
                max_bredde_navn = len(navn) if len(navn) > max_bredde_navn else max_bredde_navn
            for navn in strekk_ledninger:
                s += "\n{}:".format(navn).ljust(max_bredde_navn+4)
                s += "{:.2f} kN".format(strekk_ledninger[navn]/1000)

        self.bidragsboks.insert("end", s)


    def _beregn_reaksjonskrefter_enkeltvis(self, j, sign):
        """Beregner reaksjonskrefter ved masteinnspenning grunnet kraft ``j``.

        :param Kraft j: :class:`Kraft`-objekt påført systemet
        :param float sign: Angir fortegn på torsjonsmomentet
        :return: Matrise med reaksjonskrefter
        :rtype: :class:`numpy.array`
        """

        # Initierer R-matrisen for reaksjonskrefter
        R = numpy.zeros((5, 8, 6))

        f = j.f

        if not numpy.count_nonzero(j.q) == 0:
            f = numpy.array([j.q[0] * j.b, j.q[1] * j.b, j.q[2] * j.b])

        # Sorterer bidrag til reaksjonskrefter
        R[j.type[1], j.type[0], 0] = f[0] * j.e[2] + f[2] * (-j.e[0])
        R[j.type[1], j.type[0], 1] = f[1]
        R[j.type[1], j.type[0], 2] = f[0] * (-j.e[1]) + f[1] * j.e[0]
        R[j.type[1], j.type[0], 3] = f[2]
        R[j.type[1], j.type[0], 4] = f[0]
        if j.navn.startswith("Sidekraft: KL"):
            R[j.type[1], j.type[0], 5] = f[1] * (-j.e[2]) + f[2] * j.e[1]
        else:
            sign = 1 if sign == 0 else sign
            R[j.type[1], j.type[0], 5] = sign*(abs(f[1] * (-j.e[2])) + abs(f[2] * j.e[1]))

        return R




class ToolTip(object):
    """Klasse for visning av tooltips.

    Originalkode for implementasjon av tooltips hentet fra Voidspace_.

    .. _Voidspace: http://www.voidspace.org.uk/python/weblog/arch_d7_2006_07_01.shtml

    """

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, master, text):
        """Viser tekst i tooltip-vindu."""

        self.text = text
        if text == "km":
            km_gyldig = lister.kilometer[master.banestrekning.get()]  # Gyldige km for gitt banestrekke
            self.text = "Vennligst oppgi km mellom {} og {}".format(km_gyldig[0], km_gyldig[1])
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        try:
            # For Mac OS
            tw.tk.call("::tk::unsupported::MacWindowStyle",
                       "style", tw._w,
                       "help", "noActivates")
        except tk.TclError:
            pass
        label = tk.Label(tw, text=self.text, justify="left",
                      background="#ffffe0", relief="solid", borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        """Gjemmer tekst i tooltip-vindu."""

        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def createToolTip(master, widget, text):
    """Oppretter tooltip og binder det til visning ved mouse-over."""
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(master, text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)






if __name__ == "__main__":

    # Kjører program
    root = KL_mast()
    hovedvindu = Hovedvindu(root)
    root.mainloop()

