# -*- coding: utf-8 -*-

__author__ = 'Gaetano "Gibbster" Pellegrino'

"""
Utility for learning and testing SARIMAX models.

# based on Chad Fulton's post in here:
# https://github.com/statsmodels/statsmodels/issues/2577
"""

import warnings as wr
import pickle as pk

wr.simplefilter(action='ignore', category=FutureWarning)
from statsmodels.tsa.statespace.sarimax import SARIMAX


# AR is the order of the AR component of SARIMAX
AR = 4
# D is a boolean flag answering the question "should I differentiate the data?"
D = True
# MA is the order of the MA component of SARIMAX
MA = 1


# flat sequence loader from path
def load_flat(path):
    with open(path, "r") as fh:
        for line in fh:
            yield float(line.strip())


# flat_path_tr is the path to a flat train sequence
# md_path_out is the file path where the model will get stored permanently
def train(flat_path_tr, md_path):
    tr = [vl for vl in load_flat(flat_path_tr)]
    md = SARIMAX(tr, order=(AR, 1 if D else 0, MA), enforce_stationarity=False, enforce_invertibility=False)
    prs = md.fit(disp=0).params
    pk.dump(prs, open(md_path, "wb"))
    return prs


# md_path_out is the file path where the model is stored permanently (see train())
# flat_path_ts is the path to a testing flat sequence
# flat_path_out is a path where the results of the predictions will be stored as a flat sequence
def evaluate(md_path, flat_path_ts, flat_path_out):
    prs = pk.load(open(md_path, "rb"))
    ts = [vl for vl in load_flat(flat_path_ts)]
    md2 = SARIMAX(ts, order=(AR, 1 if D else 0, MA), enforce_stationarity=False, enforce_invertibility=False)
    rs = md2.filter(prs)
    # assembling the results
    with open(flat_path_out, "w") as oh:
        for i in xrange(len(ts)):
            oh.write(str(rs.predict(i, i)[-1]) + "\n")


if __name__ == "__main__":
    t1 = "/home/nino/PycharmProjects/rai_experiments/sinus/data16/0/train.flat"
    t2 = "/home/nino/PycharmProjects/rai_experiments/sinus/data16/0/test.flat"
    t3 = "/home/nino/PycharmProjects/rai_experiments/sinus/canc.flat"
    t4 = "/home/nino/PycharmProjects/rai_experiments/sinus/data16/0/arima.bin"
    # m = train(t1, t4)
    m = pk.load(open(t4, "rb"))
    # evaluate(t4, t2, t3)
    print m
