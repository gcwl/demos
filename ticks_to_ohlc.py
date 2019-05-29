##
## imports
##

import re
import logging

from itertools import groupby
from functools import partial
from datetime import timedelta

from util.database import ifetch

##
## global constants
##

LOG = logging.getLogger(__name__)


##
## helpers
##

# stmt in PostgreSQL format
stmt = """SELECT * FROM "{0}" WHERE datetime BETWEEN %s AND %s"""

_pat_datetime = re.compile(r"\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d\.\d{6}")


def _keyfunc(bucketsize, args):
    """Ceiling timestamp according to bucketsize;
    supported bucketsize ('10s', '20s', '30s', '1m', '2m', '3m', '5m', '10m', '15m', '20m', '30m', '1h', etc.)"""

    #    print args
    dt = args[0]
    #    print dt

    if bucketsize.endswith("s"):
        s = int(bucketsize.rstrip("s"))
        ## FIXME FIXME FIXME
        ss = (dt.second / s) * s  # floor
        rv = dt.replace(second=ss, microsecond=0) + timedelta(
            seconds=s
        )  # add timedelta to "ceiling" timestamp
        ## FIXME FIXME FIXME
    elif bucketsize.endswith("m"):
        m = int(bucketsize.rstrip("m"))
        mm = (dt.minute / m) * m
        rv = dt.replace(minute=mm, second=0, microsecond=0) + timedelta(minutes=m)
    elif bucketsize == "1h":
        rv = dt.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    else:
        raise Exception("bucketsize %d not supported" % bucketsize)
    return rv


class _ohlc_aggregator(object):
    """Perform open/first, high/max, low/min, close/last aggregation with a given group"""

    key = open = high = low = close = None

    def __init__(self, key, igroups):
        self.dt = key
        for arg in igroups:
            dt, px = arg[:2]
            if self.open is None:
                self.open = px
            self.high = max(self.high or px, px)
            self.low = min(self.low or px, px)
            self.close = px

    def aggregate(self):
        return self.dt, self.open, self.high, self.low, self.close


##
## api
##


def ohlc(db_cursor, ticker, begin, end, bucketsize):
    # assert bucketsize in ('1m', '2m', '3m', '5m', '10m', '15m', '20m', '30m', '1h')
    # assert bool(_pat_datetime.match(begin))
    # assert bool(_pat_datetime.match(end))

    query = stmt.format(ticker)
    #    LOG.debug(query)
    db_cursor.execute(query, (begin, end))

    ix = ifetch(db_cursor)
    keyfunc = partial(_keyfunc, bucketsize)

    for k, g in groupby(ix, keyfunc):
        yield _ohlc_aggregator(k, g).aggregate()
