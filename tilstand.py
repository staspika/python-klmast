import math
import numpy
import copy


class Tilstand(object):
    """Objekt med informasjon om lasttilstand fra lastfaktoranalyse.
     Lagres i masteobjekt via metoden mast.lagre_lasttilfelle(lasttilfelle)
     """

    def __init__(self, mast, i, lastsituasjon, vindretning, type, F=None, R=None, D=None,
                 G=0, L=0, T=0, S=0, V=0, iterasjon=0):
        """Initierer tilstandsobjekt.

        :param Mast mast: Aktuell mast
        :param Inndata i: Input fra bruker
        :param dict lastsituasjon: Aktuell lastsituasjon
        :param int vindretning: Aktuell vindretning
        :param tuple type: (Rad, etasje) for plassering i R- og D-matrise
        :param list F: Liste med :class:`Kraft`-objekter påført systemet
        :param numpy.array R: Reaksjonskraftmatrise
        :param numpy.array D: Forskyvningsmatrise
        :param float G: Lastfaktor egenvekt
        :param float L: Lastfaktor kabelstrekk
        :param float T: Lastfaktor temperatur
        :param float S: Lastfaktor snø/is
        :param float V: Lastfaktor vind
        :param iterasjon: Iterasjon for utregning av aktuell :class:`Tilstand`
        """
        self.metode = "EC3" if i.ec3 else "NEK"
        self.lastsituasjon = lastsituasjon
        self.vindretning = vindretning
        # 0: Vind fra mast mot spor
        # 1: Vind fra spor mot mast
        # 2: Vind parallelt spor
        self.type = type
        # 0: Bruddgrense
        # 1: Bruksgrense, forskyvning totalt
        # 2: Bruksgrense, forskyvning KL
        self.iterasjon = iterasjon

        if self.type == 0:
            # Bruddgrensetilstand
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
            self.utnyttelsesgrad = self._utnyttelsesgrad(i, mast, self.K)
            if "Ulykkeslast" in lastsituasjon:
                self.lastsituasjon = "Ulykkeslast"
        else:
            # Bruksgrensetilstand
            self.R = R
            self.D = D
            self.K = numpy.sum(numpy.sum(R, axis=0), axis=0)
            self.K_D = numpy.sum(numpy.sum(D, axis=0), axis=0)

    def __repr__(self):
        K = self.K / 1000  # Konverterer M til [kNm] og F til [kN]
        if self.type == 0:
            rep = ""
            # for j in self.F:
            #    rep += j.rep()
            rep += "Beregningsmetode: {}\n".format(self.metode)
            rep += "My = {:.3g} kNm    Vy = {:.3g} kN    Mz = {:.3g} kNm    " \
                   "Vz = {:.3g} kN    N = {:.3g} kN    T = {:.3g} kNm\n". \
                format(K[0], K[1], K[2], K[3], K[4], K[5])
            rep += "Lastsituasjon: {}\n".format(self.lastsituasjon)
            rep += "Iterasjon = {}\n".format(self.iterasjon)
            if self.lastsituasjon is not "Ulykkeslast":
                for key in self.faktorer:
                    rep += "{} = {}     ".format(key, self.faktorer[key])
                rep += "\n"
            rep += "Vindretning = {}\n".format(self.vindretning)
            rep += "My_kap: {:.3g}%    Mz_kap: {:.3g}%    " \
                   "N_kap: {:.3g}%\n".format(self.My_kap * 100, self.Mz_kap * 100, self.N_kap * 100)
            rep += "Sum kapasiteter: {}%\n".format(self.My_kap * 100 + self.Mz_kap * 100 + self.N_kap * 100)
            rep += "Utnyttelsesgrad: {}%\n".format(self.utnyttelsesgrad * 100)
        else:
            rep = ""
            rep += "Dy = {:.3f} mm    Dz = {:.3f} mm    phi = {:.3f}\n". \
                format(self.K_D[0], self.K_D[1], self.K_D[2])
            rep += "My = {:.3g} kNm    Vy = {:.3g} kN    Mz = {:.3g} kNm    " \
                   "Vz = {:.3g} kN    N = {:.3g} kN    T = {:.3g} kNm\n". \
                format(K[0], K[1], K[2], K[3], K[4], K[5])
            rep += "Lastsituasjon: {}\n".format(self.lastsituasjon)
            rep += "Iterasjon = {}\n".format(self.iterasjon)
            rep += "Vindretning = {}\n".format(self.vindretning)

        return rep

    def _beregn_momentfordeling(self):
        """Beregner mastens momentfordeling.

        Beregner ekvivalent mastelengde L_e,
        samt andeler til kritisk moment. A gir
        vindlastens, mens B angir punktlastenes
        andel av bidrag til kritisk moment.

        :return: Ekvivalent mastelengde, momentandeler A og B
        :rtype: :class:`float`, :class:`float`, :class:`float`
        """

        M_punkt, M_fordelt, M_fordelt_0, M_sum = 0, 0, 0, 0

        # (0) Vind fra mast mot spor eller (1) fra spor mot mast
        if self.vindretning == 0 or 1:
            for j in self.F:
                f = j.f
                if not numpy.count_nonzero(j.q) == 0:
                    if self.vindretning == 0:
                        f = numpy.array([0, 0, j.q[2] * j.b])
                    elif self.vindretning == 1:
                        f = numpy.array([0, 0, j.q[2] * j.b])
                    M_fordelt_0 += abs(f[2] * j.e[0])
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
                    M_fordelt_0 += abs(f[2] * j.e[0])
                    M_fordelt += abs(f[1] * j.e[0] ** 2)
                else:
                    M_punkt += abs(f[1] * j.e[0] ** 2)
                M_sum += abs(f[1] * j.e[0])

        L_e = 1000 * (M_punkt + M_fordelt) / M_sum  # [mm]
        A = abs(M_fordelt_0 / M_sum)
        B = 1 - A

        return L_e, A, B

    def _reduksjonsfaktor_knekking(self, mast, L_cr, akse):
        """Beregner faktorer for aksialkraftkapasitet etter EC3, 6.3.1.2.

        ``akse`` kan oppgis for å regne om hhv. sterk og svak akse:
        **0** = y
        **1** = z

        :param Mast mast: Aktuell mast
        :param float L_cr: Effektiv mastelengde
        :param int akse:
        :return: Reduksjonsfaktor X for knekking, slankhet lam
        :rtype: :class:`float`, :class:`float`
        """

        if akse == 0:
            N_cr = (math.pi ** 2 * mast.E * mast.Iy(mast.h)) / (L_cr ** 2)
            lam = math.sqrt((mast.A * mast.fy) / N_cr)
            alpha = 0.34 if not mast.type == "B" else 0.49
            phi = 0.5 * (1 + alpha * (lam - 0.2) + lam ** 2)
            X = 1 / (phi + math.sqrt(phi ** 2 - lam ** 2))
        else:
            N_cr = (math.pi ** 2 * mast.E * mast.Iz(mast.h)) / (L_cr ** 2)
            lam = math.sqrt((mast.A * mast.fy) / N_cr)
            alpha = 0.49 if not mast.type == "H" else 0.34
            phi = 0.5 * (1 + alpha * (lam - 0.2) + lam ** 2)
            X = 1 / (phi + math.sqrt(phi ** 2 - lam ** 2))

        X = X if X <= 1.0 else 1.0

        return X, lam

    def _reduksjonsfaktor_vipping(self, mast, L_e, A, B, My_Ed):
        """Bestemmer reduksjonsfaktoren for vipping etter EC3, 6.3.2.2 og 6.3.2.3.

        :param Mast mast: Aktuell mast
        :param float L_e: Effektiv mastelengde
        :param float A: Momentandel fra vindlast
        :param float B: Momentandel fra punktlaster
        :return: Reduksjonsfaktor X_LT for vipping
        :rtype: :class:`float`
        """

        X_LT = 1.0
        if not mast.type == "H":
            # H-masten har ingen parameter It.
            my_vind, my_punkt = 2.05, 1.28
            gaffel_v = math.sqrt(1 + (mast.E * mast.Cw / (mast.G * mast.It)) * (math.pi / L_e) ** 2)

            # Antar at lasten angriper i skjærsenteret, z_a == 0.
            M_cr_vind = my_vind * (math.pi / L_e) * math.sqrt(mast.G * mast.It * mast.E * mast.Iz(mast.h)) * gaffel_v
            M_cr_punkt = my_punkt * (math.pi / L_e) * math.sqrt(mast.G * mast.It * mast.E * mast.Iz(mast.h)) * gaffel_v

            M_cr = A * M_cr_vind + B * M_cr_punkt

            lam_LT = math.sqrt(mast.My_Rk() / M_cr)
            lam_0, beta = 0.4, 0.75
            if lam_LT > lam_0 and (My_Ed / M_cr) > lam_0 ** 2:
                if mast.type == "B":
                    alpha_LT = 0.76
                    phi_LT = 0.5 * (1 + alpha_LT * (lam_LT - 0.2) + lam_LT ** 2)
                    X_LT = 1 / (phi_LT + math.sqrt(phi_LT**2 - lam_LT**2))
                    X_LT = X_LT if X_LT <= 1.0 else 1.0
                elif mast.type == "bjelke":
                    alpha_LT = 0.34
                    phi_LT = 0.5 * (1 + alpha_LT * (lam_LT - lam_0) + beta * lam_LT**2)
                    X_LT = 1 / (phi_LT + math.sqrt(phi_LT**2 - beta * lam_LT**2))
                    if X_LT > min(1.0, (1 / lam_0 ** 2)):
                        X_LT = min(1.0, (1 / lam_0 ** 2))

        return X_LT

    def _interaksjonsfaktorer(self, mast, lam_y, N_Ed, X_y, X_z, lam_z):
        """Beregner interaksjonsfaktorer etter EC3, Tabell B.2.

        Det antas at alle master tilhører tverrsnittsklasse #1.

        :param Mast mast: Aktuell mast
        :param float lam_y: Relativ slankhet for knekking om y-aksen
        :param float N_Ed: Dimensjonerende aksialkraft
        :param float X_y: Reduksjonsfaktor for knekking om y-aksen
        :param float X_z: Reduksjonsfaktor for knekking om z-aksen
        :param float lam_z: Relativ slankhet for knekking om y-aksen
        :return: Interaksjonsfaktorer k_yy, k_yz, k_zy, k_zz
        :rtype: :class:`float`, :class:`float`, :class:`float`, :class:`float`
        """

        k_yy = 0.6 * (1 - (lam_y - 0.2) * (1.05 * N_Ed / (X_y * mast.A * mast.fy)))
        k_yy_max = 0.6 * (1 + 0.8 * (1.05 * N_Ed / (X_y * mast.A * mast.fy)))
        if k_yy > k_yy_max:
            k_yy = k_yy_max

        if lam_z < 0.4:
            k_zy = 0.6 + lam_z
            k_zy_max = 1 - (0.1 * lam_z / (0.6 - 0.25)) * (1.05 * N_Ed / (X_z * mast.A * mast.fy))
            if k_zy > k_zy_max:
                k_zy = k_zy_max
        else:
            k_zy_1 = 1 - (0.1 * lam_z / (0.6 - 0.25)) * (1.05 * N_Ed / (X_z * mast.A * mast.fy))
            k_zy_2 = 1 - (0.1 / (0.6 - 0.25)) * (1.05 * N_Ed / (X_z * mast.A * mast.fy))
            k_zy = max(k_zy_1, k_zy_2)

        k_zz = 0.6 * (1 + (2 * lam_z - 0.6) * (1.05 * N_Ed / (X_z * mast.A * mast.fy)))
        k_zz_max = 0.6 * (1 + 1.4 * (1.05 * N_Ed / (X_z * mast.A * mast.fy)))
        if k_zz > k_zz_max:
            k_zz = k_zz_max

        k_yz = 0.6 * k_zz

        return k_yy, k_yz, k_zy, k_zz

    def _utnyttelsesgrad(self, i, mast, K):
        """Beregner utnyttelsesgrad.

        Funksjonen undersøker utnyttelsesgrad for alle relevante
        bruddsituasjoner, og returnerer den høyeste verdien.

        :param Inndata i: Input fra bruker
        :param Mast mast: Aktuell mast
        :param list K: Liste med dimensjonerende reaksjonskrefter
        :return: Mastens utnyttelsesgrad UR
        :rtype: :class:`float`
        """

        u = self.N_kap + self.My_kap + self.Mz_kap

        L_e, A, B = self._beregn_momentfordeling()
        L_cr = 2 * L_e
        if i.avspenningsmast or i.fixavspenningsmast:
            L_cr = L_e

        # Konverterer [Nm] til [Nmm]
        My_Ed, Mz_Ed = 1000 * abs(K[0]), 1000 * abs(K[2])
        Vy_Ed, Vz_Ed, N_Ed = abs(K[1]), abs(K[3]), abs(K[4])

        X_y, lam_y = self._reduksjonsfaktor_knekking(mast, L_cr, 0)
        X_z, lam_z = self._reduksjonsfaktor_knekking(mast, L_cr, 1)
        X_LT = self._reduksjonsfaktor_vipping(mast, L_e, A, B, My_Ed)

        My_Rk, Mz_Rk, N_Rk = mast.My_Rk(), mast.Mz_Rk(), mast.A * mast.fy

        k_yy, k_yz, k_zy, k_zz = self._interaksjonsfaktorer(mast, lam_y, N_Ed, X_y, X_z, lam_z)

        # EC3, 6.3.3(4) ligning (6.61)
        UR_y = (1.05 * N_Ed / (X_y * mast.A * mast.fy)) + \
               k_yy * (1.05 * My_Ed / (X_LT * My_Rk)) + \
               k_yz * (1.05 * Mz_Ed / Mz_Rk)

        # EC3, 6.3.3(4) ligning (6.62)
        UR_z = (1.05 * N_Ed / (X_z * mast.A * mast.fy)) + \
               k_zy * (1.05 * My_Ed / (X_LT * My_Rk)) + \
               k_zz * (1.05 * Mz_Ed / Mz_Rk)

        UR_d, UR_g = 0, 0
        if mast.type == "H":
            # Diagonalstav:
            N_Ed_d = max(math.sqrt(2)/2 * Vy_Ed, math.sqrt(2)/2 * Vz_Ed)
            L_d = mast.k_d * mast.d_L
            d_I = mast.d_I
            alpha_d = 0.49
            N_cr_d = (math.pi**2 * mast.E * d_I) / (L_d**2)
            lam_d = math.sqrt(mast.d_A * mast.fy / N_cr_d)
            phi_d = 0.5 * (1 + alpha_d * (lam_d - 0.2) + lam_d ** 2)
            X_d = 1 / (phi_d + math.sqrt(phi_d**2 - lam_d**2))
            UR_d = (1.05 * N_Ed_d / (X_d * mast.d_A * mast.fy))

            # Gurt (vinkelprofil)
            N_Ed_g = 0.5*((My_Ed/mast.bredde(mast.h-1)) + (Mz_Ed/mast.bredde(mast.h-1)) + Vy_Ed + Vz_Ed) + N_Ed/4
            L_g = mast.k_g * 1000
            I_g = mast.Iy_profil
            alpha_g = 0.34
            N_cr_g = (math.pi**2 * mast.E * I_g) / (L_g**2)
            lam_g = math.sqrt(mast.A_profil * mast.fy / N_cr_g)
            phi_g = 0.5 * (1 + alpha_g * (lam_g - 0.2) + lam_g ** 2)
            X_g = 1 / (phi_g + math.sqrt(phi_g**2 - lam_g**2))
            UR_g = (1.05 * N_Ed_g / (X_g * mast.A_profil * mast.fy))

        return max(u, UR_y, UR_z, UR_d, UR_g)
