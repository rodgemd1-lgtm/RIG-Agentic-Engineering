# Aider Local Setup

## Installation

```bash
# Preferred: uv tool (no dependencies污染)
uv tool install aider-chat

# Or: pipx
pipx install aider-chat

# Or: pip
pip install aider-chat
```

## Verification

```bash
aider --version
# Expected: __main__.py 0.86.2
```

## Required API Key Configuration

Aider requires an LLM API key. Store it in environment:

```bash
export ANTHROPIC_API_KEY=sk-...  # for claude model
export OPENAI_API_KEY=sk-...     # for gpt model
```

Do NOT commit API keys. Use `.env` file (gitignored) or shell profile.

## Gitignore Safety

Ensure these are in `.gitignore`:

```
.env
.env.*
.aider*
.aider.chat.history.md
.aider.input.history
```

## Local Usage in RIGForge

Aider is used as a bounded Generator tool:

```bash
cd <repo>
aider --read spec.md --read DoneContract.yaml \
      --edit src/ --test "pytest tests/"
```

## Verification Commands

```bash
# Check aider is reachable
aider --version

# Check no leaked .aider files
ls -la .aider* 2>/dev/null || echo "clean"

# Check no API key in git
git grep -i "API_KEY" .gitignore || echo "no leaked keys"
```