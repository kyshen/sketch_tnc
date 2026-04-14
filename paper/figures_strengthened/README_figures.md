# Strengthened figures

## fig_pareto_frontier
- CSV: `reproduce/csv_strengthened/pareto_sweep.csv`
- Recommended placement: main text
- Recommended label: `fig:pareto_frontier`
- Recommended width: `\columnwidth`
- Caption draft: ASTNC forms a continuous set of operating points rather than only a few discrete presets. Filled markers trace the non-dominated frontier under the aligned tolerance sweep, while lighter markers show dominated alternatives. The Grid 3x3 case is visibly more trade-off sensitive, whereas Ring-8 stays comparatively stable across the sweep.

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
- Caption draft: The blockwise configuration induces a design space rather than a single isolated table entry. Point area encodes peak rank and color encodes cache hit rate, making it easy to see how accuracy, runtime, rank growth, and reuse co-vary. The paper default `b2_c1` sits near the middle as a balanced operating point rather than an extreme corner.

## fig_cache_reuse_pairs_grid
- CSV: `reproduce/csv_strengthened/cache_reuse_evidence.csv`
- Recommended placement: main text
- Recommended label: `fig:cache_reuse_pairs_grid`
- Recommended width: `0.9\columnwidth`
- Caption draft: Cache reuse produces a clean paired gain under aligned settings. For both `b2_c1` and `b2_c2`, enabling cache reduces total time relative to the matched cache-off run, with the strongest absolute gain appearing at the paper default `b2_c1`. The hit-rate annotations make the reuse effect concrete without adding table-like clutter.
