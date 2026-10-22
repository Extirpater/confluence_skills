---
name: confluence-docs
description: Write up or update results on the user's Confluence (deepgrove.atlassian.net, Deepgrove space, e.g. 2026Q4 → Edwardq4 live docs). Use whenever asked to document a run, post results, add figures, or edit a Confluence page. Covers the user's writing voice, how to pick and draw each figure (docplot.py in this folder: lines, bars, dumbbells, distributions, heatmaps and more), and how to edit pages safely through the Atlassian connector.
---

# Documenting results on Confluence

The user wants **figures first, very little text**. A section is a figure plus 1-3 short takeaways and, when it
matters, a one-line conclusion. They have rejected tables, long paragraphs, and anything that reads AI-generated.

## Where things live
- Site `deepgrove.atlassian.net`, cloudId `8a334fd3-7429-4c31-b5a4-4dc053934aca`, space `Deepgrove`.
- Quarter folders (`2026Q4`), one folder per person (`Edwardq4`), one **live doc** per project:
  "Dflash2 Training" (5177345), "Critic Math RL" (4653060), "Train on math test experiments" (3407873), "RL Todo:".
- Fig 1 on "Train on math test experiments" is the reference for content (not styling): median line + middle-50% band, cap and
  penalty-start lines labeled on the right, correct vs wrong as two series.

## Writing voice
Copy the user's own pages. Before writing, read 1-2 of their docs with the connector, and match them.
- Short "we" sentences: "We init the critic with the value model trained above. We set warmup steps to 5 steps."
- Changes as arrows: "aime26 90 → 95ish (pass @ 4 is 96)", "runaways ~30 per wave → ~1".
- Plain labels as paragraphs, not headings: `Notes:`, `To fix:`, `Open questions:`, `Evals:`, `Training:`.
- Lowercase metric/set names the way they write them (aime26, hmmt26, held out, lr, kl, auc).
- Keep every number exact, but only the numbers that matter. Let the figure carry the rest.
- No tables. If something is a table, make it a plot; pick the form from the chooser under Figures. A table survives
  only if it is genuinely lookup data.
- No filler or AI tells: no "Notably", "It's worth noting", "Key findings", "In summary", "Why this works", bold
  lead-ins on every bullet, em-dash chains, or restating the figure title in prose.
- Caveats in one short line ("early = steps 9-29, not base"), not a paragraph.

