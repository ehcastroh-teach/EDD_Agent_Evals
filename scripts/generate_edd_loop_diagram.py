"""
Generate the EDD (Evaluation-Driven Development) loop diagram.

This diagram anchors the entire three-notebook series. It shows the four
stages of the EDD cycle as a closed loop with the artifacts that flow
between them, so learners can see where each notebook fits.

Output: images/edd_loop.png

Design notes
------------
- Berkeley Blue (#003262) matches the notebook style palette so the diagram
  reads as part of the same visual language.
- Nodes are stages (verbs). Edge labels are the artifacts that move between
  stages - traces, scores, prompt changes.
- The dashed inner arrow marks the "one targeted change per cycle" discipline
  that the notebooks emphasize.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

BERKELEY = "#003262"
GOLD = "#FDB515"
INK = "#2A2C2B"
CREAM = "#F7F5EF"

fig, ax = plt.subplots(figsize=(10, 8), dpi=140)
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor("white")

# Node positions arranged as a diamond
nodes = {
    "Instrument": (5.0, 8.4, "Notebook 02\ntracing decorators\nspan kinds"),
    "Collect":    (8.4, 5.0, "run agent\non a batch\nof queries"),
    "Evaluate":   (5.0, 1.6, "Notebook 03\nLLM-as-judge +\nprogrammatic checks"),
    "Improve":    (1.6, 5.0, "one targeted change\nprompt, description,\nor parameter"),
}

# Draw the four stage nodes
node_w, node_h = 3.2, 1.6
for label, (x, y, sub) in nodes.items():
    box = FancyBboxPatch(
        (x - node_w / 2, y - node_h / 2), node_w, node_h,
        boxstyle="round,pad=0.05,rounding_size=0.12",
        linewidth=2.2, edgecolor=BERKELEY, facecolor="white", zorder=3,
    )
    ax.add_patch(box)
    ax.text(x, y + 0.30, label, ha="center", va="center",
            fontsize=15, fontweight="bold", color=BERKELEY, zorder=4)
    ax.text(x, y - 0.28, sub, ha="center", va="center",
            fontsize=9, color=INK, zorder=4)

# Curved arrows going clockwise around the loop with edge labels for artifacts
edges = [
    ("Instrument", "Collect",   "spans",         (7.15, 7.4)),
    ("Collect",    "Evaluate",  "spans + inputs",(7.15, 2.6)),
    ("Evaluate",   "Improve",   "scores +\nfailure patterns",(2.85, 2.6)),
    ("Improve",    "Instrument","new prompt or\nconfig",(2.85, 7.4)),
]

for src, dst, edge_label, label_pos in edges:
    x0, y0, _ = nodes[src]
    x1, y1, _ = nodes[dst]
    arrow = FancyArrowPatch(
        (x0, y0), (x1, y1),
        connectionstyle="arc3,rad=0.28",
        arrowstyle="-|>", mutation_scale=22,
        linewidth=2.0, color=BERKELEY, zorder=2,
    )
    ax.add_patch(arrow)
    ax.text(label_pos[0], label_pos[1], edge_label,
            ha="center", va="center", fontsize=9.5,
            color=INK, fontstyle="italic",
            bbox=dict(boxstyle="round,pad=0.25",
                      facecolor=CREAM, edgecolor="none", alpha=0.95),
            zorder=5)

# Center annotation - the discipline of EDD
ax.text(5.0, 5.4, "EDD\nCYCLE", ha="center", va="center",
        fontsize=18, fontweight="bold", color=BERKELEY, alpha=0.55)
ax.text(5.0, 4.55, "one change per turn",
        ha="center", va="center", fontsize=9.5,
        color=INK, fontstyle="italic")

# Title bar at top
ax.text(5.0, 9.55, "Evaluation-Driven Development for LLM Agents",
        ha="center", va="center", fontsize=13.5,
        fontweight="bold", color=BERKELEY)
ax.text(5.0, 9.15,
        "instrument once, observe continuously, evaluate rigorously, change one thing at a time",
        ha="center", va="center", fontsize=10, color=INK, fontstyle="italic")

# Legend at bottom noting notebook coverage
ax.text(5.0, 0.35,
        "Notebook 01 builds the system under test. Notebooks 02 and 03 wire the loop around it.",
        ha="center", va="center", fontsize=9.5, color=INK)

plt.tight_layout()
out = "/home/elcasnix/Projects/ehcastroh-teach/EDD_Agent_Evals/images/edd_loop.png"
plt.savefig(out, dpi=180, bbox_inches="tight", facecolor="white")
print(f"wrote {out}")
