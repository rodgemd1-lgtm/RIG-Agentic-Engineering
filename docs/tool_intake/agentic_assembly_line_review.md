# Agentic Assembly Line Tool Intake Review

## Context

External architecture advice recommends a local agentic assembly line:

| Tool | Proposed Role | RIGForge Assessment |
|---|---|---|
| LangGraph | Orchestrator | Optional workflow backend for Phase 6+ |
| MetaGPT | Product/Spec generator | Draft spec helper only; must go through Evaluator |
| Aider | Coder | Optional Generator tool under GEV rules |
| SonarQube | Static analysis judge | Adopt as deterministic verification gate |
| Diag-agent | Architecture visualizer | Adopt as optional C4 diagram generator |
| PR-Agent | Review assistant | Optional review aide; never replaces Evaluator/Verifier |

## Prime Rule

RIGForge remains the controlling architecture. These tools **do not** replace:

- RunEnvelope
- DoneContract
- ProofPacket
- Control Plane registries
- GEV loop
- Verifier isolation
- Cockpit approvals
- Failure runbook

## What We Adopt

| Tool | Phase | Role | Condition |
|---|---|---|---|
| SonarQube | Phase 2+ as optional, Phase 5 as required | Deterministic static analysis gate | Must have healthcheck, must emit ProofPacket |
| Aider | Phase 5+ | Generator tool under PyCode/PiCode | Cannot self-verify; requires DoneContract |
| Diag-agent | Phase 5+ | Architecture visualization (C4) | Cannot replace human approval; diagram ≠ proof |
| PR-Agent | Phase 5+ | Review assistant | Cannot replace Evaluator or Verifier |
| LangGraph | Phase 6+ | Optional workflow backend | Does not define policy; Archon owns workflow |
| MetaGPT | Phase 5+ | Draft spec/PRD helper | Output is draft only, not binding requirements |

## What We Reject

1. **LangGraph as system orchestrator** — Archon owns workflow order, RunEnvelope owns state
2. **MetaGPT as binding authority** — Only DoneContract is binding; MetaGPT output must pass Evaluator
3. **Aider self-verification** — Generator never self-verifies
4. **SonarQube as sole verifier** — One gate among many; must combine with Evaluator + Stateless Verifier
5. **Installing before Control Plane exists** — No tool enters live registry before Phase 4

## Phase Placement

```text
Phase 1 (Bootstrap):     NOT YET — only document pending registry entries
Phase 2 (Environment):   SonarQube as optional doctor check only
Phase 3 (Runtime):       NOT YET — wait for Control Plane
Phase 4 (Control Plane): Add entries to tool_registry.yaml, service_registry.yaml, proof_registry.yaml
Phase 5 (GEV):           Aider, MetaGPT, Diag-agent, PR-Agent as optional tools
Phase 6 (DeerFlow):      LangGraph as optional workflow execution backend
Phase 7 (Cockpit):       All tools must have cockpit visibility
```

## Pending Registry Entries

See `docs/pending_registry_entries/agentic_assembly_line_tools.yaml`

## Risks

1. Scope creep if tools are installed before Control Plane
2. MetaGPT may hallucinate requirements if not evaluated
3. Aider may modify files outside DoneContract scope
4. SonarQube may fail on non-standard Python 3.14 features

## Recommended Actions

1. Add SonarQube to Phase 2 optional checks
2. Add all six tools to pending registry entries
3. Create `docs/architecture/OPTIONAL_TOOL_MAPPING.md`
4. Resume Phase 4 build — do not block on tool intake

## Final Status

```text
TOOL_INTAKE_DOCUMENTED
```
