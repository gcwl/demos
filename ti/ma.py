from collections import deque
from numpy import mean


# https://docs.python.org/2/library/collections.html
def moving_average(iterable, n=3):
    # moving_average([40, 30, 50, 46, 39, 44]) --> 40.0 42.0 45.0 43.0
    # http://en.wikipedia.org/wiki/Moving_average
    from itertools import islice

    it = iter(iterable)
    d = deque(islice(it, n - 1))
    d.appendleft(0)
    s = sum(d)
    for elem in it:
        s += elem - d.popleft()
        d.append(elem)
        yield s / float(n)


class sma(object):
    """Simple moving average"""

    n = 200

    def __init__(self, n=None):
        n = n or self.n
        self.q = deque(maxlen=n)

    def __call__(self, x):
        self.q.append(x)
        return mean(self.q)


class ema(object):
    """\
    Exponential moving average

    define
    w := weight = 2/(N+1), hence 1-weight = (N-1)/(N+1)
    x := new value
    a := exponential moving average

    formula
    a = a*(1-w)+x*w = a+(x-a)*w
    """

    n = 200  # this is the same `N' in weight formula

    a = 0.0
    flag = True  # to indicate if this is the first time calling

    def __init__(self, n=None, weight=None, warmup=None):
        from itertools import chain, repeat
        from numpy import linspace

        if weight is None:
            n = n or self.n
            w = 2.0 / (n + 1)
        else:
            assert 0.0 <= weight <= 1.0
            w = weight
        # the weight effect fully kicks in after warmup number of periods
        if warmup:
            assert warmup >= 0
            self.w = chain(linspace(1 - w, w, warmup), repeat(w))
        else:  # warmup is None / warmup is False / warmup == 0
            self.w = repeat(w)

    def __call__(self, x):
        if self.flag:
            self.flag = False  # set the flag
            self.a = x
            return x
        self.a += (x - self.a) * self.w.next()
        return self.a

    @property
    def value(self):
        return self.a

