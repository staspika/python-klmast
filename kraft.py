import numpy as np

class Kraft(object):
    """Generell klasse for konsentrerte/fordelte laster og momenter"""

    def __init__(self, navn="", type=0, f=np.array([0,0,0]),
                 q=np.array([0,0,0]), b=np.array([0,0,0]),
                 e=np.array([0,0,0])):
        """
        Initierer kraft/moment-objekt.
        :param navn: Lastens navn
        :param type: Inngangsrad i R-matrise
        :param f: Kraftkomponenter [x, y, z]  [N]
        :param q: Kraftkomponenter for fordelt last [x, y, z]  [N/m]
        :param b: Utstrekning av fordelt last [x, y, z]  [m]
        :param e: Eksentrisitet fra origo [x, y, z]  [m]
        """

        self.navn = navn
        self.f = f
        self.q = q
        self.b = b
        self.e = e
        self.type = type




