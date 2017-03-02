import beregning

"""Her finnes logikken til hovedprogrammet. Kun denne filen kan kjøres!"""



print("Velkommen til Bane NORs fantastiske nye beregningsverktøy!")




with open("input.ini", "r") as ini:
    beregning.beregn(ini)



