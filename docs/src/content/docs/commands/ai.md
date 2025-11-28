---
title: AI Integration
description: Generate configuration files for AI assistants
---

Fastpy can generate configuration files for various AI coding assistants, helping them understand your project structure and conventions.

## init:ai

Generate AI assistant configuration files.

```bash
python cli.py init:ai <assistant>
```

### Supported Assistants

| Assistant | Config File |
|-----------|-------------|
| `claude` | `.claude/CLAUDE.md` |
| `copilot` | `.github/copilot-instructions.md` |
| `cursor` | `.cursorrules` |
| `gemini` | `.gemini/config.md` |

### Examples

```bash
# Claude Code
python cli.py init:ai claude

# GitHub Copilot
python cli.py init:ai copilot

# Cursor AI
python cli.py init:ai cursor
```

## What Gets Generated

The generated configuration includes:

- Project structure overview
- Technology stack details
- Coding conventions
- CLI command reference
- Field type documentation
- Common patterns and examples

## Claude Configuration

```bash
python cli.py init:ai claude
```

Creates `.claude/CLAUDE.md` with:

```markdown
# CLAUDE.md

## Project Overview
Production-ready FastAPI starter...

## Technology Stack
- Framework: FastAPI (async/await)
- ORM: SQLModel
...

## CLI Commands
### Generate resources
python cli.py make:resource Post -f title:string:required
...
```

## Benefits

AI assistants configured with these files will:

- Understand your project architecture
- Follow your coding conventions
- Know available CLI commands
- Generate code consistent with your patterns
- Suggest appropriate field types and validations
