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
        #self.geometry("{}x{}".format(self.x, self.y))


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
        self.a1 = tk.DoubleVar()
        self.a2 = tk.DoubleVar()
        self.delta_h1 = tk.DoubleVar()
        self.delta_h2 = tk.DoubleVar()
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
                                     ("a1", self.a1.get()), ("a2", self.a2.get()),
                                     ("delta_h1", self.delta_h1.get()), ("delta_h2", self.delta_h2.get()),
                                     ("vindkasthastighetstrykk", self.vindkasthastighetstrykk.get())])
        cfg["Geometri"] = OrderedDict([("h", self.h.get()), ("hfj", self.hfj.get()),
                                       ("hf", self.hf.get()), ("hj", self.hj.get()),
                                       ("hr", self.hr.get()), ("fh", self.fh.get()),
                                       ("sh", self.sh.get()), ("e", self.e.get()),
                                       ("sms", self.sms.get())])
        cfg["Div"] = OrderedDict([("s235", self.s235.get()), ("materialkoeff", self.materialkoeff.get()),
                                  ("traverslengde", self.traverslengde.get()),
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

        # Initialiserer primærvariabler
        self.master.banestrekning.set(lister.kilometer_list[0])
        self.master.km.set(lister.kilometer[lister.kilometer_list[0]][0])
        self.master.prosjektnr.set(0)
        self.master.mastenr.set(0)
        self.master.signatur.set("ANONYM")
        today = date.today()
        self.master.dato.set("{}.{}.{}".format(today.day, today.month, today.year))
        self.master.avstand_fixpunkt.set(700)
        self.master.strekkutligger.set(True)
        self.master.matefjern_antall.set(1)
        self.master.at_type.set(lister.at_list[0])
        self.master.jord_type.set(lister.jord_list[0])
        self.master.systemnavn.set(lister.system_list[0])
        self.master.radius.set(lister.radius_list[11])
        self.master.a1.set(63.0)
        self.master.a2.set(63.0)
        self.master.vindkasthastighetstrykk.set(710)
        self.master.h.set(8.0)
        self.master.hfj.set(10.0)
        self.master.hf.set(7.8)
        self.master.hj.set(7.0)
        self.master.hr.set(7.2)
        self.master.fh.set(5.6)
        self.master.sh.set(1.6)
        self.master.e.set(0.0)
        self.master.sms.set(3.5)
        self.master.avspenningsbardun.set(True)
        self.master.auto_differansestrekk.set(True)
        self.master.delta_h1.set(0.0)
        self.master.delta_h2.set(0.0)
        self.master.materialkoeff.set(1.05)
        self.master.traverslengde.set(0.6)
        self.master.ec3.set(True)
        self.master.isklasse.set(lister.isklasse_list[2])
        self.master.brukerdefinert_last.set(False)

        # Hjelpevariabler, hovedvindu
        self._mastefelt = tk.IntVar()
        self._alternative_mastefunksjoner = tk.BooleanVar()
        self._alternativ_funksjon = tk.IntVar()
        self._hoyfjellsgrense = tk.BooleanVar()
        self._samme_avstand_a = tk.BooleanVar()

        # Hjelpevariabler, vind
        self.referansevindhastighet = tk.IntVar()
        self.c_dir = tk.DoubleVar()
        self.c_season = tk.DoubleVar()
        self.c_alt = tk.DoubleVar()
        self.region = tk.StringVar()
        self.H = tk.IntVar()
        self.c_prob = tk.DoubleVar()
        self.overgangssoner = tk.BooleanVar()
        self.terrengruhetskategori = tk.IntVar()
        self.z = tk.IntVar()
        self.C_0 = tk.DoubleVar()

        # Hjelpevariabler, avansert
        self.stromavtakerbredde = tk.StringVar()

        # Hjelpevariabel, resultater
        self.mast_resultater = tk.StringVar()
        self.gittermast = tk.BooleanVar()

        # initierer
        self._mastefelt.set(0)
        self._alternative_mastefunksjoner.set(False)
        self._alternativ_funksjon.set(0)
        self._hoyfjellsgrense.set(False)
        self._samme_avstand_a.set(True)
        self.referansevindhastighet.set(22)
        self.c_dir.set(1.0)
        self.c_season.set(1.0)
        self.c_alt.set(1.0)
        self.region.set("Sør-Norge ekskl. Nord-Trøndelag")
        self.H.set(900)
        self.c_prob.set(1.00)
        self.overgangssoner.set(False)
        self.terrengruhetskategori.set(2)
        self.z.set(10)
        self.C_0.set(1)
        self.stromavtakerbredde.set(lister.stromavtaker_list[2])
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
        tk.Label(info, text="Banestrekning:", font=plain).grid(row=1, column=0, sticky="E")
        strekning_menu = tk.OptionMenu(info, self.master.banestrekning, *lister.kilometer_list)
        strekning_menu.config(font=plain)
        strekning_menu.grid(row=1, column=1, sticky="EW")

        # km
        tk.Label(info, text="Km:", font=plain).grid(row=1, column=2, sticky="E")
        km_entry = tk.Entry(info, textvariable=self.master.km, bg="red")
        km_entry.config(font=plain)
        km_entry.grid(row=1, column=3, sticky="W")
        createToolTip(self.master, km_entry, "km")

        # prosjektnr
        tk.Label(info, text="Prosj.nr:", font=plain).grid(row=0, column=4, sticky="E")
        prosj_entry = tk.Entry(info, textvariable=self.master.prosjektnr, bg="red")
        prosj_entry.config(font=plain)
        prosj_entry.grid(row=0, column=5, sticky="W")

        # mastenr
        tk.Label(info, text="Mastenr:", font=plain).grid(row=1, column=4, sticky="E")
        mastenr_entry = tk.Entry(info, textvariable=self.master.mastenr, bg="red")
        mastenr_entry.config(font=plain)
        mastenr_entry.grid(row=1, column=5, sticky="W")

        # signatur
        tk.Label(info, text="Sign.:", font=plain).grid(row=0, column=6, sticky="E")
        tk.Entry(info, textvariable=self.master.signatur, bg="red").grid(row=0, column=7, sticky="W")

        # dato
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
        self.fixavstand_spinbox = tk.Spinbox(mastefelt, from_=0.0, to=800, increment=25,
                                             width=10, font=plain, repeatinterval=100,
                                             command=lambda: self.master.avstand_fixpunkt.set(
                                                 self.fixavstand_spinbox.get()))
        self.fixavstand_spinbox.delete(0,"end")
        self.fixavstand_spinbox.insert(0, self.master.avstand_fixpunkt.get())
        self.fixavstand_spinbox.config(state="readonly")
        self.fixavstand_spinbox.pack(anchor="e", side="left", padx=5, pady=8)
        tk.Label(mastefelt, text="[m]", font=plain).pack(anchor="e", side="left")

        # ----------------------------------Mastefunksjoner----------------------------------
        mastefunksjoner = tk.LabelFrame(venstre, text="Mastefunksjoner", font=bold)
        mastefunksjoner.pack(fill="both")
        alternative_funksjoner = tk.Checkbutton(mastefunksjoner, text="Alternative mastefunksjoner",
                                                font=plain, variable=self._alternative_mastefunksjoner,
                                                onvalue=True, offvalue=False)
        alternative_funksjoner.pack(anchor="w")
        self.alternativ_funksjon_radiobutton_0 = tk.Radiobutton(mastefunksjoner, text="Fixpunktmast", font=plain,
                                                                variable=self._alternativ_funksjon, value=0)
        self.alternativ_funksjon_radiobutton_0.pack(anchor="w", padx=15)
        self.alternativ_funksjon_radiobutton_1 = tk.Radiobutton(mastefunksjoner, text="Fixavspenningsmast", font=plain,
                                                                variable=self._alternativ_funksjon, value=1)
        self.alternativ_funksjon_radiobutton_1.pack(anchor="w", padx=15)
        self.alternativ_funksjon_radiobutton_2 = tk.Radiobutton(mastefunksjoner, text="Avspenningsmast", font=plain,
                                                                variable=self._alternativ_funksjon, value=2)
        self.alternativ_funksjon_radiobutton_2.pack(anchor="w", padx=15)
        mastefunksjoner_2 = tk.Frame(mastefunksjoner, relief="groove", bd=1)
        mastefunksjoner_2.pack(pady=(10,0))
        tk.Radiobutton(mastefunksjoner_2, text="Strekkutligger", font=plain,
                       variable=self.master.strekkutligger, value=True).grid(row=0, column=0, sticky="W", pady=2)
        tk.Radiobutton(mastefunksjoner_2, text="Trykkutligger", font=plain,
                       variable=self.master.strekkutligger, value=False).grid(row=0, column=1, sticky="W", pady=2)
        tk.Checkbutton(mastefunksjoner_2, text="Neste mast på andre siden av sporet", font=plain,
                       variable=self.master.master_bytter_side, onvalue=True, offvalue=False).grid(row=1, column=0, sticky="W", columnspan=2, pady=(0,2))

        # -------------------------------Fastavspente ledninger-------------------------------
        fastavspente = tk.LabelFrame(venstre, text="Fastavspente ledninger", font=bold)
        fastavspente.pack(fill="both")

        # mate-/fjernledninger
        self.matefjern_button = tk.Checkbutton(fastavspente, text="Mate-/fjernledninger", font=plain,
                                               variable=self.master.matefjern_ledn, onvalue=True, offvalue=False)
        self.matefjern_button.grid(row=0, column=0, sticky="W")
        self.matefjern_label = tk.Label(fastavspente, text="Antall:", font=plain)
        self.matefjern_label.grid(row=0, column=1, sticky="E")
        self.matefjern_spinbox = tk.Spinbox(fastavspente, values=(1, 2), width=10, font=plain, state="readonly",
                                            command=lambda: self.master.matefjern_antall.set(
                                                self.matefjern_spinbox.get()))
        self.matefjern_spinbox.grid(row=0, column=2, sticky="W")

        # at-ledninger
        self.at_button = tk.Checkbutton(fastavspente, text="AT-ledninger (2 stk.)", font=plain,
                                        variable=self.master.at_ledn, onvalue=True, offvalue=False)
        self.at_button.grid(row=1, column=0, sticky="W")
        self.at_label = tk.Label(fastavspente, text="Type:", font=plain)
        self.at_label.grid(row=1, column=1, sticky="E")
        self.at_menu = tk.OptionMenu(fastavspente, self.master.at_type, *lister.at_list)
        self.at_menu.config(font=plain)
        self.at_menu.grid(row=1, column=2, sticky="W")

        # forbigangsledning
        self.forbigang_button = tk.Checkbutton(fastavspente, text="Forbigangsledning (1 stk.)", font=plain,
                                               variable=self.master.forbigang_ledn, onvalue=True, offvalue=False)
        self.forbigang_button.grid(row=2, column=0, sticky="W")

        # jordledning
        self.jord_button = tk.Checkbutton(fastavspente, text="Jordledning (1 stk.)", font=plain,
                                          variable=self.master.jord_ledn, onvalue=True, offvalue=False)
        self.jord_button.grid(row=3, column=0, sticky="W")
        self.jord_label = tk.Label(fastavspente, text="Type:", font=plain)
        self.jord_label.grid(row=3, column=1, sticky="E")
        self.jord_menu = tk.OptionMenu(fastavspente, self.master.jord_type, *lister.jord_list)
        self.jord_menu.config(font=plain)
        self.jord_menu.grid(row=3, column=2, sticky="W")

        # returledninger
        self.retur_button = tk.Checkbutton(fastavspente, text="Returledninger (2 stk.)", font=plain,
                                           variable=self.master.retur_ledn, onvalue=True, offvalue=False)
        self.retur_button.grid(row=4, column=0, sticky="W")

        # fiberoptisk ledning
        self.fiberoptisk_button = tk.Checkbutton(fastavspente, text="Fiberoptisk ledning (1 stk.)", font=plain,
                                                 variable=self.master.fiberoptisk_ledn, onvalue=True, offvalue=False)
        self.fiberoptisk_button.grid(row=5, column=0, sticky="W")


        # ------------------------------------System------------------------------------
        system = tk.LabelFrame(hoyre, text="System", font=bold)
        system.pack(fill="both")

        # system
        system_menu = tk.OptionMenu(system, self.master.systemnavn, *lister.system_list)
        system_menu.config(font=plain)
        system_menu.grid(row=0, column=0, sticky="W", columnspan=2)

        # radius
        tk.Label(system, text="Radius:", font=plain).grid(row=1, column=0)
        radius_menu = tk.OptionMenu(system, self.master.radius, *lister.radius_list)
        radius_menu.config(font=plain, width=8)
        radius_menu.grid(row=1, column=0, sticky="E")
        tk.Label(system, text="[m]", font=plain).grid(row=1, column=1, sticky="W")

        # høgfjellsgrense
        hoyfjellsgrense = tk.Checkbutton(system, text="Vindutsatt strekning (høyfjell)",
                                        font=plain, variable=self._hoyfjellsgrense,
                                        onvalue=True, offvalue=False)
        hoyfjellsgrense.grid(row=2, column=0, sticky="W")

        # samme avstand a
        samme_avstad_button = tk.Checkbutton(system, text="Samme avstand forrige/neste mast",
                                             font=plain, variable=self._samme_avstand_a,
                                             onvalue=True, offvalue=False,
                                             command=self._masteavstand_a1)
        samme_avstad_button.grid(row=3, column=0, sticky="W")

        # avstand forrige mast
        tk.Label(system, text="Avstand til forrige mast:", font=plain) \
            .grid(row=4, column=0, sticky="W")
        self.a1_spinbox = tk.Spinbox(system, increment=0.1, width=10, repeatinterval=20,
                                     command=self._masteavstand_a1)
        self.a1_spinbox.delete(0, "end")
        self.a1_spinbox.insert(0, self.master.a1.get())
        self.a1_spinbox.config(font=plain)
        self.a1_spinbox.grid(row=4, column=0, sticky="E")
        tk.Label(system, text="[m]", font=plain).grid(row=4, column=1, sticky="W")

        # avstand neste mast
        tk.Label(system, text="Avstand til neste mast:", font=plain) \
            .grid(row=5, column=0, sticky="W")
        self.a2_spinbox = tk.Spinbox(system, increment=0.1, width=10, repeatinterval=20,
                                     command=self._masteavstand_a2)
        self.a2_spinbox.delete(0, "end")
        self.a2_spinbox.insert(0, self.master.a2.get())
        self.a2_spinbox.config(font=plain)
        self.a2_spinbox.grid(row=5, column=0, sticky="E")
        tk.Label(system, text="[m]", font=plain).grid(row=5, column=1, sticky="W")

        # masteavstand max
        self.masteavstand_max_label = tk.Label(system, font=italic)
        self.masteavstand_max_label.grid(row=6, column=0, sticky="W", columnspan=2)

        # klima
        klima_btn = tk.Button(system, text="Klima", font=bold, width=12,
                             command=self._klima)
        klima_btn.grid(row=7, column=0, sticky="W")
        self.vk_label = tk.Label(system, text="(Vindkasthastighetstrykk = {:.2f} kN/m^2)"
                                                .format(self.master.vindkasthastighetstrykk.get()/1000), font=italic)
        self.vk_label.grid(row=8, column=0, columnspan=1, sticky="W")
        self.master.vindkasthastighetstrykk.trace("w", lambda *args:
                                                  self.vk_label.config(text="(Vindkasthastighetstrykk = {:.2f} kN/m^2)"
                                                  .format(self.master.vindkasthastighetstrykk.get()/1000)))

        # --------------------------------Geometriske data--------------------------------
        geom_data = tk.LabelFrame(hoyre, text="Høyder", font=bold)
        geom_data.pack(fill="both")
        g_1 = tk.Frame(geom_data, relief="groove", bd=1)
        g_1.pack(fill="both")

        # h
        self.h_label_1 = tk.Label(g_1, text="    (mastehøyde):                              ", font=plain)
        self.h_label_1.grid(row=0, column=0, sticky="W")
        self.h_label_2 = tk.Label(g_1, text="H", font=bold)
        self.h_label_2.grid(row=0, column=0, sticky="W")
        self.h_spinbox = tk.Spinbox(g_1, increment=0.5, repeatinterval=120, width=10, font=plain,
                                    command=lambda: self.master.h.set(self.h_spinbox.get()))
        self.h_spinbox.delete(0, "end")
        self.h_spinbox.insert(0, self.master.h.get())
        self.h_spinbox.grid(row=0, column=1, sticky="E")
        self.h_label_3 = tk.Label(g_1, text="[m]", font=plain)
        self.h_label_3.grid(row=0, column=2, sticky="W")

        # hfj
        self.hfj_label_1 = tk.Label(g_1, text="      (fjern-/AT-ledning):", font=plain)
        self.hfj_label_1.grid(row=1, column=0, sticky="W")
        self.hfj_label_2 = tk.Label(g_1, text="Hfj", font=bold)
        self.hfj_label_2.grid(row=1, column=0, sticky="W")
        self.hfj_spinbox = tk.Spinbox(g_1, increment=0.1, repeatinterval=60, width=10, font=plain,
                                    command=lambda: self.master.hfj.set(self.hfj_spinbox.get()))
        self.hfj_spinbox.delete(0, "end")
        self.hfj_spinbox.insert(0, self.master.hfj.get())
        self.hfj_spinbox.grid(row=1, column=1, sticky="E")
        self.hfj_label_3 = tk.Label(g_1, text="[m]", font=plain)
        self.hfj_label_3.grid(row=1, column=2, sticky="W")

        # hf
        self.hf_label_1 = tk.Label(g_1, text="     (forbigangs-/fiberoptisk ledning):", font=plain)
        self.hf_label_1.grid(row=2, column=0, sticky="W")
        self.hf_label_2 = tk.Label(g_1, text="Hf", font=bold)
        self.hf_label_2.grid(row=2, column=0, sticky="W")
        self.hf_spinbox = tk.Spinbox(g_1, increment=0.1, repeatinterval=60, width=10, font=plain,
                                    command=lambda: self.master.hf.set(self.hf_spinbox.get()))
        self.hf_spinbox.delete(0, "end")
        self.hf_spinbox.insert(0, self.master.hf.get())
        self.hf_spinbox.grid(row=2, column=1, sticky="E")
        self.hf_label_3 = tk.Label(g_1, text="[m]", font=plain)
        self.hf_label_3.grid(row=2, column=2, sticky="W")

        # hj
        self.hj_label_1 = tk.Label(g_1, text="     (jordledning):", font=plain)
        self.hj_label_1.grid(row=3, column=0, sticky="W")
        self.hj_label_2 = tk.Label(g_1, text="Hj", font=bold)
        self.hj_label_2.grid(row=3, column=0, sticky="W")
        self.hj_spinbox = tk.Spinbox(g_1, increment=0.1, repeatinterval=60, width=10, font=plain,
                                    command=lambda: self.master.hj.set(self.hj_spinbox.get()))
        self.hj_spinbox.delete(0, "end")
        self.hj_spinbox.insert(0, self.master.hj.get())
        self.hj_spinbox.grid(row=3, column=1, sticky="E")
        self.hj_label_3 = tk.Label(g_1, text="[m]", font=plain)
        self.hj_label_3.grid(row=3, column=2, sticky="W")

        # hr
        self.hr_label_1 = tk.Label(g_1, text="     (returledning):", font=plain)
        self.hr_label_1.grid(row=4, column=0, sticky="W")
        self.hr_label_2 = tk.Label(g_1, text="Hr", font=bold)
        self.hr_label_2.grid(row=4, column=0, sticky="W")
        self.hr_spinbox = tk.Spinbox(g_1, increment=0.1, repeatinterval=60, width=10, font=plain,
                                    command=lambda: self.master.hr.set(self.hr_spinbox.get()))
        self.hr_spinbox.delete(0, "end")
        self.hr_spinbox.insert(0, self.master.hr.get())
        self.hr_spinbox.grid(row=4, column=1, sticky="E")
        self.hr_label_3 = tk.Label(g_1, text="[m]", font=plain)
        self.hr_label_3.grid(row=4, column=2, sticky="W")


        g_2 = tk.Frame(geom_data, relief="groove", bd=1)
        g_2.pack(fill="both")

        # fh
        tk.Label(g_2, text="      (kontakttråd):                              ", font=plain).grid(row=0, column=0, sticky="W")
        tk.Label(g_2, text="FH", font=bold).grid(row=0, column=0, sticky="W")
        self.fh_spinbox = tk.Spinbox(g_2, increment=0.1, repeatinterval=60, width=10,
                                     from_=4.8, to=6.5)
        self.fh_spinbox.delete(0, "end")
        self.fh_spinbox.insert(0, self.master.fh.get())
        self.fh_spinbox.config(font=plain, state="readonly",
                               command=lambda: self.master.fh.set(self.fh_spinbox.get()))
        self.fh_spinbox.grid(row=0, column=1, sticky="E")
        tk.Label(g_2, text="[m]", font=plain).grid(row=0, column=2, sticky="W")

        # sh
        tk.Label(g_2, text="      (systemhøyde):", font=plain).grid(row=1, column=0, sticky="W")
        tk.Label(g_2, text="SH", font=bold).grid(row=1, column=0, sticky="W")
        self.sh_spinbox = tk.Spinbox(g_2, increment=0.1, repeatinterval=60, width=10,
                                     from_=0.2, to=2.0)
        self.sh_spinbox.delete(0, "end")
        self.sh_spinbox.insert(0, self.master.sh.get())
        self.sh_spinbox.config(font=plain, state="readonly",
                               command=lambda: self.master.sh.set(self.sh_spinbox.get()))
        self.sh_spinbox.grid(row=1, column=1, sticky="E")
        tk.Label(g_2, text="[m]", font=plain).grid(row=1, column=2, sticky="W")

        # e
        tk.Label(g_2, text="    (SOK - top fundament):", font=plain).grid(row=2, column=0, sticky="W")
        tk.Label(g_2, text="e", font=bold).grid(row=2, column=0, sticky="W")
        self.e_spinbox = tk.Spinbox(g_2, increment=0.1, repeatinterval=60, width=10, font=plain,
                                    command=lambda: self.master.e.set(self.e_spinbox.get()))
        self.e_spinbox.delete(0, "end")
        self.e_spinbox.insert(0, self.master.e.get())
        self.e_spinbox.grid(row=2, column=1, sticky="E")
        tk.Label(g_2, text="[m]", font=plain).grid(row=2, column=2, sticky="W")

        # sms
        tk.Label(g_2, text="      (s mast - s spor):", font=plain).grid(row=3, column=0, sticky="W")
        tk.Label(g_2, text="SMS", font=bold).grid(row=3, column=0, sticky="W")
        self.sms_spinbox = tk.Spinbox(g_2, increment=0.1, repeatinterval=60, width=10,
                                     from_=2.0, to=6.0)
        self.sms_spinbox.delete(0, "end")
        self.sms_spinbox.insert(0, self.master.sms.get())
        self.sms_spinbox.config(font=plain, state="readonly",
                               command=lambda: self.master.e.set(self.e_spinbox.get()))
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


        # advarsel ledningshøyde
        self.advarsel_ledningshoyde = tk.Label(self, font=italic, fg="red")
        self.advarsel_ledningshoyde.pack(side="left")


        self._tillat_alternative_mastefunksjoner()
        self._tillat_matefjern_antall()
        self._tillat_at_jord()
        self._beregn_masteavstand_max()
        self._masteavstand_a1()
        self._masteavstand_a2()
        self._beregn_hoyder()
        self._sjekk_avstand_kl()


        # -------------------------------Avansert/beregn-------------------------------
        av_beregn = tk.LabelFrame(hoyre)
        av_beregn.pack(fill="both")
        avansert_btn = tk.Button(av_beregn, text="Avansert", font=bold, command=self._avansert)
        avansert_btn.grid(row=0, column=0, padx=12)
        beregn_btn = tk.Button(av_beregn, text="Kjør beregning", font=bold, command=self._beregn)
        beregn_btn.grid(row=0, column=1, padx=12)
        self.resultater_btn = tk.Button(av_beregn, text="Resultater", font=bold, fg="blue", command=self._resultater)
        self.resultater_btn.grid(row=0, column=2, padx=12)
        self.resultater_btn.grid_remove()


        # tracers
        self._alternative_mastefunksjoner_tracer =\
            self._alternative_mastefunksjoner.trace("w", self._tillat_alternative_mastefunksjoner)
        self.matefjern_tracer = self.master.matefjern_ledn.trace("w", lambda *args:
                                                                      (self._sjekk_ledningskombinasjon(*args),
                                                                       self._beregn_hoyder(*args),
                                                                       self._tillat_matefjern_antall(*args)))
        self.at_tracer = self.master.at_ledn.trace("w", lambda *args:
                                                        (self._sjekk_ledningskombinasjon(*args),
                                                         self._beregn_hoyder(*args),
                                                         self._tillat_at_jord(*args),
                                                         self._sjekk_avstand_kl()))
        self.forbigang_tracer = self.master.forbigang_ledn.trace("w", lambda *args:
                                                                      (self._sjekk_ledningskombinasjon(*args),
                                                                       self._beregn_hoyder(*args)))
        self.jord_tracer = self.master.jord_ledn.trace("w", lambda *args: (self._beregn_hoyder(*args),
                                                                           self._tillat_at_jord(*args)))
        self.fiberoptisk_tracer = self.master.fiberoptisk_ledn.trace("w", lambda *args:
                                                                          (self._sjekk_ledningskombinasjon(*args),
                                                                           self._beregn_hoyder(*args)))
        self.retur_tracer = self.master.retur_ledn.trace("w", lambda *args: (self._sjekk_ledningskombinasjon(*args),
                                                                             self._beregn_hoyder(*args)))
        self.hoyfjellsgrense_tracer = self._hoyfjellsgrense.trace("w", self._beregn_masteavstand_max)
        self.vindkasthastighetstrykk_tracer = self.master.vindkasthastighetstrykk.trace("w",
                                                                                        self._beregn_masteavstand_max)
        self.systemnavn_tracer = self.master.systemnavn.trace("w", self._beregn_masteavstand_max)
        self.radius_tracer = self.master.radius.trace("w", self._beregn_masteavstand_max)
        self.stromavtakerbredde_tracer = self.stromavtakerbredde.trace("w", self._beregn_masteavstand_max)
        self.h_tracer = self.master.h.trace("w", self._beregn_hoyder)
        self.hfj_tracer = self.master.hfj.trace("w", lambda *args: (self._beregn_hoyder(*args),
                                                                    self._sjekk_avstand_kl(*args)))
        self.hf_tracer = self.master.hf.trace("w", self._beregn_hoyder)
        self.hj_tracer = self.master.hj.trace("w", self._beregn_hoyder)
        self.hr_tracer = self.master.hr.trace("w", self._beregn_hoyder)
        self.fh_tracer = self.master.fh.trace("w", lambda *args: (self._beregn_masteavstand_max(*args),
                                                                  self._beregn_hoyder(*args)))
        self.sh_tracer = self.master.sh.trace("w", self._beregn_hoyder)
        self.e_tracer = self.master.e.trace("w", self._beregn_hoyder)
        self.sms_tracer = self.master.sms.trace("w", self._beregn_hoyder)

    def _sjekk_ledningskombinasjon(self, *args):
        """Sjekker hvilke ledningsknapper som til enhver til er aktive."""

        matefjern_ledn = self.master.matefjern_ledn.get()
        at_ledn = self.master.at_ledn.get()
        forbigang_ledn = self.master.forbigang_ledn.get()
        jord_ledn = self.master.jord_ledn.get()
        fiberoptisk_ledn = self.master.fiberoptisk_ledn.get()
        retur_ledn = self.master.retur_ledn.get()

        self.matefjern_button.config(state="normal")
        self.at_button.config(state="normal")
        self.forbigang_button.config(state="normal")
        self.jord_button.config(state="normal")
        self.fiberoptisk_button.config(state="normal")
        self.retur_button.config(state="normal")

        if matefjern_ledn or forbigang_ledn or retur_ledn:
            self.at_button.config(state="disabled")
        if at_ledn:
            self.matefjern_button.config(state="disabled")
            self.forbigang_button.config(state="disabled")
            self.retur_button.config(state="disabled")
        if fiberoptisk_ledn:
            self.forbigang_button.config(state="disabled")

    def _tillat_alternative_mastefunksjoner(self, *args):
        """Tillater radiobuttons dersom alternative mastefunksjoner er aktivert."""

        if self._alternative_mastefunksjoner.get():
            self.alternativ_funksjon_radiobutton_0.config(state="normal")
            self.alternativ_funksjon_radiobutton_1.config(state="normal")
            self.alternativ_funksjon_radiobutton_2.config(state="normal")
        else:
            self.alternativ_funksjon_radiobutton_0.config(state="disabled")
            self.alternativ_funksjon_radiobutton_1.config(state="disabled")
            self.alternativ_funksjon_radiobutton_2.config(state="disabled")

    def _tillat_matefjern_antall(self, *args):
        """Tillater spinbox dersom mate-/fjernledning er aktivert."""

        if self.master.matefjern_ledn.get():
            self.matefjern_label.config(state="normal")
            self.matefjern_spinbox.config(state="readonly")
        else:
            self.matefjern_label.config(state="disabled")
            self.matefjern_spinbox.config(state="disabled")

    def _tillat_at_jord(self, *args):
        """Tillater nedtrekkslister dersom AT/jord aktivert."""

        if self.master.at_ledn.get():
            self.at_label.config(state="normal")
            self.at_menu.config(state="normal")
        else:
            self.at_label.config(state="disabled")
            self.at_menu.config(state="disabled")

        if self.master.jord_ledn.get():
            self.jord_label.config(state="normal")
            self.jord_menu.config(state="normal")
        else:
            self.jord_label.config(state="disabled")
            self.jord_menu.config(state="disabled")

    def _beregn_masteavstand_max(self, *args):
        """Beregner maksimal tillatt masteavstand grunnet utblåsning av KL."""

        systemnavn = self.master.systemnavn.get()
        systemnavn = systemnavn.split()[1] if systemnavn.startswith("System") else systemnavn
        radius = self.master.radius.get()
        fh = self.master.fh.get()
        stromavtakerbredde = self.stromavtakerbredde.get()

        B1, B2 = hjelpefunksjoner.beregn_sikksakk(systemnavn, radius)
        e = hjelpefunksjoner.vindutblasning(systemnavn, radius, fh, stromavtakerbredde)

        if systemnavn == "20A" or "20B":
            s_kl = 2 * 10000
            A_ref = (12 + 9)/1000  # [m^2/m]
        elif systemnavn == "25":
            s_kl = 2 * 15000
            A_ref = (13.2 + 10.5)/1000  # [m^2/m]
        else:  # System 35
            s_kl = 2 * 7100
            A_ref = (12 + 9)/1000  # [m^2/m]

        if self._hoyfjellsgrense.get():
            v = 37
        else:
            v = 30
        rho = 1.25
        q_p_0 = 0.5 * rho * v**2
        q_p = self.master.vindkasthastighetstrykk.get()
        q_p = q_p if q_p >= q_p_0 else q_p_0
        c_f = 1.1
        q = 1.2 * q_p * c_f * A_ref

        B1, B2 = -B1, -B2
        c1 = 2*e - B1 - B2
        c2 = 2*e + B1 + B2
        c3 = B1 - B2

        A = math.sqrt((2*s_kl / (q + s_kl/radius)) * (c2 + math.sqrt((c2**2 - c3**2))))
        if q - s_kl/radius > 0:
            B = math.sqrt((2*s_kl / (q - s_kl/radius)) * (c1 + math.sqrt((c1**2 - c3**2))))
        else:
            B = A

        masteavstand_max = min(A, B, 75.0)
        masteavstand_max_avrundet = math.floor(masteavstand_max * 10) / 10

        self.a1_spinbox.config(state="normal")
        self.a2_spinbox.config(state="normal")
        self.a1_spinbox.config(from_=0.0, to=masteavstand_max_avrundet)
        self.a2_spinbox.config(from_=0.0, to=masteavstand_max_avrundet)
        self.a1_spinbox.config(state="readonly")
        self.a2_spinbox.config(state="readonly")

        self.masteavstand_max_label.config(text="(Max. masteavstand = {:.1f} m)".format(masteavstand_max_avrundet))

    def _masteavstand_a1(self):
        """Korrigerer spinboxer ved justering av verdi."""

        self.a1_spinbox.config(state="normal")
        self.a2_spinbox.config(state="normal")
        self.master.a1.set(self.a1_spinbox.get())
        if self._samme_avstand_a.get():
            self.a2_spinbox.delete(0, "end")
            self.a2_spinbox.insert(0, self.a1_spinbox.get())
            self.master.a2.set(self.a2_spinbox.get())
        self.a1_spinbox.config(state="readonly")
        self.a2_spinbox.config(state="readonly")

    def _masteavstand_a2(self):
        """Korrigerer spinboxer ved justering av verdi."""

        self.a1_spinbox.config(state="normal")
        self.a2_spinbox.config(state="normal")
        self.master.a2.set(self.a2_spinbox.get())
        if self._samme_avstand_a.get():
            self.a1_spinbox.delete(0, "end")
            self.a1_spinbox.insert(0, self.a2_spinbox.get())
            self.master.a1.set(self.a1_spinbox.get())
        self.a1_spinbox.config(state="readonly")
        self.a2_spinbox.config(state="readonly")

    def _beregn_hoyder(self, *args):
        """Beregner tillatte høydeintervaller for ledninger og e."""

        matefjern_ledn = self.master.matefjern_ledn.get()
        at_ledn = self.master.at_ledn.get()
        forbigang_ledn = self.master.forbigang_ledn.get()
        jord_ledn = self.master.jord_ledn.get()
        fiberoptisk_ledn = self.master.fiberoptisk_ledn.get()
        retur_ledn = self.master.retur_ledn.get()
        h = self.master.h.get()
        hfj = self.master.hfj.get()
        hf = self.master.hf.get()
        hr = self.master.hr.get()
        fh = self.master.fh.get()
        sh = self.master.sh.get()
        e = self.master.e.get()

        # h
        if matefjern_ledn or at_ledn or jord_ledn:
            H = fh + sh + e + 2.5
        elif forbigang_ledn and retur_ledn:
            H = fh + sh + e + 2.0
        else:
            H = fh + sh + e + 0.7
        h_min = H - 1.5 + (0.5 - (H - 1.5) % 0.5)
        h_max = H + 5.0 + (0.5 - (H + 5.0) % 0.5)

        # hfj
        hfj_min = h - e
        hfj_max = h_max + 2.0

        # hf
        if matefjern_ledn or at_ledn or jord_ledn:
            Hf = fh + sh + 0.5
            hf_min = Hf - 1.0
            hf_max = hfj - 2.0
        else:
            hf_min = h - e
            hf_max = h_max + 2.0

        # hr
        Hr = fh + sh
        hr_min = Hr - 1.0
        if matefjern_ledn or at_ledn or jord_ledn:
            hr_max = hfj - 0.5
        elif forbigang_ledn:
            hr_max = hf - 0.5
        else:
            hr_max = h - e - 0.1

        # hj
        hj_min = fh
        hj_max = h
        if retur_ledn:
            hj_min = hr
        if forbigang_ledn:
            hj_max = hf

        # e
        e_min = - fh + 0.6
        e_max = 3.0


        # Setter tilstand for tekst og spinboxer samt skriver verdier
        self.h_spinbox.config(state="normal")
        self.h_spinbox.config(from_=h_min, to=max(h_min, h_max))
        self.h_spinbox.config(state="readonly")
        self.e_spinbox.config(state="normal")
        self.e_spinbox.config(from_=e_min, to=max(e_min, e_max))
        self.e_spinbox.config(state="readonly")


        self.hfj_label_1.config(state="normal")
        self.hfj_label_1.config(text = "      (fjern-/AT-ledning):")
        self.hfj_label_1.config(state="disabled")
        self.hfj_label_2.config(state="disabled")
        self.hfj_label_3.config(state="disabled")
        self.hfj_spinbox.config(state="disabled")
        self.hf_label_1.config(state="normal")
        self.hf_label_1.config(text = "     (forbigangs-/fiberoptisk ledning):")
        self.hf_label_1.config(state="disabled")
        self.hf_label_2.config(state="disabled")
        self.hf_label_3.config(state="disabled")
        self.hf_spinbox.config(state="disabled")
        self.hj_label_1.config(state="disabled")
        self.hj_label_2.config(state="disabled")
        self.hj_label_3.config(state="disabled")
        self.hj_spinbox.config(state="disabled")
        self.hr_label_1.config(state="disabled")
        self.hr_label_2.config(state="disabled")
        self.hr_label_3.config(state="disabled")
        self.hr_spinbox.config(state="disabled")

        if matefjern_ledn or at_ledn:
            self.hfj_label_1.config(state="normal")
            self.hfj_label_2.config(state="normal")
            self.hfj_label_3.config(state="normal")
            if matefjern_ledn:
                self.hfj_label_1.config(text="      (mate-/fjernledning):")
            else:
                self.hfj_label_1.config(text="      (AT-ledning):")
            self.hfj_spinbox.config(state="normal")
            self.hfj_spinbox.config(from_=hfj_min, to=max(hfj_min, hfj_max))
            self.hfj_spinbox.config(state="readonly")
        if forbigang_ledn or fiberoptisk_ledn:
            self.hf_label_1.config(state="normal")
            self.hf_label_2.config(state="normal")
            self.hf_label_3.config(state="normal")
            if forbigang_ledn:
                self.hf_label_1.config(text="     (forbigangsledning):")
            else:
                self.hf_label_1.config(text="     (fiberoptisk ledning):")
            self.hf_spinbox.config(state="normal")
            self.hf_spinbox.config(state="normal")
            self.hf_spinbox.config(from_=hf_min, to=max(hf_min, hf_max))
            self.hf_spinbox.config(state="readonly")
        if jord_ledn:
            self.hj_label_1.config(state="normal")
            self.hj_label_2.config(state="normal")
            self.hj_label_3.config(state="normal")
            self.hj_spinbox.config(state="normal")
            self.hj_spinbox.config(state="normal")
            self.hj_spinbox.config(from_=hj_min, to=max(hj_min, hj_max))
            self.hj_spinbox.config(state="readonly")
        if retur_ledn:
            self.hr_label_1.config(state="normal")
            self.hr_label_2.config(state="normal")
            self.hr_label_3.config(state="normal")
            self.hr_spinbox.config(state="normal")
            self.hr_spinbox.config(state="normal")
            self.hr_spinbox.config(from_=hr_min, to=max(hr_min, hr_max))
            self.hr_spinbox.config(state="readonly")

    def _sjekk_avstand_kl(self, *args):
        """Sjekker AT-ledningens avstand til KL-anlegget."""

        at_ledn = self.master.at_ledn.get()
        hfj = self.master.hfj.get()
        fh = self.master.fh.get()
        sh = self.master.sh.get()

        if at_ledn and hfj < fh + sh + 2.0:
            self.advarsel_ledningshoyde.config(text="AT-leder kan gi kritisk\nliten avstand til KL-anlegg!")
        else:
            self.advarsel_ledningshoyde.config(text="")

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
        tk.Label(refvind_frame, text="v_b,0:", font=plain).grid(row=0, column=0, sticky="W")
        self.refvind_spinbox = tk.Spinbox(refvind_frame, from_=20, to=30, width=10)
        self.refvind_spinbox.delete(0, "end")
        self.refvind_spinbox.insert(0, int(self.M.referansevindhastighet.get()))
        self.refvind_spinbox.config(font=plain, state="readonly",
                                    command=lambda: self.M.referansevindhastighet.set(self.refvind_spinbox.get()))
        self.refvind_spinbox.grid(row=0, column=1, sticky="W")
        tk.Label(refvind_frame, text="[m/s]", font=plain).grid(row=0, column=2, sticky="W")

        # --------------------------------c-faktorer--------------------------------
        c_faktorer = tk.LabelFrame(self, text="Faktorer som påvirker basisvindhastigheten", font=bold)
        c_faktorer.grid(row=1, column=0, sticky="W")
        c_faktorer.columnconfigure(0, weight=1)
        c_faktorer.columnconfigure(1, weight=49)

        # c_dir
        tk.Label(c_faktorer, text="c_dir:",
                 font=italic).grid(row=0, column=0, sticky="W")
        self.c_dir_spinbox = tk.Spinbox(c_faktorer, values=(0.8, 0.9, 1.0), width=10)
        self.c_dir_spinbox.delete(0, "end")
        self.c_dir_spinbox.insert(0, float(self.M.c_dir.get()))
        self.c_dir_spinbox.config(font=plain, state="readonly",
                                  command=lambda: self.M.c_dir.set(self.c_dir_spinbox.get()))
        self.c_dir_spinbox.grid(row=0, column=1, sticky="W")

        # c_season
        tk.Label(c_faktorer, text="c_season:",
                 font=italic).grid(row=1, column=0, sticky="W")
        self.c_season_spinbox = tk.Spinbox(c_faktorer, values=(0.8, 0.9, 1.0), width=10)
        self.c_season_spinbox.delete(0, "end")
        self.c_season_spinbox.insert(0, float(self.M.c_season.get()))
        self.c_season_spinbox.config(font=plain, state="readonly",
                                     command=lambda: self.M.c_season.set(self.c_season_spinbox.get()))
        self.c_season_spinbox.grid(row=1, column=1, sticky="W")

        # c_prob
        tk.Label(c_faktorer, text="c_prob:",
                 font=italic).grid(row=2, column=0, sticky="W")
        self.c_prob_spinbox = tk.Spinbox(c_faktorer, from_=0.8, to=1.0, increment=0.01, repeatinterval=50, width=10)
        self.c_prob_spinbox.delete(0,"end")
        self.c_prob_spinbox.insert(0, float(self.M.c_prob.get()))
        self.c_prob_spinbox.config(font=plain, state="readonly",
                                   command=lambda: self.M.c_prob.set(self.c_prob_spinbox.get()))
        self.c_prob_spinbox.grid(row=2, column=1, sticky="W")

        # --------------------------------Høydefaktor--------------------------------
        c_alt_frame = tk.Frame(c_faktorer, relief="groove", bd=1)
        c_alt_frame.grid(row=3, column=0, columnspan=2, sticky="W")
        tk.Label(c_alt_frame, text="c_alt: ", font=italic).grid(row=0, column=0, sticky="W")
        self.c_alt_entry = tk.Entry(c_alt_frame, width=11, state="readonly")
        self.c_alt_entry.config(font=plain)
        self.c_alt_entry.grid(row=0, column=1, sticky="W")
        self.regioner_menu = tk.OptionMenu(c_alt_frame, self.M.region, *lister.regioner_list)
        self.regioner_menu.config(font=plain, width=28)
        self.regioner_menu.grid(row=0, column=2)
        tk.Label(c_alt_frame, text="Stedshøyde:", font=plain).grid(row=1, column=0, sticky="W")
        self.H_spinbox = tk.Spinbox(c_alt_frame, from_=lister.regioner[self.M.region.get()]["H_0"],
                                    to=lister.regioner[self.M.region.get()]["H_topp"], increment=50,
                                    repeatinterval=50, width=6)
        self.H_spinbox.delete(0, "end")
        self.H_spinbox.insert(0, int(self.M.H.get()))
        self.H_spinbox.config(font=plain, state="readonly", command=lambda *args: self.M.H.set(self.H_spinbox.get()))
        self.H_spinbox.grid(row=1, column=1, sticky="W")
        tk.Label(c_alt_frame, text="[m]", font=plain).grid(row=1, column=1, sticky="E")
        self.H_label = tk.Label(c_alt_frame, font=plain,
                                text="(Tregrensa = {} m.o.h.)".format(lister.regioner[self.M.region.get()]["H_0"]))
        self.H_label.grid(row=1, column=2, sticky="E")


        # -------------------------------Terrengfaktorer-------------------------------
        terrengfaktorer = tk.LabelFrame(self, text="Faktorer (terrengfaktorer) som påvirker"
                                                   " stedets vindhastighet", font=bold)
        terrengfaktorer.grid(row=1, column=1, sticky="W")

        # overgangssoner
        overgangssoner = tk.Checkbutton(terrengfaktorer, text="Overgangssoner (INAKTIV)",
                                                font=plain, variable=self.M.overgangssoner,
                                                onvalue=True, offvalue=False, state="disabled")
        overgangssoner.grid(row=0, column=0, sticky="W")

        # terrengruhetskategori
        tk.Label(terrengfaktorer, text="Terrengruhetskategori:",
                 font=plain).grid(row=1, column=0, sticky="W")
        terrengruhetskategori_menu = tk.OptionMenu(terrengfaktorer,
                                                   self.M.terrengruhetskategori,
                                                   *[0,1,2,3,4])
        terrengruhetskategori_menu.config(font=plain, width=3)
        terrengruhetskategori_menu.grid(row=2, column=0)

        # høyde over terrenget z
        tk.Label(terrengfaktorer, text="Høyde over terrenget z [m]:",
                 font=plain).grid(row=1, column=1, sticky="W")
        self.z_spinbox = tk.Spinbox(terrengfaktorer, from_=1, to=50,
                                    repeatinterval=50, width=10)
        self.z_spinbox.delete(0, "end")
        self.z_spinbox.insert(0, int(self.M.z.get()))
        self.z_spinbox.config(font=plain, state="readonly",
                              command=lambda: self.M.z.set(self.z_spinbox.get()))
        self.z_spinbox.grid(row=2, column=1)

        # terrengformfaktor C_0
        tk.Label(terrengfaktorer, text="Terrengformfaktor C_0:",
                 font=plain).grid(row=3, column=2, sticky="W")
        self.C_0_spinbox = tk.Spinbox(terrengfaktorer, from_=0.5, to=1.5,
                                      increment=0.1, repeatinterval=100, width=10)
        self.C_0_spinbox.delete(0, "end")
        self.C_0_spinbox.insert(0, float(self.M.C_0.get()))
        self.C_0_spinbox.config(font=plain, state="readonly",
                                command=lambda: self.M.C_0.set(self.C_0_spinbox.get()))
        self.C_0_spinbox.grid(row=4, column=2)

        # -------------------------------BEREGNEDE VERDIER-------------------------------

        # turbulensintensitet I_v
        tk.Label(terrengfaktorer, text="Turbulensintensitet I_v:",
                 font=plain).grid(row=3, column=0, sticky="W")
        self.I_v_entry = tk.Entry(terrengfaktorer, width=10, state="readonly")
        self.I_v_entry.config(font=plain)
        self.I_v_entry.grid(row=4, column=0)

        # turbulensfaktor k_l
        tk.Label(terrengfaktorer, text="Turbulensfaktor k_l:",
                 font=plain).grid(row=3, column=1)
        self.k_l_entry = tk.Entry(terrengfaktorer, width=10, state="readonly")
        self.k_l_entry.config(font=plain)
        self.k_l_entry.grid(row=4, column=1)

        beregnede_verdier = tk.LabelFrame(self, text="Beregnede vindparametre", font=bold)
        beregnede_verdier.grid(row=2, column=0, columnspan=1, sticky="W")
        self.beregnede_verdier_label = tk.Label(beregnede_verdier, font=plain, justify="left", height=6)
        self.beregnede_verdier_label.grid(row=0, column=0, sticky="W")

        # vindkasthastighetstrykk q_p
        brukes_frame = tk.LabelFrame(self, text="Brukes i beregninger", font=bold)
        brukes_frame.grid(row=2, column=1, columnspan=2, sticky="W")
        self.q_p_label = tk.Label(brukes_frame, font=bold)
        self.q_p_label.grid(row=0, column=0, sticky="W")

        # isklasse
        tk.Label(brukes_frame, text="                         Isklasse:", font=bold).grid(row=1, column=0, sticky="W")
        self.isklasse_menu = tk.OptionMenu(brukes_frame, self.M.master.isklasse, *lister.isklasse_list)
        self.isklasse_menu.config(font=bold, width=12)
        self.isklasse_menu.grid(row=1, column=0, sticky="E")

        self._beregn_c_alt()
        self._beregn_klimaverdier()

        # -------------------------------Lukk vindu------------------------------
        lukk = tk.Frame(self)
        lukk.grid(row=2, column=1, sticky="SE")
        lukk_btn = tk.Button(lukk, text="Lukk vindu", font=bold, command=self._lukk_vindu)
        lukk_btn.pack(padx=5, pady=5)

        # tracers
        self.referansevindhastighet_tracer = self.M.referansevindhastighet.trace("w", self._beregn_klimaverdier)
        self.c_dir_tracer = self.M.c_dir.trace("w", self._beregn_klimaverdier)
        self.c_season_tracer = self.M.c_season.trace("w", self._beregn_klimaverdier)
        self.region_tracer = self.M.region.trace("w", self._sett_H)
        self.H_tracer = self.M.H.trace("w", self._beregn_c_alt)
        self.c_alt_tracer = self.M.c_alt.trace("w", self._beregn_klimaverdier)
        self.c_prob_tracer = self.M.c_prob.trace("w", self._beregn_klimaverdier)
        self.terrengruhetskategori_tracer = self.M.terrengruhetskategori.trace("w", self._beregn_klimaverdier)
        self.z_tracer = self.M.z.trace("w", self._beregn_klimaverdier)
        self.C_0_tracer = self.M.C_0.trace("w", self._beregn_klimaverdier)

    def _sett_H(self, *args):
        """Justerer byggehøyde basert på valg av region."""

        self.H_spinbox.config(state="normal")
        self.H_spinbox.config(from_=lister.regioner[self.M.region.get()]["H_0"],
                              to=lister.regioner[self.M.region.get()]["H_topp"])
        self.M.H.set(self.H_spinbox.get())
        self.H_spinbox.config(state="readonly")
        self.H_label.config(text="(Tregrensa = {} m.o.h.)".format(lister.regioner[self.M.region.get()]["H_0"]))

    def _beregn_c_alt(self, *args):
        """Beregner og lagrer høydefaktor c_alt"""

        v_b_0 = self.M.referansevindhastighet.get()
        region = self.M.region.get()
        H = self.M.H.get()

        c_alt = hjelpefunksjoner.c_alt(v_b_0, region, H)
        self.M.c_alt.set(c_alt)

        self.c_alt_entry.config(state="normal")
        self.c_alt_entry.delete(0, "end")
        self.c_alt_entry.insert(0, round(c_alt, 2))
        self.c_alt_entry.config(state="readonly")

    def _beregn_klimaverdier(self, *args):
        """Beregner øvrige klimaverdier."""

        v_b_0 = self.M.referansevindhastighet.get()
        c_dir = self.M.c_dir.get()
        c_season = self.M.c_season.get()
        c_alt = self.M.c_alt.get()
        c_prob = self.M.c_prob.get()
        C_0 = self.M.C_0.get()
        terrengkategori = self.M.terrengruhetskategori.get()
        z = self.M.z.get()

        q_p, v_b, v_m, v_p, q_m, I_v, k_l = hjelpefunksjoner.vindkasthastighetstrykk(v_b_0, c_dir, c_season, c_alt,
                                                                                     c_prob, C_0, terrengkategori, z)

        self.I_v_entry.config(state="normal")
        self.I_v_entry.delete(0, "end")
        self.I_v_entry.insert(0, round(I_v, 2))
        self.I_v_entry.config(state="readonly")
        self.k_l_entry.config(state="normal")
        self.k_l_entry.delete(0, "end")
        self.k_l_entry.insert(0, round(k_l, 2))
        self.k_l_entry.config(state="readonly")

        tekst = "Basisvindhastighet  v_b = {:.1f} m/s\n".format(v_b)
        tekst += "Middelvindhastighet  v_m = {:.1f} m/s\n".format(v_m)
        tekst += "Vindhastighet svarende til\nvindkasthastighetstrykket  v_p = {:.1f} m/s\n".format(v_p)
        tekst += "Vindhastighetstrykk  q_m = {:.2f} kN/m^2".format(q_m / 1000)
        self.beregnede_verdier_label.config(text=tekst)

        tekst = "Vindkasthastighetstrykk  q_p = {:.2f} kN/m^2".format(q_p / 1000)
        self.q_p_label.config(text=tekst)

        self.M.master.vindkasthastighetstrykk.set(q_p)

    def _lukk_vindu(self):
        """Sletter variabel-tracere og lukker vindu."""

        self.M.referansevindhastighet.trace_vdelete("w", self.referansevindhastighet_tracer)
        self.M.c_dir.trace_vdelete("w", self.c_dir_tracer)
        self.M.c_season.trace_vdelete("w", self.c_season_tracer)
        self.M.region.trace_vdelete("w", self.region_tracer)
        self.M.H.trace_vdelete("w", self.H_tracer)
        self.M.c_alt.trace_vdelete("w", self.c_alt_tracer)
        self.M.c_prob.trace_vdelete("w", self.c_prob_tracer)
        self.M.terrengruhetskategori.trace_vdelete("w", self.terrengruhetskategori_tracer)
        self.M.z.trace_vdelete("w", self.z_tracer)
        self.M.C_0.trace_vdelete("w", self.C_0_tracer)

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
        tk.Label(alternativer, text="Beregningsprosedyre:", font=plain).grid(row=0, column=0, sticky="W")
        tk.Radiobutton(alternativer, text="Eurokode (EC3)", font=plain,
                       variable=self.M.master.ec3, value=True).grid(row=0, column=1)
        tk.Radiobutton(alternativer, text="Bransjestandard (NEK)", font=plain,
                       variable=self.M.master.ec3, value=False).grid(row=0, column=2)

        # materialkoeffisient
        tk.Label(alternativer, text="Materialkoeffisient:",
                 font=plain).grid(row=1, column=0, sticky="W")
        self.materialkoeff_spinbox = tk.Spinbox(alternativer, from_=1.0, to=1.15, increment=0.05, width=10,
                                                command=lambda: self.M.master.materialkoeff.set(
                                                    self.materialkoeff_spinbox.get()))
        self.materialkoeff_spinbox.delete(0, "end")
        self.materialkoeff_spinbox.insert(0, float(self.M.master.materialkoeff.get()))
        self.materialkoeff_spinbox.config(font=plain, state="readonly")
        self.materialkoeff_spinbox.grid(row=1, column=1, sticky="E")
        tk.Label(alternativer, text="Anbefalt verdi: 1.05",
                 font=italic).grid(row=1, column=2, columnspan=2, sticky="W")

        # traverslengde
        self.traverslengde_label_1 = tk.Label(alternativer, text="Traverslengde hver side:", font=plain)
        self.traverslengde_label_1.grid(row=2, column=0, sticky="W")
        self.traverslengde_spinbox = tk.Spinbox(alternativer, font=plain, from_=0.3, to=1.0, increment=0.1, width=10,
                                                command=lambda: self.M.master.traverslengde.set(
                                                    self.traverslengde_spinbox.get()))
        self.traverslengde_spinbox.delete(0, "end")
        self.traverslengde_spinbox.insert(0, float(self.M.master.traverslengde.get()))
        self.traverslengde_spinbox.grid(row=2, column=1, sticky="E")
        self.traverslengde_label_2 = tk.Label(alternativer, text="[m]", font=plain)
        self.traverslengde_label_2.grid(row=2, column=2, sticky="W")

        # strømavtaker
        tk.Label(alternativer, text="Strømavtakerbredde:", font=plain).grid(row=3, column=0, sticky="W")
        system_menu = tk.OptionMenu(alternativer, self.M.stromavtakerbredde, *lister.stromavtaker_list)
        system_menu.config(font=plain, width=7)
        system_menu.grid(row=3, column=1, sticky="E")
        tk.Label(alternativer, text="[mm]", font=plain).grid(row=3, column=2, sticky="W")

        # avspenningsbardun
        self.avspenningsbardun_checkbtn = tk.Checkbutton(alternativer, font=plain,
                                                         text="Avspenningsbardun (dersom fixavsp.- eller avsp.mast)",
                                                         variable=self.M.master.avspenningsbardun,
                                                         onvalue=True, offvalue=False)
        self.avspenningsbardun_checkbtn.grid(row=4, column=0, columnspan=3, sticky="W")

        # differansestrekk
        differansestrekk_frame = tk.Frame(alternativer, relief="groove", bd=1)
        differansestrekk_frame.grid(row=5, column=0, columnspan=3)
        autodiff_checkbtn = tk.Checkbutton(differansestrekk_frame, text="Automatisk beregning av differansestrekk",
                                         font=plain, variable=self.M.master.auto_differansestrekk,
                                         onvalue=True, offvalue=False)
        autodiff_checkbtn.grid(row=0, column=0, columnspan=3, sticky="W")
        self.differansestrekk_label_1 = tk.Label(differansestrekk_frame, text="Differansestrekk:", font=plain)
        self.differansestrekk_label_1.grid(row=1, column=0, sticky="E")
        self.differansestrekk_entry = tk.Entry(differansestrekk_frame, width=10, font=plain,
                                               textvariable=self.M.master.differansestrekk)
        self.differansestrekk_entry.grid(row=1, column=1, sticky="E")
        self.differansestrekk_label_2 = tk.Label(differansestrekk_frame, text="[kN]", font=plain)
        self.differansestrekk_label_2.grid(row=1, column=2, sticky="W")

        # høydedifferanse
        alternativer_2 = tk.Frame(alternativer, relief="groove", bd=1)
        alternativer_2.grid(row=6, column=0, columnspan=3)
        tk.Label(alternativer_2, text="Ledningers midlere innfestingshøyde i \n"
                                      "aktuell mast i forhold til...",
                font=plain).grid(row=0, column=0, columnspan=3)
        tk.Label(alternativer_2, text="forrige mast:", font=plain).grid(row=1, column=0, sticky="E")
        tk.Entry(alternativer_2, textvariable=self.M.master.delta_h1, font=plain, width=10).grid(row=1, column=1)
        tk.Label(alternativer_2, text="[m]", font=plain).grid(row=1, column=2, sticky="W")
        tk.Label(alternativer_2, text="neste mast:", font=plain).grid(row=2, column=0, sticky="E")
        tk.Entry(alternativer_2, textvariable=self.M.master.delta_h2, font=plain, width=10).grid(row=2, column=1)
        tk.Label(alternativer_2, text="[m]", font=plain).grid(row=2, column=2, sticky="W")
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
        self.last_label_1 = tk.Label(lastvektor_frame, text="f_x = positiv nedover", font=italic)
        self.last_label_1.grid(row=4, column=0, columnspan=3, sticky="E")

        self.last_label_2 = tk.Label(lastvektor_frame, text="f_x:", font=plain)
        self.last_label_2.grid(row=1, column=0, sticky="E")
        self.last_entry_1 = tk.Entry(lastvektor_frame, textvariable=self.M.master.f_x, font=plain, width=10)
        self.last_entry_1.grid(row=1, column=1)
        self.last_label_3 = tk.Label(lastvektor_frame, text="[N]", font=plain)
        self.last_label_3.grid(row=1, column=2, sticky="W")
        self.last_label_4 = tk.Label(lastvektor_frame, text="f_y:", font=plain)
        self.last_label_4.grid(row=2, column=0, sticky="E")
        self.last_entry_2 = tk.Entry(lastvektor_frame, textvariable=self.M.master.f_y, font=plain, width=10)
        self.last_entry_2.grid(row=2, column=1)
        self.last_label_5 = tk.Label(lastvektor_frame, text="[N]", font=plain)
        self.last_label_5.grid(row=2, column=2, sticky="W")
        self.last_label_6 = tk.Label(lastvektor_frame, text="f_z:", font=plain)
        self.last_label_6.grid(row=3, column=0, sticky="E")
        self.last_entry_3 = tk.Entry(lastvektor_frame, textvariable=self.M.master.f_z, font=plain, width=10)
        self.last_entry_3.grid(row=3, column=1)
        self.last_label_7 = tk.Label(lastvektor_frame, text="[N]", font=plain)
        self.last_label_7.grid(row=3, column=2, sticky="W")

        # eksentrisitet
        eksentrisitet_frame = tk.LabelFrame(brukerdef_frame, text="Eksentrisitet fra masteinnspenning", font=bold)
        eksentrisitet_frame.grid(row=1, column=1, sticky="W")
        self.eksentrisitet_label_1 = tk.Label(eksentrisitet_frame, text="e_x = positiv oppover", font=italic)
        self.eksentrisitet_label_1.grid(row=4, column=0, columnspan=3, sticky="E")

        self.eksentrisitet_label_2 = tk.Label(eksentrisitet_frame, text="e_x:", font=plain)
        self.eksentrisitet_label_2.grid(row=1, column=0, sticky="E")
        self.eksentrisitet_entry_1 = tk.Entry(eksentrisitet_frame, textvariable=self.M.master.e_x, font=plain, width=10)
        self.eksentrisitet_entry_1.grid(row=1, column=1)
        self.eksentrisitet_label_3 = tk.Label(eksentrisitet_frame, text="[m]", font=plain)
        self.eksentrisitet_label_3.grid(row=1, column=2, sticky="W")
        self.eksentrisitet_label_4 = tk.Label(eksentrisitet_frame, text="e_y:", font=plain)
        self.eksentrisitet_label_4.grid(row=2, column=0, sticky="E")
        self.eksentrisitet_entry_2 = tk.Entry(eksentrisitet_frame, textvariable=self.M.master.e_y, font=plain, width=10)
        self.eksentrisitet_entry_2.grid(row=2, column=1)
        self.eksentrisitet_label_5 = tk.Label(eksentrisitet_frame, text="[m]", font=plain)
        self.eksentrisitet_label_5.grid(row=2, column=2, sticky="W")
        self.eksentrisitet_label_6 = tk.Label(eksentrisitet_frame, text="e_z:", font=plain)
        self.eksentrisitet_label_6.grid(row=3, column=0, sticky="E")
        self.eksentrisitet_entry_3 = tk.Entry(eksentrisitet_frame, textvariable=self.M.master.e_z, font=plain, width=10)
        self.eksentrisitet_entry_3.grid(row=3, column=1)
        self.eksentrisitet_label_7 = tk.Label(eksentrisitet_frame, text="[m]", font=plain)
        self.eksentrisitet_label_7.grid(row=3, column=2, sticky="W")

        # vindareal
        areal_frame = tk.LabelFrame(brukerdef_frame, text="Vindfang", font=bold)
        areal_frame.grid(row=2, column=0, columnspan=2, sticky="W")
        self.vindareal_label_1 = tk.Label(areal_frame, text="Effektivt areal for vind...", font=plain)
        self.vindareal_label_1.grid(row=0, column=0, columnspan=3)

        self.vindareal_label_2 = tk.Label(areal_frame, text="normalt sporet (A_xy):", font=plain)
        self.vindareal_label_2.grid(row=1, column=0, sticky="E")
        self.vindareal_entry_1 = tk.Entry(areal_frame, textvariable=self.M.master.a_vind, font=plain, width=10)
        self.vindareal_entry_1.grid(row=1, column=1)
        self.vindareal_label_3 = tk.Label(areal_frame, text="[m^2]", font=plain)
        self.vindareal_label_3.grid(row=1, column=2, sticky="W")
        self.vindareal_label_4 = tk.Label(areal_frame, text="parallelt sporet (A_xz):", font=plain)
        self.vindareal_label_4.grid(row=2, column=0, sticky="E")
        self.vindareal_entry_2 = tk.Entry(areal_frame, textvariable=self.M.master.a_vind_par, font=plain, width=10)
        self.vindareal_entry_2.grid(row=2, column=1)
        self.vindareal_label_5 = tk.Label(areal_frame, text="[m^2]", font=plain)
        self.vindareal_label_5.grid(row=2, column=2, sticky="W")


        # tracers
        self._mastefelt_tracer = self.M._mastefelt.trace("w", self._tillat_traverslengde)
        self._alternativ_funksjon_tracer = self.M._alternativ_funksjon.trace("w", self._tillat_avspenningsbardun)
        self._alternative_mastefunksjoner_tracer = self.M._alternative_mastefunksjoner.trace("w", self._tillat_avspenningsbardun)
        self.auto_differansestrekk_tracer = self.M.master.auto_differansestrekk.trace("w", self._tillat_differansestrekk)
        self.brukerdefinert_last_tracer = self.M.master.brukerdefinert_last.trace("w", self._tillat_brukerdefinert_last)

        self._tillat_traverslengde()
        self._tillat_avspenningsbardun()
        self._tillat_differansestrekk()
        self._tillat_brukerdefinert_last()


        # -------------------------------Lukk vindu-------------------------------
        lukk = tk.Frame(self)
        lukk.pack()
        lukk_btn = tk.Button(lukk, text="Lukk vindu", font=bold, command=self._lukk_vindu)
        lukk_btn.pack(padx=5, pady=5)

    def _tillat_traverslengde(self, *args):
        """Tillater spinbox dersom to utliggere er valgt."""

        if not self.M._mastefelt.get() == 0:
            self.traverslengde_label_1.config(state="normal")
            self.traverslengde_label_2.config(state="normal")
            self.traverslengde_spinbox.config(state="readonly")
        else:
            self.traverslengde_label_1.config(state="disabled")
            self.traverslengde_label_2.config(state="disabled")
            self.traverslengde_spinbox.config(state="disabled")

    def _tillat_avspenningsbardun(self, *args):
        """Tillater spinbox dersom fiavspenningsmast/avspenningsmast er valgt."""

        if self.M._alternative_mastefunksjoner.get() and not self.M._alternativ_funksjon.get() == 0:
            self.avspenningsbardun_checkbtn.config(state="normal")
        else:
            self.avspenningsbardun_checkbtn.config(state="disabled")

    def _tillat_differansestrekk(self, *args):
        """Tillater spinbox dersom automatisk differansestrekk ikke er valgt."""

        if not self.M.master.auto_differansestrekk.get():
            self.differansestrekk_label_1.config(state="normal")
            self.differansestrekk_label_2.config(state="normal")
            self.differansestrekk_entry.config(state="normal")
        else:
            self.differansestrekk_label_1.config(state="disabled")
            self.differansestrekk_label_2.config(state="disabled")
            self.differansestrekk_entry.config(state="disabled")

    def _tillat_brukerdefinert_last(self, *args):
        """Tillater tekstfelter dersom egendefinert kraftvektor er valgt."""

        if self.M.master.brukerdefinert_last.get():
            self.last_label_1.config(state="normal")
            self.last_label_1.config(state="normal")
            self.last_label_2.config(state="normal")
            self.last_label_2.config(state="normal")
            self.last_label_3.config(state="normal")
            self.last_label_3.config(state="normal")
            self.last_label_4.config(state="normal")
            self.last_label_4.config(state="normal")
            self.last_label_5.config(state="normal")
            self.last_label_5.config(state="normal")
            self.last_label_6.config(state="normal")
            self.last_label_6.config(state="normal")
            self.last_label_7.config(state="normal")
            self.last_label_7.config(state="normal")
            self.last_entry_1.config(state="normal")
            self.last_entry_1.config(state="normal")
            self.last_entry_2.config(state="normal")
            self.last_entry_2.config(state="normal")
            self.last_entry_3.config(state="normal")
            self.last_entry_3.config(state="normal")
            self.eksentrisitet_label_1.config(state="normal")
            self.eksentrisitet_label_1.config(state="normal")
            self.eksentrisitet_label_2.config(state="normal")
            self.eksentrisitet_label_2.config(state="normal")
            self.eksentrisitet_label_3.config(state="normal")
            self.eksentrisitet_label_3.config(state="normal")
            self.eksentrisitet_label_4.config(state="normal")
            self.eksentrisitet_label_4.config(state="normal")
            self.eksentrisitet_label_5.config(state="normal")
            self.eksentrisitet_label_5.config(state="normal")
            self.eksentrisitet_label_6.config(state="normal")
            self.eksentrisitet_label_6.config(state="normal")
            self.eksentrisitet_label_7.config(state="normal")
            self.eksentrisitet_label_7.config(state="normal")
            self.eksentrisitet_entry_1.config(state="normal")
            self.eksentrisitet_entry_1.config(state="normal")
            self.eksentrisitet_entry_2.config(state="normal")
            self.eksentrisitet_entry_2.config(state="normal")
            self.eksentrisitet_entry_3.config(state="normal")
            self.eksentrisitet_entry_3.config(state="normal")
            self.vindareal_label_1.config(state="normal")
            self.vindareal_label_1.config(state="normal")
            self.vindareal_label_2.config(state="normal")
            self.vindareal_label_2.config(state="normal")
            self.vindareal_label_3.config(state="normal")
            self.vindareal_label_3.config(state="normal")
            self.vindareal_label_4.config(state="normal")
            self.vindareal_label_4.config(state="normal")
            self.vindareal_label_5.config(state="normal")
            self.vindareal_label_5.config(state="normal")
            self.vindareal_entry_1.config(state="normal")
            self.vindareal_entry_1.config(state="normal")
            self.vindareal_entry_2.config(state="normal")
            self.vindareal_entry_2.config(state="normal")
        else:
            self.last_label_1.config(state="disabled")
            self.last_label_1.config(state="disabled")
            self.last_label_2.config(state="disabled")
            self.last_label_2.config(state="disabled")
            self.last_label_3.config(state="disabled")
            self.last_label_3.config(state="disabled")
            self.last_label_4.config(state="disabled")
            self.last_label_4.config(state="disabled")
            self.last_label_5.config(state="disabled")
            self.last_label_5.config(state="disabled")
            self.last_label_6.config(state="disabled")
            self.last_label_6.config(state="disabled")
            self.last_label_7.config(state="disabled")
            self.last_label_7.config(state="disabled")
            self.last_entry_1.config(state="disabled")
            self.last_entry_1.config(state="disabled")
            self.last_entry_2.config(state="disabled")
            self.last_entry_2.config(state="disabled")
            self.last_entry_3.config(state="disabled")
            self.last_entry_3.config(state="disabled")
            self.eksentrisitet_label_1.config(state="disabled")
            self.eksentrisitet_label_1.config(state="disabled")
            self.eksentrisitet_label_2.config(state="disabled")
            self.eksentrisitet_label_2.config(state="disabled")
            self.eksentrisitet_label_3.config(state="disabled")
            self.eksentrisitet_label_3.config(state="disabled")
            self.eksentrisitet_label_4.config(state="disabled")
            self.eksentrisitet_label_4.config(state="disabled")
            self.eksentrisitet_label_5.config(state="disabled")
            self.eksentrisitet_label_5.config(state="disabled")
            self.eksentrisitet_label_6.config(state="disabled")
            self.eksentrisitet_label_6.config(state="disabled")
            self.eksentrisitet_label_7.config(state="disabled")
            self.eksentrisitet_label_7.config(state="disabled")
            self.eksentrisitet_entry_1.config(state="disabled")
            self.eksentrisitet_entry_1.config(state="disabled")
            self.eksentrisitet_entry_2.config(state="disabled")
            self.eksentrisitet_entry_2.config(state="disabled")
            self.eksentrisitet_entry_3.config(state="disabled")
            self.eksentrisitet_entry_3.config(state="disabled")
            self.vindareal_label_1.config(state="disabled")
            self.vindareal_label_1.config(state="disabled")
            self.vindareal_label_2.config(state="disabled")
            self.vindareal_label_2.config(state="disabled")
            self.vindareal_label_3.config(state="disabled")
            self.vindareal_label_3.config(state="disabled")
            self.vindareal_label_4.config(state="disabled")
            self.vindareal_label_4.config(state="disabled")
            self.vindareal_label_5.config(state="disabled")
            self.vindareal_label_5.config(state="disabled")
            self.vindareal_entry_1.config(state="disabled")
            self.vindareal_entry_1.config(state="disabled")
            self.vindareal_entry_2.config(state="disabled")
            self.vindareal_entry_2.config(state="disabled")

    def _lukk_vindu(self):
        """Sletter variabel-tracere og lukker vindu."""

        self.M._mastefelt.trace_vdelete("w", self._mastefelt_tracer)
        self.M._alternativ_funksjon.trace_vdelete("w", self._alternativ_funksjon_tracer)
        self.M._alternative_mastefunksjoner.trace_vdelete("w", self._alternative_mastefunksjoner_tracer)
        self.M.master.auto_differansestrekk.trace_vdelete("w", self.auto_differansestrekk_tracer)
        self.M.master.brukerdefinert_last.trace_vdelete("w", self.brukerdefinert_last_tracer)

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


        # tracer
        self.mast_resultater_tracer = self.M.mast_resultater.trace("w", lambda *args:
                                                                        (self._sett_mastetype(*args),
                                                                         self._skriv_krefter(*args),
                                                                         self._skriv_dimensjonerende_faktorer(*args)))


        self.kraftboks = tk.Text(hovedvindu, width=96, height=15)
        self.kraftboks.grid(row=2, column=0, columnspan=3)

        tk.Label(hovedvindu, text="Faktorer for utregning av UR",
                 font=plain).grid(row=0, column=4)
        tk.Label(hovedvindu, text="M_cr = [kNm]    N_cr = [kN]",
                 font=italic).grid(row=1, column=4)

        self.faktorboks = tk.Text(hovedvindu, width=28, height=35)
        self.faktorboks.grid(row=2, column=4, rowspan=6, sticky="N")


        tk.Label(hovedvindu, text="Velg mastetype:",
                 font=plain).grid(row=5, column=0)
        self.mastetype_btn_1 = tk.Radiobutton(hovedvindu, text="Gittermast", font=plain,
                                              variable=self.M.gittermast, value=True,
                                              command=self._skriv_master)
        self.mastetype_btn_1.grid(row=5, column=1)
        self.mastetype_btn_2 = tk.Radiobutton(hovedvindu, text="Bjelkemast", font=plain,
                                              variable=self.M.gittermast, value=False,
                                              command=self._skriv_master)
        self.mastetype_btn_2.grid(row=5, column=2)

        tk.Label(hovedvindu, text="D = [mm]    phi = [grader]",
                 font=italic).grid(row=6, column=0)

        self.masteboks = tk.Text(hovedvindu, width=96, height=16)
        self.masteboks.grid(row=7, column=0, columnspan=3)

        self._sett_mastetype()
        self._skriv_krefter()
        self._skriv_dimensjonerende_faktorer()
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
                             font=bold, command=self._lukk_vindu)
        lukk_btn.pack(padx=20, pady=5, side="left")

    def _lukk_vindu(self):
        """Sletter variabel-tracere og lukker vindu."""

        self.M.mast_resultater.trace_vdelete("w", self.mast_resultater_tracer)
        self.master.destroy()

    def _sett_mastetype(self, *args):
        """Kobler valg av mast opp mot utskrift av mastetype."""

        mast = None
        for m in self.M.alle_master:
            if m.navn==self.M.mast_resultater.get():
                mast = m
                break

        if mast.type == "bjelke":
            self.M.gittermast.set(False)
        else:
            self.M.gittermast.set(True)

        self._skriv_master()


    def _skriv_krefter(self, *args):
        """Formaterer og printer resultater for valgt mast."""

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

        s = "Grensetilstand".ljust(max_bredde_tilstand + 1)
        kolonner = ("My", "Vy", "Mz", "Vz", "N", "T", "UR")
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
        UR = round(mast.tilstand_My_max.utnyttelsesgrad * 100, 1)
        s += "{}%".format(UR).rjust(kolonnebredde)
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
        temp = mast.tilstand_My_max.temp
        vindretning = "vind fra mast mot spor"
        if mast.tilstand_My_max.vindretning == 1:
            vindretning = "vind fra spor mot mast"
        elif mast.tilstand_My_max.vindretning == 2:
            vindretning = "vind parallelt spor"

        s += "Dimensjonerende lastsituasjon:  {} (T = {}C), ".format(lastsituasjon, temp)
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

    def _skriv_dimensjonerende_faktorer(self, *args):
        """Skriver parametre for utregning av utnyttelsesgrad til egen tekstboks."""

        if self.faktorboks.get(0.0) is not None:
            self.faktorboks.delete(1.0, "end")

        mast = None
        for m in self.M.alle_master:
            if m.navn==self.M.mast_resultater.get():
                mast = m
                break

        if mast.tilstand_My_max.dimensjonerende_faktorer:

            faktorer = sorted([key for key in mast.tilstand_My_max.dimensjonerende_faktorer])

            max_bredde_faktor = 0
            for g in faktorer:
                max_bredde_faktor = len(g) if len(g)>max_bredde_faktor else max_bredde_faktor

            kolonnebredde = 12

            s = "Faktor".ljust(max_bredde_faktor)
            s += "Verdi".rjust(kolonnebredde)
            s += "\n{}\n".format("-"*(max_bredde_faktor+kolonnebredde))

            for key in faktorer:
                val = mast.tilstand_My_max.dimensjonerende_faktorer[key]
                s += key.ljust(max_bredde_faktor)
                s += str(round(val, 2)).rjust(kolonnebredde)
                s += "\n"
        else:
            s = "\nIngen data tilgjengelig.\n"

        self.faktorboks.insert("end", s)


    def _skriv_master(self):
        """Formaterer og printer resultater for samtlige master av valgt type."""

        self.masteboks.delete(1.0, "end")
        masteliste = self.M.gittermaster if self.M.gittermast.get() else self.M.bjelkemaster

        anbefalt_mast = None
        for mast in masteliste:
            if mast.h_max>=self.M.master.h.get() and mast.tilstand_UR_max.utnyttelsesgrad<=1.0:
                anbefalt_mast = mast
                break

        s = "\n"
        if anbefalt_mast:
            s += "Anbefalt mast:  {}   ".format(anbefalt_mast.navn)
            UR = round(anbefalt_mast.tilstand_UR_max.utnyttelsesgrad * 100, 1)
            s += "({:.1f}% utnyttelsesgrad, slankhetskrav OK)\n\n".format(UR)
        else:
            s += "Ingen master oppfyller kravene til utnyttelsesgrad og høyde.\n\n"

        max_bredde_navn = len("Navn")
        for mast in masteliste:
            max_bredde_navn = len(mast.navn) if len(mast.navn)>max_bredde_navn else max_bredde_navn

        kolonnebredde = 10

        s += "Navn".ljust(max_bredde_navn + 1)
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


        # tracer
        self.mast_resultater_tracer = self.M.mast_resultater.trace("w", self._skriv_bidrag)


        self.bidragsboks = tk.Text(hovedvindu, width=86, height=40)
        self.bidragsboks.grid(row=2, column=0, columnspan=3)

        self._skriv_bidrag()

        lukk_btn = tk.Button(self, text="Lukk vindu",
                             font=bold, command=self._lukk_vindu)
        lukk_btn.pack(padx=5, pady=5, side="right")

    def _lukk_vindu(self):
        """Sletter variabel-tracere og lukker vindu."""

        self.M.mast_resultater.trace_vdelete("w", self.mast_resultater_tracer)
        self.master.destroy()

    def _skriv_bidrag(self, *args):
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

        s = "Navn".ljust(max_bredde_navn+1)
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
            max_bredde_navn = 0
            for navn in strekk_ledninger:
                max_bredde_navn = len(navn) if len(navn) > max_bredde_navn else max_bredde_navn
            kolonnebredde = 16
            s += "\nLedning".ljust(max_bredde_navn)
            s += "Strekkraft".rjust(kolonnebredde)
            s += "\n{}\n".format("-" * (max_bredde_navn+kolonnebredde-1))
            for navn in strekk_ledninger:
                s += "{}".format(navn).ljust(max_bredde_navn)
                faktor = mast.tilstand_My_max.faktorer["L"]
                strekkraft = faktor * strekk_ledninger[navn]/1000
                s += "{:.2f} kN\n".format(strekkraft).rjust(kolonnebredde)

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

