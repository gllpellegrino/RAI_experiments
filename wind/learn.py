# -*- coding: utf-8 -*-

__author__ = 'Gaetano "Gibbster" Pellegrino'

"""
Automata learning utility.
It may call RTI+ rather than RAI.
"""

import wind.meta as mt
import os
import rti_utility as rtu
import dot_utility as dtu


# only cleans the files produced by learn()
def clean():
    for tc in mt.TCIDS:
        print "cleaning learning products for test case", tc
        # setting the base directory for test case tc
        tcdir = mt.BASEDIR + "/" + str(tc)
        # cleaning starts
        for item in os.listdir(tcdir):
            if item.endswith(".rti") or item.endswith(".dot"):
                os.remove(os.path.join(tcdir, item))


# learns automata for all the test cases
def learn():
    # 1) learn model for RAI
    # 2) learn model for RTI+ with alphabet
    # 3) learn model for RTI+ with time
    # ----------------------------------------------------------
    # setting general parameters for all the utility moduli called in this script
    rtu.PRECISION = mt.PRECISION
    rtu.ABOUNDS = mt.ABOUNDS
    rtu.WSIZE = mt.WSIZE
    rtu.TRAINL = mt.TRAINL
    rtu.ASIZE = mt.ASIZE
    for tc in mt.TCIDS:
        print "learning automata for test case", tc
        # setting the base directory for test case tc
        tcdir = mt.BASEDIR + "/" + str(tc)
        # first it learns RAI model
        raitr = tcdir + "/rai.sw"
        raimd = tcdir + "/rai.dot"
        cmd = mt.RAI_CMD.format(TRAIN=raitr, MODEL=raimd, ALPHABET_SIZE=mt.ASIZE, PREFIX_LENGTH=mt.WSIZE / 2)
        os.system(cmd)
        # second we learn RTI+ model with alphabet
        flatr = tcdir + "/train.flat"
        # -------------------------------------------
        rtitr = tcdir + "/rtisy.sw"
        rtiou = tcdir + "/rtisy.rti"
        rtimd = tcdir + "/rtisy.dot"
        cmd = mt.RTI_CMD.format(TRAIN=rtitr, MODEL=rtiou)
        os.system(cmd)
        m = rtu.load_alpha_md(rtiou)
        m = rtu.restimate_md(m, flatr)
        dtu.export_md(m, rtimd)
        # third we learn RTI+ model with time
        rtitr = tcdir + "/rtitm.sw"
        rtiou = tcdir + "/rtitm.rti"
        rtimd = tcdir + "/rtitm.dot"
        cmd = mt.RTI_CMD.format(TRAIN=rtitr, MODEL=rtiou)
        os.system(cmd)
        m = rtu.load_time_md(rtiou)
        m = rtu.restimate_md(m, flatr)
        dtu.export_md(m, rtimd)


if __name__ == "__main__":
    clean()
    learn()
