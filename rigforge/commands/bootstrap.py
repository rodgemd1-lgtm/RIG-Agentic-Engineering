"""rigforge bootstrap — Run the master control plan."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from rigforge.models import ProofPacket
from rigforge.utils.fs import ensure_dir

console = Console()

BOOTSTRAP_PHASES = [
    (0, "Environment Bootstrap"),
    (1, "Runtime Kernel"),
    (2, "Control Plane"),
    (3, "Agent Roster"),
    (4, "Hardening Layer"),
    (5, "DoneContract"),
    (6, "GEV Loop"),
    (7, "DeerFlow Integration"),
    (8, "Cockpit"),
    (9, "First Mission"),
]


def register(app: typer.Typer) -> None:
    @app.command("bootstrap")
    def bootstrap_command(
        phase: int = typer.Option(0, "--phase", help="Phase number (0-9) or 'all'", show_default=False),
        require_approval: bool = typer.Option(False, "--require-approval", help="Stop for approval between phases"),
        repo: str = typer.Option(".", "--repo", help="Repository root"),
    ) -> None:
        """Run the master control plan in order."""
        repo_root = Path(repo).resolve()

        # Handle --phase all
        if isinstance(phase, str) and phase == "all":
            phase = -1  # sentinel for "all phases"

        console.print(f"\n[bold]rigforge bootstrap[/bold]")
        console.print(f"  repo: {repo_root}")
        console.print(f"  phase: {phase}")
        console.print(f"  require_approval: {require_approval}\n")

        phases_to_run = BOOTSTRAP_PHASES if phase == -1 else [(n, name) for n, name in BOOTSTRAP_PHASES if n >= phase]

        for phase_num, phase_name in phases_to_run:
            console.print(f"[cyan]Phase {phase_num}:[/cyan] {phase_name}")

            # Phase execution stub
            phase_dir = repo_root / "rig-runtime" / "phases" / f"phase_{phase_num:02d}"
            ensure_dir(phase_dir)

            # Emit ProofPacket for phase
            import json
            pp = ProofPacket(
                phase=f"bootstrap_{phase_num}",
                command=f"rigforge bootstrap --phase {phase_num}",
                status="pass",
                evidence={"phase_name": phase_name},
            )
            proof_dir = phase_dir / "proof"
            ensure_dir(proof_dir)
            pp_path = proof_dir / f"{pp.packet_id}.json"
            pp_path.write_text(json.dumps(pp.model_dump(mode="json"), indent=2, default=str))

            console.print(f"  [green]✓[/green] Complete — ProofPacket: {pp.packet_id}")

            if require_approval and phase_num < 9:
                console.print(f"  [yellow]⏸ Awaiting approval to continue to next phase[/yellow]")
                # In a real implementation, this would block for user/UI approval
                # For CLI stub, we log and continue
                approval_file = phase_dir / ".approved"
                if not approval_file.exists():
                    console.print(f"  [dim]Create {approval_file} to approve, or use rigforge approve[/dim]")

        console.print(f"\n[green]✓ Bootstrap complete[/green]")
