"""Figures for Confluence write-ups. Grew out of the Paradigma Limite 1B paper figures
(https://paradigma.inc/research/limite-1b-violetto.pdf, Figs 8-11): same small Inter type and "(a) Name" panels,
but one categorical palette instead of purple shades, and a helper for every kind of result, not just lines.

Look: Inter at small sizes; series colors violet / orange / teal (any two of the first three stay apart for
colorblind readers on white); soft grey axes and tick labels; a hairline grid on the value axis only; thin lines
with white-ringed markers; series-tinted bands; neutral dashed event lines and dotted references; frameless legends.

Pick the helper from what the figure has to show (SKILLS.md has the full chooser):
    change over steps ........ line, trend (raw + smoothed), band, context, step, span, ref, end_label, note
    compare a few numbers .... bars, grouped_bars (horizontal=True for long names)
    before -> after per item . dumbbell (many items), slope (few items)
    part of a whole .......... stacked_bars, stacked_area
    relation between metrics . scatter, diag
    spread of values ......... hist, cdf, boxes
    grid of values ........... heatmap (cmap="seq" for levels, "div" for signed deltas)

    import sys; sys.path.insert(0, "/root/dataDisk/edward/mono/repos/slime/.claude/skills/confluence-docs")
    import docplot as dp
    fig, axs = dp.figure(2)
    ax = axs[0]
    dp.line(ax, x, reward, label="Reward")                         # slot 0: violet, circles
    dp.line(ax, x, entropy, label="Entropy", i=1)                  # slot 1: orange, squares
    dp.step(ax, 213, "Step 213")
    dp.ref(ax, 0.5)
    dp.panel(ax, "a", "Reward", ylabel="Mean reward (%)", xlabel="Generated cohort")
    dp.legend(ax)                                                  # or dp.legend_above(fig, axs, title="First DPPO")
    dp.save(fig, "out.png")

gallery.py in this folder draws every helper on fake data.
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors as mcolors
from matplotlib import font_manager
from matplotlib.offsetbox import AnnotationBbox, HPacker, TextArea
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter

HERE = os.path.dirname(os.path.abspath(__file__))

# Series slots, in this order. Checked with the dataviz palette validator on white: slots 0-2 pass for every pair
# (worst colorblind dE 8.4), all eight pass for neighbors. More than three colored series in a panel -> highlight one
# and draw the rest with `context`, or split panels.
VIOLET, ORANGE, TEAL, BLUE = "#9874df", "#eb6834", "#199e70", "#2a78d6"
MAGENTA, GREEN, YELLOW, RED = "#e87ba4", "#008300", "#eda100", "#e34948"
C = [VIOLET, ORANGE, TEAL, BLUE, MAGENTA, GREEN, YELLOW, RED]
MARKERS = ["o", "s", "^", "D", "v", "P", "X", "h"]

INK = "#1a1a19"          # panel names, values inside light cells
INK2 = "#52514e"         # tick labels, axis labels, direct labels
MUTED = "#898781"        # panel letters, reference/event lines and their labels
AXIS = "#c3c2b7"         # baseline spine, tick marks
GRID = "#ecebe6"         # hairline grid
GREY = "#bdbcb5"         # de-emphasised marks: context series, "before" dots, non-highlighted bars
SPAN = "#f4f3ef"         # shaded phase behind the data
DPI = 220

PURPLE, LAVENDER, DEEP = C[0], C[1], C[2]   # pre-Oct-2026 names, kept so older plot scripts still run


def tint(c, keep):
    """Mix a color with white, keeping `keep` (0-1) of the color. Opaque, so overlaps don't darken."""
    r, g, b = mcolors.to_rgb(c)
    return mcolors.to_hex((1 - keep + keep * r, 1 - keep + keep * g, 1 - keep + keep * b))


SEQ = mcolors.LinearSegmentedColormap.from_list("dp_seq", ["#f6f3fd", "#d6cbf3", VIOLET, "#6250d6", "#34247f"])
DIV = mcolors.LinearSegmentedColormap.from_list(
    "dp_div", ["#1c5cab", "#86b6ef", "#f0efec", tint(RED, 0.5), "#b3302f"])   # blue / grey 0 / red


