# AI Assistant Integration

Fastpy includes built-in configuration generators for popular AI coding assistants. These configuration files help AI assistants understand your project structure, conventions, and available commands.

## Setup During Installation

When running `./setup.sh`, you'll be prompted to select an AI assistant:

```
========================================
  AI Assistant Configuration
========================================

Select an AI assistant to configure (optional):
  1) Claude (CLAUDE.md)
  2) GitHub Copilot (.github/copilot-instructions.md)
  3) Cursor (.cursorrules)
  4) Google Gemini (.gemini/instructions.md)
  5) Skip
```

## Manual Configuration

You can also generate AI configurations at any time:

```bash
# Interactive mode - choose from menu
python cli.py init:ai

# Direct selection
python cli.py init:ai claude
python cli.py init:ai copilot
python cli.py init:ai cursor
python cli.py init:ai gemini
```

## Supported AI Assistants

### Claude Code

**File:** `CLAUDE.md`

For use with [Claude Code](https://claude.ai/code) - Anthropic's CLI tool.

```bash
python cli.py init:ai claude
```

### GitHub Copilot

**File:** `.github/copilot-instructions.md`

For use with GitHub Copilot in VS Code, JetBrains, and other IDEs.

```bash
python cli.py init:ai copilot
```

### Cursor AI

**File:** `.cursorrules`

For use with the [Cursor](https://cursor.sh) AI-powered code editor.

```bash
python cli.py init:ai cursor
```

### Google Gemini

**File:** `.gemini/instructions.md`

For use with Google Gemini Code Assist.

```bash
python cli.py init:ai gemini
```

## What's Included in the Configuration

The generated configuration file includes comprehensive project context:

### Development Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Start development server
python cli.py serve
uvicorn main:app --reload
```

### Code Generation Commands

```bash
# Generate complete resource
python cli.py make:resource Post -f title:string:required -m -p

# Individual generators
python cli.py make:model Post -f title:string:required -m
python cli.py make:controller Post
python cli.py make:route Post --protected
python cli.py make:service Post
python cli.py make:repository Post
python cli.py make:middleware Logging
python cli.py make:test Post
python cli.py make:factory Post
python cli.py make:seeder Post
python cli.py make:enum Status -v active -v inactive
python cli.py make:exception NotFound -s 404
```

### Database Commands

```bash
python cli.py db:migrate
python cli.py db:rollback
python cli.py db:fresh
python cli.py db:seed
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

python cli.py make:resource Product \
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
