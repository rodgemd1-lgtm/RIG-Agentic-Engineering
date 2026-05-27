"""rigforge cockpit — Start or open the cockpit."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

console = Console()

COCKPIT_URL = "http://localhost:3000/app/cockpit"


def register(app: typer.Typer) -> None:
    @app.command("cockpit")
    def cockpit_command(
        port: int = typer.Option(3000, "--port", help="Cockpit port"),
        open_browser: bool = typer.Option(True, "--open/--no-open", help="Open in browser"),
    ) -> None:
        """Start or open the cockpit."""
        url = f"http://localhost:{port}/app/cockpit"

        console.print(f"\n[bold]rigforge cockpit[/bold]")
        console.print(f"  URL: {url}")

        if open_browser:
            import webbrowser
            webbrowser.open(url)
            console.print("[green]OK[/green] Opened in browser")

        console.print("[dim]Note: placeholder. Actual cockpit server runs separately or via Docker.[/dim]")
