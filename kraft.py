from numpy import array

class Kraft(object):
    """Generell klasse for konsentrerte/fordelte laster og momenter"""

    def __init__(self, navn="", type=0, f=[0,0,0],
                 q=[0,0,0], b=0, e=[0,0,0]):
        """
        Initierer kraft/moment-objekt.
        :param navn: Lastens navn
        :param type: Inngangsrad i R-matrise
        :param f: Kraftkomponenter [x, y, z]  [N]
        :param q: Kraftkomponenter for fordelt last [x, y, z]  [N/m]
        :param b: Utstrekning av fordelt last [m]
        :param e: Eksentrisitet fra origo [x, y, z]  [m]
        """

        self.navn = navn
        self.type = type
        self.f = array(f)
        self.q = array(q)
        self.b = b
        self.e = array(e)

    def __repr__(self):
        rep = "\n{}   type={}\n".format(self.navn, self.type)
        rep += "f = {}\n".format(self.f)
        return rep





