# -*- coding: utf8 -*-
from __future__ import unicode_literals

import numpy
from functools import total_ordering

@total_ordering
class Kraft(object):
    """Generell klasse for konsentrerte/fordelte laster."""

    def __init__(self, navn="", type=(0, 0), f=(0, 0, 0),
                 q=(0, 0, 0), b=0, e=(0, 0, 0), T=None, vindretning=None):
        """Initialiserer :class:`Kraft`-objekt.

        Alternativer for ``vindretning``:

        - 0: Vind fra mast mot spor
        - 1: Vind fra spor mot mast
        - 2: Vind parallelt spor

        Variabelen ``statisk`` settes avhengig av om lasten
        varierer med klimatiske forhold.

        Klassen bruker ``@total_ordering``-dekoratoren for enkel
        sammenlikning av :class:`Kraft`-objekter.

        :param str navn: Identifikasjonstag for kraftens opphav
        :param tuple type: (Rad, etasje) for plassering i R- og D-matrise
        :param tuple f: Kraftkomponenter [x, y, z] :math:`[N]`
        :param tuple q: Kraftkomponenter for fordelt last [x, y, z] :math:`[\\frac{N}{m}]`
        :param list b: Utstrekning av fordelt last :math:`[m]`
        :param tuple e: Eksentrisitet fra origo [x, y, z] :math:`[m]`
        :param int T: Temperatur ved forårsakende last :math:`^{\\circ}C`
        :param int vindretning: Vindretning ved forårsakende last
        """

        self.navn = navn
        self.type = type
        self.f = numpy.array(f)
        self.q = numpy.array(q)
        self.b = b
        self.e = numpy.array(e)
        self.T = T
        self.vindretning = vindretning

        if self.T is None and self.vindretning is None:
            self.statisk = True
        else:
            self.statisk = False


    def __repr__(self):
        rep = "{}   type={}".format(self.navn, self.type)
        if self.T is not None:
            rep += "    T = {}".format(self.T)
        rep += "\n"
        if not numpy.count_nonzero(self.q) == 0:
            rep += "q*b = {}\n".format(self.q * self.b)
        else:
            rep += "f = {}\n".format(self.f)
        rep += "e = {}\n".format(self.e)
        return rep

    def __lt__(self, other):
        return numpy.linalg.norm(self.f) - numpy.linalg.norm(other.f) < 0

    def __eq__(self, other):
        return numpy.linalg.norm(self.f) - numpy.linalg.norm(other.f) == 0


