from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.lines import Line2D


ROOT = Path(__file__).resolve().parent.parent
CSV_DIR = ROOT / "reproduce" / "csv_strengthened"
OUT_DIR = ROOT / "paper" / "figures_strengthened"


PALETTE = {
    "ink": "#222222",
    "slate": "#5F6C7B",
    "blue": "#3A6EA5",
    "sand": "#C7B38A",
    "light": "#D9DEE5",
}

HEATMAP_CMAP = LinearSegmentedColormap.from_list(
    "paper_blues",
    ["#F7F8FA", "#D9E3EE", "#8DA7C2", "#3A6EA5"],
)
SCATTER_CMAP = LinearSegmentedColormap.from_list(
    "paper_cache",
    ["#D8DDE3", "#9CA9B5", "#3A6EA5"],
)


def setup_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8.5,
            "axes.titlesize": 9,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "legend.fontsize": 7.5,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.edgecolor": "#666666",
            "axes.linewidth": 0.7,
            "axes.grid": False,
            "xtick.color": "#333333",
            "ytick.color": "#333333",
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "xtick.major.size": 3.0,
            "ytick.major.size": 3.0,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.03,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "figure.dpi": 180,
        }
    )


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def numeric(value: str) -> float:
    if value is None or value == "":
        return math.nan
    if value.lower() in {"true", "false"}:
        return float(value.lower() == "true")
    return float(value)


def save_figure(fig: plt.Figure, stem: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / f"{stem}.pdf")
    fig.savefig(OUT_DIR / f"{stem}.png", dpi=400)
    plt.close(fig)


def is_non_dominated(points: list[dict[str, float]], idx: int) -> bool:
    target = points[idx]
    for j, other in enumerate(points):
        if j == idx:
            continue
        if (
            other["rel_error"] <= target["rel_error"]
            and other["speedup_vs_exact"] >= target["speedup_vs_exact"]
            and (
                other["rel_error"] < target["rel_error"]
                or other["speedup_vs_exact"] > target["speedup_vs_exact"]
            )
        ):
            return False
    return True


def make_pareto_frontier() -> None:
    rows = read_csv(CSV_DIR / "pareto_sweep.csv")
    rows = [row for row in rows if row["case"] in {"Grid 3x3", "Ring-8"} and row["status"] == "ok"]
    case_styles = {
        "Grid 3x3": {"color": PALETTE["blue"], "marker": "o", "linestyle": "-"},
        "Ring-8": {"color": PALETTE["slate"], "marker": "s", "linestyle": "--"},
    }

    fig, ax = plt.subplots(figsize=(6.2, 3.3))
    for case_name in ("Grid 3x3", "Ring-8"):
        case_rows = []
        for row in rows:
            if row["case"] != case_name:
                continue
            case_rows.append(
                {
                    "sweep_id": row["sweep_id"],
                    "rel_error": numeric(row["rel_error"]),
                    "speedup_vs_exact": numeric(row["speedup_vs_exact"]),
                }
            )

        style = case_styles[case_name]
        frontier = [point for i, point in enumerate(case_rows) if is_non_dominated(case_rows, i)]
        frontier.sort(key=lambda item: item["rel_error"])

        ax.scatter(
            [point["rel_error"] for point in case_rows],
            [point["speedup_vs_exact"] for point in case_rows],
            s=24,
            marker=style["marker"],
            color=style["color"],
            alpha=0.28,
            linewidths=0,
            zorder=1,
        )
        ax.plot(
            [point["rel_error"] for point in frontier],
            [point["speedup_vs_exact"] for point in frontier],
            color=style["color"],
            linewidth=1.4,
            linestyle=style["linestyle"],
            zorder=2,
        )
        ax.scatter(
            [point["rel_error"] for point in frontier],
            [point["speedup_vs_exact"] for point in frontier],
            s=40,
            marker=style["marker"],
            facecolor=style["color"],
            edgecolor="white",
            linewidth=0.55,
            zorder=3,
        )

        if frontier:
            for point in (frontier[0], frontier[-1]):
                ax.annotate(
                    point["sweep_id"],
                    (point["rel_error"], point["speedup_vs_exact"]),
                    xytext=(5, 4),
                    textcoords="offset points",
                    fontsize=7,
                    color=style["color"],
                )

    ax.set_xscale("log")
    ax.set_xlabel("Relative error")
    ax.set_ylabel("Speedup vs. exact")
    ax.set_xlim(1e-15, 7e-2)
    ax.set_ylim(10, 110)
    ax.legend(
        handles=[
            Line2D([0], [0], color=PALETTE["blue"], marker="o", linestyle="-", markersize=4, label="Grid 3x3"),
            Line2D([0], [0], color=PALETTE["slate"], marker="s", linestyle="--", markersize=4, label="Ring-8"),
        ],
        loc="lower right",
        frameon=False,
    )
    ax.text(
        0.02,
        0.96,
        "Filled markers indicate non-dominated operating points.",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=7,
        color=PALETTE["slate"],
    )
    fig.tight_layout()
    save_figure(fig, "fig_pareto_frontier")


