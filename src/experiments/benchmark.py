from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys
from typing import Iterable, List

from src.experiments.aggregate import aggregate_runs
from src.experiments.io import load_run_record
from src.utils import _dump_json


@dataclass(frozen=True)
class BenchmarkVariant:
    name: str
    overrides: tuple[str, ...]


@dataclass(frozen=True)
class BenchmarkCase:
    name: str
    overrides: tuple[str, ...]


def _default_variants() -> list[BenchmarkVariant]:
    return [
        BenchmarkVariant("exact", ("method=exact",)),
        BenchmarkVariant(
            "boss_selective_explicit",
            (
                "method=boss",
                "method.rank_policy=fixed",
                "method.target_rank=2",
                "method.max_rank=8",
                "method.implicit_merge_sketch=false",
            ),
        ),
        BenchmarkVariant(
            "boss_selective_implicit",
            (
                "method=boss",
                "method.rank_policy=fixed",
                "method.target_rank=2",
                "method.max_rank=8",
                "method.implicit_merge_sketch=true",
            ),
        ),
        BenchmarkVariant(
            "boss_force_explicit",
            (
                "method=boss",
                "method.rank_policy=fixed",
                "method.target_rank=2",
                "method.max_rank=8",
                "method.implicit_merge_sketch=false",
                "method.compress_min_rank_product=0",
                "method.compress_max_exact_size=0",
                "method.compress_min_saving_ratio=0.0",
            ),
        ),
        BenchmarkVariant(
            "boss_force_implicit",
            (
                "method=boss",
                "method.rank_policy=fixed",
                "method.target_rank=2",
                "method.max_rank=8",
                "method.implicit_merge_sketch=true",
                "method.compress_min_rank_product=0",
                "method.compress_max_exact_size=0",
                "method.compress_min_saving_ratio=0.0",
            ),
        ),
    ]


def _rank_sweep_variants(ranks: Iterable[int]) -> list[BenchmarkVariant]:
    variants: list[BenchmarkVariant] = [BenchmarkVariant("exact", ("method=exact",))]
    for rank in ranks:
        variants.append(
            BenchmarkVariant(
                f"boss_selective_explicit_r{rank}",
                (
                    "method=boss",
                    "method.rank_policy=fixed",
                    f"method.target_rank={int(rank)}",
                    f"method.max_rank={max(int(rank), 8)}",
                    "method.implicit_merge_sketch=false",
                ),
            )
        )
        variants.append(
            BenchmarkVariant(
                f"boss_selective_implicit_r{rank}",
                (
                    "method=boss",
                    "method.rank_policy=fixed",
                    f"method.target_rank={int(rank)}",
                    f"method.max_rank={max(int(rank), 8)}",
                    "method.implicit_merge_sketch=true",
                ),
            )
        )
    return variants


def _preset_cases(preset: str) -> list[BenchmarkCase]:
    common = (
        "task.compute_exact_reference=true",
        "task.save_output_dense=false",
        "block.block_labels=2",
        "block.chunk_size=1",
        "seed=0",
    )
    if preset == "m4_probe":
        return [
            BenchmarkCase(
                "ring7_p3_b6_r2",
                (
                    "data=ring",
                    "data.num_nodes=7",
                    "data.phys_dim=3",
                    "data.bond_dim=6",
                )
                + common,
            ),
            BenchmarkCase(
                "random7_p3_b5_r2",
                (
                    "data=random_connected",
                    "data.num_nodes=7",
                    "data.phys_dim=3",
                    "data.bond_dim=5",
                    "data.edge_prob=0.45",
                )
                + common,
            ),
        ]
    if preset == "smoke":
        return [
            BenchmarkCase(
                "ring5_p2_b3_r2",
                (
                    "data=ring",
                    "data.num_nodes=5",
                    "data.phys_dim=2",
                    "data.bond_dim=3",
                )
                + common,
            ),
        ]
    raise ValueError(f"Unknown benchmark preset: {preset}")


