"""rigforge doctor — Check runtime readiness."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from rigforge.models import CheckStatus, DoctorCheck, DoctorResult, SystemStatus
from rigforge.utils.checks import (
    check_command,
    check_docker_running,
    check_git_repo,
    check_python_version,
)

console = Console()

# ═══════════════════════════════════════════════════════════════
# Service registry: name -> check function
# ═══════════════════════════════════════════════════════════════

DOCTOR_CHECKS = {
    "python": check_python_version,
    "node": lambda: check_command("node", "node", "brew install node"),
    "docker": check_docker_running,
    "git": check_git_repo,
    "uv": lambda: check_command("uv", "uv", "curl -LsSf https://astral.sh/uv/install.sh | sh"),
    "spec-kit": lambda: check_command("spec-kit", "specify", "pip install specify-cli"),
    "archon": lambda: check_command("archon", "archon", "Install Archon CLI"),
    "deerflow": lambda: check_command("deerflow", "deerflow", "Install DeerFlow"),
    "litellm": lambda: check_command("litellm", "litellm", "pip install litellm"),
    "promptfoo": lambda: check_command("promptfoo", "promptfoo", "npx promptfoo --version"),
    "deepeval": lambda: check_command("deepeval", "deepeval", "pip install deepeval"),
    "playwright": lambda: check_command("playwright", "playwright", "npx playwright install"),
    "postgres": lambda: check_command("postgres", "psql", "brew install postgresql"),
    "qdrant": lambda: check_command("qdrant", "qdrant", "docker pull qdrant/qdrant"),
    "neo4j": lambda: check_command("neo4j", "neo4j", "brew install neo4j"),
    "langfuse": lambda: check_command("langfuse", "langfuse", "docker pull langfuse/langfuse"),
    "aionui": lambda: check_command("aionui", "aionui", "Install AionUI"),
    "agent-skills": lambda: check_command("agent-skills", "echo", "N/A (path check)"),
    "sonarqube": lambda: check_command("sonarqube", "sonar-scanner", "brew install sonar-scanner or set up SonarQube container"),
}


def run_doctor() -> DoctorResult:
    """Execute all doctor checks and return aggregated result."""
    checks: list[DoctorCheck] = []
    fail_count = 0
    warn_count = 0

    for name, check_fn in DOCTOR_CHECKS.items():
        try:
            result = check_fn()
            if result.passed:
                status = CheckStatus.PASS
            else:
                status = CheckStatus.FAIL
                fail_count += 1
            checks.append(DoctorCheck(
                name=name,
                status=status,
                detail=result.detail,
                fix=result.fix,
            ))
        except Exception as e:
            checks.append(DoctorCheck(
                name=name,
                status=CheckStatus.SKIP,
                detail=f"check error: {e}",
            ))
            warn_count += 1

    # Determine overall status
    critical = {"python", "git"}  # Docker is optional (only needed for containerized services)
    critical_fails = [c for c in checks if c.name in critical and c.status == CheckStatus.FAIL]

    if critical_fails:
        overall = SystemStatus.BLOCKED
    elif fail_count > 0:
        overall = SystemStatus.DEGRADED
    else:
        overall = SystemStatus.READY

    blockers = [c.name for c in checks if c.status == CheckStatus.FAIL]

    # Determine next safe action
    if overall == SystemStatus.READY:
        next_safe = "rigforge init --repo ."
    elif overall == SystemStatus.DEGRADED:
        next_safe = f"Fix blockers: {', '.join(blockers)}"
    else:
        next_safe = "Install critical dependencies and re-run rigforge doctor"

    return DoctorResult(
        status=overall,
        checks=checks,
        blockers=blockers,
        next_safe_action=next_safe,
    )


def register(app: typer.Typer) -> None:
    @app.command("doctor")
    def doctor_command(
        json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    ) -> None:
        """Check runtime readiness. Returns READY, DEGRADED, or BLOCKED."""
        result = run_doctor()

        if json_output:
            console.print_json(data=result.model_dump(mode="json"))
            raise typer.Exit(1 if result.status == SystemStatus.BLOCKED else 0)

        # Rich table output
        table = Table(title="rigforge doctor", show_header=True, header_style="bold")
        table.add_column("Service", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Detail", style="dim")
        table.add_column("Fix", style="yellow")

        status_styles = {
            CheckStatus.PASS: "green",
            CheckStatus.WARN: "yellow",
            CheckStatus.FAIL: "red",
            CheckStatus.SKIP: "dim",
        }

        for check in result.checks:
            style = status_styles.get(check.status, "white")
            status_text = f"[{style}]{check.status.value}[/{style}]"
            table.add_row(check.name, status_text, check.detail, check.fix)

        console.print(table)

        # Summary
        overall_styles = {
            SystemStatus.READY: "bold green",
            SystemStatus.DEGRADED: "bold yellow",
            SystemStatus.BLOCKED: "bold red",
        }
        style = overall_styles.get(result.status, "bold white")
        console.print(f"\n[{style}]status: {result.status.value}[/{style}]")
        console.print(f"next_safe_action: {result.next_safe_action}")

        if result.blockers:
            console.print(f"[red]blockers: {', '.join(result.blockers)}[/red]")

        raise typer.Exit(1 if result.status == SystemStatus.BLOCKED else 0)
