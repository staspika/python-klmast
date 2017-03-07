import functools

@functools.total_ordering
class Lasttilfelle(object):
    """Objekt med informasjon om lasttilstand fra lastfaktoranalyse.
    Lagres i masteobjekt via metoden mast.lagre_lasttilfelle(lasttilfelle)
    """

    def __init__(self, sum_last, grensetilstand, g, l, f1, f2, f3, k):
        self.sum = sum_last
        self.tilstand = grensetilstand["navn"]
        self.faktorer = [g, l, f1, f2, f3, k]

    """Metoder for å kunne sortere liste av Lasttilfeller mhp. My."""
    def __eq__(self, other):
        return self.sum[0] == other.sum[0]

    def __lt__(self, other):
       return self.sum[0] < other.sum[0]



