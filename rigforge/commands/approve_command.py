"""rigforge approve — Route approval packet to AionUI or record signed approval."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import typer
from rich.console import Console
import yaml

from rigforge.models import ProofPacket
from rigforge.utils.fs import run_dir

console = Console()


def register(app: typer.Typer) -> None:
    @app.command("approve")
    def approve_command(
        run_id: str = typer.Argument(..., help="Run ID to approve"),
        approver: str = typer.Option("manual", "--by", help="Approver identity"),
        signature: str = typer.Option("", "--signature", help="Signed approval token"),
        repo: str = typer.Option(".", "--repo", help="Repository root"),
    ) -> None:
        """Route approval packet to AionUI or record signed approval."""
        repo_root = Path(repo).resolve()
        rd = run_dir(repo_root, run_id)

        # Gate: Run directory must exist
        if not rd.exists():
            console.print(f"[red]✗ Run not found: {rd}[/red]")
            raise typer.Exit(1)

        # Gate: Approval packet must exist
        approval_path = rd / "approval_packet.json"
        if approval_path.exists():
            console.print(f"[cyan]Approval packet found:[/cyan] {approval_path}")
        else:
            console.print(f"[red]✗ BLOCKED: No approval packet found.[/red]")
            console.print(f"  Expected: {approval_path}")
            console.print("  Build must emit an approval packet before approval.")
            raise typer.Exit(1)

        # Gate: ProofPacket must exist
        proof_dir = rd / "proof"
        if not proof_dir.exists() or not list(proof_dir.glob("pp_*.json")):
            console.print(f"[red]✗ BLOCKED: No ProofPackets found.[/red]")
            console.print(f"  Expected: {proof_dir / 'pp_*.json'}")
            console.print("  Build must emit ProofPackets before approval.")
            raise typer.Exit(1)
        console.print(f"[green]✓[/green] ProofPackets present")

        # Show risk level from DoneContract
        contract_path = rd / "DoneContract.yaml"
        risk_level = "UNKNOWN"
        rollback_plan = ""
        if contract_path.exists():
            contract_data = yaml.safe_load(contract_path.read_text())
            risk_level = contract_data.get("risk_level", "UNKNOWN")
            rollback_plan = contract_data.get("rollback_plan", "")
            console.print(f"[cyan]Risk level:[/cyan] {risk_level}")

        # Gate: Rollback plan required for deploy/write actions
        if risk_level in ("HIGH", "CRITICAL") and not rollback_plan:
            console.print(f"[red]✗ BLOCKED: Risk level is {risk_level} but no rollback plan provided.[/red]")
            console.print("  Update DoneContract.yaml with a rollback_plan before approval.")
            raise typer.Exit(1)

        # Gate: No auto-approval (signature or explicit approver required)
        if signature == "" and approver == "manual":
            console.print(f"[red]✗ BLOCKED: No auto-approval allowed.[/red]")
            console.print("  Provide --by <approver> and optionally --signature <token>")
            raise typer.Exit(1)

        # Record approval
        contract_path = rd / "DoneContract.yaml"
        if contract_path.exists():
            contract_data = yaml.safe_load(contract_path.read_text())
            contract_data["approved"] = True
            contract_data["approved_by"] = approver
            contract_data["approved_at"] = datetime.now(timezone.utc).isoformat()
            contract_path.write_text(yaml.dump(contract_data, default_flow_style=False))
            console.print(f"[green]✓[/green] DoneContract approved by {approver}")

        # Write ProofPacket
        pp = ProofPacket(
            run_id=run_id,
            phase="approve",
            command=f"rigforge approve {run_id}",
            status="pass",
            evidence={"approver": approver, "risk_level": risk_level},
        )
        proof_path = proof_dir / f"{pp.packet_id}.json"
        proof_path.write_text(json.dumps(pp.model_dump(mode="json"), indent=2, default=str))

        console.print(f"\n[green]✓ Approval recorded[/green]")
        console.print(f"  ProofPacket: {pp.packet_id}")
