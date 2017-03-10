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
        self.N_kap = abs(K[4]*mast.materialkoeff/(mast.fy*mast.A))
        # Ganger med 1000 for å få momenter i [Nmm]
        self.My_kap = abs(1000*K[0]*mast.materialkoeff/(mast.fy*mast.Wy_el))
        self.Mz_kap = abs(1000*K[2] * mast.materialkoeff / (mast.fy * mast.Wz_el))
        self.kap = self.N_kap + self.My_kap + self.Mz_kap


    """Metoder for å kunne sortere liste av Lasttilfeller mhp. My."""
    def __eq__(self, other):
        return self.kap == other.kap

    def __lt__(self, other):
       return self.kap > other.kap

    def __repr__(self):
        K = self.K/1000
        rep = "My = {:.3g}kNm    Vy = {:.3g}kN    Mz = {:.3g}kNm    " \
              "Vz = {:.3g}kN\n".format(K[0],K[1],K[2],K[3])
        rep += "My_kap: {:.3g}%    Mz_kap: {:.3g}%    " \
               "N_kap: {:.3g}%\n".format(self.My_kap*100, self.Mz_kap*100,self.N_kap*100)
        rep += "Utnyttelsesgrad: {:.3g}%".format(self.kap*100)
        return rep



