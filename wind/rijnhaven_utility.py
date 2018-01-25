# -*- coding: utf-8 -*-

__author__ = 'Gaetano "Gibbster" Pellegrino'


"""
Utility to plug Rijnhaven wind speed data into our experiments.
"""


import matplotlib.pyplot as plt
from math import isnan


# path to the original rijnhaven file
PATH = "/home/nino/Scaricati/Rijnhaven.csv"

# average wind speed field
FOI = 13


def extract_hourly_wspeed():
    with open(PATH, "r") as ih:
        hour = []
        for line in ih:
            fields = line.strip().split(",")
            # print fields
            if len(fields) >= FOI and fields[FOI] != "\"NAN\"" and not isnan(float(fields[FOI])):
                # each datum is about a average of 5 minutes, so we need 12 of them to cover 1 hour
                if len(hour) < 12:
                    hour.append(float(fields[FOI]))
                else:
                    yield sum(hour) / 12.
                    hour = []


# plots hourly wind speed
def plot_hourly_wspeed():
    vy = [v for v in extract_hourly_wspeed()]
    vx = [i for i in xrange(len(vy))]
    plt.title('Hourly Wind Speed (m/s)')
    plt.plot(vx, vy)
    plt.grid(True)
    plt.show()


# flat sequence loader from path
def load_flat(path):
    with open(path, "r") as fh:
        for line in fh:
            yield float(line.strip())


def export_flat(path, start=0, howmany=-1):
    # exports wind speed data to path
    with open(path, "w") as oh:
        ps = 0
        for vl in extract_hourly_wspeed():
            if start <= ps and (howmany < 0 or ps - start < howmany):
                oh.write(str(vl) + "\n")
            ps += 1


if __name__ == "__main__":
    plot_hourly_wspeed()