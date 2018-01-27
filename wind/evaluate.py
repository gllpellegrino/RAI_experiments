# -*- coding: utf-8 -*-

__author__ = 'Gaetano "Gibbster" Pellegrino'


"""
Sinus evaluation utility.
It contains everything needed to evaluate RAI on the sinus wave test cases.
Each alternative technique must return a prediction for each value within the test flat file.
"""


import warnings as wr
import numpy as np
from math import sqrt
import matplotlib.pyplot as plt
import dot_utility as du
import rti_utility as ru
import rijnhaven_utility as su
import wind.meta as mt
from hmmlearn.hmm import GaussianHMM
# workaround to ignore the pandas.core.datetools deprecation warning
from statsmodels import ConvergenceWarning
wr.simplefilter(action='ignore', category=FutureWarning)
wr.simplefilter(action='ignore', category=ConvergenceWarning)
wr.simplefilter(action='ignore', category=DeprecationWarning)
wr.simplefilter(action='ignore', category=RuntimeWarning)
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


# -----------------------------------------------------------------------------------------------------------------


# persistence baseline, only requires the flat test file path.
def persistence(flat_path_ts, flat_out_path):
    with open(flat_out_path, "w") as oh:
        prd = 0.
        for vl in su.load_flat(flat_path_ts):
            oh.write(str(prd) + "\n")
            prd = vl


# hidden marov models prediction gatherer.
# based on Qin's code.
def hmm(flat_path_tr, flat_path_ts, flat_path_out):
    # assembling the training file as GaussianHMM expects it
    flat_tr = [vl for vl in su.load_flat(flat_path_tr)]
    flat_ts = [vl for vl in su.load_flat(flat_path_ts)]
    sw_tr, sw_ts = [], []
    n_tr, n_ts = mt.TRAINL - mt.WSIZE + 1, mt.TESTL - mt.WSIZE + 1
    for i in xrange(n_tr):
        sw_tr.append(flat_tr[i:i + mt.WSIZE])
    for i in xrange(n_ts):
        sw_ts.append(flat_ts[i:i + mt.WSIZE])
    sw_ts = np.array(sw_ts)
    sw_tr = np.array(sw_tr).flatten().reshape(n_tr * mt.WSIZE, 1)
    len_tr = [mt.WSIZE for _ in xrange(n_tr)]
    # training
    md = GaussianHMM(mt.STATES, covariance_type="diag", n_iter=1000).fit(sw_tr, len_tr)
    # testing
    with open(flat_path_out, "w") as oh:
        for i in xrange(mt.WSIZE):
            oh.write(str(0.) + "\n")
        for i in xrange(n_ts - 1):
            # probability of states in each time step
            prob = md.predict_proba(sw_ts[i, :].reshape(mt.WSIZE, 1))
            prob_next_state = np.dot(prob[-1, :], md.transmat_)
            # print prob_next_state
            prd = 0.
            for j in xrange(mt.STATES):
                prd += prob_next_state[j] * md.means_[j]
            oh.write(str(prd[0]) + "\n")


# rai and rti only require the flat test file path and a model dot file path.
# we can use the same method for both techniques because we
def rairti(dot_path, flat_path_ts, flat_path_out):
    md = du.load_md(dot_path)
    with open(flat_path_out, "w") as oh:
        first_w = True
        for window in ru.windows_getter(flat_path_ts, mt.WSIZE):
            sta = 0
            if first_w:
                first_w = False
                for vl in window:
                    oh.write(str(md[sta]["p"]) + "\n")
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
                oh.write(str(prd) + "\n")


