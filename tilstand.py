import math

class Tilstand(object):
    """Objekt med informasjon om lasttilstand fra lastfaktoranalyse.
     Lagres i masteobjekt via metoden mast.lagre_lasttilfelle(lasttilfelle)
     """

    def __init__(self, mast, K, grensetilstand,
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
            self.N_kap = abs(K[4] * mast.materialkoeff / (mast.fy * mast.A))
            # Ganger med 1000 for å få momenter i [Nmm]
            self.My_kap = abs(1000 * K[0] * mast.materialkoeff / (mast.fy * mast.Wy_el))
            self.Mz_kap = abs(1000 * K[2] * mast.materialkoeff / (mast.fy * mast.Wz_el))
            self.utnyttelsesgrad = self.beregn_utnyttelsesgrad(mast, K)
        else:
            # Max tillatt utblåsning av kontaktledning i [mm]
            self.utnyttelsesgrad = K[8]/630

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

    def beregn_utnyttelsesgrad(self, mast, K):
        """Beregner dimensjonerende utnyttelsesgrad u i bruddgrensetilstand"""

        # Standard kapasitetssjekk ihht. EC3 og bransjestandard
        u = self.N_kap + self.My_kap + self.Mz_kap

        if mast.navn == "H":
            # LOKAL knekkapasitet for H-mast
            # Utføres for gurt og diagonal helt nede ved mastefot.

            # Trykkraft [N] i mest påkjente DIAGONAL er den største av:
            N_Ed_d = max(math.sqrt(2) / 2 * K[1], math.sqrt(2) / 2 * K[3])
            N_Rk_d = mast.d_A * mast.fy  # [N]Aksialkraftkap
            # Eulerlasten - kritisk aksialkraftkapasitet [N]
            l_d = 0.55 * 683  # [mm] Referansempl for 13m høy mast
            N_cr_d = (math.pi ** 2 * mast.E * mast.I_d) / (l_d ** 2)
            lam_d = math.sqrt(N_Rk_d / N_cr_d)  # Relativ slankhet [1]
            alpha_d = 0.49  # Imperfeksjonsfaktor [1] for knekkurve c
            phi_d = 0.5 * (1 + alpha_d * (lam_d - 0.2) + lam_d ** 2)
            X_d = 1 / (phi_d + math.sqrt((phi_d ** 2) - (lam_d ** 2)))
            if X_d > 1.0:
                X_d = 1.0
            knekk_d = (N_Ed_d * mast.materialkoeff) / (X_d * N_Rk_d)

            # Trykkraft i GURT (vinkelprofil) [N]:
            b = mast.bredde(mast.h - 1)
            N_Ed_g = 0.5 * ((K[0] / b) + (K[2] / b) + K[1] + K[3]) + K[4] / 4
            N_Rk_g = mast.A_profil * mast.fy  # [N]Aksialkraftkapasitet
            # Eulerlasten - kritisk aksialkraftkapasitet [N]:
            l_g = 0.85 * mast.h * 1000  # [mm] Mastehøyde
            N_cr_g = (math.pi ** 2 * mast.E * mast.Iy_profil) / (l_g ** 2)
            lam_g = math.sqrt(N_Rk_g / N_cr_g)  # Relativ slankhet [1]
            alpha_g = 0.34  # Imperfeksjonsfaktor [1] for knekkurve b
            phi_g = 0.5 * (1 + alpha_g * (lam_g - 0.2) + lam_g ** 2)
            X_g = 1 / (phi_g + math.sqrt((phi_g ** 2) - (lam_g ** 2)))
            if X_g > 1.0:
                X_g = 1.0
            # Utnyttelsesgrad av aksialkraftkapasitet i gurt
            knekk_g = (N_Ed_g * mast.materialkoeff) / (X_g * N_Rk_g)

            # GLOBAL mastekontroll
            M_y_ed = K[0]
            M_z_ed = K[2]
            N_ed = K[4]
            gamma = mast.materialkoeff
            # Momentkapasitet om sterk og svak akse [Nmm]
            # Masten er konisk. Bredden b = 0.9 i mastefot benyttes.
            b_g = 0.9 * mast.bredde(mast.h)
            M_y_Rk = b_g * N_Rk_g * 2
            M_z_Rk = M_y_Rk
            # H-mastens 2. arealmoment
            I_y = 4 * (mast.Iy_profil + mast.A_profil * (b_g / 2) ** 2)
            # Eulerlasten - globalt - for H-mast.
            N_cr_H = (math.pi * mast.E * I_y) / (0.85 * mast.h ** 2)
            # Relativ slankhet [1]
            lam_H = math.sqrt((4 * mast.A_profil * mast.fy) / N_cr_H)
            alpha_H = 0.34
            phi_H = 0.5 * (1 + alpha_H * (lam_H - 0.2) + lam_H ** 2)
            X_H = 1 / (phi_H + math.sqrt((phi_H ** 2) - (lam_H ** 2)))
            # Interaksjonsfaktorer for torsjonsstive staver
            # Tabell B.1, EC3
            # Setter forenklet C_my = C_mz = 0.6 ?????? OK ????????????
            k_yy = 0.6 * (1 + 0.6 * lam_H * (N_ed * gamma / (4 * X_H * N_Rk_g)))
            k_yz = k_yy
            # EC3, kapittel 6.3.3, interaksjonsformel om y-aksen (6.61)
            ur = ((N_ed * gamma) / (4 * gamma * N_Rk_g)) + ((k_yy * M_y_ed * gamma) / M_y_Rk) + ((k_yz * M_z_ed * gamma) / M_z_Rk)

            # Utnyttelsesrater
            knekk = max(knekk_d, knekk_g, ur)

            if knekk > u:
                u = knekk

        elif mast.navn == "B":
            # SJEKK RELEVANT KAPASITET FOR B-mast
            pass
        elif mast.navn == "bjelke":
            # SJEKK RELEVANT KAPASITET FOR bjelke-mast
            pass

        return u


    def beregn_vipping(self):
        pass












