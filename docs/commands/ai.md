# AI Commands

Fastpy includes AI-powered resource generation and configuration generators for popular AI coding assistants.

## AI-Powered Resource Generation

Generate complete resources using natural language descriptions.

```bash
fastpy ai "Create a blog with posts, categories, and tags"
```

### Configuration

Set up your preferred AI provider:

```bash
# Set provider (anthropic, openai, or ollama)
export FASTPY_AI_PROVIDER=anthropic

# Set API key for your provider
export ANTHROPIC_API_KEY=your-api-key-here
# or
export OPENAI_API_KEY=your-api-key-here
```

::: tip Getting API Keys
- **Anthropic (Claude)**: Get your key at [console.anthropic.com](https://console.anthropic.com/)
- **OpenAI (GPT-4)**: Get your key at [platform.openai.com](https://platform.openai.com/api-keys)
- **Ollama**: Free, runs locally - [ollama.ai](https://ollama.ai/)
:::

### Supported Providers

| Provider | Model | API Key Variable |
|----------|-------|------------------|
| Anthropic | Claude Sonnet | `ANTHROPIC_API_KEY` |
| OpenAI | GPT-4 | `OPENAI_API_KEY` |
| Ollama | Llama 3.2 (local) | None required |

### Usage

```bash
# Basic usage - generates commands and asks for confirmation
fastpy ai "E-commerce with products, orders, and customers"

# Auto-execute generated commands
fastpy ai "User management system" --execute

# Preview commands without executing
fastpy ai "Blog system" --dry-run

# Use a specific provider
fastpy ai "Task manager with projects" --provider ollama
```

### Examples

```bash
# Blog system
fastpy ai "Create a blog with posts, categories, tags, and comments"

# E-commerce
fastpy ai "E-commerce store with products, categories, cart, and orders"

# Project management
fastpy ai "Project management with projects, tasks, and team members"

# Social media
fastpy ai "Social network with users, posts, likes, and followers"
```

### Check Configuration

View your current AI configuration:

```bash
fastpy config
```

Output:
```
AI Configuration

  Provider: anthropic
  ANTHROPIC_API_KEY: Set

Set provider with: export FASTPY_AI_PROVIDER=anthropic|openai|ollama
```

### Using Ollama (Free, Local)

For a free, local option, use Ollama:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3.2

# Set as provider
export FASTPY_AI_PROVIDER=ollama

# Use it
fastpy ai "Create a todo app with tasks and categories"
```

Configure Ollama:
```bash
export OLLAMA_MODEL=llama3.2      # Model to use
export OLLAMA_HOST=http://localhost:11434  # Ollama server URL
```

---

## AI Assistant Configuration

Fastpy also includes configuration generators for popular AI coding assistants. These configuration files help AI assistants understand your project structure, conventions, and available commands.

## Configuration

Generate AI assistant configurations using the CLI:

```bash
# Interactive mode - choose from menu
fastpy init:ai

# Direct selection
fastpy init:ai claude
fastpy init:ai copilot
fastpy init:ai cursor
fastpy init:ai gemini
```

## Supported AI Assistants

### Claude Code

**File:** `CLAUDE.md`

For use with [Claude Code](https://claude.ai/code) - Anthropic's CLI tool.

```bash
fastpy init:ai claude
```

### GitHub Copilot

**File:** `.github/copilot-instructions.md`

For use with GitHub Copilot in VS Code, JetBrains, and other IDEs.

```bash
fastpy init:ai copilot
```

### Cursor AI

**File:** `.cursorrules`

For use with the [Cursor](https://cursor.sh) AI-powered code editor.

```bash
fastpy init:ai cursor
```

### Google Gemini

**File:** `.gemini/instructions.md`

For use with Google Gemini Code Assist.

```bash
fastpy init:ai gemini
```

## What's Included in the Configuration

The generated configuration file includes comprehensive project context:

### Development Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Start development server
fastpy serve
uvicorn main:app --reload
```

### Code Generation Commands

```bash
# Generate complete resource
fastpy make:resource Post -f title:string:required -m -p

# Individual generators
fastpy make:model Post -f title:string:required -m
fastpy make:controller Post
fastpy make:route Post --protected
fastpy make:service Post
fastpy make:repository Post
fastpy make:middleware Logging
fastpy make:test Post
fastpy make:factory Post
fastpy make:seeder Post
fastpy make:enum Status -v active -v inactive
fastpy make:exception NotFound -s 404
```

### Database Commands

```bash
fastpy db:migrate
fastpy db:rollback
fastpy db:fresh
fastpy db:seed
```

### Project Architecture

- Directory structure and purpose of each folder
- Naming conventions (tables, models, files)
- Base model features (soft deletes, timestamps)

### API Documentation

- Authentication endpoints
- Standard response formats
- Custom exceptions
- Middleware details
- Health check endpoints

### Field Types and Validation

- All available field types
- Validation rules and syntax
- Examples for common patterns

## Customizing the Configuration

After generating, you can customize the configuration file to include:

- Project-specific instructions
- Custom conventions
- Business logic guidelines
- Team coding standards

Example customization at the end of the file:

```markdown
## Project-Specific Instructions

- Use snake_case for all API endpoints
- All monetary values use the `money` field type
- Include pagination on all list endpoints
- Always add soft delete support to models
```

## Benefits of AI Configuration

1. **Consistent Code Generation** - AI follows your project patterns
2. **Faster Development** - AI understands available commands
3. **Reduced Errors** - AI knows correct syntax and conventions
4. **Better Suggestions** - AI provides contextually relevant code

## Example AI Interactions

### With Claude Code

```
You: Create a Product model with name, price, and category

Claude: I'll create a Product model using Fastpy conventions:

fastpy make:resource Product \
  -f name:string:required,max:200 \
  -f price:money:required,ge:0 \
  -f category_id:integer:required,foreign:categories.id \
  -m -p
```

### With GitHub Copilot

When you type a comment, Copilot suggests code following Fastpy patterns:

```python
# Create endpoint to get products by category
@router.get("/category/{category_id}")
async def get_by_category(
    category_id: int,
    session: AsyncSession = Depends(get_session)
):
    # Copilot suggests the correct controller method
    return await ProductController.get_by_category(session, category_id)
```
