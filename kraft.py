# -*- coding: utf8 -*-
from __future__ import unicode_literals

from numpy import array, count_nonzero

sporhoyde_e = 0

class Kraft(object):
    """Generell klasse for konsentrerte/fordelte laster."""

    def __init__(self, navn="", type=(0, 0), f=[0, 0, 0],
                 q=[0, 0, 0], b=0, e=[0, 0, 0]):
        """Initialiserer :class:`Kraft`-objekt.

        ``sporhoyde_e`` trekkes fra ``e[0]`` for å konvertere
        kreftenes lastangrepspunkt med nullpunkt i skinneoverkant
        til mastenes lokale aksesystem med origo i mastefot.

        :param str navn: Identifikasjonstag for kraftens opphav
        :param tuple type: (Rad, etasje) for plassering i R- og D-matrise
        :param list f: Kraftkomponenter [x, y, z] :math:`[N]`
        :param list q: Kraftkomponenter for fordelt last [x, y, z] :math:`[\\frac{N}{m}]`
        :param list b: Utstrekning av fordelt last :math:`[m]`
        :param list e: Eksentrisitet fra origo [x, y, z] :math:`[m]`
        """

        self.navn = navn
        self.type = type
        self.f = array(f)
        self.q = array(q)
        self.b = b
        self.e = array(e)
        self.e[0] -= sporhoyde_e
        self.e[0] = 0 if self.e[0] > 0 else self.e[0]

    def __repr__(self):
        rep = "{}   type={}\n".format(self.navn, self.type)
        if not count_nonzero(self.q) == 0:
            rep += "q*b = {}\n".format(self.q * self.b)
        else:
            rep += "f = {}\n".format(self.f)
        rep += "e = {}\n".format(self.e)
        return rep








