"""
Generate the span tree diagram used in notebook 02.

Purpose
-------
Learners often struggle to picture the parent-child relationships that
OpenTelemetry emits when a decorated agent runs. This diagram shows the
canonical span tree for a query that triggers all three tools, with each
span coloured by its kind (agent / tool / chain / LLM) so the reader can
map the visual to the Concept Check question at the end of Part 3.

Output: images/span_tree.png
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

BERKELEY = "#003262"
GOLD = "#FDB515"
INK = "#2A2C2B"

# Colour by span kind - reused as a legend
KIND_COLORS = {
    "agent": "#003262",  # Berkeley Blue
    "tool":  "#FDB515",  # Gold
    "chain": "#859438",  # Sage
    "LLM":   "#C4820E",  # Rust
}

# Tree definition. Each entry: (label, kind, depth)
# Depth is the indentation level. Order is drawing order (top to bottom).
tree = [
    ("AgentRun",                        "agent", 0),
    ("router LLM call #1",              "LLM",   1),
    ("handle_tool_calls",               "chain", 1),
    ("lookup_sales_data",               "tool",  2),
    ("generate_sql_query LLM call",     "LLM",   3),
    ("router LLM call #2",              "LLM",   1),
    ("handle_tool_calls",               "chain", 1),
    ("analyze_sales_data",              "tool",  2),
    ("analysis LLM call",               "LLM",   3),
    ("router LLM call #3",              "LLM",   1),
    ("handle_tool_calls",               "chain", 1),
    ("generate_visualization",          "chain", 2),
    ("extract_chart_config",            "chain", 3),
    ("structured output LLM call",      "LLM",   4),
    ("create_chart",                    "chain", 3),
    ("code generation LLM call",        "LLM",   4),
    ("router LLM call #4 (final)",      "LLM",   1),
]

fig, ax = plt.subplots(figsize=(12, 11), dpi=140)
ax.set_xlim(0, 12)
ax.set_ylim(-1.5, len(tree) + 2)
ax.axis("off")
fig.patch.set_facecolor("white")

row_h = 0.75
x_pad = 0.5
indent = 0.85
box_h = 0.55

# Draw guide lines for the tree structure
for i, (_, _, depth) in enumerate(tree):
    y = len(tree) - i  # top-down
    if depth > 0:
        # vertical line from parent to this row
        parent_i = None
        for j in range(i - 1, -1, -1):
            if tree[j][2] == depth - 1:
                parent_i = j
                break
        if parent_i is not None:
            py = len(tree) - parent_i
            ax.plot([x_pad + (depth - 1) * indent + 0.15,
                     x_pad + (depth - 1) * indent + 0.15],
                    [y, py - 0.20], color="#B8B8B8", linewidth=1.2, zorder=1)
            ax.plot([x_pad + (depth - 1) * indent + 0.15,
                     x_pad + depth * indent],
                    [y, y], color="#B8B8B8", linewidth=1.2, zorder=1)

# Draw the boxes
for i, (label, kind, depth) in enumerate(tree):
    y = len(tree) - i
    x = x_pad + depth * indent
    color = KIND_COLORS[kind]
    # kind chip
    chip_w = 0.75
    chip = FancyBboxPatch(
        (x, y - box_h / 2), chip_w, box_h,
        boxstyle="round,pad=0.02,rounding_size=0.06",
        linewidth=0, facecolor=color, zorder=3,
    )
    ax.add_patch(chip)
    ax.text(x + chip_w / 2, y, kind, ha="center", va="center",
            fontsize=8.5, color="white", fontweight="bold", zorder=4)
    # label
    ax.text(x + chip_w + 0.25, y, label, ha="left", va="center",
            fontsize=11, color=INK, zorder=4)

# Title
ax.text(6.0, len(tree) + 1.55,
        "Expected span tree for a query that triggers all three tools",
        ha="center", va="center", fontsize=13, fontweight="bold",
        color=BERKELEY)
ax.text(6.0, len(tree) + 1.05,
        'Example: "Show me a scatterplot of sales by store in November 2021, and explain the trend."',
        ha="center", va="center", fontsize=9.5, color=INK, fontstyle="italic")

# Legend, placed below the tree with clear separation
legend_y = -0.85
ax.text(x_pad, legend_y, "Span kinds:",
        ha="left", va="center", fontsize=10.5, fontweight="bold", color=BERKELEY)
lx = x_pad + 1.55
for kind, color in KIND_COLORS.items():
    chip = FancyBboxPatch(
        (lx, legend_y - box_h / 2), 0.75, box_h,
        boxstyle="round,pad=0.02,rounding_size=0.06",
        linewidth=0, facecolor=color,
    )
    ax.add_patch(chip)
    ax.text(lx + 0.375, legend_y, kind, ha="center", va="center",
            fontsize=8.5, color="white", fontweight="bold")
    lx += 1.55

plt.tight_layout()
out = "/home/elcasnix/Projects/ehcastroh-teach/EDD_Agent_Evals/images/span_tree.png"
plt.savefig(out, dpi=180, bbox_inches="tight", facecolor="white")
print(f"wrote {out}")
