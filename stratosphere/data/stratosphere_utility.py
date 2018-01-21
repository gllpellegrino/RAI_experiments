# -*- coding: utf-8 -*-

__author__ = 'Gaetano "Gibbster" Pellegrino'

"""
Utility to work on Stratosphere Zeus data.
"""

import matplotlib.pyplot as plt

# path to the original zeus capture
PATH = "/home/nino/PycharmProjects/rai_experiments/stratosphere/data/zeus_capture.txt"


# extracts total packets given a destination ip
def extract_packets(ip):
    with open(PATH, "r") as ih:
        # skipping the header
        ih.readline()
        # starting the extraction
        for line in ih:
            fields = line.strip().split(",")
            # field 6 is the destination address
            dip = fields[6].strip()
            if dip == ip:
                # field 11 corresponds to the total packets number
                # field 12 corresponds to the total bytes number
                yield int(fields[12].strip())


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


# plots total packets given a destination ip
def plot_packets(ip):
    vy = [v for v in extract_packets(ip)]
    vx = [i for i in xrange(len(vy))]
    plt.title('Total Packets')
    plt.plot(vx, vy)
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    hs = ["95.211.9.145", "212.124.126.66", "194.28.87.64", "97.74.144.110", "62.149.140.209"]
    plot_packets(hs[0])
    # print flows(h)
