from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analysis import explore_scenarios
from .io import load_molecules
from .splitting import SplitConfig, create_split, export_split


def _json_value(value: str | None):
    if value is None:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="molood", description="Explore molecular OOD scenarios and create reproducible splits.")
    sub = parser.add_subparsers(dest="command", required=True)
    explore = sub.add_parser("explore", help="Recommend scenarios for a dataset")
    explore.add_argument("input", type=Path)
    explore.add_argument("--smiles-column", required=True)
    explore.add_argument("--target-column")
    explore.add_argument("--ood-fraction", type=float, default=0.2)
    explore.add_argument("--output", type=Path)

    split = sub.add_parser("split", help="Create and export a split")
    split.add_argument("input", type=Path)
    split.add_argument("--smiles-column", required=True)
    split.add_argument("--target-column")
    split.add_argument("--scenario", required=True, help="random, scaffold, size, element, or property:mw/logp/tpsa")
    split.add_argument("--threshold", help="Number, string, or JSON object from the explore report")
    split.add_argument("--seed", type=int, default=42)
    split.add_argument("--ood-fraction", type=float, default=0.2)
    split.add_argument("--id-calibration-fraction", type=float, default=0.1)
    split.add_argument("--ood-calibration-fraction", type=float, default=0.5)
    split.add_argument("--output-dir", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    frame = load_molecules(args.input, args.smiles_column)
    if args.command == "explore":
        report = explore_scenarios(frame, args.smiles_column, args.target_column, args.ood_fraction)
        report.pop("_featured", None)
        rendered = json.dumps(report, indent=2, ensure_ascii=False)
        if args.output:
            args.output.write_text(rendered + "\n", encoding="utf-8")
        else:
            print(rendered)
        return 0
    config = SplitConfig(
        scenario=args.scenario,
        threshold=_json_value(args.threshold),
        seed=args.seed,
        ood_fraction=args.ood_fraction,
        id_calibration_fraction=args.id_calibration_fraction,
        ood_calibration_fraction=args.ood_calibration_fraction,
    )
    result = create_split(frame, args.smiles_column, config, args.target_column)
    for path in export_split(result, args.output_dir):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

