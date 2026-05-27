"""rigforge learn — Turn an incident into a regression test."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
import yaml

from rigforge.models import Incident, RegressionTest
from rigforge.utils.fs import ensure_dir

console = Console()


def _load_incident(repo_root: Path, incident_id: str) -> Incident | None:
    """Load incident from incidents directory or proof directory."""
    # Search for incident in common locations
    search_paths = [
        repo_root / "incidents" / f"{incident_id}.yaml",
        repo_root / "incidents" / f"{incident_id}.json",
        repo_root / "rig-runtime" / "proof" / f"{incident_id}.json",
    ]

    for p in search_paths:
        if p.exists():
            if p.suffix == ".json":
                data = json.loads(p.read_text())
            else:
                data = yaml.safe_load(p.read_text())
            return Incident(**data)

    return None


def register(app: typer.Typer) -> None:
    @app.command("learn")
    def learn_command(
        incident_id: str = typer.Argument(..., help="Incident ID to learn from"),
        name: str = typer.Option("", "--name", help="Regression test name"),
        failing_input: str = typer.Option("", "--failing-input", help="The failing input"),
        expected_output: str = typer.Option("", "--expected-output", help="Expected correct output"),
        repo: str = typer.Option(".", "--repo", help="Repository root"),
    ) -> None:
        """Turn an incident into a regression test."""
        repo_root = Path(repo).resolve()

        console.print(f"\n[bold]rigforge learn {incident_id}[/bold]\n")

        # Step 1: Read BLOCKER (load incident)
        console.print("[cyan]1.[/cyan] Reading incident...")
        incident = _load_incident(repo_root, incident_id)
        if incident:
            console.print(f"   Found: {incident.title}")
            console.print(f"   Description: {incident.description}")
            if not failing_input:
                failing_input = incident.failing_input
        else:
            console.print(f"   [dim]Incident file not found, using CLI arguments[/dim]")

        # Step 2: Extract failing input
        console.print("[cyan]2.[/cyan] Extracting failing input...")
        if not failing_input:
            console.print("[red]✗ BLOCKED: No failing input. Provide --failing-input[/red]")
            raise typer.Exit(1)
        console.print(f"   Input: {failing_input}")

        # Step 3: Create regression yaml
        console.print("[cyan]3.[/cyan] Creating regression test...")
        test_name = name or f"regression_{incident_id}"

        reg = RegressionTest(
            incident_id=incident_id,
            name=test_name,
            failing_input=failing_input,
            expected_output=expected_output or "TBD",
        )

        evals_dir = repo_root / "rig-runtime" / "evals"
        ensure_dir(evals_dir)

        reg_path = evals_dir / f"{reg.test_id}.yaml"
        reg_data = yaml.dump(reg.model_dump(mode="json", exclude={"test_id"}), default_flow_style=False)
        reg_path.write_text(reg_data)
        console.print(f"   Created: {reg_path}")

        # Step 4: Add to eval baseline
        console.print("[cyan]4.[/cyan] Adding to eval baseline...")
        baseline_path = evals_dir / "baseline.yaml"
        if baseline_path.exists():
            baseline = yaml.safe_load(baseline_path.read_text()) or {}
        else:
            baseline = {"version": "0.1.0", "tests": []}

        if "tests" not in baseline:
            baseline["tests"] = []

        baseline["tests"].append({
            "test_id": reg.test_id,
            "incident_id": incident_id,
            "name": test_name,
            "file": str(reg_path.relative_to(repo_root)),
        })
        baseline_path.write_text(yaml.dump(baseline, default_flow_style=False))
        console.print(f"   Updated: {baseline_path}")

        # Step 5: Write ProofPacket
        console.print("[cyan]5.[/cyan] Writing ProofPacket...")
        pp_dir = repo_root / "rig-runtime" / "proof"
        ensure_dir(pp_dir)

        import uuid
        from rigforge.models import ProofPacket

        pp = ProofPacket(
            packet_id=f"pp_{uuid.uuid4().hex[:12]}",
            phase="learn",
            command=f"rigforge learn {incident_id}",
            status="pass",
            evidence={
                "incident_id": incident_id,
                "test_id": reg.test_id,
                "regression_file": str(reg_path.relative_to(repo_root)),
            },
        )

        pp_path = pp_dir / f"{pp.packet_id}.json"
        pp_path.write_text(json.dumps(pp.model_dump(mode="json"), indent=2, default=str))
        console.print(f"   Emitted: {pp_path}")

        # Step 6: Update EvidenceGraph
        console.print("[cyan]6.[/cyan] Updating EvidenceGraph...")
        evidence_graph = repo_root / "rig-runtime" / "evals" / "evidence_graph.yaml"
        if evidence_graph.exists():
            graph = yaml.safe_load(evidence_graph.read_text()) or {"nodes": [], "edges": []}
        else:
            graph = {"version": "0.1.0", "nodes": [], "edges": []}

        graph["nodes"].append({
            "type": "regression_test",
            "id": reg.test_id,
            "incident": incident_id,
        })
        graph["edges"].append({
            "from": incident_id,
            "to": reg.test_id,
            "type": "learned_from",
        })
        evidence_graph.write_text(yaml.dump(graph, default_flow_style=False))
        console.print(f"   Updated: {evidence_graph}")

        console.print(f"\n[green]✓ Learning complete[/green]")
        console.print(f"  Regression test: {reg.test_id}")
        console.print(f"  File: {reg_path}")
