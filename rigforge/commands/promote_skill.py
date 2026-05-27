"""rigforge promote-skill — Promote repeated behavior into deterministic capability."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
import yaml

from rigforge.models import SkillPromotion
from rigforge.utils.fs import ensure_dir

console = Console()

PROMOTION_LADDER = [
    "repeated pattern",
    "deterministic script",
    "CLI wrapper",
    "tests",
    "ProofPacket",
    "SKILL.md",
    "registry entry",
    "approved active skill",
]


def register(app: typer.Typer) -> None:
    @app.command("promote-skill")
    def promote_skill_command(
        pattern_id: str = typer.Argument(..., help="Pattern ID to promote"),
        name: str = typer.Option("", "--name", help="Skill name"),
        description: str = typer.Option("", "--description", help="What this skill does"),
        repo: str = typer.Option(".", "--repo", help="Repository root"),
    ) -> None:
        """Promote repeated behavior into deterministic capability."""
        repo_root = Path(repo).resolve()

        skill_name = name or pattern_id.replace("_", " ").title()
        skill_desc = description or f"Auto-promoted skill from pattern: {pattern_id}"

        console.print(f"\n[bold]rigforge promote-skill {pattern_id}[/bold]\n")

        promotion = SkillPromotion(
            pattern_id=pattern_id,
            name=skill_name,
            description=skill_desc,
            status="proposed",
        )

        # Create skill proposal (not active skill — that's the rule)
        skills_dir = repo_root / "rig-runtime" / "skills" / pattern_id
        ensure_dir(skills_dir)

        # Write proposal
        proposal_path = skills_dir / "promotion_proposal.yaml"
        proposal_data = {
            "pattern_id": pattern_id,
            "name": skill_name,
            "description": skill_desc,
            "status": "proposed",
            "promotion_ladder": PROMOTION_LADDER,
            "current_step": 0,
        }
        proposal_path.write_text(yaml.dump(proposal_data, default_flow_style=False))
        console.print(f"[green]✓[/green] Promotion proposal: {proposal_path}")

        # Write skill stub (not active)
        skill_md_path = skills_dir / "SKILL.md"
        skill_md_content = f"""---
name: {pattern_id}
description: "{skill_desc}"
status: proposed
---

# {skill_name}

**Status:** PROPOSED — Not yet active.

{skill_desc}

## Details

TBD — This skill is proposed but not yet tested or approved.

## Promotion Ladder

"""
        for i, step in enumerate(PROMOTION_LADDER):
            check = "[x]" if i == 0 else "[ ]"
            skill_md_content += f"- {check} {step}\n"

        skill_md_path.write_text(skill_md_content)
        console.print(f"[green]✓[/green] Skill stub: {skill_md_path}")

        # Write ProofPacket to skill dir
        import json
        import uuid
        from rigforge.models import ProofPacket

        pp = ProofPacket(
            packet_id=f"pp_{uuid.uuid4().hex[:12]}",
            phase="promote-skill",
            command=f"rigforge promote-skill {pattern_id}",
            status="pass",
            evidence={
                "pattern_id": pattern_id,
                "proposal_path": str(proposal_path.relative_to(repo_root)),
            },
        )
        proof_path = skills_dir / "proof"
        ensure_dir(proof_path)
        pp_file = proof_path / f"{pp.packet_id}.json"
        pp_file.write_text(json.dumps(pp.model_dump(mode="json"), indent=2, default=str))

        console.print(f"\n[yellow]⚠ Skill is PROPOSED, not active.[/yellow]")
        console.print(f"  Complete the promotion ladder to make it active.")
        console.print(f"  Proposal: {proposal_path}")
