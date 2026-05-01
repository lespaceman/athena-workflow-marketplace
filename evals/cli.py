import argparse
import sys
from pathlib import Path

from evals import __version__
from evals.config import load_settings
from evals.logging_setup import configure


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--db", type=Path, default=None, help="SQLite path (default: evals/data/evals.db)"
    )
    parser.add_argument("--log-level", default="INFO")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="evals", description="Skill reliability evaluation pipeline"
    )
    parser.add_argument(
        "--version", action="version", version=f"athena-evals {__version__}"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_discover = sub.add_parser("discover", help="Emit skill.discovered events from seeds")
    _add_common(p_discover)
    p_discover.add_argument("--seeds", type=Path, default=None, help="Path to seeds YAML")

    p_extract = sub.add_parser(
        "extract", help="Fetch SKILL.md and overlays; emit skill.extracted events"
    )
    _add_common(p_extract)
    p_extract.add_argument("--skill", help="Limit to a single skill_id")

    p_eval = sub.add_parser("eval", help="Request and run evaluators")
    _add_common(p_eval)
    p_eval.add_argument("--phase", type=int, choices=[1, 2, 3, 4])
    p_eval.add_argument("--evaluator")
    p_eval.add_argument("--judge-model", default=None)
    p_eval.add_argument("--cost-cap-usd", type=float, default=None)
    p_eval.add_argument("--force", action="store_true", help="Re-run even if cached")
    p_eval.add_argument(
        "--strict", action="store_true", help="Fail run if expected evaluator missing"
    )

    p_project = sub.add_parser("project", help="Rebuild current-state projections")
    _add_common(p_project)
    p_project.add_argument("--rebuild", action="store_true")

    p_report = sub.add_parser("report", help="Render reliability report")
    _add_common(p_report)
    p_report.add_argument("--format", choices=["rich", "jsonl", "md"], default="rich")
    p_report.add_argument(
        "--all", action="store_true", help="Write rich + jsonl + md to runs/<run_id>/"
    )
    p_report.add_argument("--sort-by", default="score")
    p_report.add_argument("--filter-category", default=None)
    p_report.add_argument("--min-tier", choices=["S", "A", "B", "C", "D"], default=None)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure(level=args.log_level)
    settings = load_settings(db_path=args.db)

    if args.command == "discover":
        from evals.extraction.discoverer import run_discover

        return run_discover(settings, seeds_path=args.seeds)
    if args.command == "extract":
        from evals.extraction.extractor import run_extract

        return run_extract(settings, skill_id=args.skill)
    if args.command == "eval":
        from evals.workers.dispatcher import run_eval

        return run_eval(
            settings,
            phase=args.phase,
            evaluator=args.evaluator,
            judge_model=args.judge_model or settings.judge_model,
            cost_cap_usd=args.cost_cap_usd or settings.cost_cap_usd,
            force=args.force,
            strict=args.strict,
        )
    if args.command == "project":
        from evals.events.projections import rebuild_projections

        return rebuild_projections(settings, full=args.rebuild)
    if args.command == "report":
        from evals.reporter.table import run_report

        return run_report(
            settings,
            output_format=args.format,
            write_all=args.all,
            sort_by=args.sort_by,
            filter_category=args.filter_category,
            min_tier=args.min_tier,
        )

    print("[ERROR] Unknown command", file=sys.stderr)
    return 2
