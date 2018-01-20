# -*- coding: utf-8 -*-


__author__ = 'Gaetano "Gibbster" Pellegrino'


"""
Utility to create sinus waves.
"""


from math import sin, radians
from random import randint, seed, choice


# setting the random seed
SEED = 1984

# sinus quadrant identifiers
Q1 = 1
Q2 = 2
Q3 = 3
Q4 = 4

# sinus quadrants collection
QUADRANTS = [Q1, Q2, Q3, Q4]

# precision for floating point values
PRECISION = 3


# generate a random value within a sinus quadrant
def getv(q):
    if q not in QUADRANTS:
        raise ValueError("invalid quadrant")
    if q == Q1:
        d = randint(0, 90)
        return sin(radians(d))
    if q == Q2:
        # here is the difference !!
        d = randint(90, 135)
        return sin(radians(d))
    if q == Q3:
        d = randint(135, 270)
        return sin(radians(d))
    # q == Q4
    d = randint(270, 360)
    return sin(radians(d))


# generate a sinus wave of length n
def getw(n=1000, startq=None):
    # setting the seed
    seed(SEED)
    # setting the starting quadrant
    q = startq if startq in QUADRANTS else choice(QUADRANTS)
    # generating the whave
    for _ in xrange(n):
        yield getv(q)
        q = (q % len(QUADRANTS)) + 1


# flat sequence loader from path
def load_flat(path):
    with open(path, "r") as fh:
        for line in fh:
            yield float(line.strip())


def export_flat(n, path):
    # export a sinus wave (randomly initialized) of n elements to path
    with open(path, "w") as oh:
        for v in getw(n):
            oh.write(str(round(v, PRECISION)) + "\n")


if __name__ == "__main__":
    # for aq in xrange(20):
    #     # print (aq % 4) + 1
    #     print getv((aq % 4) + 1)
    for vl in getw(30, Q1):
        print vl