def _c(i=0, color=None):
    if isinstance(i, str):          # a hex passed where older scripts passed color positionally
        return i
    return color or C[i % len(C)]


def _num(fmt, v):
    """fmt.format(v), without a sign on values that round to zero (\"-0\", \"+0.0\")."""
    t = fmt.format(v)
    return t.lstrip("+-") if set(t) <= set("+-0.%") else t


def setup():
    for name in os.listdir(os.path.join(HERE, "fonts")):
        if name.startswith("Inter") and name.endswith(".ttf"):
            font_manager.fontManager.addfont(os.path.join(HERE, "fonts", name))
    plt.rcParams.update({
        "font.family": "Inter", "font.size": 8.5, "text.color": INK, "axes.labelcolor": INK2, "axes.labelsize": 8.2,
        "axes.labelpad": 5, "axes.edgecolor": AXIS, "axes.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
        "axes.grid": True, "axes.grid.axis": "y", "axes.axisbelow": True,
        "grid.color": GRID, "grid.linewidth": 0.7, "grid.linestyle": "-",
        "axes.facecolor": "white", "figure.facecolor": "white", "savefig.facecolor": "white",
        "xtick.color": AXIS, "ytick.color": AXIS, "xtick.labelcolor": INK2, "ytick.labelcolor": INK2,
        "xtick.labelsize": 7.6, "ytick.labelsize": 7.6, "xtick.direction": "out", "ytick.direction": "out",
        "xtick.major.size": 3, "ytick.major.size": 0, "xtick.major.width": 0.8, "ytick.major.width": 0.8,
        "xtick.major.pad": 3, "ytick.major.pad": 4, "xtick.minor.size": 0, "ytick.minor.size": 0,
        "lines.linewidth": 1.5, "lines.markersize": 4, "lines.solid_capstyle": "round",
        "lines.solid_joinstyle": "round", "lines.dash_capstyle": "butt",
        "legend.fontsize": 7.4, "legend.frameon": True, "legend.framealpha": 0.92, "legend.facecolor": "white",
        "legend.edgecolor": "none", "legend.fancybox": False, "legend.borderpad": 0.4, "legend.labelcolor": INK2,
        "legend.handlelength": 1.8, "legend.handletextpad": 0.5, "legend.columnspacing": 1.4,
        "legend.borderaxespad": 0.3, "legend.title_fontsize": 7.6,
        "axes.xmargin": 0.02, "axes.ymargin": 0.08})


