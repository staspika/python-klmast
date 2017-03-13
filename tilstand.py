import math

class Tilstand(object):
    """Objekt med informasjon om lasttilstand fra lastfaktoranalyse.
     Lagres i masteobjekt via metoden mast.lagre_lasttilfelle(lasttilfelle)
     """

    def __init__(self, mast, e, K, grensetilstand,
                 g=0, l=0, f1=0, f2=0, f3=0, k=0):
        """Initierer tilstandsobjekt med data om krefter og forskyvninger
         samt lastfaktorer ved gitt lasttilfelle.
         K[:][0:6] = reaksjonskrefter ved fundament
         K[:][6:] = torsjonsvinkel/forskyvning av kontakttråd
         """
        self.K = K
        self.navn = grensetilstand["navn"]
        if self.navn == "bruddgrense":
            self.faktorer = [g, l, f1, f2, f3, k]
            self.N_kap = abs(K[4]*mast.materialkoeff/(mast.fy*mast.A))
            # Ganger med 1000 for å få momenter i [Nmm]
            self.My_kap = abs(1000*K[0] * mast.materialkoeff / (mast.fy*mast.Wy_el))
            self.Mz_kap = abs(1000*K[2] * mast.materialkoeff / (mast.fy * mast.Wz_el))
            self.utnyttelsesgrad = self.N_kap + self.My_kap + self.Mz_kap
        else:
            e = e * 1000  # Max tillatt utblåsning av kontaktledning i [mm]
            self.utnyttelsesgrad = K[8]/e

    def __repr__(self):
        if self.navn == "bruddgrense":
            K = self.K[:][0:6]/1000  # Konverterer krefter til [kNm] og [kN]
            rep = "My = {:.3g}kNm    Vy = {:.3g}kN    Mz = {:.3g}kNm    " \
                  "Vz = {:.3g}kN    N = {:.3g}kN    T = {:.3g}kNm\n".\
                format(K[0],K[1], K[2],K[3], K[4], K[5])
            rep += "My_kap: {:.3g}%    Mz_kap: {:.3g}%    " \
                   "N_kap: {:.3g}%\n".format(self.My_kap*100, self.Mz_kap*100,self.N_kap*100)
            rep += "Utnyttelsesgrad: {:.3g}%".format(self.utnyttelsesgrad * 100)
        else:
            phi = self.K[6]*360/(2*math.pi)  # Torsjonsvinkel i grader
            rep = "Torsjonsvinkel: {:.3g} grader    Dy = {:.3g}mm    " \
                  "Dz = {:.3g}mm\n".format(phi, self.K[7], self.K[8])
            rep += "Utnyttelsesgrad: {:.3g}%".format(self.utnyttelsesgrad * 100)
        return rep




