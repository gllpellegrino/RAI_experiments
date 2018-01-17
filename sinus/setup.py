# -*- coding: utf-8 -*-

__author__ = 'Gaetano "Gibbster" Pellegrino'


"""
Test case setup.
It creates 10 training sinus series of 1000 values each, 
and 10 testing sinus series of 500 values each.
It generates a folder for each case (0 to 9).
The file format for the series consists of a value for each row in a text file with .flat extension
(train.flat, test.flat).
"""

import meta as mt
import sinus as sn
import rai_utility as rai
import rti_utility as rti
from os import mkdir, walk, rmdir, remove
from os.path import exists, join


# flat sequence loader from path
def load_flat(path):
    with open(path, "r") as fh:
        for line in fh:
            yield float(line.strip())


def export_flat(n, path):
    # export a sinus wave (randomly initialized) of n elements to path
    with open(path, "w") as oh:
        for v in sn.getw(n):
            oh.write(str(round(v, mt.PRECISION)) + "\n")


def clean():
    # cleans everything removing all files
    for root, dirs, files in walk(mt.BASEDIR, topdown=False):
        for name in files:
            remove(join(root, name))
        for name in dirs:
            rmdir(join(root, name))


def setup():
    # for each test case:
    # 1) create the directory
    # 2) generate train and test flat waves
    # 3) generate train file for RAI
    # 4) generate train file for RTI+ with alphabet criterion
    # 5) generate train file for RTI+ with time criterion
    for tc in mt.TCIDS:
        tcdir = mt.BASEDIR + "/" + str(tc)
        # creating the test case directory
        if not exists(tcdir):
            mkdir(tcdir)
        # setting the training paths
        flat = tcdir + "/train.flat"
        raisw = tcdir + "/rai.sw"
        rtissw = tcdir + "/rtisy.sw"
        rtitsw = tcdir + "/rtitm.sw"
        # generating the training flat wave file
        export_flat(mt.TRAINL, flat)
        # generating the testing flat wave file
        export_flat(mt.TESTL, tcdir + "/test.flat")
        # generating training slided file for RAI
        rai.export_sw(flat, mt.WSIZE, raisw)
        # generating training slided file for RTI with alphabet
        rti.export_alpha_sw(flat, mt.WSIZE, rtissw)
        # generating training slided file for RTI with time
        rti.export_time_sw(flat, mt.WSIZE, rtitsw)


if __name__ == "__main__":
    clean()
    setup()