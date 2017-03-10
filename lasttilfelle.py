import functools

@functools.total_ordering
class Lasttilfelle(object):
    """Objekt med informasjon om lasttilstand fra lastfaktoranalyse.
    Lagres i masteobjekt via metoden mast.lagre_lasttilfelle(lasttilfelle)
    """

    def __init__(self, mast, K, grensetilstand, g, l, f1, f2, f3, k):
        # K = krefter
        self.K = K
        self.tilstand = grensetilstand["navn"]
        self.faktorer = [g, l, f1, f2, f3, k]
        self.N_kap = K[4]*mast.materialkoeff/(mast.fy*mast.A)
        # Ganger med 1000 for å få momenter i [Nmm]
        self.My_kap = 1000*K[0]*mast.materialkoeff/(mast.fy*mast.Wy_el)
        self.Mz_kap = 1000*K[2] * mast.materialkoeff / (mast.fy * mast.Wz_el)
        self.kap = self.N_kap + self.My_kap + self.Mz_kap


    """Metoder for å kunne sortere liste av Lasttilfeller mhp. My."""
    def __eq__(self, other):
        return self.kap == other.kap

    def __lt__(self, other):
       return self.kap < other.kap