# seasonal arma and arima predictions gatherer.
# based on Chad Fulton's post in here:
# https://github.com/statsmodels/statsmodels/issues/2577
# ---------------------------------------------------------
# it expects a path to the test flat file,
# i is a boolean flag to use or not the integration (arima does, arma does not)
def sarimax(flat_path_tr, flat_path_ts, i, flat_path_out):
    # setting the integration order
    d = 1 if i else 0
    # getting training and testing data
    tr = [vl for vl in su.load_flat(flat_path_tr)]
    ts = [vl for vl in su.load_flat(flat_path_ts)]
    # training
    md1 = SARIMAX(tr, order=(mt.WSIZE, d, 1), enforce_stationarity=False, enforce_invertibility=False)
    rs1 = md1.fit(disp=0)
    # testing
    md2 = SARIMAX(ts, order=(mt.WSIZE, d, 1), enforce_stationarity=False, enforce_invertibility=False)
    rs2 = md2.filter(rs1.params)
    # assembling the results
    with open(flat_path_out, "w") as oh:
        for i in xrange(len(ts)):
            oh.write(str(rs2.predict(i, i)[-1]) + "\n")


# utility to plot the predictions for a test case identifier [0 to 9 on sinus]
def plot(test_case):
    # ------------------------------------------------------------------------------
    rai_path = mt.EXPDIR + "/" + str(test_case) + "/rai.res"
    rtisy_path = mt.EXPDIR + "/" + str(test_case) + "/rtisy.res"
    rtitm_path = mt.EXPDIR + "/" + str(test_case) + "/rtitm.res"
    pers_path = mt.EXPDIR + "/" + str(test_case) + "/pers.res"
    arma_path = mt.EXPDIR + "/" + str(test_case) + "/arma.res"
    arima_path = mt.EXPDIR + "/" + str(test_case) + "/arima.res"
    hmm_path = mt.EXPDIR + "/" + str(test_case) + "/hmm.res"
    gold_path = mt.BASEDIR + "/" + str(test_case) + "/test.flat"
    # ------------------------------------------------------------------------------
    res = {}
    # gold
    gl = [vl for vl in su.load_flat(gold_path)]
    # persistence
    pr = [vl for vl in su.load_flat(pers_path)]
    res["Persistence"] = {"MAE": mae(pr, gl), "MAPE": mape(pr, gl), "RMSE": rmse(pr, gl)}
    # RAI
    ra = [vl for vl in su.load_flat(rai_path)]
    res["RAI"] = {"MAE": mae(ra, gl), "MAPE": mape(ra, gl), "RMSE": rmse(ra, gl)}
    # RTI+ symbols
    rs = [vl for vl in su.load_flat(rtisy_path)]
    res["RTI+ symbols"] = {"MAE": mae(rs, gl), "MAPE": mape(rs, gl), "RMSE": rmse(rs, gl)}
    # RTI+ time
    rt = [vl for vl in su.load_flat(rtitm_path)]
    res["RTI+ time"] = {"MAE": mae(rt, gl), "MAPE": mape(rt, gl), "RMSE": rmse(rt, gl)}
    # ARIMA
    ai = [vl for vl in su.load_flat(arima_path)]
    res["ARIMA"] = {"MAE": mae(ai, gl), "MAPE": mape(ai, gl), "RMSE": rmse(ai, gl)}
    # ARMA
    am = [vl for vl in su.load_flat(arma_path)]
    res["ARMA"] = {"MAE": mae(am, gl), "MAPE": mape(am, gl), "RMSE": rmse(am, gl)}
    # HMM
    hm = [vl for vl in su.load_flat(hmm_path)]
    res["HMM"] = {"MAE": mae(hm, gl), "MAPE": mape(hm, gl), "RMSE": rmse(hm, gl)}
    # ------------------------------------------------------------------------------
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
    plt.plot(ix, hm, label="HMM", color="orange")
    plt.grid(True)
    plt.legend()
    # plt.savefig("/home/nino/Scrivania/plot.png")
    plt.show()


