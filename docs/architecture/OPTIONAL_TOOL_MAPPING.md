# Optional Tool Mapping for RIGForge

## Principle

RIGForge remains the controlling architecture.
These tools are optional adapters and execution backends.
They do not replace core contracts.

## Tool Matrix

| Tool | Phase | Role | Replaces? | Regsitry Entry |
|---|---|---|---|---|
| SonarQube | Phase 2 (optional), Phase 5 (required) | Static analysis gate | Nothing — adds verification | `config/service_registry.yaml` |
| Aider | Phase 5+ | Generator implementation | Nothing — adds editing capability | `config/tool_registry.yaml` |
| MetaGPT | Phase 5+ | Spec draft helper | Nothing — output is draft, not binding | `config/tool_registry.yaml` |
| Diag-agent | Phase 5+ | Architecture viz | Nothing — adds diagrams | `config/tool_registry.yaml` |
| PR-Agent | Phase 5+ | Review assistant | Nothing — adds review aid | `config/tool_registry.yaml` |
| LangGraph | Phase 6+ | Workflow execution | Nothing — Archon owns policy | `config/service_registry.yaml` |

## What Each Tool Must Obey

### SonarQube
- Healthcheck must respond before use
- Must emit ProofPacket after analysis
- Must not block builds with false positives (Evaluator reviews)
- Must be registered in service_registry with owner=verifier

### Aider
- Can only edit files in allowed_files list
- Cannot edit frozen contracts (contracts/v1/)
- Cannot bypass DoneContract
- Cannot self-verify

### MetaGPT
- Output is draft_spec.md only
- Must pass Evaluator critique
- Must be wrapped in DoneContract negotiation
- Cannot write binding requirements

### Diag-agent
- Output is documentation only
- C4 diagrams are advisory, not proof
- Cannot replace Mike approval for architecture decisions

### PR-Agent
- Cannot replace Verifier
- Cannot replace SonarQube
- Cannot approve without Evaluator review
- Cannot see Evaluator/Generator chat history

### LangGraph
- Executes workflows defined by Archon
- Does not define workflow nodes
- Does not skip gates
- Does not approve external side effects
