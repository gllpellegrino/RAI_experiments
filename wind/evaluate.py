# -*- coding: utf-8 -*-

__author__ = 'Gaetano "Gibbster" Pellegrino'


"""
Sinus evaluation utility.
It contains everything needed to evaluate RAI on the sinus wave test cases.
Each alternative technique must return a prediction for each value within the test flat file.
"""


import matplotlib.pyplot as plt
import dot_utility as du
import rti_utility as ru
import wind.meta as mt
import hmms_utility as hmu
import sarimax_utility as sxu
import pickle as pk
from math import sqrt


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


# flat sequence loader from path
def load_flat(path):
    with open(path, "r") as fh:
        for line in fh:
            yield float(line.strip())


# -----------------------------------------------------------------------------------------------------------------


# persistence baseline, only requires the flat test file path.
def persistence(flat_path_ts, flat_out_path):
    with open(flat_out_path, "w") as oh:
        prd = 0.
        for vl in load_flat(flat_path_ts):
            oh.write(str(prd) + "\n")
            prd = vl


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
    # gold
    gl = [vl for vl in load_flat(gold_path)]
    # persistence
    pr = [vl for vl in load_flat(pers_path)]
    # RAI
    ra = [vl for vl in load_flat(rai_path)]
    # RTI+ symbols
    rs = [vl for vl in load_flat(rtisy_path)]
    # RTI+ time
    rt = [vl for vl in load_flat(rtitm_path)]
    # ARIMA
    ai = [vl for vl in load_flat(arima_path)]
    # ARMA
    am = [vl for vl in load_flat(arma_path)]
    # HMM
    hm = [vl for vl in load_flat(hmm_path)]
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
        rai_dot = mt.BASEDIR + "/" + str(tc) + "/rai.dot"
        rtisy_dot = mt.BASEDIR + "/" + str(tc) + "/rtisy.dot"
        rtitm_dot = mt.BASEDIR + "/" + str(tc) + "/rtitm.dot"
        arm_md = mt.BASEDIR + "/" + str(tc) + "/arma.bin"
        ari_md = mt.BASEDIR + "/" + str(tc) + "/arima.bin"
        hmm_md = mt.BASEDIR + "/" + str(tc) + "/hmm.bin"
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
        sxu.evaluate(arm_md, flat_path_ts, arma_path)
        sxu.evaluate(ari_md, flat_path_ts, arima_path)
        hmu.evaluate(hmm_md, flat_path_ts, hmm_path)


def evaluate():
    res = {}
    res_path = mt.EXPDIR + "/results.bin"
    # setting general parameters for all the utility moduli called in this script
    ru.PRECISION = mt.PRECISION
    ru.ABOUNDS = mt.ABOUNDS
    ru.ASIZE = mt.ASIZE
    ru.WSIZE = mt.WSIZE
    ru.TRAINL = mt.TRAINL
    # -----------------------------------------------------------------------------------
    for tc in mt.TCIDS:
        print "evaluating test case", tc
        res[tc] = evaluate_single(tc)
    # ------------------------------------------------------------------------------
    # dumping
    pk.dump(res, open(res_path, "wb"))


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
    gl = [vl for vl in load_flat(gold_path)]
    # persistence
    pr = [vl for vl in load_flat(pers_path)]
    res["Persistence"] = {"MAE": mae(pr, gl), "MAPE": mape(pr, gl), "RMSE": rmse(pr, gl)}
    # RAI
    ra = [vl for vl in load_flat(rai_path)]
    res["RAI"] = {"MAE": mae(ra, gl), "MAPE": mape(ra, gl), "RMSE": rmse(ra, gl)}
    # RTI+ symbols
    rs = [vl for vl in load_flat(rtisy_path)]
    res["RTI+ symbols"] = {"MAE": mae(rs, gl), "MAPE": mape(rs, gl), "RMSE": rmse(rs, gl)}
    # RTI+ time
    rt = [vl for vl in load_flat(rtitm_path)]
    res["RTI+ time"] = {"MAE": mae(rt, gl), "MAPE": mape(rt, gl), "RMSE": rmse(rt, gl)}
    # ARIMA
    ai = [vl for vl in load_flat(arima_path)]
    res["ARIMA"] = {"MAE": mae(ai, gl), "MAPE": mape(ai, gl), "RMSE": rmse(ai, gl)}
    # ARMA
    am = [vl for vl in load_flat(arma_path)]
    res["ARMA"] = {"MAE": mae(am, gl), "MAPE": mape(am, gl), "RMSE": rmse(am, gl)}
    # HMM
    hm = [vl for vl in load_flat(hmm_path)]
    res["HMM"] = {"MAE": mae(hm, gl), "MAPE": mape(hm, gl), "RMSE": rmse(hm, gl)}
    # ------------------------------------------------------------------------------
    for tn in res:
        print "\n", tn
        for pm in res[tn]:
            if pm == "MAE":
                print pm, res[tn][pm]
    print "\n"
    return res


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
    store_predictions()
    evaluate()
    # evaluate_single(0)