def build_benchmark_plan(preset: str) -> list[tuple[BenchmarkCase, BenchmarkVariant]]:
    if preset == "rank_sweep":
        variants = _rank_sweep_variants((2, 4, 6, 8, 12, 16, 24))
    else:
        variants = _default_variants()
    return [(case, variant) for case in _preset_cases(preset if preset != "rank_sweep" else "m4_probe") for variant in variants]


def _run_single(
    *,
    python_exe: str,
    repo_root: Path,
    suite: str,
    case: BenchmarkCase,
    variant: BenchmarkVariant,
) -> Path:
    experiment_group = f"benchmarks/{suite}"
    experiment_name = f"{case.name}__{variant.name}"
    cmd = [
        python_exe,
        "run.py",
        f"experiment.group={experiment_group}",
        f"experiment.name={experiment_name}",
        *case.overrides,
        *variant.overrides,
    ]
    subprocess.run(cmd, cwd=repo_root, check=True)
    run_root = repo_root / "outputs" / "benchmarks" / suite / experiment_name
    candidates = [path for path in run_root.iterdir() if path.is_dir()]
    if not candidates:
        raise RuntimeError(f"No run directories found for {experiment_name}")
    return max(candidates, key=lambda path: path.name)


def _write_suite_metadata(
    *,
    repo_root: Path,
    suite: str,
    preset: str,
    plan: Iterable[tuple[BenchmarkCase, BenchmarkVariant]],
    run_dirs: list[Path],
) -> Path:
    suite_root = repo_root / "outputs" / "benchmarks" / suite
    plan_rows = []
    for case, variant in plan:
        plan_rows.append(
            {
                "case": case.name,
                "variant": variant.name,
                "case_overrides": list(case.overrides),
                "variant_overrides": list(variant.overrides),
            }
        )
    _dump_json(
        suite_root / "benchmark_plan.json",
        {
            "suite": suite,
            "preset": preset,
            "created_at": datetime.now().isoformat(),
            "runs": plan_rows,
            "run_dirs": [str(path) for path in run_dirs],
        },
    )
    return suite_root


def _write_comparison_report(suite_root: Path, run_dirs: list[Path]) -> Path:
    records = []
    for run_dir in run_dirs:
        record = load_run_record(run_dir)
        if record is not None:
            records.append(record)
    _dump_json(suite_root / "benchmark_results.json", records)
    return suite_root / "benchmark_results.json"


def run_benchmark_suite(
    *,
    preset: str,
    suite: str | None = None,
    repo_root: Path | str | None = None,
    python_exe: str | None = None,
) -> dict[str, Path]:
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    exe = python_exe if python_exe is not None else sys.executable
    suite_name = suite or f"{preset}_{datetime.now():%Y%m%d_%H%M%S}"
    plan = build_benchmark_plan(preset)
    run_dirs: list[Path] = []
    for case, variant in plan:
        run_dirs.append(
            _run_single(
                python_exe=exe,
                repo_root=root,
                suite=suite_name,
                case=case,
                variant=variant,
            )
        )
    suite_root = _write_suite_metadata(
        repo_root=root,
        suite=suite_name,
        preset=preset,
        plan=plan,
        run_dirs=run_dirs,
    )
    summary_paths = aggregate_runs(suite_root, suite_root / "summary")
    report_path = _write_comparison_report(suite_root, run_dirs)
    return {
        "suite_root": suite_root,
        "summary_csv": summary_paths["csv"],
        "summary_jsonl": summary_paths["jsonl"],
        "results_json": report_path,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a predefined benchmark suite and aggregate the results.")
    parser.add_argument("--preset", default="m4_probe", help="Benchmark preset name.")
    parser.add_argument("--suite", default=None, help="Optional suite name. Defaults to a timestamped name.")
    args = parser.parse_args()
    outputs = run_benchmark_suite(preset=args.preset, suite=args.suite)
    print(json.dumps({key: str(value) for key, value in outputs.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
