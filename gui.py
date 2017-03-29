from tkinter import *
from PIL import ImageTk, Image
import configparser
import kilometrering
from collections import OrderedDict
from datetime import date

"""Grafisk brukergrensesnitt, avlesing/skriving av inndata til .ini-fil"""


# Hovedvindu
root = Tk()
root.title("KL_fund 2.0")
#root.state("zoomed")
bredde = 1920
hoyde = 1080
root.geometry("{}x{}".format(bredde, hoyde))

# Variabeloversikt
# Info
banestrekning = StringVar()
km = DoubleVar()
prosjektnr = IntVar()
mastenr = IntVar()
signatur = StringVar()
dato = StringVar()

# Mastealternativer
siste_for_avspenning = BooleanVar()
linjemast_utliggere = IntVar()
avstand_fixpunkt = IntVar()
fixpunktmast = BooleanVar()
fixavspenningsmast = BooleanVar()
avspenningsmast = BooleanVar()
strekkutligger = BooleanVar()
master_bytter_side = BooleanVar()
avspenningsbardun = BooleanVar()

# Fastavspente ledninger
matefjern_ledn = BooleanVar()
matefjern_antall = IntVar()
at_ledn = BooleanVar()
at_type = IntVar()
forbigang_ledn = BooleanVar()
jord_ledn = BooleanVar()
jord_type = IntVar()
fiberoptisk_ledn = BooleanVar()
retur_ledn = BooleanVar()
differansestrekk = DoubleVar()

# System
systemnavn = StringVar()
radius = IntVar()
hogfjellsgrense = BooleanVar()
masteavstand = DoubleVar()
vindkasthastighetstrykk = DoubleVar()

# Geometri
h = DoubleVar()
hfj = DoubleVar()
hf = DoubleVar()
hj = DoubleVar()
hr = DoubleVar()
fh = DoubleVar()
sh = DoubleVar()
e = DoubleVar()
sms = DoubleVar()

# Diverse
s235 = BooleanVar()
materialkoeff = DoubleVar()
traverslengde = DoubleVar()
ec3 = BooleanVar()


def _valider(event):
    """Validerer programtilstand"""
    print("Tilstand OK.")
    return True

def _skriv_ini():
    """Skriver varibelverdier til input-fil"""
    cfg = configparser.ConfigParser(dict_type=OrderedDict)
    cfg["Info"] = OrderedDict([("banestrekning", banestrekning.get()),
                               ("km", km.get()),
                               ("prosjektnr", prosjektnr.get()),
                               ("mastenr", mastenr.get()),
                               ("signatur", signatur.get()),
                               ("dato", dato.get())])
    cfg["Mastealternativer"] = OrderedDict([("siste_for_avspenning", siste_for_avspenning.get()),
                                            ("linjemast_utliggere", linjemast_utliggere.get()),
                                            ("avstand_fixpunkt", avstand_fixpunkt.get()),
                                            ("fixpunktmast", fixpunktmast.get()),
                                            ("fixavspenningsmast", fixavspenningsmast.get()),
                                            ("avspenningsmast", avspenningsmast.get()),
                                            ("strekkutligger", strekkutligger.get()),
                                            ("master_bytter_side", master_bytter_side.get()),
                                            ("avspenningsbardun", avspenningsbardun.get())])
    cfg["Fastavspent"] = OrderedDict([("matefjern_ledn", matefjern_ledn.get()),
                                      ("matefjern_antall", matefjern_antall.get()),
                                      ("at_ledn", at_ledn.get()),
                                      ("at_type", at_type.get()),
                                      ("forbigang_ledn", forbigang_ledn.get()),
                                      ("jord_ledn", jord_ledn.get()),
                                      ("jord_type", jord_type.get()),
                                      ("fiberoptisk_ledn", fiberoptisk_ledn.get()),
                                      ("retur_ledn", retur_ledn.get()),
                                      ("differansestrekk", differansestrekk.get())])
    cfg["System"] = OrderedDict([("systemnavn", systemnavn.get()),
                                 ("radius", radius.get()),
                                 ("hogfjellsgrense", hogfjellsgrense.get()),
                                 ("masteavstand", masteavstand.get()),
                                 ("vindkasthastighetstrykk", vindkasthastighetstrykk.get())])
    cfg["Geometri"] = OrderedDict([("h", h.get()), ("hfj", hfj.get()),
                                   ("hf", hf.get()), ("hj", hj.get()),
                                   ("hr", hr.get()), ("fh", fh.get()),
                                   ("sh", sh.get()), ("e", e.get()),
                                   ("sms", sms.get())])
    cfg["Div"] = OrderedDict([("s235", s235.get()), ("materialkoeff", materialkoeff.get()),
                              ("traverslengde", traverslengde.get()), ("ec3", ec3.get())])

    with open("input_test.ini", "w") as ini:
        cfg.write(ini)
    root.destroy()


