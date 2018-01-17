# -*- coding: utf-8 -*-

__author__ = 'Gaetano "Gibbster" Pellegrino'


"""
Utility to manage dot file loading and exporting.
"""

import re


STATE_RE = r'(-?\d+) \[shape=circle, label=\"(-?\d+)\\n(\S+)\"\];'
TRANS_RE = r'\t(-?\d+)->(-?\d+) \[ label=\"\](\S+), (\S+)(\]|\[)\"\];'


# loader of automata stored in dot format
def load_md(path):
    rt = {}
    trp = re.compile(TRANS_RE)
    stp = re.compile(STATE_RE)
    with open(path, "r") as rh:
        for line in rh:
            md = stp.match(line)
            # state check
            if md is not None:
                sta = int(md.group(1))
                pr = float(md.group(3))
                if sta in rt:
                    rt[sta]["p"] = pr
                else:
                    rt[sta] = {"p": pr, "t": []}
            md = trp.match(line)
            if md is not None:
                sr = int(md.group(1))
                ds = int(md.group(2))
                lg = -float("inf") if "Infinity" in md.group(3) else float(md.group(3))
                rg = float("inf") if "Infinity" in md.group(4) else float(md.group(4))
                print ">", line, lg, rg
                if ds not in rt:
                    rt[ds] = {"p": 0., "t": []}
                # we skip transitions to the sink state (id: -1)
                if ds >= 0:
                    tr = (sr, ds, lg, rg)
                    rt[sr]["t"].append(tr)
    return rt


# export a model loaded with load_alpha_md() or load_time_md() into .dot format
def export_md(rt, path):
    with open(path, "w") as eh:
        eh.write("digraph a {")
        for sta in rt:
            # we skip the sink
            ln = "\n" + str(sta) + " [shape=circle, label=\"" + str(sta) + "\\n" + str(rt[sta]["p"]) + "\"];"
            eh.write(ln)
            for _, ds, lg, rg in rt[sta]["t"]:
                # we skip transition to the sink
                fl = "]" + str(lg) if lg != -float("inf") else "]-Infinity"
                fr = str(rg) + "]" if rg != float("inf") else "Infinity["
                ln = "\n\t" + str(sta) + "->" + str(ds) + " [ label=\"" + fl + ", " + fr + "\"];"
                eh.write(ln)
        eh.write("\n}")


if __name__ == "__main__":
    m = load_md("/home/nino/PycharmProjects/rai_experiments/sinus/data/0/rtitm.dot")
    print m