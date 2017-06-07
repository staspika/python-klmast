"""Grafisk brukergrensesnitt, avlesing/skriving av inndata til .ini-fil."""

import tkinter as tk
import configparser
import lister
import ctypes
import math
from collections import OrderedDict
from datetime import date


# Fonter
skrifttype = "Helvetica"
skriftstr = 11
banner = (skrifttype, math.floor(skriftstr*1.3))
plain = (skrifttype, skriftstr)
bold = (skrifttype, skriftstr, "bold")
italic = (skrifttype, skriftstr, "italic")

class KL_fund(tk.Tk):
    """Hovedprogram."""

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("KL_fund 2.0")

        # root.state("zoomed")
        user32 = ctypes.windll.user32
        self.x = int(user32.GetSystemMetrics(0) * 0.95)
        self.y = int(user32.GetSystemMetrics(1) * 0.90)
        self.geometry("{}x{}".format(self.x, self.y))

        self.masteavstand_max = 63.0
        self.h_range = [10.0, 8.0, 13.0]
        self.hfj_type = "fjern-/AT-ledning"
        self.hfj_range = [10.5, 8.0, 13.0]
        self.hf_type = "forbigangs-/fiberoptisk ledning"
        self.hf_range = [7.8, 8.0, 13.0]
        self.hj_range = [7.3, 8.0, 13.0]
        self.hr_range = [7.3, 8.0, 13.0]
        self.fh_range = [5.7, 8.0, 13.0]
        self.sh_range = [1.6, 8.0, 13.0]
        self.e_range = [0.0, 8.0, 13.0]
        self.sms_range = [3.5, -5.1, 3]

        self._gittermast = tk.BooleanVar()


        # --- Variabeloversikt ---
        # Variabler med prefix _ er kun hjelpevariabler
        # og skrives ikke til .ini-fil.

        # Info
        self.banestrekning = tk.StringVar()
        self.km = tk.DoubleVar()
        self.prosjektnr = tk.IntVar()
        self.mastenr = tk.IntVar()
        self.signatur = tk.StringVar()
        self.dato = tk.StringVar()

        # Mastealternativer
        self._mastefelt = tk.IntVar()
        self.siste_for_avspenning = tk.BooleanVar()
        self.linjemast_utliggere = tk.IntVar()
        self.avstand_fixpunkt = tk.IntVar()
        self._alternative_mastefunksjoner = tk.IntVar()
        self._alternativ_funksjon = tk.IntVar()
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
        self.differansestrekk = tk.DoubleVar()

        # System
        self.systemnavn = tk.StringVar()
        self.radius = tk.IntVar()
        self.hogfjellsgrense = tk.BooleanVar()
        self.masteavstand = tk.DoubleVar()
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
        self._s235 = tk.StringVar()
        self.s235 = tk.BooleanVar()
        self.materialkoeff = tk.DoubleVar()
        self.traverslengde = tk.DoubleVar()
        self.ec3 = tk.BooleanVar()


