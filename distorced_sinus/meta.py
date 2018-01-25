# -*- coding: utf-8 -*-

__author__ = 'Gaetano "Gibbster" Pellegrino'


"""
Meta-informations about the sinus experiment.
"""

# directory where all the test cases are stored
BASEDIR = "/home/nino/PycharmProjects/rai_experiments/distorced_sinus/data"

# directory where all the results of the experiments are stored
EXPDIR = "/home/nino/PycharmProjects/rai_experiments/distorced_sinus/experiments"

# length of the training flat waves
TRAINL = 1000

# length of the testing flat waves
TESTL = 250

# precision of sinus values (used in setup.py)
PRECISION = 3

# number of test cases
TESTCASES = 10

# test case ids
TCIDS = [tc for tc in xrange(TESTCASES)]

# window size for generating the slided files (used in setup.py and learn.py)
WSIZE = 16

# sinus wave period (used in evaluate.py)
PERIOD = 4

# alphabet size (used by learn.py)
ASIZE = 2

# symbol bounds
ABOUNDS = {"0": (-float("inf"), .0), "1": (.0, float("inf"))}

# RTI+ bash command (used in learn.py)
RTI_CMD = "/home/nino/bin/RTI/build/rti 1 0.05 {TRAIN} > {MODEL}"

# RAI bash command (used in learn.py)
RAI_CMD = "/usr/lib/jvm/java-1.8.0-openjdk-amd64/bin/java " \
          "-javaagent:/home/nino/bin/idea-IC-173.4127.27/lib/idea_rt.jar=44277:" \
          "/home/nino/bin/idea-IC-173.4127.27/bin " \
          "-Dfile.encoding=UTF-8 -classpath " \
          "/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/charsets.jar:" \
          "/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/cldrdata.jar:" \
          "/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/dnsns.jar:" \
          "/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/icedtea-sound.jar:" \
          "/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/jaccess.jar:" \
          "/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/java-atk-wrapper.jar:" \
          "/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/localedata.jar:" \
          "/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/nashorn.jar:" \
          "/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/sunec.jar:" \
          "/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/sunjce_provider.jar:" \
          "/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/sunpkcs11.jar:" \
          "/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/ext/zipfs.jar:" \
          "/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/jce.jar:" \
          "/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/jsse.jar:" \
          "/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/management-agent.jar:" \
          "/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/resources.jar:" \
          "/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre/lib/rt.jar:" \
          "/home/nino/LEMMA/state_merging_regressor/out/production/state_merging_regressor:" \
          "/home/nino/LEMMA/state_merging_regressor/lib/guava-18.0.jar:" \
          "/home/nino/LEMMA/state_merging_regressor/lib/commons-math3-3.6.jar " \
          "trans.launchers.Sinus {TRAIN} {MODEL} {ALPHABET_SIZE} {PREFIX_LENGTH}"

