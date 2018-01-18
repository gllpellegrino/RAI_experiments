# -*- coding: utf-8 -*-

__author__ = 'Gaetano "Gibbster" Pellegrino'


"""
Sinus evaluation utility.
It contains everything needed to evaluate RAI on the sinus wave test cases.
Each alternative technique must return a prediction for each value within the test flat file.
"""


import setup as st
import rti_utility as ru
import dot_utility as du


# persistence baseline, only requires the flat test file path.
def persistence(test_flat):
    prd = 0.
    for vl in st.load_flat(test_flat):
        yield prd, vl
        prd = vl


# rai and rti only require the flat test file path and a model dot file path.
# we can use the same methon for both techniques because we
def rairti(dot_path, test_flat):
    #@todo nota che la wsize qua è 16 e RAI lo usiamo con prefix a 8
    md = du.load_md(dot_path)
    first_w = True
    for window in ru.windows_getter(test_flat):
        sta = 0
        if first_w:
            first_w = False
            for vl in window:
                yield md[sta]["p"], vl
                # looking for the next state
                for _, ds, lg, rg in md[sta]["t"]:
                    if lg < vl <= rg:
                        sta = ds
                        break
        else:
            prd = 0.
            for vl in window:
                prd = md[sta]["p"]
                # looking for the next state
                for _, ds, lg, rg in md[sta]["t"]:
                    if lg < vl <= rg:
                        sta = ds
                        break
            yield prd, window[-1]


if __name__ == "__main__":
    pass