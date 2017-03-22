import math

class Tilstand(object):
    """Objekt med informasjon om lasttilstand fra lastfaktoranalyse.
     Lagres i masteobjekt via metoden mast.lagre_lasttilfelle(lasttilfelle)
     """

    def __init__(self, mast, i, R, K, grensetilstand, vindretning,
                 g=0, l=0, f1=0, f2=0, f3=0, k=0):
        """Initierer tilstandsobjekt med data om krefter og forskyvninger
         samt lastfaktorer ved gitt lasttilfelle.
         K[:][0:6] = reaksjonskrefter ved fundament
         K[:][6:] = torsjonsvinkel/forskyvning av kontakttråd
         """
        self.K = K
        self.navn = grensetilstand["Navn"]
        # Vindretning #1 = fra mast mot spor
        # Vindretning #2 = fra spor mot mast
        # Vindretning #3 = parallelt spor
        self.vindretning = vindretning
        if self.navn == "bruddgrense":
            self.faktorer = [g, l, f1, f2, f3, k]
            self.N_kap = abs(K[4] * mast.materialkoeff / (mast.fy * mast.A))
            # Ganger med 1000 for å få momenter i [Nmm]
            self.My_kap = abs(1000 * K[0] * mast.materialkoeff / (mast.fy * mast.Wy_el))
            self.Mz_kap = abs(1000 * K[2] * mast.materialkoeff / (mast.fy * mast.Wz_el))
            self.utnyttelsesgrad = self._beregn_utnyttelsesgrad(mast, i, K, R)
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

    def _trykkapasitet(self, mast, I, L, N_Ed, N_Rk, alpha):
        """Beregner aksialkraftkapasitet etter EC3, 6.3.1.2"""

        # Konstanter
        E = mast.E                  # [N / mm^2] E-modulen til stål
        gamma = mast.materialkoeff  # [1] Partialfaktor for stål

        # Eulerlasten - kritisk aksialkraftkapasitet [N]
        N_cr = (math.pi ** 2 * E * I) / (L ** 2)
        lam_knekk = math.sqrt(N_Rk / N_cr)
        phi = 0.5 * (1 + alpha * (lam_knekk - 0.2) + lam_knekk ** 2)
        # Reduksjonsfaktoren X e [0, 1.0] && X <= 1.0
        X = 1 / (phi + math.sqrt(phi ** 2 - lam_knekk ** 2))
        if X > 1.0:
            X = 1.0

        # Utnyttelsesgrad av aksialkraftkapasitet
        UR_aksial = (gamma * N_Ed) / (X * N_Rk)

        return UR_aksial, X, lam_knekk

    def _beregn_vipping(self, mast, L_e, C_w, I_T, I_z, A, B, M_y_Rk, alpha_LT, W_y_pl):
        """Beregner kritisk moment for vipping av bjelkesøyler."""

        # Konstanter
        E = mast.E  # [N / mm^2]
        G = mast.G  # [N / mm^2]
        fy = mast.fy
        my_vind = 2.05
        my_punkt = 1.28

        # Hvelvningens bidrag til torsjonsstivheten
        gaffel_v = math.sqrt(1 + ((math.pi / L_e) ** 2 * ((E * C_w) / (G * I_T))))

        C = (L_e / math.pi) * math.sqrt((G * I_T) / (E * I_z)) * gaffel_v

        # Antar at lasten angriper i skjærsenteret, z_a == 0.
        M_cr_vind = my_vind * E * I_z * C * (math.pi / L_e) ** 2
        M_cr_punkt = my_punkt * E * I_z * C * (math.pi / L_e) ** 2

        # Kritisk moment
        M_cr = A * M_cr_vind + B * M_cr_punkt

        # EC3, 6.3.2.3: Reduksjonsfaktor for vipping
        lam_LT = math.sqrt(M_y_Rk / M_cr)
        beta = 0.75
        lam_0 = 0.40
        phi_LT = 0.5 * (1 + alpha_LT * (lam_LT - lam_0 ** 2) + beta * lam_LT ** 2)
        X_LT = 1 / (phi_LT + math.sqrt(phi_LT ** 2 - beta * lam_LT ** 2))

        # Kapasitet
        M_y_Rd = X_LT * W_y_pl * fy

        return M_y_Rd

    def _utnyttelsesgrad(self, mast, vindretning, lam_y, UR_Ny, lam_z, UR_Nz, M_y_Ed, M_y_Rk, M_z_Ed, M_z_Rk):
        """Beregner interaksjonsfaktorer k_ij for staver."""

        # EC3, Tabell B.3: Ekvivalente momentfaktorer
        # Setter forenklet C_ij = 0.6 da trekantmomentlast antas.
        C_my, C_mz, C_mLT = 0.6, 0.6, 0.6
        gamma = mast.materialkoeff

        # EC3, Tabell B.1 og B.2: Interaksjonsfaktorer
        k_yy = C_my * (1 + (lam_y - 0.2) * UR_Ny)
        k_yy_max = C_my * (1 + 0.8 * UR_Ny)
        if k_yy > k_yy_max:
            k_yy = k_yy_max

        # Dette betyr at B-masten antas torsjonsstiv (EC3, Tabell B.1)
        k_zy = 0.6 * k_yy

        # Bjelkemasten er torsjonsmyk (EC3, Tabell B.2)
        if mast.type == "bjelke":
            k_zy = 1 - (0.1 / (C_mLT - 0.25)) * UR_Nz
            k_zy_max = 1 - ((0.1 * lam_z) / (C_mLT - 0.25)) * UR_Nz
            if lam_z < 0.4:
                k_zy = 0.6 + lam_z
                k_zy_max = 1 - ((0.1 * lam_z) / (C_mLT - 0.25)) * UR_Nz
            if k_zy > k_zy_max:
                k_zy = k_zy_max

        k_zz = C_mz * (1 + (2 * lam_z - 0.6) * UR_Nz)
        k_zz_max = C_mz * (1 + 1.4 * UR_Nz)
        if k_zz > k_zz_max:
            k_zz = k_zz_max

        k_yz = 0.6 * k_zz

        # EC3, 6.3.3, kapasitet om y-aksen, lign (6.61):
        UR = UR_Ny + k_yy * ((M_y_Ed * gamma) / M_y_Rk) + k_yz * ((M_z_Ed * gamma) / M_z_Rk)

        if vindretning == 3:
            # Vinden blåser parallelt sporet
            # EC3, 6.3.3, kapasitet om z-aksen, lign (6.62):
            UR = UR_Nz + k_zy * ((M_y_Ed * gamma) / M_y_Rk) + k_zz * ((M_z_Ed * gamma) / M_z_Rk)

        return UR

    def _beregn_utnyttelsesgrad(self, mast, i, K, R):
        """Beregner dimensjonerende utnyttelsesgrad u i bruddgrensetilstand"""

        # Standard kapasitetssjekk ihht. EC3 og EN 50119
        u = self.N_kap + self.My_kap + self.Mz_kap

        # Last på mast
        M_y_Ed = K[0]
        M_z_Ed = K[2]
        N_Ed = K[4]

        if mast.type == "H":
            """LOKAL knekkapasitet for H-mast"""
            # Utføres for gurt og diagonal helt nede ved mastefot.

            # DIAGONALSTAV
            # Trykkraft [N] i mest påkjente diagonal er den største av:
            N_Ed_d = max(math.sqrt(2) / 2 * K[1], math.sqrt(2) / 2 * K[3])
            N_Rk_d = mast.d_A * mast.fy  # [N] Aksialkraftkap diagonal
            L_d = 0.55 * 683             # [mm] Lengde diagonal
            I_d = mast.I_d               # [mm^4] diagonal
            alpha_d = 0.49               # [1] Imperfeksjonsfaktor

            UR_d, X, lam_knekk = self._trykkapasitet(mast, I_d, L_d, N_Ed_d, N_Rk_d, alpha_d)

            # GURT (Vinkelprofil)
            # Trykkraft i GURT (vinkelprofil) [N]:
            b = mast.bredde(mast.h - 1)
            N_Ed_g = 0.5 * ((K[0] / b) + (K[2] / b) + K[1] + K[3]) + K[4] / 4
            N_Rk_g = mast.A_profil * mast.fy    # [N]Aksialkraftkapasitet
            L_g = 0.85 * mast.h * 1000          # [mm] Mastehøyde
            I_g = mast.Iy_profil                # [mm^4] 2. arealmoment
            alpha_g = 0.34                      # [1] Imperfeksjonsfaktor

            UR_g, X, lam_knekk = self._trykkapasitet(mast, I_g, L_g, N_Ed_g, N_Rk_g, alpha_g)

            """GLOBAL mastekontroll for H-mast"""
            gamma = mast.materialkoeff
            # Kapasiteter
            # Masten er konisk. Bredden b = 0.9 i mastefot benyttes.
            b_g = 0.9 * mast.bredde(mast.h)  # [mm]
            M_y_Rk = b_g * N_Rk_g * 2        # [Nmm] sterk akse
            M_z_Rk = M_y_Rk                  # [Nmm] svak akse

            # Aksialkraftkapasitet
            N_Rk_mast = 4 * mast.A_profil * mast.fy
            L_cr_mast = 0.85 * mast.h
            I_y = 4 * (mast.Iy_profil + mast.A_profil * (b_g / 2) ** 2)
            alpha_mast = 0.34

            UR_Ny, X, lam_knekk_y = self._trykkapasitet(mast, I_y, L_cr_mast, N_Ed, N_Rk_mast, alpha_mast)

            # Interaksjonsfaktorer for torsjonsstive staver
            # EC3, Tabell B.1
            k_yy = 0.6 * (1 + 0.6 * lam_knekk_y * UR_Ny)
            # Pga. symmetri må k_yy == k_zz.
            k_yz = 0.6 * k_yy

            # EC3, kapittel 6.3.3, interaksjonsformel om y-aksen (6.61)
            UR_mast = UR_Ny + ((k_yy * M_y_Ed * gamma) / M_y_Rk) + ((k_yz * M_z_Ed * gamma) / M_z_Rk)

            # Utnyttelsesgrader
            knekk = max(UR_d, UR_g, UR_mast)

            if knekk > u:
                u = knekk

            return u

        elif mast.type == "B":
            """GLOBAL mastekontroll for B-mast"""
            # Inngangsparametre
            I_z = mast.Iz_profil        # [mm^4] svak akse, profil
            I_y = mast.Iy_profil        # [mm^4] sterk akse, profil
            W_y_pl = mast.Wyp           # [mm^3]
            A_B = mast.A_profil         # [mm^2] Profilets tv.sn. areal
            A_d = mast.d_h * mast.d_b   # [mm^2] diagonalens areal
            l_diagonal = 1000           # [mm] avst mellom festepkt.
            alpha_y = 0.49              # [1] knekkfaktor, y-akse
            alpha_z = 0.49              # [1] knekkfaktor, z-akse
            alpha_LT = 0.76             # [1] imperfeksjonsfaktor, vipp

            # 90% av mastebredden ved mastefot (pga. konisk form) [mm]
            b_g = 0.9 * mast.bredde(mast.h)

            # Hvelvningskonstanten for ett stk. kanalprofil [mm^6]
            C_w = 0.5 * I_y * b_g ** 2

            # 2. Arealmoment for B-masten om sterk akse [mm^4]
            I_y_B = I_y + A_B * (b_g / 2) ** 2

            # 2. Arealmoment for B-masten om svak akse [mm^4]
            I_z_B = 2 * I_z

            # Torsjonstreghetsmoment for ett stk. kanalprofil [mm^4]
            L_diagonal = 800  # [mm]
            if mast.navn == "B6":
                L_diagonal = 917  # [mm]
            t = (mast.E / mast.G) * ((l_diagonal * b_g * A_d) / L_diagonal ** 3)
            I_T = 2 * mast.It + ((1 / 3) * b_g * t ** 3)

            # Kapasiteter, ganger med x2 for å ta med begge kanalprofilene
            M_y_Rk = 2 * A_B * b_g * mast.fy
            M_z_Rk = 2 * mast.Wyp * mast.fy   # ??????? W_yp ??????????
            N_Rk = 2 * A_B * mast.fy

            """(1) Vind fra mast mot spor eller (2) fra spor mot mast"""
            if vindretning == 1 or 2:
                # Ekvivalent lengde, Le1
                L_e1 = ((R[0][0] * (i.fh + i.sh / 2)) + (R[1][0] * i.fh) + (R[2][0] * (i.fh + i.sh))
                        + (R[3][0] * (i.fh + i.sh)) + (R[4][0] * (i.fh + i.sh / 2)) + (R[5][0] * i.hf)
                        + (R[6][0] * i.hr) + (R[7][0] * i.fh) + (R[8][0] * i.hfj) + (R[9][0] * i.hfj)
                        + (R[10][0] * i.hj) + (R[11][0] * (i.fh + i.sh)) + (R[12][0] * (2 / 3) * mast.h)) / K[0]

                # Andel av vippemoment fra jevnt fordelt last.
                A1 = abs(R[12][0] / K[0])
                B1 = 1 - A1

                # Redusert momentkapasitet om y-aksen pga vipping.
                # W_y_pl her gjelder bare for én kanalprofil
                M_y_Rk = self._beregn_vipping(mast, L_e1, C_w, I_T, I_z, A1, B1, M_y_Rk, alpha_LT, W_y_pl)

                # Mastens knekklengde
                L_cr = 2 * L_e1
                if i.avspenningsmast or i.fixavspenningsmast:
                    L_cr = L_e1

                # Aksialkraftkapasitet om sterk akse (y-aksen)
                UR_Ny, X_y, lam_y = self._trykkapasitet(mast, I_y_B, L_cr, N_Ed, N_Rk, alpha_y)

                # Aksialkraftkapasitet om svak akse (z-aksen)
                UR_Nz, X_z, lam_z = self._trykkapasitet(mast, I_z_B, L_cr, N_Ed, N_Rk, alpha_z)

                # EC3, kap. 6.3.3, interaksjonsformel om y-aksen (6.61)
                UR_y_B = self._utnyttelsesgrad(mast, vindretning, lam_y, UR_Ny, lam_z, UR_Nz, M_y_Ed, M_y_Rk,
                                               M_z_Ed, M_z_Rk)
                if UR_y_B > u:
                    u = UR_y_B

                return u

            """(3) Vind parallelt spor"""
            elif vindretning == 3:
            # Ekvivalent lengde, Le3
            L_e3 = ((R[0][2] * (i.fh + i.sh / 2)) + (R[1][2] * i.fh) + (R[2][2] * (i.fh + i.sh))
                    + (R[3][2] * (i.fh + i.sh)) + (R[4][2] * (i.fh + i.sh / 2)) + (R[5][2] * i.hf) + (R[6][2] * i.hr)
                    + (R[7][2] * i.fh) + (R[8][2] * i.hfj) + (R[9][2] * i.hfj) + (R[10][2] * i.hj)
                    + (R[11][2] * (i.fh + i.sh)) + (R[14][2] * (2 / 3) * mast.h)) / K[2]

            # Andel av vippemoment fra jevnt fordelt last.
            A3 = abs(R[14][2] / K[2])
            B3 = 1 - A3

            # Redusert momentkapasitet om y-aksen pga. vipping.
            # Må det brukes "inverse" tv.sn. egenskaper ???????????????
            # W_y_pl gjelder for bare én kanalprofil
            M_y_Rk = self._beregn_vipping(mast, L_e3, C_w, I_T, I_z_B, A3, B3, M_y_Rk, alpha_LT, W_y_pl)

            # Knekklengde
            L_cr = 2 * L_e3
            if i.avspenningsmast or i.fixavspenningsmast:
                L_cr = L_e3

            # Aksialkraftkapasitet om sterk akse (y-aksen)
            UR_Ny, X_y, lam_y = self._trykkapasitet(mast, I_y_B, L_cr, N_Ed, N_Rk, alpha_y)

            # Aksialkraftkapasitet om svak akse (z-aksen)
            UR_Nz, X_z, lam_z = self._trykkapasitet(mast, I_z_B, L_cr, N_Ed, N_Rk, alpha_z)

            # EC3, kap. 6.3.3, interaksjonsformel om z-aksen (6.62)
            UR_z_B = self._utnyttelsesgrad(mast, vindretning, lam_y, UR_Ny, lam_z, UR_Nz, M_y_Ed, M_y_Rk,
                                                    M_z_Ed, M_z_Rk)

            if UR_z_B > u:
                u = UR_z_B

        elif mast.type == "bjelke":
            """GLOBAL mastekontroll av bjelkemast"""
            # Det beregnes utnyttelsesgrad (UR) for tre tilfeller:
            # (1) Vind fra mast mot spor,
            # (2) vind fra spor mot mast og
            # (3) vindparallelt spor

            # Inngangsparametre
            C_w = mast.Cw         # [mm^6]
            I_T = mast.It         # [mm^4]
            I_z = mast.Iz_profil  # [mm^4]
            I_y = mast.Iy_profil  # [mm^4]
            W_y_pl = mast.Wyp     # [mm^3]
            alpha_LT = 0.34       # [1] imperfeksjonsfaktor, vipp
            alpha_y = 0.34        # [1] imperfeksjonsfaktor, knekk(y)
            alpha_z = 0.49        # [1] imperfeksjonsfaktor, knekk(z)

            # Kapasiteter
            M_y_Rk = mast.Wyp * mast.fy      # [Nmm] sterk akse
            M_z_Rk = mast.Wzp * mast.fy      # [Nmm] svak akse
            N_Rk = mast.A_profil * mast.fy   # [N] trykkapasitet

            """(1) Vind fra mast mot spor eller (2) fra spor mot mast"""
            if vindretning == 1 or 2:
                # Ekvivalent lengde, Le1
                L_e1 = ((R[0][0] * (i.fh + i.sh / 2)) + (R[1][0] * i.fh) + (R[2][0] * (i.fh + i.sh))
                        + (R[3][0] * (i.fh + i.sh)) + (R[4][0] * (i.fh + i.sh / 2)) + (R[5][0] * i.hf) + (R[6][0] * i.hr)
                        + (R[7][0] * i.fh) + (R[8][0] * i.hfj) + (R[9][0] * i.hfj) + (R[10][0] * i.hj)
                        + (R[11][0] * (i.fh + i.sh)) + (R[12][0] * (2 / 3) * mast.h)) / K[0]

                # Andel av vippemoment fra jevnt fordelt last.
                A1 = abs(R[12][0] / K[0])
                B1 = 1 - A1

                # Redusert momentkapasitet om y-aksen pga vipping.
                M_y_Rk = self._beregn_vipping(mast, L_e1, C_w, I_T, I_z, A1, B1, M_y_Rk, alpha_LT, W_y_pl)

                # Mastens knekklengde
                L_cr = 2 * L_e1
                if i.avspenningsmast or i.fixavspenningsmast:
                    L_cr = L_e1

                # Aksialkraftkapasitet om sterk akse (y-aksen)
                UR_Ny, X_y, lam_y = self._trykkapasitet(mast, I_y, L_cr, N_Ed, N_Rk, alpha_y)

                # Aksialkraftkapasitet om svak akse (z-aksen)
                UR_Nz, X_z, lam_z = self._trykkapasitet(mast, I_z, L_cr, N_Ed, N_Rk, alpha_z)

                # EC3, kap. 6.3.3, interaksjonsformel om y-aksen (6.61)
                UR_y_bjelkemast = self._utnyttelsesgrad(mast, vindretning, lam_y, UR_Ny, lam_z, UR_Nz, M_y_Ed, M_y_Rk,
                                                    M_z_Ed, M_z_Rk)
                if UR_y_bjelkemast > u:
                    u = UR_y_bjelkemast

                return u

            """(3) Vind parallelt spor"""
            elif vindretning == 3:
                # Ekvivalent lengde, Le3
                L_e3 = ((R[0][2] * (i.fh + i.sh / 2)) + (R[1][2] * i.fh) + (R[2][2] * (i.fh + i.sh))
                        + (R[3][2] * (i.fh + i.sh)) + (R[4][2] * (i.fh + i.sh / 2)) + (R[5][2] * i.hf) + (R[6][2] * i.hr)
                        + (R[7][2] * i.fh) + (R[8][2] * i.hfj) + (R[9][2] * i.hfj) + (R[10][2] * i.hj)
                        + (R[11][2] * (i.fh + i.sh)) + (R[14][2] * (2 / 3) * mast.h)) / K[2]

                # Andel av vippemoment fra jevnt fordelt last.
                A3 = abs(R[14][2] / K[2])
                B3 = 1 - A3

                # Redusert momentkapasitet om y-aksen pga. vipping.
                # Må det brukes "inverse" tv.sn. egenskaper ???????????????
                M_y_Rk = self._beregn_vipping(mast, L_e3, C_w, I_T, I_z, A3, B3, M_y_Rk, alpha_LT, W_y_pl)

                # Aksialkraftkapasitet om sterk akse (y-aksen)
                L_cr = 2 * L_e3
                if i.avspenningsmast or i.fixavspenningsmast:
                    L_cr = L_e3

                UR_Ny, X_y, lam_y = self._trykkapasitet(mast, I_y, L_cr, N_Ed, N_Rk, alpha_y)

                # Aksialkraftkapasitet om svak akse (z-aksen)
                UR_Nz, X_z, lam_z = self._trykkapasitet(mast, I_z, L_cr, N_Ed, N_Rk, alpha_z)

                # EC3, kap. 6.3.3, interaksjonsformel om z-aksen (6.62)
                UR_z_bjelkemast = self._utnyttelsesgrad(mast, vindretning, lam_y, UR_Ny, lam_z, UR_Nz, M_y_Ed, M_y_Rk,
                                                        M_z_Ed, M_z_Rk)

                if UR_z_bjelkemast > u:
                    u = UR_z_bjelkemast

            return u
