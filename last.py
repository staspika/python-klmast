import numpy as np

class Last(object):
    """Generell klasse for konsentrerte/fordelte laster og momenter"""

    def __init__(self, f=np.array([0,0,0]), q=np.array([0,0,0]),
                 b=np.array([0,0,0]), e=np.array([0,0,0]),
                 type=0, kat=None):
        """Initierer kraft/moment-objekt.
        :param f: Kraftkomponenter [x, y, z]  [N]
        :param q: Kraftkomponenter for fordelt last [x, y, z]  [N/m]
        :param b: Utstrekning av fordelt last [x, y, z]  [m]
        :param e: Eksentrisitet fra origo [x, y, z]  [m]
        :param type: 0=punktlast, 1=uniformt distribuert last,
                     2=vindlast, 3=moment
        :param kat: Lastkategori for applikasjon av partialfaktorer 
        """

        self.e = e
        self.type = type
        self.kat = kat

        if type==0:
            self.f = f
        elif type==1 or type==2:
            self.q = q
            self.b = b
        elif type==3:
            self.m = f * e



