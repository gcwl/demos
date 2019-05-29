# https://en.wikipedia.org/wiki/Parabolic_SAR
# https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:parabolic_sar

from itertools import repeat, chain


def seq(start, stop, step):
    i = start
    while i < stop:
        yield i
        i += step


class sar_base(object):
    """Parabolic SAR
    https://en.wikipedia.org/wiki/Parabolic_SAR"""

    # sar = sar value of previous period
    # af (acceleration factor) = .02, .04, .06, ..., .18, .20, .20, .20, ...
    sar = None
    ep = None

    def __init__(self, start=0.02, stop=0.2, step=0.02):
        self.af = start
        self.af_chain = chain(seq(start, stop, step), repeat(stop))


class sar_up(sar_base):
    # Rising (Up) SAR formula:
    # Current SAR = Prior SAR + Prior AF(Prior EP - Prior SAR)
    # ep (extreme point) = highest high of the current period
    def __call__(self, high):
        if self.sar is None:  # first time; init self.sar and self.ep values
            self.sar = high
            self.ep = high
            return self.sar
        sar = self.sar + self.af * (self.ep - self.sar)
        if high > self.ep:
            self.ep = high
            self.af = self.af_chain.next()
        self.sar = sar
        return sar


class sar_dn(sar_base):
    # Falling (dn) SAR formula:
    # Current SAR = Prior SAR - Prior AF(Prior SAR - Prior EP)
    # ep (extreme point) = lowest low of the current down trend
    def __call__(self, low):
        if self.sar is None:  # first time; init self.sar and self.ep values
            self.sar = low
            self.ep = low
            return self.sar
        sar = self.sar - self.af * (self.sar - self.ep)
        if low < self.ep:
            self.ep = low
            self.af = self.af_chain.next()
        self.sar = sar
        return sar
