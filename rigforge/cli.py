"""rigforge — Deterministic CLI command surface for RIG Agentic Engineering and RIG App Studio.

The CLI is the deterministic backend.
The App Studio is the visual cockpit over the CLI.
Agents call the CLI.
The UI calls the CLI/API.
No studio process exists only in chat.
"""

from __future__ import annotations

import typer
from rich.console import Console

from rigforge import __version__
from rigforge.commands.approve_command import register as register_approve
from rigforge.commands.bootstrap import register as register_bootstrap
from rigforge.commands.build import register as register_build
from rigforge.commands.cockpit_command import register as register_cockpit
from rigforge.commands.doctor import register as register_doctor
from rigforge.commands.init import register as register_init
from rigforge.commands.learn import register as register_learn
from rigforge.commands.mission_commands import register as register_mission
from rigforge.commands.promote_skill import register as register_promote_skill
from rigforge.commands.retrofit import register as register_retrofit
from rigforge.commands.status_command import register as register_status
from rigforge.commands.verify import register as register_verify

console = Console()

app = typer.Typer(
    name="rigforge",
    help="Deterministic CLI command surface for RIG Agentic Engineering and RIG App Studio",
    no_args_is_help=True,
    rich_markup_mode="rich",
)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", help="Show version"),
) -> None:
    """rigforge — The forge for RIG App Studio."""
    if version:
        console.print(f"rigforge v{__version__}")
        raise typer.Exit(0)
    if ctx.invoked_subcommand is None:
        console.print(f"[bold]rigforge[/bold] v{__version__}")
        console.print("Deterministic CLI for RIG Agentic Engineering")
        console.print("\nRun [cyan]rigforge --help[/cyan] for available commands.")


# ═══════════════════════════════════════════════════════════════
# Register all commands
# ═══════════════════════════════════════════════════════════════

register_doctor(app)
register_init(app)
register_bootstrap(app)
register_retrofit(app)
register_mission(app)  # new, interview, specify, plan
register_build(app)
register_verify(app)
register_approve(app)
register_status(app)
register_cockpit(app)
register_learn(app)
register_promote_skill(app)