# Info
info = Frame(root, width=0.98 * bredde, height=0.10 * hoyde, bd=3, relief="ridge")
info.grid(row=0, column=0, padx=5, pady=5, sticky=W, columnspan=2)

Label(info, text="KONTAKTLEDNINGSMASTER OG KREFTER I TOPP FUNDAMENT",
      font=("", 16), fg="blue").grid(row=0, column=0, sticky=W, columnspan=4)

# banestrekning
banestrekning.set(kilometrering.kilometer_list[0])
Label(info, text="Banestrekning:").grid(row=1, column=0, sticky=E)
OptionMenu(info, banestrekning, *kilometrering.kilometer_list)\
    .grid(row=1, column=1, sticky=W)
# km
km.set(kilometrering.kilometer[kilometrering.kilometer_list[0]][0])
Label(info, text="Km:").grid(row=1, column=2, sticky=E)
Entry(info, textvariable=km, bg="red").grid(row=1, column=3, sticky=W)
# prosjektnr
prosjektnr.set(0)
Label(info, text="Prosj.nr:").grid(row=0, column=4, sticky=E)
Entry(info, textvariable=prosjektnr, bg="red").grid(row=0, column=5, sticky=W)
# mastenr
mastenr.set(0)
Label(info, text="Mastenr:").grid(row=1, column=4, sticky=E)
Entry(info, textvariable=mastenr, bg="red").grid(row=1, column=5, sticky=W)
# signatur
signatur.set("ANONYM")
Label(info, text="Sign.:").grid(row=0, column=6, sticky=E)
Entry(info, textvariable=signatur, bg="red").grid(row=0, column=7, sticky=W)
# dato
today = date.today()
dato.set("{}.{}.{}".format(today.day, today.month, today.year))
Label(info, text="Dato:").grid(row=0, column=8, sticky=E)
Entry(info, textvariable=dato, state="readonly").grid(row=0, column=9, sticky=W)
# kontroll
Label(info, text="Kontroll:").grid(row=1, column=6, sticky=E)
# kontrolldato
Label(info, text="Dato for kontroll:").grid(row=1, column=8, sticky=E)

# Inngangsdata
inngangsdata = Frame(root, width=0.48 * bredde, height=0.78 * hoyde, bd=3, relief="ridge")
inngangsdata.grid(row=1, column=0, padx=5, pady=5, sticky=W)

# Grafikk
grafikk = Frame(root, width=0.48 * bredde, height=0.6 * hoyde)
grafikk.grid(row=1, column=1, padx=5, pady=5, sticky=W)
bilde = "mast_grafikk.jpg"
img = ImageTk.PhotoImage(Image.open(bilde))
Label(grafikk, image=img).grid(row=0, column=0)

# Kjør
kjor = Frame(root, width=0.48 * bredde, height=0.10 * hoyde)
kjor.grid(row=2, column=0, padx=5, pady=5, sticky=W)
Button(kjor, text="KJØR", command=_skriv_ini).grid(row=0, column=0)







root.mainloop()

