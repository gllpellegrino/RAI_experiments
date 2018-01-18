# -*- coding: utf-8 -*-


__author__ = 'Gaetano "Gibbster" Pellegrino'


"""
Uitility to interface RAI with this experiment.
"""


import sinus.sinus_utility as su


# utility to export a flat file to RAI sliding window training file
def export_sw(inpath, wsize, oupath):
    with open(oupath, "w") as th:
        window = []
        for vl in su.load_flat(inpath):
            if len(window) < wsize:
                window.append(str(vl))
            else:
                th.write(" ".join(window) + "\n")
                window = window[1:] + [str(vl)]
        th.write(" ".join(window))


if __name__ == "__main__":
    export_sw("/home/nino/LEMMA/state_merging_regressor/experiments/sinus/0/test.flat",
              4,
              "/home/nino/LEMMA/state_merging_regressor/experiments/sinus/0/test.sw")
