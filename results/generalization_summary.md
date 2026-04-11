# Generalization Summary (Section 3.6)

## Scope and Data Completeness
- Cases: 13 (easy=5, medium=5, boundary=3).
- Methods: ASTNC-L1/L2/L3 + exact + fixed-rank baseline.
- Seeds: easy={0,1,2}, medium={0,1}, boundary={0}.
- Seed reduction reason: medium/boundary are costlier and include timeout risk.

## Direct Answers
1. 主结果泛化：stable regime 数量=5/13。
2. easy->medium->boundary 的 timeout_rate 均值：0.000 -> 0.925 -> 1.000。
3. `L1 dominates L2` 比例：easy=2/5, medium=0/0, boundary=0/0。
4. regime 分布：stable=5, transition=0, boundary=8。
5. boundary 主要问题：timeout 增长、completed_fraction 降低、部分 case 的 exact 锚点缺失。
6. L2 在更难 case 是否更合理：仅能按 case-dependent 推荐，未观察到统一翻盘规律。
7. L3 在更难 case 是否有价值：仅在显著降时延时才有成本效益，需逐 case 判断。
8. 推荐 boundary illustration case: `boundary_ring_12`。
9. 可更强结论：tradeoff 与 regime 边界具有明显 case 依赖性。
10. 需保守结论：`L1 dominates L2` 不能写成全局规律。

## 10-15 Lines Paper-ready Result Abstract
- We evaluated ASTNC generalization across chain/ring/tree/grid2d/random_connected under easy/medium/boundary scales.
- Easy cases mostly preserve the previously observed behavior with usable exact anchors.
- As scale increases to medium, completion pressure rises and method preference becomes workload-dependent.
- Boundary cases show clear stress signals, including higher timeout rates and weaker exact anchoring.
- Therefore, the runtime-accuracy relationship is not a single global law across all topologies.
- `L1 dominates L2` appears in part of the workload space but does not universally hold at larger scales.
- `L2` should be treated as a practical operating point only when supported by per-case data.
- `L3` is beneficial only when its extra approximation yields meaningful runtime relief.
- Recommended settings should be selected per case/regime rather than fixed globally.
- Timeout and anchor-missing events are informative boundary signals, not data to discard.
- The selected boundary case provides a direct illustration of where exact and ASTNC both enter stress.
- These observations support a case-dependent narrative for generalization and boundary behavior.