# it calls all the evaluation routines, which will store the predictions in flat files
def store_predictions():
    # setting general parameters for all the utility moduli called in this script
    su.PRECISION = mt.PRECISION
    ru.PRECISION = mt.PRECISION
    ru.ABOUNDS = mt.ABOUNDS
    ru.ASIZE = mt.ASIZE
    ru.WSIZE = mt.WSIZE
    ru.TRAINL = mt.TRAINL
    # -----------------------------------------------------------------------------------
    for tc in mt.TCIDS:
        print "storing predictions for test case", tc
        # setting the paths
        flat_path_ts = mt.BASEDIR + "/" + str(tc) + "/test.flat"
        flat_path_tr = mt.BASEDIR + "/" + str(tc) + "/train.flat"
        rai_dot = mt.BASEDIR + "/" + str(tc) + "/rai.dot"
        rtisy_dot = mt.BASEDIR + "/" + str(tc) + "/rtisy.dot"
        rtitm_dot = mt.BASEDIR + "/" + str(tc) + "/rtitm.dot"
        # ----------------------------------------------
        rai_path = mt.EXPDIR + "/" + str(tc) + "/rai.res"
        rtisy_path = mt.EXPDIR + "/" + str(tc) + "/rtisy.res"
        rtitm_path = mt.EXPDIR + "/" + str(tc) + "/rtitm.res"
        pers_path = mt.EXPDIR + "/" + str(tc) + "/pers.res"
        arma_path = mt.EXPDIR + "/" + str(tc) + "/arma.res"
        arima_path = mt.EXPDIR + "/" + str(tc) + "/arima.res"
        hmm_path = mt.EXPDIR + "/" + str(tc) + "/hmm.res"
        # calling the right routines
        persistence(flat_path_ts, pers_path)
        rairti(rai_dot, flat_path_ts, rai_path)
        rairti(rtisy_dot, flat_path_ts, rtisy_path)
        rairti(rtitm_dot, flat_path_ts, rtitm_path)
        sarimax(flat_path_tr, flat_path_ts, False, arma_path)
        sarimax(flat_path_tr, flat_path_ts, True, arima_path)
        hmm(flat_path_tr, flat_path_ts, hmm_path)


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
        print "evaluating test case", tc
        # ------------------------------------------------------------------------------
        rai_path = mt.EXPDIR + "/" + str(tc) + "/rai.res"
        rtisy_path = mt.EXPDIR + "/" + str(tc) + "/rtisy.res"
        rtitm_path = mt.EXPDIR + "/" + str(tc) + "/rtitm.res"
        pers_path = mt.EXPDIR + "/" + str(tc) + "/pers.res"
        arma_path = mt.EXPDIR + "/" + str(tc) + "/arma.res"
        arima_path = mt.EXPDIR + "/" + str(tc) + "/arima.res"
        hmm_path = mt.EXPDIR + "/" + str(tc) + "/hmm.res"
        gold_path = mt.BASEDIR + "/" + str(tc) + "/test.flat"
        # ------------------------------------------------------------------------------
        res = {}
        # gold
        gl = [vl for vl in su.load_flat(gold_path)]
        # persistence
        pr = [vl for vl in su.load_flat(pers_path)]
        res["Persistence"] = {"MAE": mae(pr, gl), "MAPE": mape(pr, gl), "RMSE": rmse(pr, gl)}
        # RAI
        ra = [vl for vl in su.load_flat(rai_path)]
        res["RAI"] = {"MAE": mae(ra, gl), "MAPE": mape(ra, gl), "RMSE": rmse(ra, gl)}
        # RTI+ symbols
        rs = [vl for vl in su.load_flat(rtisy_path)]
        res["RTI+ symbols"] = {"MAE": mae(rs, gl), "MAPE": mape(rs, gl), "RMSE": rmse(rs, gl)}
        # RTI+ time
        rt = [vl for vl in su.load_flat(rtitm_path)]
        res["RTI+ time"] = {"MAE": mae(rt, gl), "MAPE": mape(rt, gl), "RMSE": rmse(rt, gl)}
        # ARIMA
        ai = [vl for vl in su.load_flat(arima_path)]
        res["ARIMA"] = {"MAE": mae(ai, gl), "MAPE": mape(ai, gl), "RMSE": rmse(ai, gl)}
        # ARMA
        am = [vl for vl in su.load_flat(arma_path)]
        res["ARMA"] = {"MAE": mae(am, gl), "MAPE": mape(am, gl), "RMSE": rmse(am, gl)}
        # HMM
        hm = [vl for vl in su.load_flat(hmm_path)]
        res["HMM"] = {"MAE": mae(hm, gl), "MAPE": mape(hm, gl), "RMSE": rmse(hm, gl)}
        # ------------------------------------------------------------------------------
        for tn in res:
            print "\n", tn
            for pm in res[tn]:
                if pm == "MAE":
                    print pm, res[tn][pm]
        print "\n"


