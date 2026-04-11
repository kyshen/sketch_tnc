# Generalization Summary (Section 3.6)

## Scope and Data Completeness
- Cases: 13 total (`easy=5`, `medium=5`, `boundary=3`).
- Topologies covered: `chain`, `ring`, `tree`, `grid2d`, `random_connected`.
- Methods: `ASTNC-L1`, `ASTNC-L2`, `ASTNC-L3`, `exact`, and `fixed-rank baseline` (fixed-rank kept for easy anchors).
- Seeds: easy uses `{0,1,2}`; medium uses `{0,1}`; boundary uses `{0}`.
- Seed reduction reason: larger scales showed strong timeout pressure; reduced seeds preserve topology coverage and boundary signals.

## Direct Answers
1. Which conclusions are stable on easy cases?
   Easy cases are fully stable in this run set: all methods completed (`completed_fraction=1.0` for all five easy cases), exact anchors are available, and ASTNC keeps clear speedups over exact.
2. Which conclusions start changing on medium cases?
   Medium scale is where behavior changes sharply: completion drops to near-zero for most cases, exact anchors disappear, and only `medium_chain_10` retains partial ASTNC completion.
3. Where does boundary regime start?
   Boundary behavior appears already at medium scale in this run budget. All five medium cases are classified as boundary (timeout-driven), not only the nominal boundary scale.
4. Does `L1 dominates L2` still hold at larger scale?
   It holds in part of easy cases (`2/5` strict dominance) and in the only medium case with usable ASTNC pairs (`medium_chain_10`), but coverage is too sparse at larger scales to claim universality.
5. Does `L2` become more reasonable on harder cases?
   Not supported by current data. Harder cases mostly time out before producing enough paired comparisons.
6. Does `L3` show real value on harder cases?
   Not supported in this run set. At medium/boundary scales, `L3` rarely completes, so cost-effectiveness cannot be established.
7. Best boundary illustration case for the paper?
   `boundary_ring_12` (all methods timed out, no exact anchor, clear boundary signal).
8. Which claims can be stronger vs conservative?
   Stronger: easy-regime findings are robust; boundary signals (timeouts + missing exact anchors) are unambiguous.
   Conservative: any global claim about L1/L2/L3 ordering at larger scales.

## 10-15 Lines Paper-ready Result Abstract
- We tested ASTNC generalization across five topologies and three scale bands.
- Easy cases are fully stable: all methods complete and exact anchors are available.
- In easy cases, ASTNC retains strong runtime gains against exact while preserving low error.
- `L1` is often strong in easy cases, but not uniformly dominant in every topology.
- Medium scale is the turning point in this run budget.
- Most medium cases already show boundary-like behavior: high timeout rates and missing exact anchors.
- Nominal boundary cases (`ring_12`, `grid2d_4x4`, `random_12`) show complete timeout across tested methods.
- This indicates a practical regime boundary where exact quickly becomes unusable and ASTNC also enters stress.
- Therefore, conclusions from easy cases should not be extrapolated as global laws.
- Recommended method choice must remain case-dependent.
- Timeout and failure events are informative boundary evidence, not noise to discard.
- The boundary illustration should highlight both anchor loss (exact unavailable) and ASTNC completion collapse.
