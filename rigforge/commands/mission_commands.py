"""rigforge new, interview, specify, plan — Mission creation commands."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

import typer
from rich.console import Console
import yaml

from rigforge.models import DoneContract, RunEnvelope
from rigforge.utils.fs import ensure_dir, runs_dir

console = Console()


def _create_run_directory(repo_root: Path, studio: str, idea: str) -> tuple[str, Path]:
    """Create a run directory and return (run_id, run_dir)."""
    run_id = f"run_{uuid.uuid4().hex[:12]}"
    rd = runs_dir(repo_root) / run_id
    ensure_dir(rd)
    ensure_dir(rd / "proof")
    ensure_dir(rd / "evals")
    return run_id, rd


def register(app: typer.Typer) -> None:

    @app.command("new")
    def new_command(
        studio: str = typer.Argument(..., help="Studio name"),
        idea: str = typer.Argument(..., help="Build idea"),
        repo: str = typer.Option(".", "--repo", help="Repository root"),
    ) -> None:
        """Create a new build mission from an idea."""
        repo_root = Path(repo).resolve()

        console.print(f"\n[bold]rigforge new {studio}[/bold]")
        console.print(f"  idea: {idea}\n")

        # Create run directory
        run_id, rd = _create_run_directory(repo_root, studio, idea)
        console.print(f"[cyan]Run directory:[/cyan] {rd}")

        # Create RunEnvelope
        envelope = RunEnvelope(
            run_id=run_id,
            studio=studio,
            idea=idea,
            status="created",
        )
        envelope_path = rd / "RunEnvelope.json"
        envelope_path.write_text(json.dumps(envelope.model_dump(mode="json"), indent=2, default=str))
        console.print(f"[green]✓[/green] RunEnvelope: {envelope_path}")

        # Create DoneContract stub
        contract = DoneContract(
            run_id=run_id,
            studio=studio,
            definition_of_done=idea,
            acceptance_criteria=[],
            non_goals=[],
        )
        contract_path = rd / "DoneContract.yaml"
        contract_path.write_text(yaml.dump(contract.model_dump(mode="json"), default_flow_style=False))
        console.print(f"[green]✓[/green] DoneContract: {contract_path}")

        # Create spec stub
        spec_path = rd / "spec.md"
        spec_path.write_text(f"# Spec: {studio}\n\n{idea}\n\n## Acceptance Criteria\n\n- TBD\n")
        console.print(f"[green]✓[/green] spec.md: {spec_path}")

        # Create plan stub
        plan_path = rd / "plan.md"
        plan_path.write_text(f"# Plan: {studio}\n\n## Architecture\n\nTBD\n\n## Tasks\n\n- TBD\n")
        console.print(f"[green]✓[/green] plan.md: {plan_path}")

        # Create tasks stub
        tasks_path = rd / "tasks.md"
        tasks_path.write_text(f"# Tasks: {studio}\n\n- [ ] Interview\n- [ ] Specify\n- [ ] Plan\n- [ ] Build\n- [ ] Verify\n- [ ] Approve\n")
        console.print(f"[green]✓[/green] tasks.md: {tasks_path}")

        # Create intent stub
        intent_path = rd / "intent.md"
        intent_path.write_text(f"# Intent: {studio}\n\n**Idea:** {idea}\n\n## Wound Statement\n\nTBD\n\n## Non-Goals\n\nTBD\n\n## Definition of Done\n\nTBD\n\n## Risk Level\n\nMEDIUM\n")
        console.print(f"[green]✓[/green] intent.md: {intent_path}")

        console.print(f"\n[green]✓ Mission created[/green]")
        console.print(f"  run_id: {run_id}")
        console.print(f"\n[cyan]Next:[/cyan] rigforge interview {studio}")

    @app.command("interview")
    def interview_command(
        studio: str = typer.Argument(..., help="Studio name"),
        repo: str = typer.Option(".", "--repo", help="Repository root"),
    ) -> None:
        """Start the interview-me process for a studio."""
        repo_root = Path(repo).resolve()

        console.print(f"\n[bold]rigforge interview {studio}[/bold]\n")
        console.print("Qualified Intent Brief")
        console.print(f"  Studio: {studio}")
        console.print(f"  Wound statement: [Provide what's broken or needed]")
        console.print(f"  Non-goals: [What's explicitly out of scope]")
        console.print(f"  Definition of done: [Clear completion criteria]")
        console.print(f"  Risk level: LOW | MEDIUM | HIGH | CRITICAL")
        console.print(f"\n[cyan]Next:[/cyan] rigforge specify {studio}")

    @app.command("specify")
    def specify_command(
        studio: str = typer.Argument(..., help="Studio name"),
        from_file: str = typer.Option("", "--from", help="Source intent file"),
        run_id: str = typer.Option("", "--run-id", help="Run ID"),
        repo: str = typer.Option(".", "--repo", help="Repository root"),
    ) -> None:
        """Run Spec Kit specify phase for a studio."""
        repo_root = Path(repo).resolve()

        console.print(f"\n[bold]rigforge specify {studio}[/bold]")

        if from_file:
            intent_path = Path(from_file)
            if intent_path.exists():
                console.print(f"\n[cyan]Loading intent from:[/cyan] {intent_path}")
            else:
                console.print(f"[yellow]Intent file not found: {intent_path}, using defaults[/yellow]")

        # Ensure run directory
        if run_id:
            rd = runs_dir(repo_root) / run_id
        else:
            run_id, rd = _create_run_directory(repo_root, studio, "")

        ensure_dir(rd)

        # Create spec outputs
        (rd / "requirements.md").write_text(f"# Requirements: {studio}\n\nTBD\n")
        (rd / "acceptance_criteria.md").write_text(f"# Acceptance Criteria: {studio}\n\n- TBD\n")

        console.print(f"[green]✓[/green] spec.md: {rd / 'spec.md'}")
        console.print(f"[green]✓[/green] requirements.md: {rd / 'requirements.md'}")
        console.print(f"[green]✓[/green] acceptance_criteria.md: {rd / 'acceptance_criteria.md'}")
        console.print(f"\n[cyan]Next:[/cyan] rigforge plan {studio}")

    @app.command("plan")
    def plan_command(
        studio: str = typer.Argument(..., help="Studio name"),
        run_id: str = typer.Option("", "--run-id", help="Run ID"),
        repo: str = typer.Option(".", "--repo", help="Repository root"),
    ) -> None:
        """Run Spec Kit plan phase for a studio."""
        repo_root = Path(repo).resolve()

        console.print(f"\n[bold]rigforge plan {studio}[/bold]")

        if run_id:
            rd = runs_dir(repo_root) / run_id
        else:
            run_id, rd = _create_run_directory(repo_root, studio, "")

        ensure_dir(rd)

        plan_files = {
            "architecture.md": f"# Architecture: {studio}\n\nTBD\n",
            "data_model.md": f"# Data Model: {studio}\n\nTBD\n",
            "api_contract.md": f"# API Contract: {studio}\n\nTBD\n",
            "permission_matrix.md": f"# Permission Matrix: {studio}\n\nTBD\n",
            "test_plan.md": f"# Test Plan: {studio}\n\nTBD\n",
            "deployment_plan.md": f"# Deployment Plan: {studio}\n\nTBD\n",
            "observability_plan.md": f"# Observability Plan: {studio}\n\nTBD\n",
        }

        for filename, content in plan_files.items():
            (rd / filename).write_text(content)
            console.print(f"[green]✓[/green] {filename}")

        console.print(f"\n[cyan]Next:[/cyan] rigforge build {studio} --run-id {run_id}")