def evaluate_single(test_case):
    # ------------------------------------------------------------------------------
    rai_path = mt.EXPDIR + "/" + str(test_case) + "/rai.res"
    rtisy_path = mt.EXPDIR + "/" + str(test_case) + "/rtisy.res"
    rtitm_path = mt.EXPDIR + "/" + str(test_case) + "/rtitm.res"
    pers_path = mt.EXPDIR + "/" + str(test_case) + "/pers.res"
    arma_path = mt.EXPDIR + "/" + str(test_case) + "/arma.res"
    arima_path = mt.EXPDIR + "/" + str(test_case) + "/arima.res"
    hmm_path = mt.EXPDIR + "/" + str(test_case) + "/hmm.res"
    gold_path = mt.BASEDIR + "/" + str(test_case) + "/test.flat"
    # ------------------------------------------------------------------------------
    res = {}
    # gold
    gl = [vl for vl in su.load_flat(gold_path)]
    # persistence
    pr = [vl for vl in su.load_flat(pers_path)]
    res["Persistence"] = {"MAE": mae(pr, gl), "MAPE": mape(pr, gl), "RMSE": rmse(pr, gl)}
    # RAI
    ra = [vl for vl in su.load_flat(rai_path)]
    res["RAI"] = {"MAE": mae(ra, gl), "MAPE": mape(ra, gl), "RMSE": rmse(ra, gl)}
    # RTI+ symbols
    rs = [vl for vl in su.load_flat(rtisy_path)]
    res["RTI+ symbols"] = {"MAE": mae(rs, gl), "MAPE": mape(rs, gl), "RMSE": rmse(rs, gl)}
    # RTI+ time
    rt = [vl for vl in su.load_flat(rtitm_path)]
    res["RTI+ time"] = {"MAE": mae(rt, gl), "MAPE": mape(rt, gl), "RMSE": rmse(rt, gl)}
    # ARIMA
    ai = [vl for vl in su.load_flat(arima_path)]
    res["ARIMA"] = {"MAE": mae(ai, gl), "MAPE": mape(ai, gl), "RMSE": rmse(ai, gl)}
    # ARMA
    am = [vl for vl in su.load_flat(arma_path)]
    res["ARMA"] = {"MAE": mae(am, gl), "MAPE": mape(am, gl), "RMSE": rmse(am, gl)}
    # HMM
    hm = [vl for vl in su.load_flat(hmm_path)]
    res["HMM"] = {"MAE": mae(hm, gl), "MAPE": mape(hm, gl), "RMSE": rmse(hm, gl)}
    # ------------------------------------------------------------------------------
    for tn in res:
        print "\n", tn
        for pm in res[tn]:
            if pm == "MAE":
                print pm, res[tn][pm]
    print "\n"


if __name__ == "__main__":
    f1 = "/home/nino/PycharmProjects/rai_experiments/sinus/data/0/test.flat"
    f2 = "/home/nino/PycharmProjects/rai_experiments/sinus/data/0/train.flat"
    # m = "/home/nino/PycharmProjects/rai_experiments/sinus/data/0/rai.dot"
    # vs1 = [v for v, _ in sarimax(f1, f2)]
    # print "LEN", len(vs1)
    # print "VALS", vs1
    # evaluate()
    # plot(0)
    # for v in hmm(f2, f1):
    #     print v
    # store_predictions()
    evaluate()
    # evaluate_single(0)