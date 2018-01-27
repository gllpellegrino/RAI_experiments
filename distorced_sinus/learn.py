# -*- coding: utf-8 -*-

__author__ = 'Gaetano "Gibbster" Pellegrino'

"""
Automata learning utility.
It may call RTI+ rather than RAI.
"""

import time
import pickle as pk
import distorced_sinus.meta as mt
import os
import rti_utility as rtu
import dot_utility as dtu
import sarimax_utility as sxu
import hmms_utility as hmu


# only cleans the files produced by learn()
def clean():
    for tc in mt.TCIDS:
        print "cleaning learning products for test case", tc
        # setting the base directory for test case tc
        tcdir = mt.BASEDIR + "/" + str(tc)
        # cleaning starts
        for item in os.listdir(tcdir):
            if item.endswith(".rti") or item.endswith(".dot") or item.endswith(".md") or item.endswith(".bin"):
                os.remove(os.path.join(tcdir, item))


# learns automata for all the test cases
def learn():
    # 1) learn model for RAI
    # 2) learn model for RTI+ with alphabet
    # 3) learn model for RTI+ with time
    # 4) learn ARMA model
    # 5) learn ARIMA model
    # 6) learn HMM model
    # ----------------------------------------------------------
    # setting the time infos
    times = {}
    # setting general parameters for all the utility moduli called in this script
    rtu.PRECISION = mt.PRECISION
    rtu.ABOUNDS = mt.ABOUNDS
    rtu.WSIZE = mt.WSIZE
    rtu.TRAINL = mt.TRAINL
    rtu.ASIZE = mt.ASIZE
    hmu.WSIZE, hmu.STATES = mt.WSIZE, mt.STATES
    sxu.AR = mt.WSIZE
    for tc in mt.TCIDS:
        print "learning automata for test case", tc
        print "--------------------------------------------"
        # defining the time structure
        tc_time = {}
        # setting the base directory for test case tc
        tcdir = mt.BASEDIR + "/" + str(tc)
        # first it learns RAI model
        raitr = tcdir + "/rai.sw"
        raimd = tcdir + "/rai.dot"
        cmd = mt.RAI_CMD.format(TRAIN=raitr, MODEL=raimd, ALPHABET_SIZE=mt.ASIZE, PREFIX_LENGTH=mt.WSIZE / 2)
        start_time = time.time()
        os.system(cmd)
        delta_time = time.time() - start_time
        tc_time["RAI"] = delta_time
        # second we learn RTI+ model with alphabet
        flatr = tcdir + "/train.flat"
        # -------------------------------------------
        rtitr = tcdir + "/rtisy.sw"
        rtiou = tcdir + "/rtisy.rti"
        rtimd = tcdir + "/rtisy.dot"
        cmd = mt.RTI_CMD.format(TRAIN=rtitr, MODEL=rtiou)
        start_time = time.time()
        os.system(cmd)
        delta_time = time.time() - start_time
        tc_time["RTISY"] = delta_time
        m = rtu.load_alpha_md(rtiou)
        m = rtu.restimate_md(m, flatr)
        dtu.export_md(m, rtimd)
        # third we learn RTI+ model with time
        rtitr = tcdir + "/rtitm.sw"
        rtiou = tcdir + "/rtitm.rti"
        rtimd = tcdir + "/rtitm.dot"
        cmd = mt.RTI_CMD.format(TRAIN=rtitr, MODEL=rtiou)
        start_time = time.time()
        os.system(cmd)
        delta_time = time.time() - start_time
        tc_time["RTITM"] = delta_time
        m = rtu.load_time_md(rtiou)
        m = rtu.restimate_md(m, flatr)
        dtu.export_md(m, rtimd)
        # fourth we learn ARMA model
        sxu.D = False
        arma_md = tcdir + "/arma.bin"
        start_time = time.time()
        sxu.train(flatr, arma_md)
        delta_time = time.time() - start_time
        tc_time["ARMA"] = delta_time
        # fifth, we learn ARIMA model
        sxu.D = True
        arima_md = tcdir + "/arima.bin"
        start_time = time.time()
        sxu.train(flatr, arima_md)
        delta_time = time.time() - start_time
        tc_time["ARIMA"] = delta_time
        # sixth we learn HMM model
        hmm_md = tcdir + "/hmm.bin"
        hmm_dot = tcdir + "/hmm.dot"
        start_time = time.time()
        md = hmu.train(flatr, hmm_md)
        delta_time = time.time() - start_time
        tc_time["HMM"] = delta_time
        hmu.export_md(md, hmm_dot)
        # updating the time structure
        times[tc] = tc_time
    pk.dump(times, open(mt.BASEDIR + "/times.bin", "wb"))
    return times


def show_times(tm_data):
    avgs = {}
    for tc in tm_data:
        print "test case: ", tc
        for tch in tm_data[tc]:
            if tch not in avgs:
                avgs[tch] = []
            avgs[tch].append(tm_data[tc][tch])
            print tch, tm_data[tc][tch], "seconds"
    print "averages:"
    for tch in avgs:
        print tch, sum(avgs[tch]) / float(len(avgs[tch])), "seconds"


if __name__ == "__main__":
    clean()
    print "--------------------------------------------"
    tm = learn()
    print "--------------------------------------------"
    show_times(tm)
