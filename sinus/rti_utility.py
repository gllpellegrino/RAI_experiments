# -*- coding: utf-8 -*-


__author__ = 'Gaetano "Gibbster" Pellegrino'


"""
Utility to interface RTI+ with this experiment.
"""


import meta as mt
import setup as st
import re


STATE_REGEX = "^(\d+) prob: symbol=(( \d+)+)"
TRANSITION_REGEX = "^(\d+) (\d+) \[(\d+), (\d+)\]->(-?\d+)\\n$"


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
    trp = re.compile(TRANSITION_REGEX)
    stp = re.compile(STATE_REGEX)
    with open(path, "r") as rh:
        for line in rh:
            m = stp.match(line)
            # state check
            if m is not None:
                sta = int(m.group(1))
                rt[sta] = {"p": 0., "t": []}
            m = trp.match(line)
            if m is not None:
                sr = int(m.group(1))
                sy = m.group(2)
                ds = int(m.group(5))
                # we skip the sink state
                if ds not in rt and ds > 0:
                    rt[ds] = {"p": 0., "t": []}
                # and we skip transitions to the sink state
                if ds > 0:
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
    trp = re.compile(TRANSITION_REGEX)
    stp = re.compile(STATE_REGEX)
    with open(path, "r") as rh:
        for line in rh:
            m = stp.match(line)
            # state check
            if m is not None:
                sta = int(m.group(1))
                rt[sta] = {"p": 0., "t": []}
            m = trp.match(line)
            if m is not None:
                sr = int(m.group(1))
                ds = int(m.group(5))
                lg = (float(m.group(3)) - 1000.) * pow(10, -mt.PRECISION)
                rg = (float(m.group(4)) - 1000.) * pow(10, -mt.PRECISION)
                if ds not in rt:
                    rt[ds] = {"p": 0., "t": []}
                # we skip transitions to the sink state (id: -1)
                if ds > 0:
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


# export a model loaded with load_alpha_md() or load_time_md() into .dot format
def export_md(rt, path):
    with open(path, "w") as eh:
        eh.write("digraph a {")
        for sta in rt:
            # we skip the sink
            ln = "\n" + str(sta) + " [shape=circle, label=\"" + str(sta) + "\\n" + str(rt[sta]["p"]) + "\"];"
            eh.write(ln)
            for _, ds, lg, rg in rt[sta]["t"]:
                # we skip transition to the sink
                fl = "]" + str(lg) if lg != -float("inf") else "]-Infinity"
                fr = str(rg) + "]" if rg != float("inf") else "Infinity["
                ln = "\n\t" + str(sta) + "->" + str(ds) + " [ label=\"" + fl + ", " + fr + "\"];"
                eh.write(ln)
        eh.write("\n}")


if __name__ == "__main__":
    m = load_time_md("/home/nino/LEMMA/state_merging_regressor/experiments/sinus/0/model.rtitm")
    export_md(m, "/home/nino/LEMMA/state_merging_regressor/experiments/sinus/0/rtitm.dot")
    print m