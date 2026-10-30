"""Every docplot helper on fake data, one panel each. Copy the panel closest to what you need.

    python gallery.py [out.png]
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import docplot as dp

rng = np.random.default_rng(3)
fig, axs = dp.figure(16, ncols=4)
ax = iter(axs)

# (a) noisy training metric, two runs, an lr change and a warmup phase
a = next(ax)
s = np.arange(300)
for i, (name, top) in enumerate([("DPPO", 0.72), ("GRPO", 0.64)]):
    dp.trend(a, s, top - 0.4 * np.exp(-s / 70) + rng.normal(0, 0.035, len(s)), label=name, i=i, window=15)
dp.span(a, 0, 20, "warmup")
dp.step(a, 180, "lr 3e-5")
dp.panel(a, "a", "Train reward", ylabel="Mean reward", xlabel="RL step")
dp.legend(a, loc="lower right")

# (b) evals per checkpoint against base +- eval noise, values at the line ends
b = next(ax)
s = np.arange(0, 126, 10)
base = 82.0
dp.band(b, [0, 125], [base - 2.5] * 2, [base + 2.5] * 2, color=dp.GREY, alpha=0.18)
dp.ref(b, base, label="base ± noise")
l1 = dp.line(b, s, base + 9 * (1 - np.exp(-s / 40)) + rng.normal(0, 0.8, len(s)), label="aime26")
l2 = dp.line(b, s, base - 6 + 7 * (1 - np.exp(-s / 50)) + rng.normal(0, 0.8, len(s)), label="hmmt26", i=1)
dp.end_label(b, l1, fmt="{:.0f}")
dp.end_label(b, l2, fmt="{:.0f}")
dp.panel(b, "b", "Evals", ylabel="avg @ 4 (%)", xlabel="RL step")
dp.legend_top(b)

# (c) one run against the spread of the others
c = next(ax)
s = np.arange(200)
for k in range(7):
    dp.context(c, s, dp.smooth(0.5 + 0.15 * (1 - np.exp(-s / 60)) + rng.normal(0, 0.03, len(s)), 10),
               label="other seeds" if k == 0 else None)
best = dp.smooth(0.5 + 0.28 * (1 - np.exp(-s / 50)) + rng.normal(0, 0.03, len(s)), 10)
dp.line(c, s, best, label="seed 4")
dp.note(c, 120, best[120], "seed 4 keeps climbing", dx=6, dy=-14)
dp.panel(c, "c", "Seeds", ylabel="Held-out acc", xlabel="RL step")
dp.legend(c, loc="lower right")

# (d) one number per benchmark, one highlighted
d = next(ax)
dp.bars(d, ["aime26", "hmmt26", "held out", "amc", "math500"], [91, 74, 68, 88, 96], horizontal=True,
        highlight="held out")
dp.panel(d, "d", "Pass @ 1 after RL", xlabel="%")

# (e) a few configs across benchmarks
e = next(ax)
dp.grouped_bars(e, ["aime26", "hmmt26", "held out"],
                {"base": [82, 68, 61], "RL": [90, 73, 64], "RL + critic": [93, 77, 69]}, values=True)
e.set_ylim(40, 108)
dp.panel(e, "e", "Configs", ylabel="avg @ 4 (%)")
dp.legend(e, loc="upper right", ncol=3)

# (f) before -> after for many items
f = next(ax)
names = ["geometry", "algebra", "number th.", "combin.", "prob.", "calculus", "inequal."]
before = np.array([52, 71, 58, 44, 63, 80, 39])
after = before + np.array([14, 3, 9, 12, -2, 1, 16])
order = np.argsort(after - before)[::-1]
dp.dumbbell(f, [names[k] for k in order], before[order], after[order], labels=("base", "step 125"))
dp.panel(f, "f", "Per topic", xlabel="Pass rate (%)")

# (g) few items, two moments, one highlighted
g = next(ax)
dp.slope(g, [61, 70, 55, 48, 66], [74, 72, 57, 63, 65], ["hard", "medium", "easy", "long", "short"],
         labels=("base", "RL"), highlight=["hard", "long"])
dp.panel(g, "g", "Cohorts")

# (h) composition over steps
h = next(ax)
s = np.arange(0, 301, 10)
right = 40 + 35 * (1 - np.exp(-s / 90))
trunc = 20 * np.exp(-s / 60) + 2
dp.stacked_area(h, s, {"correct": right, "wrong": 100 - right - trunc, "truncated": trunc}, normalize=True)
dp.panel(h, "h", "Outcome mix", ylabel="Share of rollouts (%)", xlabel="RL step")

# (i) composition per checkpoint
i_ = next(ax)
dp.stacked_bars(i_, ["0", "50", "100", "150", "200"],
                {"correct": [410, 520, 600, 640, 660], "wrong": [480, 400, 340, 320, 310],
                 "truncated": [134, 104, 84, 64, 54]},
                normalize=True, values=True)
dp.panel(i_, "i", "By checkpoint", ylabel="Share (%)", xlabel="RL step")

# (j) per-problem relation, two groups, y = x
j = next(ax)
for k, name in enumerate(["short", "long"]):
    xb = rng.uniform(0, 100, 80)
    dp.scatter(j, xb, np.clip(xb + rng.normal(6 + 8 * k, 10, 80), 0, 100), label=name, i=k)
j.set_xlim(0, 100)
j.set_ylim(0, 100)
dp.diag(j, "no change")
dp.panel(j, "j", "Per problem", ylabel="Pass rate after (%)", xlabel="Pass rate before (%)")
dp.legend(j, loc="lower right")

# (k) two distributions with shared bins
k_ = next(ax)
edges = dp.hist(k_, rng.lognormal(8.3, 0.35, 3000), bins=40, range=(0, 12000), label="correct", median=True)
dp.hist(k_, rng.lognormal(8.8, 0.4, 2000), bins=edges, label="wrong", i=1)
dp.kfmt(k_, axis="x")
dp.panel(k_, "k", "Response length", ylabel="Rollouts", xlabel="Tokens")
dp.legend(k_, loc="upper right")

# (l) three distributions as CDFs
l_ = next(ax)
for k, (name, mu) in enumerate([("no penalty", 8.9), ("lenpen 0.1", 8.6), ("lenpen 0.3", 8.3)]):
    dp.cdf(l_, rng.lognormal(mu, 0.35, 2000), label=name, i=k)
dp.ref(l_, 50, "median")
dp.kfmt(l_, axis="x")
dp.panel(l_, "l", "Length CDF", ylabel="Rollouts (%)", xlabel="Tokens")
dp.legend(l_, loc="lower right")

# (m) spread per group
m = next(ax)
dp.boxes(m, {f"{p}/8": np.clip(rng.normal(0.15 + 0.1 * p, 0.12, 300), 0, 1) for p in range(1, 8)})
dp.panel(m, "m", "Reward by base pass", ylabel="Mean reward", xlabel="Base pass @ 8")

# (n) levels on a grid
n = next(ax)
M = np.clip(rng.normal(np.linspace(20, 80, 6)[None, :], 12, (8, 6)), 0, 100)
dp.heatmap(n, M, xlabels=[str(x) for x in range(0, 126, 25)], ylabels=[f"p{r}" for r in range(8)])
dp.panel(n, "n", "Pass rate per problem", xlabel="RL step")

# (o) signed changes on a grid
o = next(ax)
D = rng.normal(2, 6, (6, 5))
dp.heatmap(o, D, xlabels=["lr 1e-6", "2e-6", "5e-6", "1e-5", "2e-5"],
           ylabels=[f"kl {v}" for v in [0, .001, .01, .02, .05, .1]], cmap="div", fmt="{:+.0f}")
dp.panel(o, "o", "Change vs base (pts)")

# (p) your systems against published ones on two metrics, with lines of equal combined score
p_ = next(ax)
systems = {"Big-31B": (92, 76), "Reference": (88, 72), "Small-4B A": (86, 60), "Small-4B B": (81, 46), "uniform": (90, 1),
           "ours, trained": (83, 40), "ours, base": (58, 32)}
p_.set_xlim(55, 100)
p_.set_ylim(-5, 85)
dp.iso(p_, (50, 60, 70, 80), lambda c, x: 2 * c - x)
dp.labeled_points(p_, systems, highlight={"ours, trained": 0, "ours, base": 0}, offsets={"Big-31B": (-5, 3), "Reference": (-5, -3), "Small-4B B": (5, 4), "ours, trained": (5, -5)})
dp.panel(p_, "p", "Against published", ylabel="Accuracy", xlabel="Calibration")

print(dp.save(fig, sys.argv[1] if len(sys.argv) > 1 else "gallery.png"))
