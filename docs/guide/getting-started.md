# Getting Started

This guide will help you install Fastpy CLI and create your first project.

## Installation

### pip (recommended)

```bash
pip install fastpy-cli
```

### pipx (isolated environment)

```bash
pipx install fastpy-cli
```

::: tip Why pipx?
pipx automatically handles PATH configuration and keeps packages isolated. It's the easiest way to install CLI tools.
:::

### Homebrew (macOS)

```bash
brew tap vutia-ent/tap
brew install fastpy
```

### Verify Installation

```bash
fastpy version
```

## Troubleshooting: Command Not Found

If you get `fastpy: command not found` after installing with pip, the Python scripts directory isn't in your PATH.

### macOS

```bash
# Add Python scripts to PATH
echo 'export PATH="'$(python3 -m site --user-base)/bin':$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Linux

```bash
# Add Python scripts to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Windows (PowerShell)

```powershell
# Find Python scripts path
python -m site --user-site

# The Scripts folder is typically:
# C:\Users\USERNAME\AppData\Roaming\Python\Python3X\Scripts

# Add to PATH via:
# System Properties > Environment Variables > Path > Edit > New
```

### Alternative Solutions

1. **Use pipx** - Automatically handles PATH:
   ```bash
   pipx install fastpy-cli
   ```

2. **Use Homebrew (macOS)** - No PATH issues:
   ```bash
   brew install vutia-ent/tap/fastpy
   ```

3. **Run as Python module**:
   ```bash
   python3 -m fastpy_cli.main version
   ```

## Quick Start

### 1. Create a New Project

```bash
fastpy new my-api
```

This clones the Fastpy template and optionally runs setup.

### 2. Navigate to the Project

```bash
cd my-api
```

### 3. Run Setup (if not done during creation)

```bash
fastpy setup
```

This will:
- Create a virtual environment
- Install dependencies
- Generate `.env` file
- Run database migrations

### 4. Start the Development Server

```bash
fastpy serve
```

Your API is now running at `http://localhost:8000`

## Verify Everything Works

```bash
# Check API health
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs
```

## Next Steps

- [Configuration](/guide/configuration) - Configure your project
- [AI Commands](/commands/ai) - Generate code with AI
- [Commands Overview](/commands/overview) - All available commands
