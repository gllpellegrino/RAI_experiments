# -*- coding: utf-8 -*-

__author__ = 'Gaetano "Gibbster" Pellegrino'


"""
Sinus evaluation utility.
It contains everything needed to evaluate RAI on the sinus wave test cases.
Each alternative technique must return a prediction for each value within the test flat file.
"""


import warnings as wr
from math import sqrt
import matplotlib.pyplot as plt
import dot_utility as du
import rti_utility as ru
import distorced_sinus.sinus_utility as su
import distorced_sinus.meta as mt
# workaround to ignore the pandas.core.datetools deprecation warning
from statsmodels import ConvergenceWarning
wr.simplefilter(action='ignore', category=FutureWarning)
wr.simplefilter(action='ignore', category=ConvergenceWarning)
from statsmodels.tsa.statespace.sarimax import SARIMAX


# ------------------------------------------------------------------------------------------------------------------


# mean absolute error.
# expects a list of predictions, and a list of observations, of the same size
def mae(prd, obs):
    sm = 0.
    for i in xrange(len(prd)):
        sm += abs(prd[i] - obs[i])
    return sm / float(len(prd))


# mean absolute percentage error.
# expects a list of predictions, and a list of observations, of the same size
def mape(prd, obs):
    sm = 0.
    for i in xrange(len(prd)):
        sm += abs((obs[i] - prd[i]) / obs[i]) if obs[i] != 0. else 0.
    return 100. / float(len(prd)) * sm


# root-mean-square error
# expects a list of predictions, and a list of observations, of the same size
def rmse(prd, obs):
    sm = 0.
    for i in xrange(len(prd)):
        sm += (prd[i] - obs[i]) * (prd[i] - obs[i])
    return sqrt(sm / float(len(prd)))


# persistence baseline, only requires the flat test file path.
def persistence(flat_path):
    prd = 0.
    for vl in su.load_flat(flat_path):
        yield prd, vl
        prd = vl


# -----------------------------------------------------------------------------------------------------------------


# rai and rti only require the flat test file path and a model dot file path.
# we can use the same method for both techniques because we
def rairti(flat_path, dot_path):
    md = du.load_md(dot_path)
    first_w = True
    for window in ru.windows_getter(flat_path, mt.PERIOD):
        sta = 0
        if first_w:
            first_w = False
            for vl in window:
                yield md[sta]["p"], vl
                # looking for the next state
                for _, ds, lg, rg in md[sta]["t"]:
                    if lg < vl <= rg:
                        sta = ds
                        break
        else:
            prd = 0.
            for vl in window:
                prd = md[sta]["p"]
                # looking for the next state
                for _, ds, lg, rg in md[sta]["t"]:
                    if lg < vl <= rg:
                        sta = ds
                        break
            yield prd, window[-1]


# seasonal arma and arima predictions gatherer.
# based on Chad Fulton's post in here:
# https://github.com/statsmodels/statsmodels/issues/2577
# ---------------------------------------------------------
# it expects a path to the test flat file,
# i is a boolean flag to use or not the integration (arima does, arma does not)
def sarimax(flat_path, tr_flat_path, i=True):
    # setting the integration order
    d = 1 if i else 0
    # getting training and testing data
    tr = [vl for vl in su.load_flat(tr_flat_path)]
    ts = [vl for vl in su.load_flat(flat_path)]
    # training
    md1 = SARIMAX(tr, order=(mt.PERIOD, d, 1), enforce_stationarity=False, enforce_invertibility=False)
    rs1 = md1.fit(disp=0)
    # testing
    md2 = SARIMAX(ts, order=(mt.PERIOD, d, 1), enforce_stationarity=False, enforce_invertibility=False)
    rs2 = md2.filter(rs1.params)
    # assembling the results
    for i in xrange(len(ts)):
        yield list(rs2.predict(i, i))[-1], ts[i]


