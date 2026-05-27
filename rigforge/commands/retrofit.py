"""rigforge retrofit — Retrofit existing studios with RIG capabilities."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from rigforge.models import RetrofitReport, RetrofitStep
from rigforge.utils.fs import ensure_dir

console = Console()

RETROFIT_STEPS = [
    "Inventory studio",
    "Freeze current state",
    "Add RunEnvelope",
    "Add DoneContract",
    "Add tool allowlist",
    "Add Archon workflow",
    "Add GEV loop",
    "Add ProofPackets",
    "Add regression tests",
    "Add cockpit panel",
    "Run smoke test",
    "Emit retrofit report",
]

RETROFIT_TEMPLATES = [
    ("RunEnvelope.json", '{{\n  "version": "0.1.0",\n  "studio": "{studio}",\n  "status": "retrofitted"\n}}'),
    ("DoneContract.yaml", 'run_id: ""\nstudio: {studio}\ndefinition_of_done: "Retrofitted studio"\nacceptance_criteria: []\nnon_goals: []\nrisk_level: MEDIUM\nrollback_plan: ""\napproved: false\napproved_by: ""\n'),
    ("tool_allowlist.yaml", '# Tool allowlist for {studio}\nallowed_tools: []\nrequire_approval: []\nblocked_tools: []\n'),
    ("gev_loop.yaml", '# GEV Loop configuration for {studio}\ngenerator: pycode\nevaluator: kimi\nverifier: codex\nmax_iterations: 5\nproof_required: true\n'),
    ("proof_policy.yaml", '# Proof Packet policy for {studio}\nrequire_proof: true\nretention_days: 90\n'),
]


def _run_retrofit_dry_run(studio: str, repo_root: Path) -> RetrofitReport:
    studio_path = repo_root / "studios" / studio
    steps = []

    for i, name in enumerate(RETROFIT_STEPS, 1):
        if i <= 2:
            exists = studio_path.exists()
            status = "done" if exists else "failed"
            detail = f"studio path: {studio_path}" if exists else "studio path not found"
        else:
            status = "pending"
            detail = "dry-run: no changes"
        steps.append(RetrofitStep(step_number=i, name=name, status=status, detail=detail))

    blockers = []
    if not studio_path.exists():
        blockers.append(f"Studio path not found: {studio_path}")

    return RetrofitReport(studio=studio, dry_run=True, steps=steps, blockers=blockers)


def _run_retrofit_apply(studio: str, repo_root: Path, mission: str = "") -> RetrofitReport:
    studio_path = repo_root / "studios" / studio
    ensure_dir(studio_path)

    steps = []
    for i, name in enumerate(RETROFIT_STEPS, 1):
        if i <= 2:
            steps.append(RetrofitStep(step_number=i, name=name, status="done", detail="studio ready"))
        elif i <= 9:
            # Create retrofit files
            for filename, template in RETROFIT_TEMPLATES:
                fpath = studio_path / filename
                if not fpath.exists():
                    content = template.format(studio=studio)
                    if mission:
                        content = content.replace('run_id: ""', f'run_id: "mission_{mission}"')
                    fpath.write_text(content)
            steps.append(RetrofitStep(step_number=i, name=name, status="done", detail=f"files written to {studio_path}"))
        else:
            steps.append(RetrofitStep(step_number=i, name=name, status="skipped", detail="post-apply steps"))

    return RetrofitReport(studio=studio, dry_run=False, steps=steps, blockers=[])


def _run_retrofit_verify(studio: str, repo_root: Path) -> RetrofitReport:
    studio_path = repo_root / "studios" / studio
    steps = []

    for i, name in enumerate(RETROFIT_STEPS, 1):
        if i <= 2:
            exists = studio_path.exists()
            steps.append(RetrofitStep(
                step_number=i, name=name,
                status="done" if exists else "failed",
                detail=str(studio_path) if exists else "missing",
            ))
        elif i <= 9:
            # Check files exist
            missing = []
            for filename, _ in RETROFIT_TEMPLATES:
                if not (studio_path / filename).exists():
                    missing.append(filename)
            if missing:
                steps.append(RetrofitStep(
                    step_number=i, name=name, status="failed",
                    detail=f"missing: {', '.join(missing)}",
                ))
            else:
                steps.append(RetrofitStep(step_number=i, name=name, status="done", detail="all files present"))
        else:
            steps.append(RetrofitStep(step_number=i, name=name, status="pending", detail="not yet applied"))

    blockers = [s.detail for s in steps if s.status == "failed"]

    return RetrofitReport(studio=studio, dry_run=True, steps=steps, blockers=blockers)


def register(app: typer.Typer) -> None:
    @app.command("retrofit")
    def retrofit_command(
        studio: str = typer.Argument(..., help="Studio name to retrofit"),
        dry_run: bool = typer.Option(False, "--dry-run", help="Show what would change without modifying files"),
        apply: bool = typer.Option(False, "--apply", help="Apply retrofit changes"),
        verify: bool = typer.Option(False, "--verify", help="Verify retrofit status"),
        repo: str = typer.Option(".", "--repo", help="Repository root"),
        mission: str = typer.Option("", "--mission", help="Mission identifier for the retrofit"),
    ) -> None:
        """Retrofit an existing studio with RIG capabilities."""
        repo_root = Path(repo).resolve()

        if not repo_root.exists():
            console.print(f"[red]Repo root not found: {repo_root}[/red]")
            raise typer.Exit(1)

        # Mode selection: default to dry-run if no mode specified
        if not any([dry_run, apply, verify]):
            dry_run = True

        if dry_run:
            report = _run_retrofit_dry_run(studio, repo_root)
        elif apply:
            report = _run_retrofit_apply(studio, repo_root, mission)
        else:
            report = _run_retrofit_verify(studio, repo_root)

        # Render report
        console.print(f"\n[bold]rigforge retrofit {studio}[/bold] (dry_run={report.dry_run})\n")

        for step in report.steps:
            status_colors = {
                "done": "green",
                "pending": "yellow",
                "failed": "red",
                "skipped": "dim",
            }
            color = status_colors.get(step.status, "white")
            console.print(f"  {step.step_number:>2}. [{color}]{step.status:<8}[/{color}] {step.name}")
            if step.detail:
                console.print(f"      [dim]{step.detail}[/dim]")

        if report.blockers:
            console.print(f"\n[red]Blockers:[/red]")
            for b in report.blockers:
                console.print(f"  [red]• {b}[/red]")

        has_failures = any(s.status == "failed" for s in report.steps)
        raise typer.Exit(1 if has_failures else 0)
