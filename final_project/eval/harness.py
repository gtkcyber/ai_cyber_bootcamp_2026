"""Scoring harness CLI.

Usage:
    python -m eval.harness --report                # human-readable scorecard
    python -m eval.harness --json                  # machine-readable JSON
    python -m eval.harness --dry-run               # connectivity + LLM cred check
    python -m eval.harness --target http://...     # override target
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import httpx
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from .score import score_target


def dry_run(target: str, console: Console) -> int:
    ok = True
    console.print(f"[bold]Checking Juice Shop at {target}[/bold]")
    try:
        r = httpx.get(target + "/api/Challenges/", timeout=5.0)
        r.raise_for_status()
        data = r.json()
        n = len(data.get("data", data))
        console.print(f"  [green]OK[/green] — {n} challenges reachable")
    except Exception as e:
        console.print(f"  [red]FAIL[/red] — {e}")
        console.print("  Is Juice Shop running? Try: [cyan]docker compose up -d juiceshop[/cyan]")
        ok = False

    console.print("\n[bold]Checking LLM credentials[/bold]")
    model = os.environ.get("LLM_MODEL")
    if not model:
        console.print("  [red]FAIL[/red] — LLM_MODEL not set in environment (.env)")
        ok = False
    else:
        try:
            from agent.llm import LLMClient, Message

            client = LLMClient(model=model)
            resp = client.complete(
                messages=[Message(role="user", content="Reply with the single word: ok")],
            )
            content = (resp.content or "").strip().lower()
            if "ok" in content:
                console.print(f"  [green]OK[/green] — {model} responded")
            else:
                console.print(
                    f"  [yellow]WARN[/yellow] — {model} responded, but content was: {content!r}"
                )
        except Exception as e:
            console.print(f"  [red]FAIL[/red] — {type(e).__name__}: {e}")
            ok = False
    return 0 if ok else 1


def human_report(target: str, console: Console) -> int:
    card = score_target(target)
    console.rule(f"[bold cyan]Scorecard — {target}")
    console.print(
        f"Solved: [bold green]{card.solved}[/bold green] / {card.total} "
        f"({card.fraction:.1%})"
    )

    table = Table(title="By category")
    table.add_column("Category")
    table.add_column("Solved")
    table.add_column("Total")
    for cat, (s, t) in sorted(card.by_category().items()):
        table.add_row(cat, str(s), str(t))
    console.print(table)

    solved = card.solved_challenges()
    if solved:
        table2 = Table(title="Solved challenges")
        table2.add_column("Difficulty", justify="right")
        table2.add_column("Category")
        table2.add_column("Name")
        for c in sorted(solved, key=lambda x: (x.difficulty, x.category, x.name)):
            table2.add_row(str(c.difficulty), c.category, c.name)
        console.print(table2)
    return 0


def json_report(target: str) -> int:
    card = score_target(target)
    payload = {
        "target": card.target,
        "solved": card.solved,
        "total": card.total,
        "fraction": card.fraction,
        "by_category": {k: {"solved": s, "total": t} for k, (s, t) in card.by_category().items()},
        "challenges": [
            {
                "key": c.key,
                "name": c.name,
                "category": c.category,
                "difficulty": c.difficulty,
                "solved": c.solved,
            }
            for c in card.challenges
        ],
    }
    print(json.dumps(payload, indent=2))
    return 0


def main() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Juice Shop scoring harness.")
    parser.add_argument(
        "--target",
        default=os.environ.get("TARGET_URL", "http://localhost:3000"),
        help="Target URL",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true", help="Connectivity + LLM check")
    group.add_argument("--report", action="store_true", help="Human-readable scorecard")
    group.add_argument("--json", action="store_true", help="Machine-readable JSON")
    args = parser.parse_args()

    console = Console()
    if args.dry_run:
        return dry_run(args.target, console)
    if args.json:
        return json_report(args.target)
    return human_report(args.target, console)


if __name__ == "__main__":
    sys.exit(main())