def fmt_metric(metric: str, value: float) -> str:
    if metric == "rel_error":
        return f"{value:.1e}"
    if metric == "total_time_sec":
        return f"{value:.2f}s"
    if metric in {"peak_rank", "num_cached_states"}:
        return f"{value:.0f}"
    if metric == "num_implicit_merge_sketches":
        return f"{value:.1f}"
    if metric == "cache_hit_rate":
        return f"{100.0 * value:.0f}%"
    return f"{value:.2f}"


def make_mechanism_fingerprint() -> None:
    rows = read_csv(CSV_DIR / "mechanism_internal_ablation.csv")
    selected = ["ASTNC default", "no-blockwise", "no-implicit", "no-cache"]
    metric_order = [
        "rel_error",
        "total_time_sec",
        "peak_rank",
        "num_implicit_merge_sketches",
        "cache_hit_rate",
        "num_cached_states",
    ]
    metric_labels = [
        "Relative\nerror",
        "Total time",
        "Peak\nrank",
        "Implicit\nsketches",
        "Cache\nhit rate",
        "Cached\nstates",
    ]
    baseline = next(row for row in rows if row["setting"] == "ASTNC default")

    values = np.zeros((len(selected), len(metric_order)))
    cell_text: list[list[str]] = []
    for row_idx, setting in enumerate(selected):
        row = next(row for row in rows if row["setting"] == setting)
        row_text: list[str] = []
        for col_idx, metric in enumerate(metric_order):
            value = numeric(row[metric])
            base = numeric(baseline[metric])
            if metric in {"rel_error", "total_time_sec", "peak_rank"}:
                raw = max(0.0, math.log2(max(value, 1e-15) / max(base, 1e-15)))
            else:
                raw = max(0.0, (base - value) / max(base, 1e-12))
            values[row_idx, col_idx] = raw
            row_text.append(fmt_metric(metric, value))
        cell_text.append(row_text)

    for col_idx in range(values.shape[1]):
        col_max = values[:, col_idx].max()
        if col_max > 0:
            values[:, col_idx] /= col_max

    fig, ax = plt.subplots(figsize=(6.4, 2.6))
    im = ax.imshow(values, cmap=HEATMAP_CMAP, vmin=0.0, vmax=1.0, aspect="auto")
    ax.set_xticks(range(len(metric_labels)), metric_labels)
    ax.set_yticks(range(len(selected)), selected)
    ax.set_xlabel("Internal metrics (normalized by observed degradation)")

    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            tone = "white" if values[i, j] > 0.55 else PALETTE["ink"]
            ax.text(
                j,
                i,
                cell_text[i][j],
                ha="center",
                va="center",
                fontsize=7,
                color=tone,
            )

    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks(np.arange(-0.5, values.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-0.5, values.shape[0], 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.8)
    ax.tick_params(which="minor", bottom=False, left=False)

    cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cbar.set_label("Relative mechanism disruption", rotation=90)
    cbar.outline.set_linewidth(0.5)

    fig.tight_layout()
    save_figure(fig, "fig_mechanism_fingerprint_grid")


def setting_label(row: dict[str, str]) -> str:
    if row["block_enabled"].lower() == "false":
        return "block_disabled"
    return f"b{int(numeric(row['block_labels']))}_c{int(numeric(row['chunk_size']))}"


def scale_sizes(values: list[float], low: float = 60.0, high: float = 240.0) -> list[float]:
    min_v, max_v = min(values), max(values)
    if math.isclose(min_v, max_v):
        return [0.5 * (low + high)] * len(values)
    return [low + (value - min_v) / (max_v - min_v) * (high - low) for value in values]


def make_blockwise_operating_points() -> None:
    rows = read_csv(CSV_DIR / "blockwise_sensitivity.csv")
    chosen = {"block_disabled", "b1_c1", "b2_c1", "b2_c2", "b3_c1"}
    points = []
    for row in rows:
        if row["case"] != "Grid 3x3" or row["status"] != "ok":
            continue
        label = setting_label(row)
        if label not in chosen:
            continue
        points.append(
            {
                "label": label,
                "time": numeric(row["total_time_sec"]),
                "error": numeric(row["rel_error"]),
                "rank": numeric(row["peak_rank"]),
                "cache": numeric(row["cache_hit_rate"]),
            }
        )

    sizes = scale_sizes([point["rank"] for point in points])
    fig, ax = plt.subplots(figsize=(5.6, 3.5))
    scatter = ax.scatter(
        [point["time"] for point in points],
        [point["error"] for point in points],
        s=sizes,
        c=[point["cache"] for point in points],
        cmap=SCATTER_CMAP,
        norm=Normalize(vmin=0.0, vmax=0.5),
        edgecolors="white",
        linewidths=0.75,
        zorder=3,
    )

    for point in points:
        if point["label"] == "b2_c1":
            ax.scatter(
                [point["time"]],
                [point["error"]],
                s=scale_sizes([point["rank"]], 280, 280),
                facecolors="none",
                edgecolors=PALETTE["ink"],
                linewidths=1.0,
                zorder=4,
            )
            ax.annotate(
                "b2_c1 (paper default)",
                (point["time"], point["error"]),
                xytext=(12, -14),
                textcoords="offset points",
                fontsize=7.2,
                color=PALETTE["ink"],
                arrowprops={"arrowstyle": "-", "lw": 0.6, "color": PALETTE["ink"]},
            )
        else:
            ax.annotate(
                point["label"],
                (point["time"], point["error"]),
                xytext=(5, 5),
                textcoords="offset points",
                fontsize=7,
                color=PALETTE["ink"],
            )

    ax.set_xlabel("Total time (s)")
    ax.set_ylabel("Relative error")
    ax.set_yscale("log")
    ax.set_xlim(0.16, 0.90)
    ax.set_ylim(1e-13, 2e-2)

    size_handles = [
        plt.scatter([], [], s=size, color=PALETTE["light"], edgecolors="white", linewidths=0.75)
        for size in scale_sizes([64.0, 222.0])
    ]
    ax.legend(
        size_handles,
        ["Peak rank 64", "Peak rank 222"],
        frameon=False,
        loc="lower right",
        title="Point area",
        title_fontsize=7.5,
    )

    cbar = fig.colorbar(scatter, ax=ax, fraction=0.045, pad=0.025)
    cbar.set_label("Cache hit rate", rotation=90)
    ticks = [0.0, 0.25, 0.5]
    cbar.set_ticks(ticks)
    cbar.set_ticklabels([f"{100 * tick:.0f}%" for tick in ticks])
    cbar.outline.set_linewidth(0.5)

    fig.tight_layout()
    save_figure(fig, "fig_blockwise_operating_points_grid")


def make_cache_reuse_pairs() -> None:
    rows = read_csv(CSV_DIR / "cache_reuse_evidence.csv")
    rows = [row for row in rows if row["case"] == "Grid 3x3" and row["setting_id"] in {"b2_c1", "b2_c2"}]
    ordered_settings = ["b2_c1", "b2_c2"]
    y_positions = {"b2_c1": 1, "b2_c2": 0}

    fig, ax = plt.subplots(figsize=(5.8, 2.5))
    for setting in ordered_settings:
        pair = [row for row in rows if row["setting_id"] == setting]
        cache_on = next(row for row in pair if row["cache_enabled"].lower() == "true")
        cache_off = next(row for row in pair if row["cache_enabled"].lower() == "false")
        y = y_positions[setting]
        x_on = numeric(cache_on["total_time_sec"])
        x_off = numeric(cache_off["total_time_sec"])

        ax.plot([x_on, x_off], [y, y], color=PALETTE["slate"], linewidth=1.4, zorder=1)
        ax.scatter(
            [x_off],
            [y],
            s=42,
            facecolors="white",
            edgecolors=PALETTE["ink"],
            linewidths=0.9,
            zorder=3,
        )
        ax.scatter(
            [x_on],
            [y],
            s=42,
            color=PALETTE["blue"],
            edgecolors="white",
            linewidths=0.6,
            zorder=4,
        )

        ratio = x_off / x_on
        ax.text((x_on + x_off) / 2.0, y + 0.13, f"{ratio:.2f}x", ha="center", va="bottom", fontsize=7, color=PALETTE["slate"])
        hit_rate = numeric(cache_on["cache_hit_rate"])
        ax.text(x_on - 0.003, y - 0.15, f"{100 * hit_rate:.0f}% hits", ha="right", va="top", fontsize=7, color=PALETTE["blue"])

        label = f"{setting} (paper default)" if setting == "b2_c1" else setting
        ax.text(0.664, y, label, ha="left", va="center", fontsize=7.5, color=PALETTE["ink"])

    ax.set_yticks([])
    ax.set_xlabel("Total time (s)")
    ax.set_xlim(0.52, 0.67)
    ax.set_ylim(-0.5, 1.5)
    ax.legend(
        handles=[
            Line2D([0], [0], marker="o", linestyle="", markerfacecolor=PALETTE["blue"], markeredgecolor="white", markersize=5.5, label="cache on"),
            Line2D([0], [0], marker="o", linestyle="", markerfacecolor="white", markeredgecolor=PALETTE["ink"], markersize=5.5, label="cache off"),
        ],
        loc="lower right",
        frameon=False,
    )

    fig.tight_layout()
    save_figure(fig, "fig_cache_reuse_pairs_grid")


def write_readme() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    content = """# Strengthened figures

## fig_pareto_frontier
- CSV: `reproduce/csv_strengthened/pareto_sweep.csv`
- Recommended placement: main text
- Recommended label: `fig:pareto_frontier`
- Recommended width: `\\columnwidth`
- Caption draft: ASTNC forms a continuous set of operating points rather than only a few discrete presets. Filled markers trace the non-dominated frontier under the aligned tolerance sweep, while lighter markers show dominated alternatives. The Grid 3x3 case is visibly more trade-off sensitive, whereas Ring-8 stays comparatively stable across the sweep.

## fig_mechanism_fingerprint_grid
- CSV: `reproduce/csv_strengthened/mechanism_internal_ablation.csv`
- Recommended placement: appendix
- Recommended label: `fig:mechanism_fingerprint_grid`
- Recommended width: `\\columnwidth`
- Caption draft: Internal metrics reveal that the mechanism variants do not fail in the same way. Removing blockwise processing primarily raises error and peak rank, removing implicit merge sketches mainly increases runtime, and disabling cache sharply collapses reuse statistics while also slowing execution. The matrix is normalized per metric to highlight behavioral fingerprints rather than raw scale differences.

## fig_blockwise_operating_points_grid
- CSV: `reproduce/csv_strengthened/blockwise_sensitivity.csv`
- Recommended placement: appendix
- Recommended label: `fig:blockwise_operating_points_grid`
- Recommended width: `\\columnwidth`
- Caption draft: The blockwise configuration induces a design space rather than a single isolated table entry. Point area encodes peak rank and color encodes cache hit rate, making it easy to see how accuracy, runtime, rank growth, and reuse co-vary. The paper default `b2_c1` sits near the middle as a balanced operating point rather than an extreme corner.

## fig_cache_reuse_pairs_grid
- CSV: `reproduce/csv_strengthened/cache_reuse_evidence.csv`
- Recommended placement: main text
- Recommended label: `fig:cache_reuse_pairs_grid`
- Recommended width: `0.9\\columnwidth`
- Caption draft: Cache reuse produces a clean paired gain under aligned settings. For both `b2_c1` and `b2_c2`, enabling cache reduces total time relative to the matched cache-off run, with the strongest absolute gain appearing at the paper default `b2_c1`. The hit-rate annotations make the reuse effect concrete without adding table-like clutter.
"""
    (OUT_DIR / "README_figures.md").write_text(content, encoding="utf-8")


def main() -> None:
    setup_style()
    make_pareto_frontier()
    make_mechanism_fingerprint()
    make_blockwise_operating_points()
    make_cache_reuse_pairs()
    write_readme()
    print(f"Wrote figures to {OUT_DIR}")


if __name__ == "__main__":
    main()
