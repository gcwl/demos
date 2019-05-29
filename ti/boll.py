from numpy import sqrt
from ma import sma, ema


class bb(object):
    """\
    ma = moving average
    upper band = ma + k*sigma
    lower band = ma - k*sigma
    """

    def __init__(self, filter=None, n=20, k=2):
        filter = filter or sma
        #        assert filter is sma or filter is ema
        self.k = k  # multiple of standard deviation
        self.m = filter(n)  # moving average
        self.v = filter(n)  # filter for upper/lower band calculation
        self._rv = -1.0

    _lower = None
    _upper = None

    lower = property(lambda self: self._lower)
    upper = property(lambda self: self._upper)

    rv = property(lambda self: self._rv)

    def __call__(self, x):
        c = self.m(x)  # center
        self._rv = sqrt(self.v(x * x) - c * c)
        z = self.k * self._rv
        self._lower = c - z
        self._upper = c + z
        return self._lower, self._upper
