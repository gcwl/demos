import logging
from ma import ema

log = logging.getLogger(__name__)


class tr(object):
    """True Range
    https://en.wikipedia.org/wiki/Average_true_range
    """

    prev_close = None

    def __call__(self, o, h, l, c):
        if self.prev_close is None:
            r = h - l  # TODO is this assumption correct?
        else:
            x = self.prev_close
            r = max(h - l, abs(h - x), abs(l - x))
        self.prev_close = c
        return r


class atr(object):
    """Average True Range"""

    n = 14

    def __init__(self, n):
        self.n = n or self.n
        self.tr = tr()
        self.atr = ema(self.n)

    def __call__(self, o, h, l, c):
        return self.atr(self.tr(o, h, l, c))


class adx(object):
    """Average Directional Movement Index
    https://en.wikipedia.org/wiki/Average_directional_index
    """

    n = 14
    prev = None

    def __init__(self, n=None):
        self.n = n or self.n
        self.dm_plus = ema(self.n)
        self.dm_minus = ema(self.n)
        self.atr = atr(self.n)
        self.adx = ema(self.n)

    def __call__(self, o, h, l, c):
        atr = self.atr(o, h, l, c)
        if self.prev is None:
            self.prev = o, h, l, c
            return self.adx(0.2) * 100, 20.0, 20.0
        ox, hx, lx, cx = self.prev
        u = h - hx  # up
        d = lx - l  # down
        di_plus = self.dm_plus(max(0, u) if u > d else 0) / atr * 100.0
        di_minus = self.dm_minus(max(0, d) if u < d else 0) / atr * 100.0
        x = abs(di_plus - di_minus)
        y = di_plus + di_minus
        try:
            z = x / y
        except ZeroDivisionError as e:
            log.warn(e, exc_info=True)
            z = self.adx.value
        finally:
            adx = self.adx(z) * 100.0

        self.prev = o, h, l, c
        return adx, di_plus, di_minus
