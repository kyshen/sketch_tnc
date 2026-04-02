# BOSS-TNC

This repository now uses a more standard Hydra experiment layout:

- `config/`: Hydra config groups for `data`, `method`, `task`, `block`, `experiment`, and `hydra`
- `run.py`: thin Hydra entrypoint
- `src/config`: structured config validation
- `src/experiments`: experiment runner, result serialization, and aggregation utilities
- `src/data`: graph-based tensor-network generators
- `src/methods`: exact and BOSS materialization methods
- `src/tasks`: task orchestration and evaluation
- `src/core`: tensor-network, partition, blocking, and low-rank sketch internals
- `src/tests`: smoke tests

## Install

```bash
pip install -r requirements.txt
```

## Example runs

Exact ring materialization:

```bash
python run.py experiment=paper experiment.name=ring_exact data=ring method=exact
```

BOSS on a ring with blockwise output:

```bash
python run.py experiment=paper experiment.name=ring_boss data=ring method=boss \
  data.num_nodes=7 data.phys_dim=3 data.bond_dim=6 \
  block.block_labels=2 block.chunk_size=1 \
  method.target_rank=2 seed=7
```

BOSS on a custom connected graph:

```bash
python run.py experiment=paper experiment.name=custom_boss data=custom_edges method=boss \
  data.num_nodes=8 data.edge_file=examples/custom_graph.yaml \
  data.phys_dim=3 data.bond_dim=5 \
  block.block_labels=2 block.chunk_size=1 \
  method.target_rank=3 seed=11
```

Aggregate a directory of runs into CSV and JSONL summaries:

```bash
python -m src.experiments.aggregate outputs/paper
```

Each run directory includes:

- `state.mat`
- `eval.json`
- `metrics.json`
- `logs.json`
- `manifest.json`
- `resolved_config.yaml`

## Notes

- The top-level `seed` is treated as the experiment seed and is propagated into both data generation and randomized BOSS compression.
- `eval.json` is preserved for backward compatibility, while `metrics.json` is added for downstream analysis.
- This is a research codebase for paper experiments, not a fully optimized industrial implementation.
