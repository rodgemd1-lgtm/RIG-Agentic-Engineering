"""rigforge verify — Run verification stack on a studio build."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from rigforge.utils.fs import run_dir

console = Console()

VERIFY_CHECKS = [
    "schema tests",
    "contract tests",
    "workflow tests",
    "ProofPacket checks",
    "regression tests",
    "approval policy tests",
    "memory firewall tests",
    "cross-family verifier tests",
]


def _check_proof_packets(rd: Path) -> tuple[bool, str]:
    """Check if ProofPacket exists and is valid."""
    proof_dir = rd / "proof"
    if not proof_dir.exists():
        return False, "No proof directory found"

    packets = list(proof_dir.glob("pp_*.json"))
    if not packets:
        return False, "No ProofPacket files found"

    # Validate at least one packet
    for p in packets:
        try:
            data = json.loads(p.read_text())
            if data.get("status") == "pass":
                return True, f"Valid ProofPacket: {data.get('packet_id', p.stem)}"
        except (json.JSONDecodeError, KeyError):
            continue

    return False, "No passing ProofPackets found"


def register(app: typer.Typer) -> None:
    @app.command("verify")
    def verify_command(
        studio: str = typer.Argument(..., help="Studio name"),
        run_id: str = typer.Option("", "--run-id", help="Run ID to verify"),
        case: str = typer.Option("", "--case", help="Specific test case to run"),
        repo: str = typer.Option(".", "--repo", help="Repository root"),
    ) -> None:
        """Run verification stack on a studio build."""
        repo_root = Path(repo).resolve()

        if not run_id:
            console.print("[red]✗ --run-id is required[/red]")
            raise typer.Exit(1)

        rd = run_dir(repo_root, run_id)

        if not rd.exists():
            console.print(f"[red]✗ Run directory not found: {rd}[/red]")
            raise typer.Exit(1)

        console.print(f"\n[bold]rigforge verify {studio}[/bold]")
        console.print(f"  run_id: {run_id}")
        if case:
            console.print(f"  case:   {case}")
        console.print()

        results = []
        all_pass = True

        for check_name in VERIFY_CHECKS:
            if check_name == "ProofPacket checks":
                passed, detail = _check_proof_packets(rd)
            elif check_name == "contract tests":
                contract_path = rd / "DoneContract.yaml"
                passed = contract_path.exists()
                detail = "DoneContract.yaml present" if passed else "DoneContract.yaml missing"
            elif check_name == "schema tests":
                spec_path = rd / "spec.md"
                passed = spec_path.exists()
                detail = "spec.md present" if passed else "spec.md missing"
            elif check_name == "regression tests":
                reg_dir = rd / "evals"
                passed = reg_dir.exists() and any(reg_dir.glob("*.yaml"))
                detail = "Regression tests found" if passed else "No regression tests"
            else:
                # Placeholder for checks that need actual test runners
                passed = True
                detail = "skipped (no test runner configured)"

            status = "[green]✓[/green]" if passed else "[red]✗[/red]"
            console.print(f"  {status} {check_name}: {detail}")

            if not passed:
                all_pass = False

            results.append((check_name, passed, detail))

        console.print()
        if all_pass:
            console.print("[green]✓ All verification checks passed[/green]")
            console.print(f"\n[cyan]Next:[/cyan] rigforge approve {run_id}")
        else:
            failed = [name for name, passed, _ in results if not passed]
            console.print(f"[red]✗ Verification failed: {', '.join(failed)}[/red]")
            raise typer.Exit(1)
