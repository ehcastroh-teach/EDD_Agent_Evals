"""
Generate the evaluation matrix diagram for notebook 03.

Purpose
-------
Learners need to see, at a glance, how the four evaluations in the series
map to (a) the span kind they query, (b) the judgement mechanism they use,
and (c) the failure mode they surface. A single table beats four scattered
paragraphs.

Output: images/eval_matrix.png
"""

import matplotlib.pyplot as plt

BERKELEY = "#003262"
GOLD = "#FDB515"
INK = "#2A2C2B"
CREAM = "#F7F5EF"

rows = [
    # (name, span kind, mechanism, surfaces)
    ("Tool calling",       "LLM (tool call turns)", "Phoenix built-in\nLLM-as-judge",
     "Router picked the wrong tool\nor filled wrong parameters"),
    ("Code runnability",   "chain (generate_visualization)", "exec() in a try/except\n(no LLM cost)",
     "Chart code parses but crashes\nat run time"),
    ("Response clarity",   "agent (root span)", "Custom LLM-as-judge\n(clear vs unclear)",
     "Final answer is vague,\ndisorganized, or misses the ask"),
    ("SQL generation",     "LLM (SQL turns)", "Custom LLM-as-judge\n(correct vs incorrect)",
     "Generated SQL runs but returns\nthe wrong answer"),
]

headers = ["Evaluation", "Queried span kind", "Judgement mechanism", "Failure it surfaces"]

fig, ax = plt.subplots(figsize=(13, 6), dpi=140)
ax.set_xlim(0, 13)
ax.set_ylim(0, 7.2)
ax.axis("off")
fig.patch.set_facecolor("white")

# Title
ax.text(6.5, 6.85, "The four evaluations, at a glance",
        ha="center", va="center", fontsize=14, fontweight="bold", color=BERKELEY)
ax.text(6.5, 6.45,
        "Every eval targets a specific span kind and returns a signal you can act on with one prompt change.",
        ha="center", va="center", fontsize=10, color=INK, fontstyle="italic")

# Column x positions and widths
col_x = [0.3, 2.5, 5.4, 8.4]
col_w = [2.0, 2.7, 2.8, 4.3]

# Header row
header_y = 5.65
header_h = 0.55
for i, h in enumerate(headers):
    ax.add_patch(plt.Rectangle((col_x[i], header_y), col_w[i], header_h,
                               facecolor=BERKELEY, edgecolor="white", linewidth=1.5))
    ax.text(col_x[i] + col_w[i] / 2, header_y + header_h / 2, h,
            ha="center", va="center", fontsize=11, fontweight="bold", color="white")

# Data rows
row_h = 1.15
for r, row in enumerate(rows):
    y = header_y - (r + 1) * row_h
    bg = "white" if r % 2 == 0 else CREAM
    for i, val in enumerate(row):
        ax.add_patch(plt.Rectangle((col_x[i], y), col_w[i], row_h,
                                   facecolor=bg, edgecolor="#DDDDDD", linewidth=1))
        weight = "bold" if i == 0 else "normal"
        color = BERKELEY if i == 0 else INK
        ax.text(col_x[i] + 0.15, y + row_h / 2, val,
                ha="left", va="center", fontsize=10.5,
                fontweight=weight, color=color)

plt.tight_layout()
out = "/home/elcasnix/Projects/ehcastroh-teach/EDD_Agent_Evals/images/eval_matrix.png"
plt.savefig(out, dpi=180, bbox_inches="tight", facecolor="white")
print(f"wrote {out}")
