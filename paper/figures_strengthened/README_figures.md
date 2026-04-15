# Strengthened figures

## fig_pareto_frontier
- CSV: `reproduce/csv_strengthened/pareto_sweep.csv`
- Recommended placement: main text
- Recommended label: `fig:pareto_frontier`
- Recommended width: `\columnwidth`
- Caption draft: ASTNC forms a continuous set of operating points rather than only a few discrete presets. Solid markers and connecting lines trace the non-dominated frontier, while lighter hollow markers indicate dominated sweep settings. The Grid 3x3 case exhibits a visibly broader speed-accuracy trade-off than Random-8, which remains comparatively stable across the aligned sweep.

## fig_mechanism_fingerprint_grid
- CSV: `reproduce/csv_strengthened/mechanism_internal_ablation.csv`
- Recommended placement: appendix
- Recommended label: `fig:mechanism_fingerprint_grid`
- Recommended width: `\columnwidth`
- Caption draft: Internal metrics reveal that the mechanism variants do not fail in the same way. Removing blockwise processing primarily raises error and peak rank, removing implicit merge sketches mainly increases runtime, and disabling cache sharply collapses reuse statistics while also slowing execution. The matrix is normalized per metric to highlight behavioral fingerprints rather than raw scale differences.

## fig_blockwise_operating_points_grid
- CSV: `reproduce/csv_strengthened/blockwise_sensitivity.csv`
- Recommended placement: appendix
- Recommended label: `fig:blockwise_operating_points_grid`
- Recommended width: `\columnwidth`
- Caption draft: Blockwise settings define a design space rather than a single isolated table entry. In the main panel, point area encodes peak rank and color encodes cache hit rate, revealing how runtime, approximation error, rank growth, and reuse co-vary across the practical operating region. The inset separates the near-exact `b1_c1` corner so that the paper default `b2_c1` remains readable as a balanced interior operating point rather than being visually flattened by an extreme error scale.

## fig_cache_reuse_pairs_grid
- CSV: `reproduce/csv_strengthened/cache_reuse_evidence.csv`
- Recommended placement: main text
- Recommended label: `fig:cache_reuse_pairs_grid`
- Recommended width: `0.9\columnwidth`
- Caption draft: Cache reuse produces a clean paired gain under aligned settings. For both `b2_c1` and `b2_c2`, enabling cache reduces total time relative to the matched cache-off run, with the strongest absolute gain appearing at the paper default `b2_c1`. The hit-rate annotations make the reuse effect concrete without adding table-like clutter.

## fig_strength_sensitivity_trend
- CSV: `reproduce/csv_strengthened/strength_sensitivity.csv`
- Recommended placement: main text
- Recommended label: `fig:strength-sensitivity-trend`
- Recommended width: `0.92\columnwidth`
- Caption draft: Approximation strength acts as a stable error-control knob. Across all four core cases, relative error rises from \textsf{L1} to \textsf{L2} and again to \textsf{L3}; the thicker black line marks the average trend. Because the \textsf{L1} points are near machine precision, the plot uses a log-scale y-axis and displays them at a small visual floor for readability.