# evaluate a single test case.
# flat_path_ts is the flat data path for testing
# flat_path_tr is the flat data path for training
# rai_dot is the dot file path of an automaton with RAI
# rtisy_dot is the dot file path of an automaton with RTI+ and symbols
# rtitm_dot is the dot file path of an automaton with RTI+ and time
def evaluate_tc(flat_path_ts, flat_path_tr, rai_dot, rtisy_dot, rtitm_dot):
    res = {}
    # -----------------------------------------------------------------------------------
    # gold
    gl = [vl for _, vl in persistence(flat_path_ts)]
    # persistence
    pr = [vl for vl, _ in persistence(flat_path_ts)]
    res["Persistence"] = {"MAE": mae(pr, gl), "MAPE": mape(pr, gl), "RMSE": rmse(pr, gl)}
    # RAI
    ra = [vl for vl, _ in rairti(flat_path_ts, rai_dot)]
    res["RAI"] = {"MAE": mae(ra, gl), "MAPE": mape(ra, gl), "RMSE": rmse(ra, gl)}
    # RTI+ symbols
    rs = [vl for vl, _ in rairti(flat_path_ts, rtisy_dot)]
    res["RTI+ symbols"] = {"MAE": mae(rs, gl), "MAPE": mape(rs, gl), "RMSE": rmse(rs, gl)}
    # RTI+ time
    rt = [vl for vl, _ in rairti(flat_path_ts, rtitm_dot)]
    res["RTI+ time"] = {"MAE": mae(rt, gl), "MAPE": mape(rt, gl), "RMSE": rmse(rt, gl)}
    # ARIMA
    ai = [vl for vl, _ in sarimax(flat_path_ts, flat_path_tr)]
    res["ARIMA"] = {"MAE": mae(ai, gl), "MAPE": mape(ai, gl), "RMSE": rmse(ai, gl)}
    # ARMA
    am = [vl for vl, _ in sarimax(flat_path_ts, flat_path_tr, False)]
    res["ARMA"] = {"MAE": mae(am, gl), "MAPE": mape(am, gl), "RMSE": rmse(am, gl)}
    # -----------------------------------------------------------------------------------
    return res


# utility to plot the predictions for a test case identifier [0 to 9 on sinus]
def plot(test_case):
    # setting the paths
    tcdir = mt.BASEDIR + "/" + str(test_case)
    ts_flat = tcdir + "/test.flat"
    tr_flat = tcdir + "/train.flat"
    rai_dot = tcdir + "/rai.dot"
    rtisy_dot = tcdir + "/rtisy.dot"
    rtitm_dot = tcdir + "/rtitm.dot"
    # getting the predictions
    # -----------------------------------------------------
    # gold
    gl = [vl for _, vl in persistence(ts_flat)]
    # persistence
    pr = [vl for vl, _ in persistence(ts_flat)]
    # RAI
    ra = [vl for vl, _ in rairti(ts_flat, rai_dot)]
    # RTI+ symbols
    rs = [vl for vl, _ in rairti(ts_flat, rtisy_dot)]
    # RTI+ time
    rt = [vl for vl, _ in rairti(ts_flat, rtitm_dot)]
    # ARIMA
    ai = [vl for vl, _ in sarimax(ts_flat, tr_flat)]
    # ARMA
    am = [vl for vl, _ in sarimax(ts_flat, tr_flat, False)]
    # -----------------------------------------------------
    # now we plot)
    # index
    ix = [i for i in xrange(len(gl))]
    plt.title('Predicions')
    plt.plot(ix, gl, label="Gold", color="y")
    plt.plot(ix, pr, label="Persistence", color="b")
    plt.plot(ix, ra, label="RAI", color="g")
    plt.plot(ix, rs, label="RTI+(sy)", color="r")
    plt.plot(ix, rt, label="RTI+(tm)", color="c")
    plt.plot(ix, ai, label="ARIMA", color="m")
    plt.plot(ix, am, label="ARMA", color="k")
    plt.grid(True)
    plt.legend()
    # plt.savefig("/home/nino/Scrivania/plot.png")
    plt.show()


# main evaluation method.
def evaluate():
    # setting general parameters for all the utility moduli called in this script
    su.PRECISION = mt.PRECISION
    ru.PRECISION = mt.PRECISION
    ru.ABOUNDS = mt.ABOUNDS
    ru.ASIZE = mt.ASIZE
    ru.WSIZE = mt.WSIZE
    ru.TRAINL = mt.TRAINL
    # -----------------------------------------------------------------------------------
    for tc in mt.TCIDS:
        print "learning automata for test case", tc
        # sets the paths
        tcdir = mt.BASEDIR + "/" + str(tc)
        ts_flat = tcdir + "/test.flat"
        tr_flat = tcdir + "/train.flat"
        rai_dot = tcdir + "/rai.dot"
        rtisy_dot = tcdir + "/rtisy.dot"
        rtitm_dot = tcdir + "/rtitm.dot"
        # evaluation of test case tc
        rs = evaluate_tc(ts_flat, tr_flat, rai_dot, rtisy_dot, rtitm_dot)
        # showing the results
        for tn in rs:
            print "\n", tn
            for pm in rs[tn]:
                if pm == "MAE":
                    print pm, rs[tn][pm]
        print "\n"


if __name__ == "__main__":
    # f1 = "/home/nino/PycharmProjects/rai_experiments/sinus/data/0/test.flat"
    # f2 = "/home/nino/PycharmProjects/rai_experiments/sinus/data/0/train.flat"
    # m = "/home/nino/PycharmProjects/rai_experiments/sinus/data/0/rai.dot"
    # vs1 = [v for v, _ in sarimax(f1, f2)]
    # print "LEN", len(vs1)
    # print "VALS", vs1
    evaluate()
    # plot(5)
