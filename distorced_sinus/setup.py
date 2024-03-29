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

import distorced_sinus.meta as mt
import rai_utility as rai
import rti_utility as rti
import distorced_sinus.sinus_utility as su
from os import mkdir, walk, rmdir, remove
from os.path import exists, join


def clean():
    # cleans everything removing all data files
    for root, dirs, files in walk(mt.BASEDIR, topdown=False):
        for name in files:
            remove(join(root, name))
        for name in dirs:
            rmdir(join(root, name))
    # cleans everything removing all results files
    for root, dirs, files in walk(mt.EXPDIR, topdown=False):
        for name in files:
            remove(join(root, name))
        for name in dirs:
            rmdir(join(root, name))
    # removes the base directories
    if exists(mt.BASEDIR):
        rmdir(mt.BASEDIR)
    if exists(mt.EXPDIR):
        rmdir(mt.EXPDIR)


def setup():
    # for each test case:
    # 1) create the directories
    # 2) generate train and test flat waves
    # 3) generate train file for RAI
    # 4) generate train file for RTI+ with alphabet criterion
    # 5) generate train file for RTI+ with time criterion
    # ----------------------------------------------------------
    # setting general parameters for all the utility moduli called in this script
    su.PRECISION = mt.PRECISION
    rti.PRECISION = mt.PRECISION
    rti.ABOUNDS = mt.ABOUNDS
    rti.WSIZE = mt.WSIZE
    rti.TRAINL = mt.TRAINL
    rti.ASIZE = mt.ASIZE
    # creating the base directories
    if not exists(mt.BASEDIR):
        mkdir(mt.BASEDIR)
    if not exists(mt.EXPDIR):
        mkdir(mt.EXPDIR)
    # now we can start
    for tc in mt.TCIDS:
        print "setting up test case", tc
        # setting a specific seed for this test case (for the flat sequences generation)
        su.SEED += tc
        # setting the data directory for test case tc
        tcdir = mt.BASEDIR + "/" + str(tc)
        # creating the test case data directory
        if not exists(tcdir):
            mkdir(tcdir)
        # creating the test case experiments directory
        expdir = mt.EXPDIR + "/" + str(tc)
        if not exists(expdir):
            mkdir(expdir)
        # setting the training paths
        flat = tcdir + "/train.flat"
        raisw = tcdir + "/rai.sw"
        rtissw = tcdir + "/rtisy.sw"
        rtitsw = tcdir + "/rtitm.sw"
        # generating the training flat wave file
        su.export_flat(mt.TRAINL, flat)
        # generating the testing flat wave file
        su.export_flat(mt.TESTL, tcdir + "/test.flat")
        # generating training slided file for RAI
        rai.export_sw(flat, mt.WSIZE, raisw)
        # generating training slided file for RTI with alphabet
        rti.export_alpha_sw(flat, mt.WSIZE, rtissw)
        # generating training slided file for RTI with time
        rti.export_time_sw(flat, mt.WSIZE, rtitsw)


if __name__ == "__main__":
    clean()
    setup()