## Figures (use docplot.py)
Every figure should be good to look at and fit what it shows. Don't default to line charts. For each figure, decide
what it has to show, then pick the form from the chooser below. A write-up usually ends up with several kinds
(training curves, a dumbbell of per-benchmark changes, a length histogram, a sweep heatmap), but the variety comes
from the data. Never switch chart types just for variety. The style started from the Paradigma Limite 1B paper
(https://paradigma.inc/research/limite-1b-violetto.pdf, Figs 8-11). The user rejected a card/dashboard look and an
"editorial" look with finding-titles as AI-generated, so keep it plain.

| What the figure has to show | Form | docplot |
|---|---|---|
| A metric over training steps (reward, loss, entropy, kl) | line; noisy per-step metrics as pale raw + smoothed | `trend`, `line` |
| Evals per checkpoint against base | line + dotted base + grey noise band; final values labeled | `line`, `ref`, `band`, `end_label` |
| One run against many (seeds, a sweep) | the run in color, the rest grey | `line` + `context` |
| One number per benchmark / config | bars, horizontal for long names; highlight the one the text is about | `bars(highlight=)` |
| A few configs × a few benchmarks | grouped bars | `grouped_bars` |
| Before → after for many items (benchmarks, topics, problem groups) | dumbbell, sorted by change | `dumbbell` |
| Before → after for ≤ ~8 items, when crossings or rank changes matter | slope chart | `slope` |
| Mix of outcomes (correct / wrong / truncated) | over steps: stacked area; at a few checkpoints: stacked bars; `normalize=True` for shares | `stacked_area`, `stacked_bars` |
| Two per-item metrics against each other (per-problem pass before vs after, length vs reward) | scatter, with y = x when it's before/after | `scatter`, `diag` |
| Spread of a value (response length, reward) | 1-2 groups: histogram with shared bins; 3+ groups or long tails: CDF; across many buckets: boxes | `hist`, `cdf`, `boxes` |
| A grid (problem × checkpoint, lr × kl sweep, confusion matrix) | heatmap: `cmap="seq"` for levels, `"div"` for signed changes | `heatmap` |
| Phases and events on a curve | shaded phase, dashed event line, a callout for one point | `span`, `step`, `note` |
| A single headline number | no figure: say it in the text with an arrow ("aime26 90 → 95") | |

Look (docplot sets all of it): Inter at small sizes, soft grey axes, a hairline grid on the value axis only, thin
lines with white-ringed markers, series-tinted bands, frameless legends, grey `(a) Name` label above each panel.

```python
import sys; sys.path.insert(0, "/root/dataDisk/edward/mono/repos/slime/.claude/skills/confluence-docs")
import docplot as dp
fig, axs = dp.figure(3)                               # 3.6x2.5in panels; dp.figure(4, ncols=2) for a 2x2
a, b, c = axs
dp.trend(a, steps, reward_rl, label="RL", i=1)        # i = the run's slot, the same in every figure on the page
dp.trend(a, steps, reward_critic, label="RL + critic", i=2)
dp.step(a, 40, "lr 3e-5")
dp.panel(a, "a", "Train reward", ylabel="mean reward", xlabel="RL step")
dp.legend(a)                                          # only with >= 2 series
dp.dumbbell(b, sets, base, final, labels=("base", "step 125"), i=2)   # sets sorted by change
dp.panel(b, "b", "Evals", xlabel="avg @ 4 (%)")
edges = dp.hist(c, len_rl, bins=40, label="RL", i=1)
dp.hist(c, len_critic, bins=edges, label="RL + critic", i=2, median=True)
dp.kfmt(c, axis="x")
dp.panel(c, "c", "Response length", ylabel="rollouts", xlabel="tokens")
dp.legend(c)
dp.save(fig, "critic.png")                            # 220 dpi, white
```
`gallery.py` (this folder) draws every helper on fake data. When unsure what a form looks like, run
`python gallery.py /tmp/gallery.png`, read the PNG, and copy the closest panel's code.

Rules:
- Colors are slots in `dp.C`: violet, orange, teal, blue, magenta, green, yellow, red. Assign them in order. A slot
  means one thing on the whole page: if "RL + critic" is teal in Fig 1, it is teal everywhere.
- At most three colored series per panel (any two of slots 0-2 stay distinct for colorblind readers). More → color
  the one the text is about and grey the rest (`context`, `bars(highlight=)`), or split into panels.
- One y-axis per panel. Two quantities → two panels, never a dual axis.
- Sort categories by value unless they already have an order (steps, difficulty, base pass @ 8).
- Panel names are names ("Evals", "Response length"), not findings. The finding goes in the page text.
- Legend only with >= 2 series, never on top of data: `legend` picks the emptiest corner, `legend_top` sits beside
  the panel name when the data fills the plot (keep that name short), `legend_above` shares one across panels.
  Stacks and dumbbells label themselves.
- Label sparingly: `end_label` on the final values the text quotes, values on bars. Never a number on every point.
- Splits beat aggregates: early vs late, long vs short problems, hard cohort (base pass 1-3/8). The user liked
  per-problem splits that tie a training change to an eval change.
- Worked example of a full section (older style; its calls still run): /root/dataDisk/edward/specforge-night/lenpen/plot_v4.py
- Render, then **look at the PNG** (Read it) before posting: labels or legends on top of data, clipped text, a panel's
  labels running into its neighbor. Fix and re-render.

## Editing pages through the connector
- Tools come from the claude.ai "Atlassian MCP" connector and load only at session start. If they are missing
  mid-session, run a headless agent with them:
  `claude -p "<task>" --allowedTools "mcp__claude_ai_Atlassian_MCP" "Read" "Bash(curl:*)" --output-format text < /dev/null`
  and give it exact page ids, the local file to post, and what must not change.
- Images: `executeWrite` op `createConfluenceAttachment` (contentId + localFilePath) returns a curl command; run it,
  then embed the returned media id. Multi-panel figures go full width (1800px), with the stored width/height set to the PNG's pixel size.
- Edit in HTML/storage format so inline W&B link cards survive; markdown round-trips drop them.
- Only touch the section you were asked about: append at the end, or replace from that section's heading to its
  end. Never rewrite the user's own text.
- Live docs stay at version 1 and show "draft"; that is normal. A save conflict means someone has the page open:
  re-read, re-apply, and tell the user.
- Always re-read after saving and check the rest of the page is unchanged.

## Order of work
1. Read the target page (and one of the user's other docs for voice).
2. Pull the data; pick each figure's form from the chooser; draw it with docplot; look at it.
3. Write ~3 takeaways per figure in the user's voice; one conclusion; short "To fix:" if there is a next step.
4. Post the section; verify; reply with the link and one line on what changed.

