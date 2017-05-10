import math
import numpy
import copy

class Tilstand(object):
    """Objekt med informasjon om lasttilstand fra lastfaktoranalyse.
     Lagres i masteobjekt via metoden mast.lagre_lasttilfelle(lasttilfelle)
     """

    def __init__(self, mast, i, lastsituasjon, vindretning, F=None, R=None, D=None,
                 G=0, L=0, T=0, S=0, V=0):
        """Initierer tilstandsobjekt med data om krefter og forskyvninger
         samt lastfaktorer ved gitt lasttilfelle.
         """
        self.metode = "EC3" if i.ec3 else "NEK"
        self.lastsituasjon = lastsituasjon
        self.vindretning = vindretning
        # 0: Vind fra mast mot spor
        # 1: Vind fra spor mot mast
        # 2: Vind parallelt spor

        if R is not None:
            self.type = 0  # Bruddgrensetilstand
            self.F = copy.copy(F)
            self.R = R
            self.K = numpy.sum(numpy.sum(R, axis=0), axis=0)
            self.G = G
            self.L = L
            self.T = T
            self.S = S
            self.V = V
            self.faktorer = {"G": G, "L": L, "T": T, "S": S, "V": V}
            self.N_kap = abs(self.K[4] * mast.materialkoeff / (mast.fy * mast.A))
            self.My_kap = abs(1000 * self.K[0] * mast.materialkoeff / (mast.fy * mast.Wy_el))
            self.Mz_kap = abs(1000 * self.K[2] * mast.materialkoeff / (mast.fy * mast.Wz_el))
            self.utnyttelsesgrad = self._beregn_utnyttelsesgrad(mast, i, self.K)
        else:
            self.type = 1  # Bruksgrensetilstand
            self.D = D
            self.K = numpy.sum(numpy.sum(D, axis=0), axis=0)


    def __repr__(self):
        return self.rep()

    def rep(self):
        if self.type == 0:
            K = self.K/1000  # Konverterer krefter til [kNm] og [kN]
            rep = ""
            #for j in self.F:
            #    rep += j.rep()
            rep += "\nBeregningsmetode: {}\n".format(self.metode)
            rep += "My = {:.3g} kNm    Vy = {:.3g} kN    Mz = {:.3g} kNm    " \
                  "Vz = {:.3g} kN    N = {:.3g} kN    T = {:.3g} kNm\n".\
                format(K[0], K[1], K[2], K[3], K[4], K[5])
            rep += "Lastsituasjon: {}\n".format(self.lastsituasjon)
            for key in self.faktorer:
                rep += "{} = {}     ".format(key, self.faktorer[key])
            rep += "\nVindretning = {}\n".format(self.vindretning)
            rep += "My_kap: {:.3g}%    Mz_kap: {:.3g}%    " \
                   "N_kap: {:.3g}%\n".format(self.My_kap*100, self.Mz_kap*100,self.N_kap*100)
            rep += "Sum kapasiteter: {}%\n".format(self.My_kap*100 + self.Mz_kap*100 + self.N_kap*100)
            rep += "Utnyttelsesgrad: {}%".format(self.utnyttelsesgrad * 100)
        else:
            rep = ""
            rep += "Dy = {:.3f} mm    Dz = {:.3f} mm    phi = {:.3f}\n".\
                format(self.K[0], self.K[1], self.K[2])
            rep += "Lastsituasjon: {}\n".format(self.lastsituasjon)
            rep += "Vindretning = {}\n".format(self.vindretning)



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

    def _beregn_vipping(self, mast, L_e, A, B, M_y_Rk, W_y_pl):
        """Beregner kritisk moment for vipping av bjelkesøyler."""

        # Konstanter
        E = mast.E  # [N / mm^2]
        G = mast.G  # [N / mm^2]
        C_w = mast.Cw
        I_T = mast.It
        I_z = mast.Iz(mast.h)
        fy = mast.fy
        my_vind = 2.05
        my_punkt = 1.28
        alpha_LT = 0.76
        if mast.type == "bjelke":
            alpha_LT = 0.34

        # Hvelvningens bidrag til torsjonsstivheten
        gaffel_v = math.sqrt(1 + ((math.pi / L_e) ** 2 * ((E * C_w) / (G * I_T))))

        C = (L_e / math.pi) * math.sqrt((G * I_T) / (E * I_z)) * gaffel_v

        # Antar at lasten angriper i skjærsenteret, z_a == 0.
        M_cr_vind = my_vind * E * I_z * C * (math.pi / L_e) ** 2
        M_cr_punkt = my_punkt * E * I_z * C * (math.pi / L_e) ** 2

        # Kritisk moment
        M_cr = A * M_cr_vind + B * M_cr_punkt  # [Nmm]

        # EC3, 6.3.2.3: Reduksjonsfaktor for vipping
        lam_LT = math.sqrt(abs(M_y_Rk / M_cr))
        phi_LT = 0.5 * (1 + alpha_LT * (lam_LT - 0.2) + lam_LT ** 2)
        X_LT = 1 / (phi_LT + math.sqrt(phi_LT ** 2 - lam_LT ** 2))
        if mast.type == "bjelke":
            beta = 0.75
            lam_0 = 0.40
            phi_LT = 0.5 * (1 + alpha_LT * (lam_LT - lam_0 ** 2) + beta * lam_LT ** 2)
            X_LT = 1 / (phi_LT + math.sqrt(phi_LT ** 2 - beta * lam_LT ** 2))

        # Kapasitet
        M_y_Rd = X_LT * W_y_pl * fy

        return M_y_Rd

    def _utnyttelsesgrad(self, mast, lam_y, UR_Ny, lam_z, UR_Nz, M_y_Ed, M_y_Rk, M_z_Ed, M_z_Rk):
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
        if self.vindretning == 0 or self.vindretning == 1:
            UR = UR_Ny + k_yy * ((M_y_Ed * gamma) / M_y_Rk) + k_yz * ((M_z_Ed * gamma) / M_z_Rk)
        else:
            # Vinden blåser parallelt sporet (Alternativ 3)
            # EC3, 6.3.3, kapasitet om z-aksen, lign (6.62):
            UR = UR_Nz + k_zy * ((M_y_Ed * gamma) / M_y_Rk) + k_zz * ((M_z_Ed * gamma) / M_z_Rk)

        return UR

    def _beregn_momentfordeling(self):
        """Beregner ekvivalent mastelengde L_e,
         samt momentandelene A og B
         """

        M_punkt, M_fordelt, M_sum = 0, 0, 0

        # (0) Vind fra mast mot spor eller (1) fra spor mot mast
        if self.vindretning == 0 or 1:
            for j in self.F:
                f = j.f
                if not numpy.count_nonzero(j.q) == 0:
                    if self.vindretning == 0:
                        f = numpy.array([0, 0, j.q[2] * j.b])
                    elif self.vindretning == 1:
                        f = numpy.array([0, 0, j.q[2] * j.b])
                    M_fordelt += abs(f[2] *j.e[0] ** 2)
                else:
                    M_punkt += abs(f[2] * j.e[0] ** 2)
                M_sum += abs(f[2] * j.e[0])

        # (2) Vind parallelt spor
        elif self.vindretning == 2:
            # Beregner ekvivalent mastelengde
            for j in self.F:
                f = j.f
                if not numpy.count_nonzero(j.q) == 0:
                    f = numpy.array([0, j.q[1] * j.b, 0])
                    M_fordelt += abs(f[1] * j.e[0] ** 2)
                else:
                    M_punkt += abs(f[1] * j.e[0] ** 2)
                M_sum += abs(f[1] * j.e[0])

        L_e = 1000 * (M_punkt + M_fordelt) / M_sum  # [mm]
        # A = andel av vippemoment fra jevnt fordelt last.
        A = abs(M_fordelt / M_sum)
        B = 1 - A

        return L_e, A, B

    def _beregn_utnyttelsesgrad(self, mast, i, K):
        """Beregner dimensjonerende utnyttelsesgrad u i bruddgrensetilstand"""

        # Standard kapasitetssjekk ihht. EC3 og EN 50119
        u = self.N_kap + self.My_kap + self.Mz_kap

        # Last på mast
        M_y_Ed = abs(K[0]) * 1000  # [Nmm]
        M_z_Ed = abs(K[2]) * 1000  # [Nmm]
        V_y_Ed = abs(K[1])  # [N]
        V_z_Ed = abs(K[3])  # [N]
        N_Ed = abs(K[4])  # [N]

        if mast.type == "H":
            """LOKAL knekkapasitet for H-mast"""
            # Utføres for gurt og diagonal helt nede ved mastefot.

            # DIAGONALSTAV
            # Trykkraft [N] i mest påkjente diagonal er den største av:
            N_Ed_d = max(math.sqrt(2) / 2 * V_y_Ed, math.sqrt(2) / 2 * V_z_Ed)
            N_Rk_d = mast.d_A * mast.fy  # [N] Aksialkraftkap diagonal
            L_d = mast.k_d * mast.d_L    # [mm] Lengde diagonal
            d_I = mast.d_I               # [mm^4] diagonal
            alpha_d = 0.49               # [1] Imperfeksjonsfaktor

            UR_d, X, lam_knekk = self._trykkapasitet(mast, d_I, L_d, N_Ed_d, N_Rk_d, alpha_d)

            # GURT (Vinkelprofil)
            # Trykkraft i GURT (vinkelprofil) [N]:
            b = mast.bredde(mast.h - 1)
            N_Ed_g = 0.5 * ((M_y_Ed / b) + (M_z_Ed / b) + V_y_Ed + V_z_Ed) + N_Ed / 4
            N_Rk_g = mast.A_profil * mast.fy    # [N] Aksialkraftkapasitet
            L_g = mast.k_g * 1000               # [mm] Knekklengde gurt
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
            I_y = mast.Iy(mast.h)
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
            W_y_pl = 2 * mast.A_profil *\
                     0.9 * mast.bredde(mast.h)           # [mm^3]
            alpha_y = 0.49              # [1] knekkfaktor, y-akse
            alpha_z = 0.49              # [1] knekkfaktor, z-akse

            # 90% av mastebredden ved mastefot (pga. konisk form) [mm]
            b_g = 0.9 * mast.bredde(mast.h)

            # 2. Arealmoment for B-masten om sterk akse [mm^4]
            I_y_B = mast.Iy(mast.h, 0.9)

            # 2. Arealmoment for B-masten om svak akse [mm^4]
            I_z_B = mast.Iz(mast.h)

            # Kapasiteter, ganger med x2 for å ta med begge kanalprofilene
            M_y_Rk = 2 * mast.A_profil * b_g * mast.fy
            M_z_Rk = 2 * mast.Wyp * mast.fy
            N_Rk = 2 * mast.A_profil * mast.fy

            L_e, A, B = self._beregn_momentfordeling()

            # Redusert momentkapasitet om y-aksen pga vipping.
            # W_y_pl gjelder for bare én kanalprofil
            M_y_Rk = self._beregn_vipping(mast, L_e, A, B, M_y_Rk, W_y_pl)

            # Knekklengde
            L_cr = 2 * L_e
            if i.avspenningsmast or i.fixavspenningsmast:
                L_cr = L_e

            # Aksialkraftkapasitet om sterk akse (y-aksen)
            UR_Ny, X_y, lam_y = self._trykkapasitet(mast, I_y_B, L_cr, N_Ed, N_Rk, alpha_y)

            # Aksialkraftkapasitet om svak akse (z-aksen)
            UR_Nz, X_z, lam_z = self._trykkapasitet(mast, I_z_B, L_cr, N_Ed, N_Rk, alpha_z)

            # (0) Vind fra mast mot spor eller (1) fra spor mot mast
            if self.vindretning == 0 or 1:

                # EC3, kap. 6.3.3, interaksjonsformel om y-aksen (6.61)
                UR_y_B = self._utnyttelsesgrad(mast, lam_y, UR_Ny, lam_z, UR_Nz, M_y_Ed, M_y_Rk,
                                               M_z_Ed, M_z_Rk)
                if UR_y_B > u:
                    u = UR_y_B

                return u

            # (2) Vind parallelt spor
            elif self.vindretning == 2:
                # Ulogisk å beregne vipping når belastningen er om svak akse???????????????

                # EC3, kap. 6.3.3, interaksjonsformel om z-aksen (6.62)
                UR_z_B = self._utnyttelsesgrad(mast, lam_y, UR_Ny, lam_z, UR_Nz, M_y_Ed, M_y_Rk, M_z_Ed, M_z_Rk)

                if UR_z_B > u:
                    u = UR_z_B

        elif mast.type == "bjelke":
            """GLOBAL mastekontroll av bjelkemast"""

            # Inngangsparametre
            I_z = mast.Iz_profil   # [mm^4]
            I_y = mast.Iy_profil   # [mm^4]
            W_y_pl = mast.Wyp      # [mm^3]
            alpha_y = 0.34         # [1] imperfeksjonsfaktor, knekk(y)
            alpha_z = 0.49         # [1] imperfeksjonsfaktor, knekk(z)

            # Kapasiteter
            M_y_Rk = mast.Wyp * mast.fy      # [Nmm] sterk akse
            M_z_Rk = mast.Wzp * mast.fy      # [Nmm] svak akse
            N_Rk = mast.A_profil * mast.fy   # [N] trykkapasitet

            L_e, A, B = self._beregn_momentfordeling()

            # Redusert momentkapasitet om y-aksen pga vipping.
            M_y_Rk = self._beregn_vipping(mast, L_e, A, B, M_y_Rk, W_y_pl)

            # Mastens knekklengde
            L_cr = 2 * L_e
            if i.avspenningsmast or i.fixavspenningsmast:
                L_cr = L_e

            UR_Ny, X_y, lam_y = self._trykkapasitet(mast, I_y, L_cr, N_Ed, N_Rk, alpha_y)

            # Aksialkraftkapasitet om svak akse (z-aksen)
            UR_Nz, X_z, lam_z = self._trykkapasitet(mast, I_z, L_cr, N_Ed, N_Rk, alpha_z)

            # (0) Vind fra mast mot spor eller (1) fra spor mot mast
            if self.vindretning == 0 or 1:

                # EC3, kap. 6.3.3, interaksjonsformel om y-aksen (6.61)
                UR_y_bjelkemast = self._utnyttelsesgrad(mast, lam_y, UR_Ny, lam_z, UR_Nz, M_y_Ed, M_y_Rk,
                                                    M_z_Ed, M_z_Rk)
                if UR_y_bjelkemast > u:
                    u = UR_y_bjelkemast

                return u

            # (2) Vind parallelt spor
            elif self.vindretning == 2:
                # Ulogisk å beregne vipping når belastningen er om svak akse???????????????

                # EC3, kap. 6.3.3, interaksjonsformel om z-aksen (6.62)
                UR_z_bjelkemast = self._utnyttelsesgrad(mast, lam_y, UR_Ny, lam_z, UR_Nz, M_y_Ed, M_y_Rk,
                                                        M_z_Ed, M_z_Rk)

                if UR_z_bjelkemast > u:
                    u = UR_z_bjelkemast

        return u
