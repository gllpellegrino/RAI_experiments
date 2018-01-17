# -*- coding: utf-8 -*-

__author__ = 'Gaetano "Gibbster" Pellegrino'


"""
Meta-informations about the sinus experiment.
"""

# directory where all the test cases are stored
BASEDIR = "/home/nino/PycharmProjects/rai_experiments/sinus/data/"

# length of the training flat waves
TRAINL = 1000

# length of the testing flat waves
TESTL = 100

# precision of sinus values (used in setup.py)
PRECISION = 3

# number of test cases
TESTCASES = 10

# test case ids
TCIDS = [tc for tc in xrange(TESTCASES)]

# window size for generating the slided files
WSIZE = 16

