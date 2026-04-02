# BOSS-TNC (experiment-style repository)

This repository reorganizes the paper-system code into an experiment layout that mirrors your uploaded template:

- `conf.py`: Hydra ConfigStore registration via dataclasses
- `run.py`: one unified experiment entrypoint
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
python run.py exp=paper subexp=ring_exact data=ring method=exact
```

BOSS on a ring with blockwise output:

```bash
python run.py exp=paper subexp=ring_boss data=ring method=boss \
  data.num_nodes=7 data.phys_dim=3 data.bond_dim=6 \
  block.block_labels=2 block.chunk_size=1 \
  method.target_rank=2
```

BOSS on a custom connected graph:

```bash
python run.py exp=paper subexp=custom_boss data=custom_edges method=boss \
  data.num_nodes=8 data.edge_file=examples/custom_graph.yaml \
  data.phys_dim=3 data.bond_dim=5 \
  block.block_labels=2 block.chunk_size=1 \
  method.target_rank=3
```

## Notes

- The environment used to generate this zip did **not** have `hydra-core` installed, so the Hydra entrypoint itself could not be executed here.
- Core algorithm modules, data generators, task orchestration, and tests were smoke-tested directly without Hydra.
- This is a research codebase for paper experiments, not a fully optimized industrial implementation.
