from ma import ema


class macd(object):
    """MACD"""

    def __init__(self, fast=12, slow=26, signal=9):
        self.fast = ema(n=fast)
        self.slow = ema(n=slow)
        self.signal = ema(n=signal)

    def __call__(self, x):
        return self.fast(x) - self.slow(x), self.signal(x)
