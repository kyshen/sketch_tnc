from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List

from src.experiments.io import load_run_record, write_summary


def _iter_run_dirs(search_root: Path) -> Iterable[Path]:
    for path in search_root.rglob("*"):
        if not path.is_dir():
            continue
        record = load_run_record(path)
        if record is not None:
            yield path


def aggregate_runs(search_root: Path | str, output_dir: Path | str | None = None) -> dict[str, Path]:
    root = Path(search_root)
    summary_dir = Path(output_dir) if output_dir is not None else root / "summary"
    records: List[dict] = []
    for run_dir in _iter_run_dirs(root):
        record = load_run_record(run_dir)
        if record is not None:
            records.append(record)
    records.sort(key=lambda row: str(row.get("run_dir", "")))
    return write_summary(records, summary_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate experiment outputs into summary tables.")
    parser.add_argument("search_root", type=Path, help="Directory containing Hydra run outputs.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for summary files. Defaults to <search_root>/summary.",
    )
    args = parser.parse_args()
    aggregate_runs(args.search_root, args.output_dir)


if __name__ == "__main__":
    main()
