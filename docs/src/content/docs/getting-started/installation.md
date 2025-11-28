---
title: Installation
description: Get Fastpy up and running on your system
---

import { Tabs, TabItem } from '@astrojs/starlight/components';

## Prerequisites

Before installing Fastpy, ensure you have:

- **Python 3.9+** - [Download Python](https://www.python.org/downloads/)
- **PostgreSQL 12+** or **MySQL 5.7+** (MySQL 8.0 recommended)
- **pip** (comes with Python)

## Quick Installation

The fastest way to get started:

```bash
# Clone the repository
git clone https://github.com/vutia-ent/fastpy.git
cd fastpy

# Run the setup script
./setup.sh
```

The setup script will:
1. Check Python version
2. Create a virtual environment
3. Install dependencies (handling common issues automatically)
4. Configure your database
5. Generate a secure secret key
6. Run initial migrations (optional)

## Manual Installation

If you prefer manual setup:

<Tabs>
  <TabItem label="PostgreSQL">
```bash
# Clone and enter directory
git clone https://github.com/vutia-ent/fastpy.git
cd fastpy

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your database credentials
# DB_DRIVER=postgresql
# DATABASE_URL=postgresql://user:pass@localhost:5432/fastpy_db

# Run migrations
alembic upgrade head

# Start the server
uvicorn main:app --reload
```
  </TabItem>
  <TabItem label="MySQL">
```bash
# Clone and enter directory
git clone https://github.com/vutia-ent/fastpy.git
cd fastpy

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your database credentials
# DB_DRIVER=mysql
# DATABASE_URL=mysql://root:pass@localhost:3306/fastpy_db

# Run migrations
alembic upgrade head

# Start the server
uvicorn main:app --reload
```
  </TabItem>
</Tabs>

## Troubleshooting

### mysqlclient fails on macOS

```bash
brew install mysql-client
export PATH="/opt/homebrew/opt/mysql-client/bin:$PATH"  # Apple Silicon
# or
export PATH="/usr/local/opt/mysql-client/bin:$PATH"     # Intel
pip install mysqlclient
```

### bcrypt errors

```bash
pip install bcrypt==4.2.1 passlib==1.7.4
```

### greenlet missing

```bash
pip install greenlet==3.2.4
```

### Migration shows "sqlmodel not defined"

Add this import to the migration file:
```python
import sqlmodel
```

## Verify Installation

After installation, verify everything works:

```bash
# Check the CLI
python cli.py list

# Run tests
pytest

# Start dev server
uvicorn main:app --reload
```

Visit http://localhost:8000/docs to see the API documentation.

## Next Steps

- Follow the [Quick Start](/fastpy/getting-started/quickstart/) tutorial
- Learn about [Configuration](/fastpy/getting-started/configuration/) options
- Explore [CLI Commands](/fastpy/commands/overview/)
