# source:
# https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:stochastic_oscillator

# %K = (Current Close - Lowest Low)/(Highest High - Lowest Low) * 100
# %D = 3-day SMA of %K
# Lowest Low = lowest low for the look-back period
# Highest High = highest high for the look-back period
# %K is multiplied by 100 to move the decimal point two places

# Fast Stochastic Oscillator:
# Fast %K = %K basic calculation
# Fast %D = 3-period SMA of Fast %K

# Slow Stochastic Oscillator:
# Slow %K = Fast %K smoothed with 3-period SMA
# Slow %D = 3-period SMA of Slow %K

# Full Stochastic Oscillator:
# Full %K = Fast %K smoothed with X-period SMA
# Full %D = X-period SMA of Full %K

from collections import deque
from ma import sma


class stoch(object):
    n = 14

    def __init__(self):
        self.hi = deque(maxlen=self.n)
        self.lo = deque(maxlen=self.n)

    def append_high(self, hi):
        self.hi.append(hi)

    def append_low(self, lo):
        self.lo.append(lo)

    @property
    def hh(self):
        """highest high"""
        return max(self.hi)

    @property
    def ll(self):
        """lowest low"""
        return min(self.lo)


class fullstoch(stoch):
    def __init__(self, n=None, nd=None, nk=None):
        self.n = n or self.n
        super(fullstoch, self).__init__()
        self.nd = nd or self.nd
        self.d = sma(self.nd)
        self.nk = nk or self.nk
        self.k = sma(self.nk)

    def __call__(self, x):
        k = self.k((x - self.ll) / (self.hh - self.ll) * 100.0)
        d = self.d(k)
        return k, d


class slowstoch(fullstoch):
    nk = nd = 3


class faststoch(fullstoch):
    nk = 1
    nd = 3
