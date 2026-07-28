"""Entrypoint. Wires the LLM client, tools, and agent together.

Usage:
    python -m agent.main --max-steps 100 --target http://localhost:3000
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console

from .agent import PentestAgent
from .llm import LLMClient
from . import tools  # noqa: F401 — triggers tool registration


def main() -> int:
    load_dotenv()
    console = Console()

    parser = argparse.ArgumentParser(description="Juice Shop pentest agent.")
    parser.add_argument(
        "--target",
        default=os.environ.get("TARGET_URL", "http://localhost:3000"),
        help="Target URL (default: TARGET_URL env or http://localhost:3000)",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=int(os.environ.get("MAX_STEPS", "100")),
        help="Max agent iterations",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("LLM_MODEL"),
        help="LiteLLM-compatible model identifier",
    )
    parser.add_argument(
        "--report",
        default="reports/final_report.md",
        help="Where to write the final pentest report",
    )
    parser.add_argument(
        "--log-dir",
        default="agent_logs",
        help="Directory for run logs (one subdir per run)",
    )
    args = parser.parse_args()

    os.environ["TARGET_URL"] = args.target
    log_dir = Path(args.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    console.rule("[bold cyan]Juice Shop Pentest Agent")
    console.print(f"  target: {args.target}")
    console.print(f"  model:  {args.model}")
    console.print(f"  steps:  {args.max_steps}")

    llm = LLMClient(model=args.model)
    agent = PentestAgent(
        llm=llm,
        target_url=args.target,
        max_steps=args.max_steps,
        log_dir=log_dir,
    )

    try:
        summary = agent.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/yellow]")
        return 130

    console.rule("[bold cyan]Run complete")
    for k, v in summary.items():
        console.print(f"  {k}: {v}")

    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    agent.generate_report(report_path)
    console.print(f"\n[green]Report written to {report_path}[/green]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
