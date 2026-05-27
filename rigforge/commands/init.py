"""rigforge init — Initialize a repo for RIG agentic engineering."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from rigforge.utils.fs import ensure_dir

console = Console()

INIT_DIRS = [
    "rig-runtime",
    "rig-runtime/config",
    "rig-runtime/contracts",
    "rig-runtime/workflows",
    "rig-runtime/agents",
    "rig-runtime/studios",
    "rig-runtime/scripts",
    "rig-runtime/tests",
    "rig-runtime/evals",
    "rig-runtime/proof",
    "rig-runtime/docs",
    "rig-runtime/runs",
]

INIT_FILES = {
    "rig-runtime/config/rig.yaml": """# RIG Runtime Configuration
version: 0.1.0
owner: ""
created_at: ""

studios: []
default_harness: archon
default_generator: pycode
proof_policy: required
approval_policy: required
""",
    "rig-runtime/config/.gitattributes": "*.yaml linguist-language=YAML\n*.json linguist-language=JSON\n",
    "rig-runtime/proof/.gitkeep": "",
    "rig-runtime/runs/.gitkeep": "",
    "rig-runtime/tests/.gitkeep": "",
    "rig-runtime/evals/.gitkeep": "",
}


def register(app: typer.Typer) -> None:
    @app.command("init")
    def init_command(
        repo: str = typer.Option(".", "--repo", help="Repository root path"),
    ) -> None:
        """Initialize a repo for RIG agentic engineering."""
        root = Path(repo).resolve()

        if not root.exists():
            console.print(f"[red]Path does not exist: {root}[/red]")
            raise typer.Exit(1)

        console.print(f"[cyan]Initializing RIG runtime in {root}[/cyan]")

        created_dirs = 0
        created_files = 0

        for dir_path in INIT_DIRS:
            full = root / dir_path
            if not full.exists():
                ensure_dir(full)
                created_dirs += 1
                console.print(f"  [green]dir+[/green]  {dir_path}")
            else:
                console.print(f"  [dim]dir~[/dim]  {dir_path} (exists)")

        for file_path, content in INIT_FILES.items():
            full = root / file_path
            if not full.exists():
                full.parent.mkdir(parents=True, exist_ok=True)
                full.write_text(content)
                created_files += 1
                console.print(f"  [green]file+[/green] {file_path}")
            else:
                console.print(f"  [dim]file~[/dim] {file_path} (exists)")

        console.print(f"\n[green]✓[/green] Created {created_dirs} dirs, {created_files} files")

        if (root / "rig-runtime" / "config" / "rig.yaml").exists():
            console.print("[cyan]Next:[/cyan] rigforge doctor && rigforge bootstrap --phase 0")
