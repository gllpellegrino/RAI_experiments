# -*- coding: utf-8 -*-


__author__ = 'Gaetano "Gibbster" Pellegrino'


"""
Utility to interface RTI+ with this experiment.
"""


import meta as mt
import setup as st
import re


RTI_STATE_RE = "^(-?\d+) prob: symbol=(( \d+)+)"
RTI_TRANS_RE = "^(-?\d+) (\d+) \[(\d+), (\d+)\]->(-?\d+)\\n$"


# utility to export a flat file to RAI sliding window training file
# by using an alphabet of 2 symbols (positive or negative)
def export_alpha_sw(inpath, wsize, oupath):
    with open(oupath, "w") as th:
        # writing the header
        th.write(str(mt.TRAINL - wsize + 1) + " 2")
        # now the content
        window = []
        for vl in st.load_flat(inpath):
            sy = "0" if vl < 0. else "1"
            if len(window) < wsize:
                window.append(sy)
            else:
                th.write("\n" + str(len(window)))
                for sv in window:
                    th.write(" " + sv + " 0")
                window = window[1:] + [sy]
        # handling last pending window
        th.write("\n" + str(len(window)))
        for sv in window:
            th.write(" " + sv + " 0")


# utility to export a flat file to RTI+ sliding window training file
# by using the time delay inferring mechanism of the algorithm
def export_time_sw(inpath, wsize, oupath):
    with open(oupath, "w") as th:
        # writing the header
        th.write(str(mt.TRAINL - wsize + 1) + " 1")
        # now the content
        window = []
        for vl in st.load_flat(inpath):
            timev = int(vl * pow(10, mt.PRECISION) + 1000)
            if len(window) < wsize:
                window.append(str(timev))
            else:
                th.write("\n" + str(len(window)))
                for sv in window:
                    th.write(" 0 " + sv)
                window = window[1:] + [str(timev)]
        # handling last pending window
        th.write("\n" + str(len(window)))
        for sv in window:
            th.write(" 0 " + sv)


# this method loads a model, inferred by RTI+ with alphabet, in memory
def load_alpha_md(path):
    rt = {}
    trp = re.compile(RTI_TRANS_RE)
    stp = re.compile(RTI_STATE_RE)
    with open(path, "r") as rh:
        for line in rh:
            md = stp.match(line)
            # state check
            if md is not None:
                sta = int(md.group(1))
                # we skip the sink state (id:-1)
                if sta >= 0:
                    rt[sta] = {"p": 0., "t": []}
            md = trp.match(line)
            if md is not None:
                sr = int(md.group(1))
                sy = md.group(2)
                ds = int(md.group(5))
                # we skip the sink state
                if ds not in rt and ds > 0:
                    rt[ds] = {"p": 0., "t": []}
                # and we skip transitions to the sink state
                if ds >= 0:
                    tr = (sr, ds, -float("inf"), 0.) if sy == "0" else (sr, ds, 0., float("inf"))
                    rt[sr]["t"].append(tr)
        # extend guards from -inf to inf
        for sta in rt:
            trs = sorted(rt[sta]["t"], key=lambda x: x[2])
            if trs:
                prrg = -float("inf")
                for i in xrange(len(trs)):
                    trs[i] = (trs[i][0], trs[i][1], prrg, trs[i][3])
                    prrg = trs[i][3]
                trs[-1] = (trs[-1][0], trs[-1][1], trs[-1][2], float("inf"))
                rt[sta]["t"] = trs
    return rt


# this method loads a model, inferred by RTI+ by using time, in memory
def load_time_md(path):
    rt = {}
    trp = re.compile(RTI_TRANS_RE)
    stp = re.compile(RTI_STATE_RE)
    with open(path, "r") as rh:
        for line in rh:
            md = stp.match(line)
            # state check
            if md is not None:
                sta = int(md.group(1))
                # we skip the sink state (id: -1)
                if sta >= 0:
                    rt[sta] = {"p": 0., "t": []}
            md = trp.match(line)
            if md is not None:
                sr = int(md.group(1))
                ds = int(md.group(5))
                lg = (float(md.group(3)) - 1000.) * pow(10, -mt.PRECISION)
                rg = (float(md.group(4)) - 1000.) * pow(10, -mt.PRECISION)
                if ds not in rt:
                    rt[ds] = {"p": 0., "t": []}
                # we skip transitions to the sink state (id: -1)
                if ds >= 0:
                    tr = (sr, ds, lg, rg)
                    rt[sr]["t"].append(tr)
        # extend guards from -inf to inf
        for sta in rt:
            trs = sorted(rt[sta]["t"], key=lambda x: x[2])
            if trs:
                prrg = -float("inf")
                for i in xrange(len(trs)):
                    trs[i] = (trs[i][0], trs[i][1], prrg, trs[i][3])
                    prrg = trs[i][3]
                trs[-1] = (trs[-1][0], trs[-1][1], trs[-1][2], float("inf"))
                rt[sta]["t"] = trs
    return rt


# sliding window iterator given a flat file
def windows_getter(path, wsize=None):
    if wsize is None:
        wsize = mt.WSIZE
    window = []
    for vl in st.load_flat(path):
        if len(window) < wsize:
            window.append(vl)
        else:
            yield window
            window = window[1:] + [vl]
    # handling last window
    yield window


# estimate state probabilities by using a flat file.
# it uses the mean value as a predictor in each state.
# important! it updates the model provided in input.
def restimate_md(md, path):
    # this dict contains the values collected in each state
    stvs = {sta: [] for sta in md}
    # now we start collecting those values
    for window in windows_getter(path):
        sta = 0
        for vl in window:
            cvl = 0.
            # move to the next state
            for _, ds, lg, rg in md[sta]["t"]:
                if lg < vl <= rg:
                    sta = ds
                    cvl = vl
                    break
        stvs[sta].append(cvl)
    # now we can reestimate
    for sta in md:
        md[sta]["p"] = sum(stvs[sta]) / float(len(stvs[sta])) if stvs[sta] else 0.
    # ready to return
    return md


if __name__ == "__main__":
    # m = load_time_md("/home/nino/PycharmProjects/rai_experiments/sinus/data/0/rtitm.rti")
    # print m
    # export_md(m, "/home/nino/LEMMA/state_merging_regressor/experiments/sinus/0/rtitm.dot")
    p = "/home/nino/PycharmProjects/rai_experiments/sinus/data/0/rtisy.dot"
    f = "/home/nino/PycharmProjects/rai_experiments/sinus/data/0/train.flat"
    # for v in windows_getter(p):
    #     print v
    import dot_utility as du
    m = du.load_md(p)
    print m
    m = restimate_md(m, f)
    print m
    du.export_md(m, "/home/nino/PycharmProjects/rai_experiments/sinus/data/0/canc.dot")