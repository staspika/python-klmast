from numpy import array, zeros, count_nonzero, double

class Kraft(object):
    """Generell klasse for konsentrerte/fordelte laster."""

    def __init__(self, navn="", type=(0, 0), f=[0,0,0],
                 q=[0,0,0], b=0, e=[0,0,0]):
        """Initierer kraftobjekt.

        :param str navn: Identifikasjonstag for kraftens opphav
        :param tuple type: (Rad, etasje) for plassering i R- og D-matrise
        :param list f: Kraftkomponenter [x, y, z]  [N]
        :param list q: Kraftkomponenter for fordelt last [x, y, z]  [N/m]
        :param list b: Utstrekning av fordelt last [m]
        :param list e: Eksentrisitet fra origo [x, y, z]  [m]
        """

        self.navn = navn
        self.type = type
        self.f = array(f)
        self.q = array(q)
        self.b = b
        self.e = array(e)


    def __repr__(self):
        rep = "{}   type={}\n".format(self.navn, self.type)
        if not count_nonzero(self.q) == 0:
            rep += "q*b = {}\n".format(self.q * self.b)
        else:
            rep += "f = {}\n".format(self.f)
        rep += "e = {}\n".format(self.e)
        return rep







