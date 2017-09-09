# -*- coding: utf8 -*-
from __future__ import unicode_literals

import math
import numpy
import copy


class Tilstand(object):
    """Objekt med informasjon om lasttilstand fra lastfaktoranalyse.
     Lagres i masteobjekt via metoden mast.lagre_lasttilfelle(lasttilfelle)
     """

    def __init__(self, mast, i, lastsituasjon, vindretning, grensetilstand, F=None, R=None, D=None,
                 G=1, L=1, T=1, S=1, V=1, psi_T=1, psi_S=1, psi_V=1, temp=5, iterasjon=0):
        """Initialiserer :class:`Tilstand`-objekt.

        Alternativer for ``vindretning``:

        - 0: Vind fra mast mot spor
        - 1: Vind fra spor mot mast
        - 2: Vind parallelt spor

        Alternativer for ``grensetilstand``:

        - 0: Bruddgrense
        - 1: Bruksgrense, forskyvning totalt
        - 2: Bruksgrense, forskyvning KL
        - 3: Ulykkestilstand

        :param Mast mast: Aktuell mast
        :param Inndata i: Input fra bruker
        :param str lastsituasjon: Aktuell lastsituasjon
        :param int vindretning: Aktuell vindretning
        :param int grensetilstand: (Rad, etasje) for plassering i R- og D-matrise
        :param list F: Liste med :class:`Kraft`-objekter påført systemet
        :param numpy.array R: Reaksjonskraftmatrise
        :param numpy.array D: Forskyvningsmatrise
        :param float G: Lastfaktor egenvekt
        :param float L: Lastfaktor kabelstrekk
        :param float T: Lastfaktor temperatur
        :param float S: Lastfaktor snø/is
        :param float V: Lastfaktor vind
        :param float psi_T: Lastkombinasjonsfaktor temperatur
        :param float psi_S: Lastkombinasjonsfaktor snø/is
        :param float psi_V: Lastkombinasjonsfaktor vind
        :param int T: Temperatur ved gitt lastsituasjon
        :param iterasjon: Iterasjon for utregning av aktuell :class:`Tilstand`
        """

        self.metode = "EC3" if i.ec3 else "NEK"
        self.lastsituasjon = lastsituasjon
        self.vindretning = vindretning
        self.grensetilstand = grensetilstand
        self.temp = temp
        self.iterasjon = iterasjon

        if self.grensetilstand==0 or self.grensetilstand==3:
            # Bruddgrensetilstand
            self.F = copy.copy(F)
            self.R = R
            self.K = numpy.sum(numpy.sum(R, axis=0), axis=0)
            self.faktorer = {"G": G, "L": L, "T": T, "S": S, "V": V,
                             "psi_T": psi_T, "psi_S": psi_S, "psi_V": psi_V}
            self.N_kap = abs(self.K[4] * mast.materialkoeff / (mast.fy * mast.A))
            self.My_kap = abs(1000 * self.K[0] * mast.materialkoeff / (mast.fy * mast.Wy_el))
            self.Mz_kap = abs(1000 * self.K[2] * mast.materialkoeff / (mast.fy * mast.Wz_el))
            self.dimensjonerende_faktorer = {}
            self.utnyttelsesgrad = self._utnyttelsesgrad(i, mast, self.K)
        else:
            # Bruksgrensetilstand
            self.R = R
            self.D = D
            self.K = numpy.sum(numpy.sum(R, axis=0), axis=0)
            self.K_D = numpy.sum(numpy.sum(D, axis=0), axis=0)

    def __repr__(self):
        K = self.K / 1000  # Konverterer M til [kNm] og V/N til [kN]
        rep = ""
        if self.grensetilstand == 0 or self.grensetilstand == 3:
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
            rep += "Dy = {:.3f} mm    Dz = {:.3f} mm    phi = {:.3f}\n". \
                format(self.K_D[0], self.K_D[1], self.K_D[2])
            rep += "My = {:.3g} kNm    Vy = {:.3g} kN    Mz = {:.3g} kNm    " \
                   "Vz = {:.3g} kN    N = {:.3g} kN    T = {:.3g} kNm\n". \
                format(K[0], K[1], K[2], K[3], K[4], K[5])
            rep += "Lastsituasjon: {}\n".format(self.lastsituasjon)
            rep += "Iterasjon = {}\n".format(self.iterasjon)
            rep += "Vindretning = {}\n".format(self.vindretning)

        return rep

    def _utnyttelsesgrad(self, i, mast, K):
        """Beregner utnyttelsesgrad.

        Funksjonen undersøker utnyttelsesgrad for alle relevante
        bruddsituasjoner, og returnerer den høyeste verdien.

        :param Inndata i: Input fra bruker
        :param Mast mast: Aktuell mast
        :param numpy.array K: Liste med dimensjonerende reaksjonskrefter
        :return: Mastens utnyttelsesgrad
        :rtype: :class:`float`
        """

        u = self.N_kap + self.My_kap + self.Mz_kap

        A, B = self._beregn_momentfordeling()

        self.dimensjonerende_faktorer["A (M_vind)"] = A
        self.dimensjonerende_faktorer["B (M_punkt)"] = B
        self.dimensjonerende_faktorer["bredde_fot [mm]"] = mast.bredde(mast.h)

        # Konverterer [Nm] til [Nmm]
        My_Ed, Mz_Ed = 1000 * abs(K[0]), 1000 * abs(K[2])
        Vy_Ed, Vz_Ed, N_Ed = abs(K[1]), abs(K[3]), abs(K[4])

        My_Rk, Mz_Rk, N_Rk = mast.My_Rk, mast.Mz_Rk, mast.N_Rk

        self.dimensjonerende_faktorer["My_Rk"] = My_Rk / 10**6  # [kNm]
        self.dimensjonerende_faktorer["Mz_Rk"] = Mz_Rk / 10**6  # [kNm]
        self.dimensjonerende_faktorer["N_Rk"] = N_Rk / 1000  # [kN]

        X_y, lam_y = self._reduksjonsfaktor_knekking(mast, "y")
        X_z, lam_z = self._reduksjonsfaktor_knekking(mast, "z")
        X_LT = self._reduksjonsfaktor_vipping(mast, A, B, My_Ed)

        self.dimensjonerende_faktorer["X_y"] = X_y
        self.dimensjonerende_faktorer["lam_y"] = lam_y
        self.dimensjonerende_faktorer["X_z"] = X_z
        self.dimensjonerende_faktorer["lam_z"] = lam_z
        self.dimensjonerende_faktorer["X_LT"] = X_LT

        k_yy, k_yz, k_zy, k_zz = self._interaksjonsfaktorer(mast, lam_y, N_Ed, X_y, X_z, lam_z)

        self.dimensjonerende_faktorer["k_yy"] = k_yy
        self.dimensjonerende_faktorer["k_yz"] = k_yz
        self.dimensjonerende_faktorer["k_zy"] = k_zy
        self.dimensjonerende_faktorer["k_zz"] = k_zz

        # EC3, 6.3.3(4) ligning (6.61)
        UR_y = mast.materialkoeff*(N_Ed/(X_y*N_Rk) + k_yy*My_Ed/(X_LT*My_Rk) + k_yz*Mz_Ed/Mz_Rk)

        # EC3, 6.3.3(4) ligning (6.62)
        UR_z = mast.materialkoeff*(N_Ed/(X_z*N_Rk) + k_zy*My_Ed/(X_LT*My_Rk) + k_zz*Mz_Ed/Mz_Rk)

        UR_d, UR_g = self._knekking_lokal(mast, My_Ed, Mz_Ed, Vy_Ed, Vz_Ed, N_Ed)

        self.dimensjonerende_faktorer["UR_diag"] = UR_d
        self.dimensjonerende_faktorer["UR_gurt"] = UR_g
        self.dimensjonerende_faktorer["UR_y"] = UR_y
        self.dimensjonerende_faktorer["UR_z"] = UR_z
        self.dimensjonerende_faktorer["UR"] = max(u, UR_y, UR_z, UR_d, UR_g)

        return max(u, UR_y, UR_z, UR_d, UR_g)

    def _beregn_momentfordeling(self):
        """Beregner momentandeler til kritisk moment.

        ``A`` angir andel av bidrag til totalmomentet fra
        fordelte laster (vindlast på mast), mens ``B``
        angir andel av bidrag til totalmomentet fra
        punktlaster (øvrige laster).

        :return: Momentandeler ``A`` og ``B``
        :rtype: :class:`float`, :class:`float`
        """

        M_total, M_vind = 0, 0

        # (0) Vind fra mast mot spor eller (1) fra spor mot mast
        if self.vindretning == 0 or 1:
            M_total = self.K[0]
            for j in self.F:
                if not numpy.count_nonzero(j.q) == 0:
                    M_vind += j.q[2] * j.b * (-j.e[0])
            M_vind *= self.faktorer["V"] * self.faktorer["psi_V"]

        # (2) Vind parallelt spor
        elif self.vindretning == 2:
            M_total = self.K[2]
            for j in self.F:
                if not numpy.count_nonzero(j.q) == 0:
                    M_vind += j.q[1] * j.b * (-j.e[0])
            M_vind *= self.faktorer["V"] * self.faktorer["psi_V"]

        A = abs(M_vind/M_total)
        B = 1 - A

        return A, B

    def _reduksjonsfaktor_knekking(self, mast, akse):
        """Beregner reduksjonsfaktor for stavknekking etter NS-EN 1993-1-1 seksjon 6.3.1.2.

        ``akse`` styrer beregning om hhv. sterk og svak akse:

        - y: Beregner knekkfaktorer om mastas sterke akse
        - z: Beregner knekkfaktorer om mastas svake akse

        :param Mast mast: Aktuell mast
        :param str akse: Aktuell akse
        :return: Reduksjonsfaktor for stavknekking ``X`` for knekking, slankhet ``lam``
        :rtype: :class:`float`, :class:`float`
        """

        if akse == "y":
            lam = mast.lam_y
            alpha = 0.34 if not mast.type == "B" else 0.49
            phi = 0.5 * (1 + alpha * (lam - 0.2) + lam ** 2)
            X = 1 / (phi + math.sqrt(phi ** 2 - lam ** 2))

            self.dimensjonerende_faktorer["N_cr_y"] = mast.N_cr_y / 1000  # [kN]
            self.dimensjonerende_faktorer["lam_y"] = lam
            self.dimensjonerende_faktorer["alpha_y"] = alpha

        else:  # z-akse
            lam = mast.lam_z
            alpha = 0.49 if not mast.type == "H" else 0.34
            phi = 0.5 * (1 + alpha * (lam - 0.2) + lam ** 2)
            X = 1 / (phi + math.sqrt(phi ** 2 - lam ** 2))

            self.dimensjonerende_faktorer["N_cr_z"] = mast.N_cr_z / 1000  # [kN]
            self.dimensjonerende_faktorer["lam_z"] = lam
            self.dimensjonerende_faktorer["alpha_z"] = alpha

        X = X if X <= 1.0 else 1.0

        return X, lam

    def _reduksjonsfaktor_vipping(self, mast, A, B, My_Ed):
        """Bestemmer reduksjonsfaktoren for vipping etter NS-EN 1993-1-1 seksjon 6.3.2.2 og 6.3.2.3.

        Det antas at alle laster angriper midt i tverrsnittet,
        dvs. :math:`z_a = 0`.

        :param Mast mast: Aktuell mast
        :param float A: Momentandel fra vindlast
        :param float B: Momentandel fra punktlaster
        :return: Reduksjonsfaktor for vipping
        :rtype: :class:`float`
        """

        X_LT = 1.0

        if not mast.type == "H":
            psi_vind, psi_punkt = 2.05, 1.28
            M_cr = (A * psi_vind + B * psi_punkt) * mast.M_cr_0
            lam_LT = math.sqrt(mast.My_Rk / M_cr)

            if mast.type == "B":
                alpha_LT = 0.76
                phi_LT = 0.5 * (1 + alpha_LT * (lam_LT - 0.2) + lam_LT**2)
                X_LT = 1 / (phi_LT + math.sqrt(phi_LT**2 - lam_LT**2))
                X_LT = X_LT if X_LT <= 1.0 else 1.0
            else:  # bjelke
                alpha_LT = 0.34
                lam_LT_0, beta_LT = 0.4, 0.75
                phi_LT = 0.5 * (1 + alpha_LT * (lam_LT - lam_LT_0) + beta_LT * lam_LT**2)
                X_LT = 1 / (phi_LT + math.sqrt(phi_LT**2 - beta_LT * lam_LT**2))
                if X_LT > min(1.0, (1 / lam_LT**2)):
                    X_LT = min(1.0, (1 / lam_LT**2))

                self.dimensjonerende_faktorer["lam_LT_0"] = lam_LT_0
                self.dimensjonerende_faktorer["beta_LT"] = beta_LT

            self.dimensjonerende_faktorer["alpha_LT"] = alpha_LT
            self.dimensjonerende_faktorer["phi_LT"] = phi_LT
            self.dimensjonerende_faktorer["C_W [10^-7 m^6]"] = mast.Cw / 1000**6 * 10**7
            self.dimensjonerende_faktorer["I_T [10^-7 m^4]"] = mast.It / 1000**4 * 10**7
            self.dimensjonerende_faktorer["I_z [10^-7 m^4]"] = mast.Iz(mast.h) / 10**7
            self.dimensjonerende_faktorer["I_y [10^-7 m^4]"] = mast.Iy(mast.h) / 10**7
            self.dimensjonerende_faktorer["psi_v"] = mast.psi_v
            self.dimensjonerende_faktorer["M_cr_0"] = mast.M_cr_0 / 10**6  # [kNm]
            self.dimensjonerende_faktorer["M_cr"] = M_cr / 10**6  # [kNm]
            self.dimensjonerende_faktorer["lam_LT"] = lam_LT

        return X_LT

    def _interaksjonsfaktorer(self, mast, lam_y, N_Ed, X_y, X_z, lam_z):
        """Beregner interaksjonsfaktorer etter NS-EN 1993-1-1 tabell B.2.

        Det antas at alle master tilhører tverrsnittsklasse #1.

        :param Mast mast: Aktuell mast
        :param float lam_y: Relativ slankhet for knekking om y-aksen
        :param float N_Ed: Dimensjonerende aksialkraft :math:`[N]`
        :param float X_y: Reduksjonsfaktor for knekking om y-aksen
        :param float X_z: Reduksjonsfaktor for knekking om z-aksen
        :param float lam_z: Relativ slankhet for knekking om y-aksen
        :return: Interaksjonsfaktorer ``k_yy``, ``k_yz``, ``k_zy``, ``k_zz``
        :rtype: :class:`float`, :class:`float`, :class:`float`, :class:`float`
        """

        N_Rk = mast.N_Rk
        matkoeff = mast.materialkoeff

        k_yy = 0.6 * (1 + (lam_y - 0.2) * (matkoeff * N_Ed / (X_y*N_Rk)))
        k_yy_max = 0.6 * (1 + 0.8 * (matkoeff * N_Ed / (X_y*N_Rk)))
        if k_yy > k_yy_max:
            k_yy = k_yy_max

        if lam_z < 0.4:
            k_zy = 0.6 + lam_z
            k_zy_max = 1 - (0.1 * lam_z / (0.6 - 0.25)) * (matkoeff * N_Ed / (X_z*N_Rk))
            if k_zy > k_zy_max:
                k_zy = k_zy_max
        else:
            k_zy_1 = 1 - (0.1 * lam_z / (0.6 - 0.25)) * (matkoeff * N_Ed / (X_z*N_Rk))
            k_zy_2 = 1 - (0.1 / (0.6 - 0.25)) * (matkoeff * N_Ed / (X_z*N_Rk))
            k_zy = max(k_zy_1, k_zy_2)

        k_zz = 0.6 * (1 + (2 * lam_z - 0.6) * (matkoeff * N_Ed / (X_z*N_Rk)))
        k_zz_max = 0.6 * (1 + 1.4 * (matkoeff * N_Ed / (X_z*N_Rk)))
        if k_zz > k_zz_max:
            k_zz = k_zz_max

        k_yz = 0.6 * k_zz

        return k_yy, k_yz, k_zy, k_zz

    def _knekking_lokal(self, mast, My_Ed, Mz_Ed, Vy_Ed, Vz_Ed, N_Ed):
        """Beregner utnyttelsesgrad for lokal stavknekking etter NS-EN 1993-1-1 seksjon 6.3.1.2.

        :param Mast mast: Aktuell mast
        :param float My_Ed: Dimensjonerende moment om mastas y-akse :math:`[Nmm]`
        :param float Mz_Ed: Dimensjonerende moment om mastas z-akse :math:`[Nmm]`
        :param float Vy_Ed: Dimensjonerende skjærkraft parallelt mastas y-akse :math:`[N]`
        :param float Vz_Ed: Dimensjonerende skjærkraft parallelt mastas z-akse :math:`[N]`
        :param float N_Ed: Dimensjonerende normaltkraft i masta :math:`[N]`
        :return: Utnyttelsesgrader for diagonal og gurt, ``UR_d`` og ``UR_g``
        :rtype: :class:`float`, :class:`float`
        """

        matkoeff = mast.materialkoeff
        UR_d, UR_g = 0, 0

        if not mast.type == "bjelke":
            if mast.type == "H":
                # Gurt (L-profil)
                N_Ed_g = 0.5*(My_Ed/mast.bredde(mast.h-1) + Mz_Ed/mast.bredde(mast.h-1)) + N_Ed/4
                # Diagonalstav
                N_Ed_d = max(Vy_Ed, Vz_Ed) / math.sqrt(2)
            else:  # B-mast
                # Gurt (U-profil)
                N_Ed_g = My_Ed/mast.bredde(mast.h - 1) + Mz_Ed/mast.bredde(mast.h - 1) + N_Ed/2
                # Diagonalstav
                N_Ed_d = Vz_Ed * math.sqrt(2)

            phi_g = 0.5 * (1 + mast.alpha_g * (mast.lam_g - 0.2) + mast.lam_g**2)
            X_g = 1 / (phi_g + math.sqrt(phi_g**2 - mast.lam_g**2))
            UR_g = matkoeff*N_Ed_g / (X_g*mast.A_profil*mast.fy)

            phi_d = 0.5 * (1 + mast.alpha_d * (mast.lam_d - 0.2) + mast.lam_d**2)
            X_d = 1 / (phi_d + math.sqrt(phi_d**2 - mast.lam_d**2))
            UR_d = matkoeff*N_Ed_d / (X_d*mast.d_A*mast.fy)

            self.dimensjonerende_faktorer["N_Ed_gurt"] = N_Ed_g / 1000  # [kN]
            self.dimensjonerende_faktorer["N_cr_gurt"] = mast.N_cr_g / 1000  # [kN]
            self.dimensjonerende_faktorer["alpha_gurt"] = mast.alpha_g
            self.dimensjonerende_faktorer["lam_gurt"] = mast.lam_g
            self.dimensjonerende_faktorer["phi_gurt"] = phi_g
            self.dimensjonerende_faktorer["X_gurt"] = X_g

            self.dimensjonerende_faktorer["N_Ed_diag"] = N_Ed_d / 1000  # [kN]
            self.dimensjonerende_faktorer["N_cr_diag"] = mast.N_cr_d / 1000  # [kN]
            self.dimensjonerende_faktorer["alpha_diag"] = mast.alpha_d
            self.dimensjonerende_faktorer["lam_diag"] = mast.lam_d
            self.dimensjonerende_faktorer["phi_diag"] = phi_d
            self.dimensjonerende_faktorer["X_diag"] = X_d

        return UR_d, UR_g



