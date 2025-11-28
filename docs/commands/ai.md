# AI Integration

Fastpy includes AI-powered code generation for rapid prototyping.

## ai:generate

Generate code using AI based on natural language descriptions.

```bash
python cli.py ai:generate "Create a user profile model with avatar and bio"
```

::: warning API Key Required
Set your OpenAI API key in `.env`:
```bash
OPENAI_API_KEY=sk-your-api-key
```
:::

## How It Works

1. Describe what you want in plain English
2. AI generates appropriate code following Fastpy patterns
3. Review and customize the generated code

## Examples

### Generate a Model

```bash
python cli.py ai:generate "Create a Product model with name, price, SKU, and inventory count"
```

**Output:**

```python
from decimal import Decimal
from sqlmodel import Field
from app.models.base import BaseModel

class Product(BaseModel, table=True):
    __tablename__ = "products"

    name: str = Field(max_length=200)
    price: Decimal = Field(decimal_places=2)
    sku: str = Field(max_length=50, unique=True, index=True)
    inventory_count: int = Field(default=0, ge=0)
```

### Generate an Endpoint

```bash
python cli.py ai:generate "Create an endpoint to search products by name"
```

### Generate a Service Method

```bash
python cli.py ai:generate "Create a method to calculate order totals with tax"
```

## Supported Generation Types

| Type | Example Prompt |
|------|----------------|
| Models | "Create a model for blog comments" |
| Controllers | "Create CRUD controller for orders" |
| Routes | "Create endpoints for user settings" |
| Services | "Create email notification service" |
| Utilities | "Create helper for slug generation" |
| Tests | "Create tests for the Order model" |

## Best Practices

### Be Specific

```bash
# Good - specific requirements
python cli.py ai:generate "Create a Review model with rating (1-5), title, body, and foreign key to Product"

# Less effective - vague
python cli.py ai:generate "Create a review thing"
```

### Specify Constraints

```bash
python cli.py ai:generate "Create an Order model with:
- status enum (pending, processing, shipped, delivered)
- total as decimal with 2 places
- soft delete support
- timestamps"
```

### Review Generated Code

Always review AI-generated code before using:

1. Check field types are correct
2. Verify validation rules
3. Test edge cases
4. Ensure security best practices

## Limitations

- Generated code may need adjustment
- Complex business logic may require manual refinement
- Always validate against your specific requirements
- AI may not know about recent Fastpy updates

## Configuration

```bash
# .env
OPENAI_API_KEY=sk-your-api-key
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo
AI_MAX_TOKENS=2000
```

## Alternative: Use make:resource

For standard CRUD resources, the `make:resource` command is often faster and more reliable:

```bash
# This is deterministic and well-tested
python cli.py make:resource Product \
  -f name:string:required,max:200 \
  -f price:decimal:required \
  -f sku:string:required,unique,max:50 \
  -f inventory_count:integer:default:0,min:0 \
  -m -p
```

Use `ai:generate` for:
- Complex custom logic
- Non-standard patterns
- Prototyping ideas
- Learning Fastpy patterns