class Hovedvindu(tk.Frame):
    """Vindu for hovedprogram."""

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.pack(fill="both")


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

        # mastefelt
        mastefelt = tk.LabelFrame(venstre, text="Mastefelt", font=bold)
        mastefelt.pack(fill="both")
        tk.Radiobutton(mastefelt, text="Linjemast med enkel utligger", font=plain,
                       variable=self.master._mastefelt, value=0).pack(anchor="w")
        tk.Radiobutton(mastefelt, text="Linjemast med dobbel utligger", font=plain,
                       variable=self.master._mastefelt, value=1).pack(anchor="w")
        tk.Radiobutton(mastefelt, text="Siste seksjonsmast før avspenning", font=plain,
                       variable=self.master._mastefelt, value=2).pack(anchor="w")
        tk.Label(mastefelt, text="Avstand til fixpunkt: [m]  ", font=plain).pack(anchor="w", side="left")
        self.master.avstand_fixpunkt.set(700)
        fixverdier = tuple(f for f in range(0, 801, 25))
        self.fixavstand_spinbox = tk.Spinbox(mastefelt, values=fixverdier,
                                             width=10)
        self.fixavstand_spinbox.delete(0,"end")
        self.fixavstand_spinbox.insert(0, self.master.avstand_fixpunkt.get())
        self.fixavstand_spinbox.config(font=plain, state="readonly")
        self.fixavstand_spinbox.pack(anchor="e", side="right", padx=5, pady=8)

        # mastefunksjoner
        mastefunksjoner = tk.LabelFrame(venstre, text="Mastefunksjoner", font=bold)
        mastefunksjoner.pack(fill="both")
        alternative_funksjoner = tk.Checkbutton(mastefunksjoner, text="Alternative mastefunksjoner",
                                                font=plain, variable=self.master._alternative_mastefunksjoner,
                                                onvalue=True, offvalue=False)
        alternative_funksjoner.pack(anchor="w")
        tk.Radiobutton(mastefunksjoner, text="Fixpunktmast", font=plain,
                       variable=self.master._alternativ_funksjon, value=0)\
                       .pack(anchor="w", padx=15)
        tk.Radiobutton(mastefunksjoner, text="Fixavspenningsmast", font=plain,
                       variable=self.master._alternativ_funksjon, value=1)\
                       .pack(anchor="w", padx=15)
        tk.Radiobutton(mastefunksjoner, text="Avspenningsmast", font=plain,
                       variable=self.master._alternativ_funksjon, value=2)\
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

        # fastavspente ledninger
        fastavspente = tk.LabelFrame(venstre, text="Fastavspente ledninger", font=bold)
        fastavspente.pack(fill="both")
        tk.Checkbutton(fastavspente, text="Mate-/fjernledning", font=plain,
                       variable=self.master.matefjern_ledn, onvalue=True,
                       offvalue=False).grid(row=0, column=0, sticky="W")
        tk.Label(fastavspente, text="Antall:    ", font=plain).grid(row=0, column=1, sticky="E")
        self.master.matefjern_antall.set(1)
        self.matefjern_spinbox = tk.Spinbox(fastavspente, values=(1, 2), width=10)
        self.matefjern_spinbox.delete(0, "end")
        self.matefjern_spinbox.insert(0, self.master.matefjern_antall.get())
        self.matefjern_spinbox.config(font=plain, state="readonly")
        self.matefjern_spinbox.grid(row=0, column=2, sticky="W")
        tk.Checkbutton(fastavspente, text="AT-ledninger (2 stk.)", font=plain,
                       variable=self.master.at_ledn, onvalue=True,
                       offvalue=False).grid(row=1, column=0, sticky="W")
        self.master.at_type.set(lister.at_list[0])
        at_menu= tk.OptionMenu(fastavspente, self.master.at_type, *lister.at_list)
        at_menu.config(font=plain)
        at_menu.grid(row=1, column=1, sticky="W", columnspan=2)
        tk.Checkbutton(fastavspente, text="Forbigangsledning (1 stk.)", font=plain,
                       variable=self.master.forbigang_ledn, onvalue=True,
                       offvalue=False).grid(row=2, column=0, sticky="W")
        tk.Checkbutton(fastavspente, text="Jordledning (1 stk.)", font=plain,
                       variable=self.master.jord_ledn, onvalue=True,
                       offvalue=False).grid(row=3, column=0, sticky="W")
        self.master.jord_type.set(lister.jord_list[0])
        jord_menu = tk.OptionMenu(fastavspente, self.master.jord_type, *lister.jord_list)
        jord_menu.config(font=plain)
        jord_menu.grid(row=3, column=1, sticky="W", columnspan=2)
        tk.Checkbutton(fastavspente, text="Returledninger (2 stk.)", font=plain,
                       variable=self.master.retur_ledn, onvalue=True,
                       offvalue=False).grid(row=4, column=0, sticky="W")
        tk.Checkbutton(fastavspente, text="Fiberoptisk ledning (1 stk.)", font=plain,
                       variable=self.master.fiberoptisk_ledn, onvalue=True,
                       offvalue=False).grid(row=5, column=0, sticky="W")
        tk.Label(fastavspente, text="Differansestrekk: [kN]  ", font=plain)\
                 .grid(row=6, column=0)
        self.master.differansestrekk.set(0.2)
        diffverdier = ()
        for d in [a for a in range(0, 201, 5)]:
            diffverdier += (d/100,)
        self.diff_spinbox = tk.Spinbox(fastavspente, values=diffverdier, width=10)
        self.diff_spinbox.delete(0, "end")
        self.diff_spinbox.insert(0, self.master.differansestrekk.get())
        self.diff_spinbox.config(font=plain, state="readonly")
        self.diff_spinbox.grid(row=6, column=1)

        # system
        system = tk.LabelFrame(hoyre, text="System", font=bold)
        system.pack(fill="both")
        self.master.systemnavn.set(lister.system_list[0])
        system_menu = tk.OptionMenu(system, self.master.systemnavn, *lister.system_list)
        system_menu.config(font=plain)
        system_menu.grid(row=0, column=0, sticky="W", columnspan=2)
        tk.Label(system, text="Radius: [m]  ", font=plain)\
            .grid(row=1, column=0, sticky="W")
        self.master.radius.set(lister.radius_list[11])
        radius_menu = tk.OptionMenu(system, self.master.radius, *lister.radius_list)
        radius_menu.config(font=plain)
        radius_menu.grid(row=1, column=1, sticky="W")
        hogfjellsgrense = tk.Checkbutton(system, text="Høgfjellsgrense",
                                        font=plain, variable=self.master.hogfjellsgrense,
                                        onvalue=True, offvalue=False)
        hogfjellsgrense.grid(row=2, column=0, sticky="W")
        tk.Label(system, text="Masteavstand: [m]  ", font=plain) \
            .grid(row=3, column=0, sticky="W")
        self.master.masteavstand.set(self.master.masteavstand_max)
        self.masteavstand_spinbox = tk.Spinbox(system, from_=0.0, to=63.0,
                                        increment=0.1, width=10, repeatinterval=25)
        self.masteavstand_spinbox.delete(0, "end")
        self.masteavstand_spinbox.insert(0, self.master.masteavstand.get())
        self.masteavstand_spinbox.config(font=plain, state="readonly")
        self.masteavstand_spinbox.grid(row=3, column=1, sticky="W")
        tk.Label(system, text="(Max. masteavstand = {} m)"
                 .format(self.master.masteavstand_max), font=italic)\
                 .grid(row=4, column=0, sticky="W", columnspan=2)
        vind_btn = tk.Button(system, text="Vind", font=bold, width=12)
        vind_btn.grid(row=5, column=0, sticky="W")
        self.master.vindkasthastighetstrykk.set(0.71)
        tk.Label(system, text="(Vindkasthastighetstrykk = {} kN/m^2)"
                 .format(self.master.vindkasthastighetstrykk.get()), font=italic) \
            .grid(row=5, column=1, sticky="W")

        # geometriske data
        geom_data = tk.LabelFrame(hoyre, text="System", font=bold)
        geom_data.pack(fill="both")
        g_1 = tk.Frame(geom_data, relief="groove", bd=1)
        g_1.pack(fill="both")

        # h
        tk.Label(g_1, text="    (mastehøyde): [m]  ", font=plain) \
            .grid(row=0, column=0, sticky="W")
        tk.Label(g_1, text="H", font=bold) \
            .grid(row=0, column=0, sticky="W")
        self.master.h.set(self.master.h_range[0])
        self.h_spinbox = tk.Spinbox(g_1, from_=self.master.h_range[1], to=self.master.h_range[2],
                                    increment=0.5, repeatinterval=120, width=10)
        self.h_spinbox.delete(0, "end")
        self.h_spinbox.insert(0, self.master.h.get())
        self.h_spinbox.config(font=plain, state="readonly")
        self.h_spinbox.grid(row=0, column=1, sticky="W")

        # hfj
        tk.Label(g_1, text="      ({}): [m]  ".format(self.master.hfj_type), font=plain) \
            .grid(row=1, column=0, sticky="W")
        tk.Label(g_1, text="Hfj", font=bold) \
            .grid(row=1, column=0, sticky="W")
        self.master.hfj.set(self.master.hfj_max)
        self.hfj_spinbox = tk.Spinbox(g_1, from_=0.0, to=self.master.hfj_max,
                                    increment=0.1, repeatinterval=60, width=10)
        self.hfj_spinbox.delete(0, "end")
        self.hfj_spinbox.insert(0, self.master.hfj.get())
        self.hfj_spinbox.config(font=plain, state="readonly")
        self.hfj_spinbox.grid(row=1, column=1, sticky="W")

        # hf
        tk.Label(g_1, text="     ({}): [m]  ".format(self.master.hf_type), font=plain) \
            .grid(row=2, column=0, sticky="W")
        tk.Label(g_1, text="Hf", font=bold) \
            .grid(row=2, column=0, sticky="W")
        self.master.hf.set(self.master.hf_max)
        self.hf_spinbox = tk.Spinbox(g_1, from_=0.0, to=self.master.hf_max,
                                      increment=0.1, repeatinterval=60, width=10)
        self.hf_spinbox.delete(0, "end")
        self.hf_spinbox.insert(0, self.master.hf.get())
        self.hf_spinbox.config(font=plain, state="readonly")
        self.hf_spinbox.grid(row=2, column=1, sticky="W")

        # hj
        tk.Label(g_1, text="     (jordledning): [m]  ", font=plain) \
            .grid(row=3, column=0, sticky="W")
        tk.Label(g_1, text="Hj", font=bold) \
            .grid(row=3, column=0, sticky="W")
        self.master.hj.set(self.master.hj_max)
        self.hj_spinbox = tk.Spinbox(g_1, from_=0.0, to=self.master.hj_max,
                                     increment=0.1, repeatinterval=60, width=10)
        self.hj_spinbox.delete(0, "end")
        self.hj_spinbox.insert(0, self.master.hj.get())
        self.hj_spinbox.config(font=plain, state="readonly")
        self.hj_spinbox.grid(row=3, column=1, sticky="W")

        # hr
        tk.Label(g_1, text="     (returledning): [m]  ", font=plain) \
            .grid(row=4, column=0, sticky="W")
        tk.Label(g_1, text="Hr", font=bold) \
            .grid(row=4, column=0, sticky="W")
        self.master.hr.set(self.master.hr_max)
        self.hr_spinbox = tk.Spinbox(g_1, from_=0.0, to=self.master.hr_max,
                                     increment=0.1, repeatinterval=60, width=10)
        self.hr_spinbox.delete(0, "end")
        self.hr_spinbox.insert(0, self.master.hr.get())
        self.hr_spinbox.config(font=plain, state="readonly")
        self.hr_spinbox.grid(row=4, column=1, sticky="W")
        g_2 = tk.Frame(geom_data, relief="groove", bd=1)
        g_2.pack(fill="both")

        # fh
        tk.Label(g_2, text="      (kontakttråd): [m]  ", font=plain) \
            .grid(row=0, column=0, sticky="W")
        tk.Label(g_2, text="FH", font=bold) \
            .grid(row=0, column=0, sticky="W")
        self.master.fh.set(self.master.fh_max)
        self.fh_spinbox = tk.Spinbox(g_2, from_=0.0, to=self.master.fh_max,
                                     increment=0.1, repeatinterval=60, width=10)
        self.fh_spinbox.delete(0, "end")
        self.fh_spinbox.insert(0, self.master.fh.get())
        self.fh_spinbox.config(font=plain, state="readonly")
        self.fh_spinbox.grid(row=0, column=1, sticky="W")

        # sh
        tk.Label(g_2, text="      (systemhøyde): [m]  ", font=plain) \
            .grid(row=1, column=0, sticky="W")
        tk.Label(g_2, text="SH", font=bold) \
            .grid(row=1, column=0, sticky="W")
        self.master.sh.set(self.master.sh_max)
        self.sh_spinbox = tk.Spinbox(g_2, from_=0.0, to=self.master.sh_max,
                                     increment=0.1, repeatinterval=60, width=10)
        self.sh_spinbox.delete(0, "end")
        self.sh_spinbox.insert(0, self.master.sh.get())
        self.sh_spinbox.config(font=plain, state="readonly")
        self.sh_spinbox.grid(row=1, column=1, sticky="W")

        # e
        tk.Label(g_2, text="    (SOK - top fundament): [m]  ", font=plain) \
            .grid(row=2, column=0, sticky="W")
        tk.Label(g_2, text="e", font=bold) \
            .grid(row=2, column=0, sticky="W")
        self.master.e.set(self.master.e_max)
        self.e_spinbox = tk.Spinbox(g_2, from_=0.0, to=self.master.e_max,
                                     increment=0.1, repeatinterval=60, width=10)
        self.e_spinbox.delete(0, "end")
        self.e_spinbox.insert(0, self.master.e.get())
        self.e_spinbox.config(font=plain, state="readonly")
        self.e_spinbox.grid(row=2, column=1, sticky="W")

        # sms
        tk.Label(g_2, text="      (s mast - s spor): [m]  ", font=plain) \
            .grid(row=3, column=0, sticky="W")
        tk.Label(g_2, text="SMS", font=bold) \
            .grid(row=3, column=0, sticky="W")
        self.master.sms.set(self.master.sms_max)
        self.sms_spinbox = tk.Spinbox(g_2, from_=0.0, to=self.master.sms_max,
                                    increment=0.1, repeatinterval=60, width=10)
        self.sms_spinbox.delete(0, "end")
        self.sms_spinbox.insert(0, self.master.sms.get())
        self.sms_spinbox.config(font=plain, state="readonly")
        self.sms_spinbox.grid(row=3, column=1, sticky="W")

        # mast
        mast = tk.LabelFrame(hoyre, text="Mast", font=bold)
        mast.pack(fill="both")
        self.master._gittermast.set(True)
        tk.Radiobutton(mast, text="Gittermast", font=plain,
                       variable=self.master._gittermast, value=True) \
            .grid(row=0, column=0, sticky="W", pady=2)
        tk.Radiobutton(mast, text="Bjelkemast", font=plain,
                       variable=self.master._gittermast, value=False) \
            .grid(row=0, column=1, sticky="W", pady=2)
        self.master._s235.set(False)
        tk.Label(mast, text="Stålkvalitet:", font=plain).grid(row=1, column=0)
        self.master._s235.set("S355")
        system_menu = tk.OptionMenu(mast, self.master._s235, *lister.staal_list)
        system_menu.config(font=plain)
        system_menu.grid(row=1, column=1, sticky="W", columnspan=1)

        # avansert/beregn
        av_beregn = tk.LabelFrame(hoyre, text="Fullfør", font=bold)
        av_beregn.pack(fill="both")
        avansert_btn = tk.Button(av_beregn, text="Avansert", font=plain)
        avansert_btn.pack(side="left")
        beregn_btn = tk.Button(av_beregn, text="Kjør beregning", font=bold)
        beregn_btn.pack(side="right")





    def _skriv_ini(self):
        """Skriver varibelverdier fra hovedprogram til .ini-fil."""

        self.master.siste_for_avspenning.set(False)
        if self.master._mastefelt.get() == 0:
            self.master.linjemast_utliggere.set(1)
        elif self.master._mastefelt.get() == 1:
            self.master.linjemast_utliggere.set(2)
        else:
            self.master.siste_for_avspenning.set(True)
            self.master.linjemast_utliggere.set(2)

        self.master.avstand_fixpunkt.set(self.fixavstand_spinbox.get())

        self.master.fixpunktmast.set(False)
        self.master.fixavspenningsmast.set(False)
        self.master.avspenningsmast.set(False)
        if self.master._alternativ_funksjon.get() == 0:
            self.master.fixpunktmast.set(True)
        elif self.master._alternativ_funksjon.get() == 1:
            self.master.fixavspenningsmast.set(True)
        elif self.master._alternativ_funksjon.get() == 2:
            self.master.avspenningsmast.set(True)

        self.master.differansestrekk.set(self.diff_spinbox.get())

        self.master.s235 = False if self.master._s235.get() == "S235" else True


        cfg = configparser.ConfigParser(dict_type=OrderedDict)
        cfg["Info"] = OrderedDict([("banestrekning", self.master.banestrekning.get()),
                                   ("km", self.master.km.get()),
                                   ("prosjektnr", self.master.prosjektnr.get()),
                                   ("mastenr", self.master.mastenr.get()),
                                   ("signatur", self.master.signatur.get()),
                                   ("dato", self.master.dato.get())])
        cfg["Mastealternativer"] = OrderedDict([("siste_for_avspenning", self.master.siste_for_avspenning.get()),
                                                ("linjemast_utliggere", self.master.linjemast_utliggere.get()),
                                                ("avstand_fixpunkt", self.master.avstand_fixpunkt.get()),
                                                ("fixpunktmast", self.master.fixpunktmast.get()),
                                                ("fixavspenningsmast", self.master.fixavspenningsmast.get()),
                                                ("avspenningsmast", self.master.avspenningsmast.get()),
                                                ("strekkutligger", self.master.strekkutligger.get()),
                                                ("master_bytter_side", self.master.master_bytter_side.get()),
                                                ("avspenningsbardun", self.master.avspenningsbardun.get())])
        cfg["Fastavspent"] = OrderedDict([("matefjern_ledn", self.master.matefjern_ledn.get()),
                                          ("matefjern_antall", self.master.matefjern_antall.get()),
                                          ("at_ledn", self.master.at_ledn.get()),
                                          ("at_type", self.master.at_type.get()),
                                          ("forbigang_ledn", self.master.forbigang_ledn.get()),
                                          ("jord_ledn", self.master.jord_ledn.get()),
                                          ("jord_type", self.master.jord_type.get()),
                                          ("fiberoptisk_ledn", self.master.fiberoptisk_ledn.get()),
                                          ("retur_ledn", self.master.retur_ledn.get()),
                                          ("differansestrekk", self.master.differansestrekk.get())])
        cfg["System"] = OrderedDict([("systemnavn", self.master.systemnavn.get()),
                                     ("radius", self.master.radius.get()),
                                     ("hogfjellsgrense", self.master.hogfjellsgrense.get()),
                                     ("masteavstand", self.master.masteavstand.get()),
                                     ("vindkasthastighetstrykk", self.master.vindkasthastighetstrykk.get())])
        cfg["Geometri"] = OrderedDict([("h", self.master.h.get()), ("hfj", self.master.hfj.get()),
                                       ("hf", self.master.hf.get()), ("hj", self.master.hj.get()),
                                       ("hr", self.master.hr.get()), ("fh", self.master.fh.get()),
                                       ("sh", self.master.sh.get()), ("e", self.master.e.get()),
                                       ("sms", self.master.sms.get())])
        cfg["Div"] = OrderedDict([("s235", self.master.s235.get()), ("materialkoeff", self.master.materialkoeff.get()),
                                  ("traverslengde", self.master.traverslengde.get()), ("ec3", self.master.ec3.get())])

        with open("input_test.ini", "w") as ini:
            cfg.write(ini)

    def _vind(self):
        pass





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



def _valider(event):
    """Validerer programtilstand."""
    print("Tilstand OK.")
    return True






if __name__ == "__main__":

    # Kjører program
    root = KL_fund()
    hovedvindu = Hovedvindu(root)
    root.mainloop()

