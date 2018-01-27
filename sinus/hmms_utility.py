# -*- coding: utf-8 -*-

__author__ = 'Gaetano "Gibbster" Pellegrino'

"""
Utility to train and test HMMs.
"""

import pickle as pk
import warnings as wr
import numpy as np
from hmmlearn.hmm import GaussianHMM
from statsmodels import ConvergenceWarning

wr.simplefilter(action='ignore', category=ConvergenceWarning)
wr.simplefilter(action='ignore', category=DeprecationWarning)
wr.simplefilter(action='ignore', category=RuntimeWarning)


# window size to learn and test models
WSIZE = 16
# number of states to use in HMMs inferred models
STATES = 10

np.random.seed(1984)


# flat sequence loader from path
def load_flat(path):
    with open(path, "r") as fh:
        for line in fh:
            yield float(line.strip())


# flat_path_tr is the path to a flat train sequence
# md_path_out is the file path where the model will get stored permanently
def train(flat_path_tr, md_path):
    tr = [vl for vl in load_flat(flat_path_tr)]
    n_tr, sw_tr = len(tr) - WSIZE + 1, []
    for i in xrange(n_tr):
        sw_tr.append(tr[i:i + WSIZE])
    sw_tr = np.array(sw_tr).flatten().reshape(n_tr * WSIZE, 1)
    len_tr = [WSIZE for _ in xrange(n_tr)]
    md = GaussianHMM(STATES, covariance_type="diag", n_iter=1000).fit(sw_tr, len_tr)
    pk.dump(md, open(md_path, "wb"))
    return md


# md_path_out is the file path where the model is stored permanently (see train())
# flat_path_ts is the path to a testing flat sequence
# flat_path_out is a path where the results of the predictions will be stored as a flat sequence
def evaluate(md_path, flat_path_ts, flat_path_out):
    md = pk.load(open(md_path, "rb"))
    ts = [vl for vl in load_flat(flat_path_ts)]
    n_ts, sw_ts = len(ts) - WSIZE + 1, []
    for i in xrange(n_ts):
        sw_ts.append(ts[i:i + WSIZE])
    sw_ts = np.array(sw_ts)
    with open(flat_path_out, "w") as oh:
        for i in xrange(WSIZE):
            oh.write(str(0.) + "\n")
        for i in xrange(n_ts - 1):
            # probability of states in each time step
            prob = md.predict_proba(sw_ts[i, :].reshape(WSIZE, 1))
            prob_next_state = np.dot(prob[-1, :], md.transmat_)
            # print prob_next_state
            prd = 0.
            for j in xrange(STATES):
                prd += prob_next_state[j] * md.means_[j]
            oh.write(str(prd[0]) + "\n")


# exports a model learned with GaussianHHM of hmmlearn library
def export_md(hmm, path, ss=.0, tr=.2):
    with open(path, "w") as eh:
        # getting the data
        trans = hmm.transmat_
        init = hmm.startprob_
        means = hmm.means_
        # priting them in dot format
        eh.write("digraph a {")
        for s0 in xrange(len(means)):
            ri = round(init[s0], 3)
            if ri > ss:
                rm = round(means[s0][0], 3)
                eh.write("\n" + str(s0) + " [shape=circle, label=\"" + str(s0) + "\\nI=" + str(ri) + "\\nP=" + str(rm) + "\"];")
                for s1 in xrange(len(means)):
                    tp = round(trans[s0][s1], 3)
                    if tp > tr:
                        eh.write("\n\t" + str(s0) + " -> " + str(s1) + " [label=\"" + str(tp) + "\"];")
        eh.write("\n}")


if __name__ == "__main__":
    t1 = "/home/nino/PycharmProjects/rai_experiments/sinus/data16/0/train.flat"
    t2 = "/home/nino/PycharmProjects/rai_experiments/sinus/data16/0/test.flat"
    t3 = "/home/nino/PycharmProjects/rai_experiments/sinus/canc.flat"
    t4 = "/home/nino/PycharmProjects/rai_experiments/sinus/data16/0/hmm.bin"
    t5 = "/home/nino/PycharmProjects/rai_experiments/sinus/data16/0/hmm.dot"
    # m = train(t1, t4)
    m = pk.load(open(t4, "rb"))
    # evaluate(t4, t2, t3)
    # export_md(m, t5)
    print m

