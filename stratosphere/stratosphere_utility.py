# -*- coding: utf-8 -*-

__author__ = 'Gaetano "Gibbster" Pellegrino'

"""
Utility to work on Stratosphere Zeus data.
"""


import matplotlib.pyplot as plt
from datetime import datetime as dtm


# path to the original zeus capture
PATH = "/home/nino/PycharmProjects/rai_experiments/stratosphere/zeus_capture.txt"


# extracts the delay between consecutive packets (in seconds)
def extract_delays(ip):
    with open(PATH, "r") as ih:
        # skipping the header
        ih.readline()
        # starting the extraction
        first, t0, ps = True, 0, 0
        for line in ih:
            fields = line.strip().split(",")
            # field 6 is the destination address
            dip = fields[6].strip()
            # print ps, start, howmany
            if dip == ip:
                # field 0 corresponds to the date of arrival
                # es: 1970/01/01 01:00:00.000000
                t = int(dtm.strptime(fields[0].strip(), "%Y/%m/%d %H:%M:%S.%f").strftime('%s'))
                if first:
                    first = False
                    t0 = t
                else:
                    yield t - t0
                    t0 = t
            ps += 1


# number of flows given a destination ip
def flows(ip):
    count = 0
    with open(PATH, "r") as ih:
        # skipping the header
        ih.readline()
        # starting the extraction
        for line in ih:
            fields = line.strip().split(",")
            # field 6 is the destination address
            dip = fields[6].strip()
            if dip == ip:
                count += 1
    return count


# plots time delays given a destination ip
def plot_delays(ip):
    vy = [v for v in extract_delays(ip)]
    vx = [i for i in xrange(len(vy))]
    plt.title('Time Delays (seconds)')
    plt.plot(vx, vy)
    plt.grid(True)
    plt.show()


# flat sequence loader from path
def load_flat(path):
    with open(path, "r") as fh:
        for line in fh:
            yield float(line.strip())


def export_flat(ip, path, start=0, howmany=-1):
    # export a sinus wave (randomly initialized) of n elements to path
    with open(path, "w") as oh:
        ps = 0
        for vl in extract_delays(ip):
            if start <= ps and (howmany < 0 or ps - start < howmany):
                oh.write(str(vl) + "\n")
            ps += 1


if __name__ == "__main__":
    hs = ["95.211.9.145", "212.124.126.66", "194.28.87.64", "97.74.144.110", "62.149.140.209"]
    ah = 0
    # plot_packets(hs[ah])
    # print flows(hs[ah])
    # i = 0
    # for v in extract_delays(hs[ah]):
    #     print i, v
    #     i += 1
    # print i
    plot_delays(hs[2])
    # export_flat("/home/nino/PycharmProjects/rai_experiments/stratosphere/data/canc.flat", hs[ah], 10, 1000)