def figure(n, ncols=None, size=(3.6, 2.5)):
    """n panels, size per panel in inches (keep panels small)."""
    setup()
    ncols = ncols or n
    nrows = -(-n // ncols)
    w, h = size[0] * ncols, size[1] * nrows
    fig, axs = plt.subplots(nrows, ncols, figsize=(w, h), dpi=DPI, squeeze=False)
    fig.subplots_adjust(left=0.62 / w, right=1 - 0.15 / w, bottom=0.5 / h, top=1 - 0.36 / h,
                        wspace=0.85 / size[0], hspace=1.2 / size[1])
    axs = list(axs.ravel())
    for ax in axs[n:]:
        ax.remove()
    return fig, axs[:n]


# ---- change over steps -------------------------------------------------------------------------------------------

def line(ax, x, y, label=None, i=0, second=False, color=None, marker=None, markevery=None, lw=None, ls=None,
         ms=None, **kw):
    """Series in slot i (second=True is slot 1). Each slot has its own marker; dense series get sparse markers.
    marker="" for none."""
    if second:
        i = 1
    c = _c(i, color)
    m = MARKERS[i % len(MARKERS)] if marker is None else marker
    if markevery is None and len(x) > 40:
        markevery = max(1, len(x) // 20)
    return ax.plot(x, y, color=c, marker=m, markevery=markevery, lw=lw or 1.5, ls=ls or "-", ms=ms or 4,
                   mfc=c, mec="white", mew=0.8, label=label, zorder=3, **kw)


def noisy(ax, x, y, label=None, i=0, color=None, **kw):
    """Raw noisy series: thin pale line in the series hue, drawn under its smoothed version."""
    return ax.plot(x, y, color=tint(_c(i, color), 0.38), lw=0.8, label=label, zorder=2, **kw)


def smooth(y, window):
    """Trailing rolling mean that starts at the first point (shorter windows at the start)."""
    y = np.asarray(y, float)
    c = np.cumsum(np.insert(y, 0, 0.0))
    k = np.arange(1, len(y) + 1)
    lo = np.maximum(0, k - window)
    return (c[k] - c[lo]) / (k - lo)


def trend(ax, x, y, label=None, i=0, window=None, color=None, **kw):
    """Noisy per-step metric: pale raw line + solid rolling mean with sparse markers."""
    window = window or max(3, len(y) // 20)
    noisy(ax, x, y, i=i, color=color)
    return line(ax, x, smooth(y, window), label=label, i=i, color=color, **kw)


def context(ax, x, y, label=None, lw=1.0, **kw):
    """Grey line for series that are only background (other runs, other seeds) next to a highlighted one."""
    return ax.plot(x, y, color=GREY, lw=lw, label=label, zorder=2, **kw)


def band(ax, x, lo, hi, i=0, color=None, alpha=0.14, label=None):
    """Spread (iqr, seeds, eval noise) in the series hue."""
    return ax.fill_between(x, lo, hi, color=_c(i, color), alpha=alpha, lw=0, label=label, zorder=1)


def step(ax, x, text=None, color=None):
    """Dashed vertical event line (lr change, checkpoint), labeled at the top."""
    ax.axvline(x, color=color or MUTED, lw=0.9, ls=(0, (3.5, 2.6)), zorder=1)
    if text:
        ax.annotate(text, (x, 1), xycoords=("data", "axes fraction"), xytext=(-3, -2), textcoords="offset points",
                    ha="right", va="top", fontsize=7.2, color=INK2)


def span(ax, x0, x1, text=None):
    """Shaded phase (warmup, eval-only steps), labeled at its top-left."""
    ax.axvspan(x0, x1, color=SPAN, lw=0, zorder=0)
    if text:
        ax.annotate(text, (x0, 1), xycoords=("data", "axes fraction"), xytext=(3, -2), textcoords="offset points",
                    ha="left", va="top", fontsize=7.2, color=MUTED)


def ref(ax, y, text=None, color=None, label=None, ls=(0, (1, 1.8))):
    """Dotted horizontal reference (base, chance, cap). text = small label at the right end;
    label = legend entry instead (use when the data runs through the line's right end)."""
    ax.axhline(y, color=color or MUTED, lw=0.9, ls=ls, zorder=1, label=label)
    if text:
        ax.annotate(text, (1, y), xycoords=("axes fraction", "data"), xytext=(-2, 2), textcoords="offset points",
                    ha="right", va="bottom", fontsize=7.2, color=MUTED)


def end_label(ax, line, text=None, fmt="{:.1f}", dx=5, dy=0):
    """Direct label at a line's last point (the value by default). Pass what line()/ax.plot returned."""
    ln = line[0] if isinstance(line, (list, tuple)) else line
    x, y = ln.get_xdata()[-1], ln.get_ydata()[-1]
    ax.annotate(fmt.format(y) if text is None else text, (x, y), xytext=(dx, dy), textcoords="offset points",
                ha="left", va="center", fontsize=7.2, color=INK2, annotation_clip=False)


def note(ax, x, y, text, dx=14, dy=14):
    """Callout for one point (a spike, the best checkpoint) with a thin leader line."""
    ax.annotate(text, (x, y), xytext=(dx, dy), textcoords="offset points", fontsize=7.2, color=INK2,
                ha="left" if dx >= 0 else "right", va="bottom" if dy >= 0 else "top",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7, shrinkA=1, shrinkB=3), zorder=5)


# ---- comparing numbers ---------------------------------------------------------------------------------------------

def _cat_axes(ax, n, horizontal):
    """Category axis without ticks; value axis keeps the grid; the baseline is the only spine."""
    if horizontal:
        ax.grid(False)
        ax.grid(axis="x")
        ax.spines["left"].set_visible(True)
        ax.spines["bottom"].set_visible(False)
        ax.tick_params(axis="both", length=0)
        ax.set_ylim(n - 0.5, -0.5)
    else:
        ax.tick_params(axis="x", length=0)
        ax.set_xlim(-0.5, n - 0.5)


def _zero_line(ax, vals, horizontal):
    """Bars that go negative grow from a drawn 0, not from the axis edge."""
    if np.nanmin(np.asarray(vals, float)) < 0:
        (ax.axvline if horizontal else ax.axhline)(0, color=AXIS, lw=0.8, zorder=2.5)


def _bar_values(ax, bs, vals, fmt, horizontal):
    ax.bar_label(bs, labels=[_num(fmt, v) for v in vals], padding=2.5, fontsize=7.2, color=INK2)
    ax.margins(**{("x" if horizontal else "y"): 0.12})


def bars(ax, cats, vals, label=None, i=0, color=None, horizontal=False, highlight=None, values=True, fmt="{:.0f}",
         width=0.62):
    """One series of bars, all in one color. highlight = category names (or indices) to keep in color, the rest go
    grey. Values sit at the bar ends."""
    c = _c(i, color)
    if highlight is not None:
        hl = set(highlight) if isinstance(highlight, (list, tuple, set)) else {highlight}
        colors = [c if (k in hl or cat in hl) else GREY for k, cat in enumerate(cats)]
    else:
        colors = c
    pos = np.arange(len(cats))
    if horizontal:
        bs = ax.barh(pos, vals, height=width, color=colors, label=label, zorder=2)
        ax.set_yticks(pos, cats)
    else:
        bs = ax.bar(pos, vals, width, color=colors, label=label, zorder=2)
        ax.set_xticks(pos, cats)
    _cat_axes(ax, len(cats), horizontal)
    _zero_line(ax, vals, horizontal)
    if values:
        _bar_values(ax, bs, vals, fmt, horizontal)
    return bs


def grouped_bars(ax, cats, series, slots=None, horizontal=False, values=False, fmt="{:.0f}", width=0.78):
    """series = {name: values per category}; series j uses slot slots[j] (default j). Keep the same slot for the
    same run/config across every figure on the page."""
    k = len(series)
    w = width / k
    pos = np.arange(len(cats))
    out = []
    for j, (name, vals) in enumerate(series.items()):
        c = C[slots[j] if slots else j]
        p = pos - width / 2 + w * (j + 0.5)
        if horizontal:
            bs = ax.barh(p, vals, height=w, color=c, edgecolor="white", linewidth=0.8, label=name, zorder=2)
        else:
            bs = ax.bar(p, vals, w, color=c, edgecolor="white", linewidth=0.8, label=name, zorder=2)
        if values:
            _bar_values(ax, bs, vals, fmt, horizontal)
        _zero_line(ax, vals, horizontal)
        out.append(bs)
    (ax.set_yticks if horizontal else ax.set_xticks)(pos, cats)
    _cat_axes(ax, len(cats), horizontal)
    return out


def _ink_on(rgb):
    r, g, b = mcolors.to_rgb(rgb)
    return "white" if 0.2126 * r + 0.7152 * g + 0.0722 * b < 0.5 else INK


def _spread(ys, gap=9):
    """Nudge label rows (in points) at least `gap` apart, keeping them centred on where they started."""
    out, last = np.empty(len(ys)), -np.inf
    for k in np.argsort(ys):
        last = max(ys[k], last + gap)
        out[k] = last
    return out - np.mean(out - ys)


def _ppu(ax):
    """Points per y data unit, from the axes' size and current y limits."""
    lo, hi = ax.get_ylim()
    return ax.get_position().height * ax.figure.get_figheight() * 72 / (hi - lo)


def stacked_bars(ax, cats, series, slots=None, horizontal=False, normalize=False, values=False, fmt="{:.0f}",
                 width=0.62, key=True):
    """Composition per category (outcome mix per checkpoint). normalize=True shows shares in %. values=True labels
    the segments big enough to hold a number. key=True adds legend_top (a stack has no free corner)."""
    names = list(series)
    data = np.array([list(series[n]) for n in names], float)
    if normalize:
        data = data / data.sum(0) * 100
    pos = np.arange(len(cats))
    base = np.zeros(len(cats))
    span_ = data.sum(0).max()
    for j, name in enumerate(names):
        c = C[slots[j] if slots else j]
        if horizontal:
            bs = ax.barh(pos, data[j], height=width, left=base, color=c, edgecolor="white", linewidth=0.8,
                         label=name, zorder=2)
        else:
            bs = ax.bar(pos, data[j], width, bottom=base, color=c, edgecolor="white", linewidth=0.8, label=name,
                        zorder=2)
        if values:
            for p, b, v in zip(pos, base, data[j]):
                if v / span_ >= 0.07:
                    xy = (b + v / 2, p) if horizontal else (p, b + v / 2)
                    ax.text(*xy, _num(fmt, v), ha="center", va="center", fontsize=6.8, color=_ink_on(c), zorder=3)
        base += data[j]
    (ax.set_yticks if horizontal else ax.set_xticks)(pos, cats)
    _cat_axes(ax, len(cats), horizontal)
    if normalize:
        (ax.set_xlim if horizontal else ax.set_ylim)(0, 100)
    if key:
        legend_top(ax)


def stacked_area(ax, x, series, slots=None, normalize=False, key=True):
    """Composition over steps (share of correct / wrong / truncated). key=True adds legend_top (a stack has no free
    corner)."""
    names = list(series)
    data = np.array([list(series[n]) for n in names], float)
    if normalize:
        data = data / data.sum(0) * 100
    cs = [C[slots[j] if slots else j] for j in range(len(names))]
    out = ax.stackplot(x, data, labels=names, colors=cs, edgecolor="white", linewidth=0.6, alpha=0.92, zorder=2)
    ax.set_xlim(x[0], x[-1])
    if normalize:
        ax.set_ylim(0, 100)
    if key:
        legend_top(ax)
    return out


# ---- before -> after ---------------------------------------------------------------------------------------------

def dumbbell(ax, cats, before, after, labels=("before", "after"), i=0, horizontal=True, values=True,
             fmt="{:.0f}", key=True):
    """Per-item change (per benchmark, per problem group): grey dot = before, colored dot = after, joined by a
    tinted bar. Sort cats by change when order carries no meaning. key=True names the two dots on the first item
    (sorting by change gives it the widest gap); key=False -> dp.legend."""
    c = _c(i)
    pos = np.arange(len(cats))
    for p, b, a in zip(pos, before, after):
        xy = ([b, a], [p, p]) if horizontal else ([p, p], [b, a])
        ax.plot(*xy, color=tint(c, 0.32), lw=2.4, solid_capstyle="butt", zorder=2)
    pts = lambda v: (v, pos) if horizontal else (pos, v)
    ax.scatter(*pts(before), s=26, color=GREY, edgecolors="white", linewidths=0.8, label=labels[0], zorder=3)
    ax.scatter(*pts(after), s=26, color=c, edgecolors="white", linewidths=0.8, label=labels[1], zorder=4)
    if values:
        for p, b, a in zip(pos, before, after):
            off = 6 if a >= b else -6
            xy, xyt = ((a, p), (off, 0)) if horizontal else ((p, a), (0, off))
            ax.annotate(_num(fmt, a), xy, xytext=xyt, textcoords="offset points", fontsize=7.2, color=INK2,
                        ha=("left" if off > 0 else "right") if horizontal else "center",
                        va="center" if horizontal else ("bottom" if off > 0 else "top"))
        ax.margins(**{("x" if horizontal else "y"): 0.1})
    (ax.set_yticks if horizontal else ax.set_xticks)(pos, cats)
    _cat_axes(ax, len(cats), horizontal)
    if horizontal:
        ax.spines["left"].set_visible(False)
    if key:
        for v, t, col in ((before[0], labels[0], MUTED), (after[0], labels[1], INK2)):
            ax.annotate(t, (v, 0) if horizontal else (0, v), xytext=(0, 7) if horizontal else (8, 0),
                        textcoords="offset points", ha="center" if horizontal else "left",
                        va="bottom" if horizontal else "center", fontsize=7, color=col)
        if horizontal:
            ax.set_ylim(len(cats) - 0.5, -0.95)


def slope(ax, before, after, names, labels=("before", "after"), highlight=None, i=0, fmt="{:.0f}"):
    """Few items (<= ~10), two moments: one line per item, named at the right end. highlight = names kept in
    color, the others grey."""
    c = _c(i)
    lo, hi = min(min(before), min(after)), max(max(before), max(after))
    pad = 0.08 * (hi - lo or 1)
    ax.set_ylim(lo - pad, hi + pad)
    ppu = _ppu(ax)
    b_pts, a_pts = np.asarray(before, float) * ppu, np.asarray(after, float) * ppu
    b_row, a_row = _spread(b_pts), _spread(a_pts)
    for k, (b, a, n) in enumerate(zip(before, after, names)):
        on = highlight is None or n in highlight
        col = c if on else GREY
        ax.plot([0, 1], [b, a], color=col, lw=1.5 if on else 1.0, marker="o", ms=4, mfc=col, mec="white", mew=0.8,
                zorder=3 if on else 2)
        ax.annotate(f"{n}  {fmt.format(a)}", (1, a), xytext=(8, a_row[k] - a_pts[k]), textcoords="offset points",
                    fontsize=7.2, color=INK2 if on else MUTED, ha="left", va="center", annotation_clip=False)
        ax.annotate(fmt.format(b), (0, b), xytext=(-7, b_row[k] - b_pts[k]), textcoords="offset points",
                    fontsize=7.2, color=INK2 if on else MUTED, ha="right", va="center", annotation_clip=False)
    ax.set_xticks([0, 1], labels)
    ax.set_xlim(-0.12, 1.12)
    ax.grid(False)
    ax.tick_params(axis="x", length=0)
    ax.tick_params(axis="y", labelleft=False)
    ax.spines["bottom"].set_visible(False)


# ---- relations -----------------------------------------------------------------------------------------------------

def scatter(ax, x, y, label=None, i=0, color=None, s=None, alpha=None, marker=None):
    """Points sized and faded by count. Up to three groups in one panel (slots 0-2)."""
    n = len(x)
    s = s or (18 if n < 200 else 8 if n < 2000 else 3)
    alpha = alpha or (0.9 if n < 200 else 0.6 if n < 2000 else 0.35)
    return ax.scatter(x, y, s=s, color=_c(i, color), edgecolors="white" if n < 2000 else "none", linewidths=0.5,
                      alpha=alpha, marker=marker or MARKERS[i % len(MARKERS)], label=label, zorder=3)


def diag(ax, text=None):
    """Dotted y = x line (per-item before vs after, predicted vs actual). Call after the data is drawn."""
    xl, yl = ax.get_xlim(), ax.get_ylim()
    lo, hi = min(xl[0], yl[0]), max(xl[1], yl[1])
    ax.plot([lo, hi], [lo, hi], color=MUTED, lw=0.9, ls=(0, (1, 1.8)), zorder=1)
    ax.set_xlim(xl)
    ax.set_ylim(yl)
    if text:
        t = min(xl[1], yl[1])
        ax.annotate(text, (t, t), xytext=(-3, 3), textcoords="offset points", ha="right", va="bottom",
                    fontsize=7.2, color=MUTED)


# ---- spread --------------------------------------------------------------------------------------------------------

def hist(ax, data, bins=30, label=None, i=0, color=None, density=False, range=None, median=False, fmt="{:.0f}"):
    """Filled outline histogram; overlay two or three with shared bins (pass the edges this returns as bins).
    median=True marks the median with a dashed line in the series hue."""
    c = _c(i, color)
    _, edges, _ = ax.hist(data, bins=bins, range=range, density=density, histtype="stepfilled",
                          facecolor=mcolors.to_rgba(c, 0.18), edgecolor=c, linewidth=1.1, label=label, zorder=2)
    if median:
        m = float(np.median(data))
        ax.axvline(m, color=c, lw=0.9, ls=(0, (3, 2)), zorder=3)
        ax.annotate(f"median {fmt.format(m)}", (m, 1), xycoords=("data", "axes fraction"), xytext=(3, -2),
                    textcoords="offset points", ha="left", va="top", fontsize=7.2, color=INK2)
        ax.margins(y=0.16)                         # headroom so the label clears the bars
    return edges


def cdf(ax, data, label=None, i=0, color=None, pct=True):
    """Empirical CDF, y in % by default. Reads better than overlaid histograms once there are 3 groups or heavy
    tails (response lengths, latencies)."""
    x = np.sort(np.asarray(data, float))
    y = np.arange(1, len(x) + 1) / len(x) * (100 if pct else 1)
    out = ax.step(np.r_[x[0], x], np.r_[0, y], where="post", color=_c(i, color), lw=1.5, label=label, zorder=3)
    ax.set_ylim(0, 100 if pct else 1)
    return out


def boxes(ax, groups, i=0, slots=None, points=True, horizontal=False, width=0.5, max_points=400, seed=0):
    """groups = {name: values}. Box = middle 50%, bar = median, whiskers to 1.5 iqr, with the raw points jittered
    behind (sampled to max_points). One color for all groups unless slots gives one per group."""
    rng = np.random.default_rng(seed)
    names = list(groups)
    for k, name in enumerate(names):
        d = np.asarray(groups[name], float)
        c = C[slots[k]] if slots else _c(i)
        q1, med, q3 = np.percentile(d, [25, 50, 75])
        lo = d[d >= q1 - 1.5 * (q3 - q1)].min()
        hi = d[d <= q3 + 1.5 * (q3 - q1)].max()
        P = (lambda a, b: (b, a)) if horizontal else (lambda a, b: (a, b))
        if points:
            pts = d if len(d) <= max_points else rng.choice(d, max_points, replace=False)
            jit = k + rng.uniform(-width * 0.38, width * 0.38, len(pts))
            ax.scatter(*P(jit, pts), s=5, color=c, alpha=0.35, lw=0, zorder=2)
        else:
            out = d[(d < lo) | (d > hi)]
            ax.scatter(*P(np.full(len(out), k), out), s=8, facecolors="none", edgecolors=MUTED, lw=0.6, zorder=2)
        xy, wh = P(k - width / 2, q1), P(width, q3 - q1)
        ax.add_patch(Rectangle(xy, *wh, facecolor=mcolors.to_rgba(c, 0.14), edgecolor=c, lw=1.0, zorder=3))
        ax.plot(*P([k - width / 2, k + width / 2], [med, med]), color=c, lw=2.2, solid_capstyle="butt", zorder=4)
        for a, b in ((q3, hi), (q1, lo)):
            ax.plot(*P([k, k], [a, b]), color=MUTED, lw=0.9, zorder=3)
            ax.plot(*P([k - width / 6, k + width / 6], [b, b]), color=MUTED, lw=0.9, zorder=3)
    (ax.set_yticks if horizontal else ax.set_xticks)(range(len(names)), names)
    _cat_axes(ax, len(names), horizontal)
    if horizontal:
        ax.spines["left"].set_visible(False)
    ax.autoscale_view()


# ---- grids ---------------------------------------------------------------------------------------------------------

def heatmap(ax, M, xlabels=None, ylabels=None, cmap="seq", vmin=None, vmax=None, values=None, fmt="{:.0f}",
            cbar=None, cbar_label=None):
    """Matrix of values (pass rate per problem x checkpoint, ablation grid, confusion matrix). cmap="seq" (one hue,
    light = low) for levels, "div" (blue / grey / red around 0) for signed changes. Cells are numbered when there
    are <= 120 of them; the colorbar shows only when they are not."""
    M = np.asarray(M, float)
    if cmap == "div":
        lim = vmax if vmax is not None else np.nanmax(np.abs(M))
        vmin, vmax, cm = -lim, lim, DIV
    else:
        cm = SEQ if cmap == "seq" else cmap
    values = M.size <= 120 if values is None else values
    im = ax.imshow(M, cmap=cm, vmin=vmin, vmax=vmax, aspect="auto", interpolation="nearest")
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    ny, nx = M.shape
    for n, labels, set_ticks in ((nx, xlabels, ax.set_xticks), (ny, ylabels, ax.set_yticks)):
        labels = list(labels) if labels is not None else list(range(n))
        every = -(-n // 12)                       # at most ~12 labels per side
        set_ticks(range(0, n, every), labels[::every])
    gap = 1.2 if max(nx, ny) <= 15 else 0.5 if max(nx, ny) <= 40 else 0
    if gap:
        ax.set_xticks(np.arange(-0.5, nx), minor=True)
        ax.set_yticks(np.arange(-0.5, ny), minor=True)
        ax.grid(which="minor", axis="both", color="white", lw=gap)
    ax.tick_params(which="both", length=0)
    if values:
        for (r, q), v in np.ndenumerate(M):
            if np.isfinite(v):
                ax.text(q, r, _num(fmt, v), ha="center", va="center", fontsize=6.8,
                        color=_ink_on(cm(im.norm(v))))
    if cbar if cbar is not None else not values:
        cb = ax.figure.colorbar(im, ax=ax, fraction=0.05, pad=0.03, aspect=22)
        cb.outline.set_visible(False)
        cb.ax.tick_params(length=0, labelsize=7, labelcolor=INK2)
        if cbar_label:
            cb.ax.set_title(cbar_label, fontsize=7, color=INK2, loc="left", pad=5)
    return im


# ---- labels, legends, formats, output ------------------------------------------------------------------------------

def panel(ax, letter, name, ylabel=None, xlabel=None):
    """Grey "(a)" + the panel name above the plot. A name, not a finding: the finding goes in the page text."""
    parts = [TextArea(f"({letter})", textprops=dict(color=MUTED, fontsize=8.4))] if letter else []
    parts.append(TextArea(name, textprops=dict(color=INK, fontsize=8.4, fontweight="medium")))
    ax.add_artist(AnnotationBbox(HPacker(children=parts, sep=4, pad=0, align="baseline"), (0, 1),
                                 xycoords="axes fraction", xybox=(0, 9), boxcoords="offset points",
                                 box_alignment=(0, 0), frameon=False, pad=0, annotation_clip=False))
    if ylabel:
        ax.set_ylabel(ylabel)
    if xlabel:
        ax.set_xlabel(xlabel)


def legend(ax, loc="best", **kw):
    return ax.legend(loc=loc, **kw)


def legend_top(ax, ncol=None, **kw):
    """One-row legend at the top right, level with the panel name (keep that name short). For panels whose data
    fills every corner (stacks, dense lines)."""
    _, labels = ax.get_legend_handles_labels()
    return ax.legend(loc="lower right", bbox_to_anchor=(1, 1), ncol=ncol or len(labels), frameon=False,
                     borderaxespad=0.35, borderpad=0, handlelength=1.2, handleheight=0.8, columnspacing=1.1, **kw)


def legend_above(fig, axs, title=None, ncol=None):
    """One shared legend centred above the panels, with an optional title (like 'First DPPO')."""
    handles, labels = [], []
    for ax in axs:
        for h, l in zip(*ax.get_legend_handles_labels()):
            if l not in labels:
                handles.append(h)
                labels.append(l)
    return fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=ncol or len(labels),
                      title=title, frameon=False)


def pct(ax, decimals=0, axis="y", sign=False):
    f = f"{{:{'+' if sign else ''}.{decimals}f}}"
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(FuncFormatter(lambda v, _: f.format(v)))


def kfmt(ax, axis="y"):
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(
        FuncFormatter(lambda v, _: "0" if v == 0 else f"{v / 1e3:.0f}k"))


def save(fig, path):
    fig.savefig(path, dpi=DPI, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    return path
