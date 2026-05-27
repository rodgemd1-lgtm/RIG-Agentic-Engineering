"""rigforge status — Show platform status."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from rigforge.utils.fs import runs_dir

console = Console()


def register(app: typer.Typer) -> None:
    @app.command("status")
    def status_command(
        repo: str = typer.Option(".", "--repo", help="Repository root"),
    ) -> None:
        """Show platform status."""
        repo_root = Path(repo).resolve()
        rd = runs_dir(repo_root)

        # Scan runs
        active_runs = []
        blocked_runs = []

        if rd.exists():
            for run_path in sorted(rd.iterdir()):
                if not run_path.is_dir():
                    continue
                envelope_path = run_path / "RunEnvelope.json"
                contract_path = run_path / "DoneContract.yaml"

                if envelope_path.exists():
                    import json
                    envelope = json.loads(envelope_path.read_text())
                    status = envelope.get("status", "unknown")

                    if contract_path.exists():
                        import yaml
                        contract = yaml.safe_load(contract_path.read_text())
                        if not contract.get("approved", False):
                            blocked_runs.append((run_path.name, status))
                            continue

                    active_runs.append((run_path.name, status))

        console.print(f"\n[bold]rigforge status[/bold]\n")

        # Active runs
        console.print(f"[cyan]Active runs:[/cyan] {len(active_runs)}")
        for run_id, status in active_runs:
            console.print(f"  • {run_id} ({status})")

        # Blocked runs
        console.print(f"\n[yellow]Blocked runs:[/yellow] {len(blocked_runs)}")
        for run_id, status in blocked_runs:
            console.print(f"  • {run_id} ({status})")

        # Approval queue
        console.print(f"\n[cyan]Approval queue:[/cyan] {len(blocked_runs)} pending")

        # Agent health (stub)
        console.print(f"\n[cyan]Agent health:[/cyan]")
        console.print(f"  archon:  ready")
        console.print(f"  deerflow: ready")
        console.print(f"  pycode:  ready")

        # Service health (stub)
        console.print(f"\n[cyan]Service health:[/cyan]")
        console.print(f"  litellm:  ready")
        console.print(f"  langfuse: ready")

        # Cost today (stub)
        console.print(f"\n[cyan]Cost today:[/cyan] $0.00")

        # Latest incidents (stub)
        console.print(f"\n[cyan]Latest incidents:[/cyan] none")

        console.print()
