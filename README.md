# SchemaWiki

AI-native feature documentation and engineering memory system that enables coding agents (like Claude Code, Cursor IDE) to recreate features using a replay protocol. Provides searchable knowledge base for features and integrates into a Dockerized environment.

## Features

- **Feature Management**: CRUD operations with semantic versioning
- **Replay Engine**: Generate replay protocols to recreate features from documentation
- **Knowledge Extraction**: Parse code for API routes, DB migrations, imports
- **Git Integration**: Automatic commits for every feature file change
- **Search**: Text search across features and file contents
- **Agent CLI**: Command-line interface for interacting with SchemaWiki

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Running with Docker

```bash
cd docker
docker-compose up -d
```

The API will be available at `http://localhost:8080`

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your database URL

# Run the API
uvicorn api.server:app --reload
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/features` | POST | Create a new feature |
| `/features/{name}` | GET | Get feature details |
| `/features` | GET | List all features |
| `/features/{name}` | PATCH | Update feature metadata |
| `/features/{name}` | DELETE | Delete a feature |
| `/features/{name}/files` | PUT | Update a feature file |
| `/features/{name}/replay` | GET | Get replay protocol |
| `/features/{name}/version/bump` | POST | Bump feature version |
| `/search` | GET | Search features |
| `/hooks` | POST | Record development events |

## CLI Commands

```bash
# Record a new feature
schemawiki record-feature "feature-name" -d "Description" -t "tag1,tag2"

# Get feature plan
schemawiki get-plan "feature-name"

# Search features
schemawiki search "query" --tags "tag1"

# Recreate feature (get replay protocol)
schemawiki recreate "feature-name"

# List all features
schemawiki list-features

# Update a feature file
schemawiki update-file "feature-name" plan.md "@/path/to/file.md"
```

## Feature Structure

Each feature is stored in `/data/features/{feature_name}/` with:

```
feature_name/
├── plan.md              # Feature plan/specification
├── implementation.md    # Implementation details
├── agent_steps.yaml    # Step-by-step agent instructions
├── replay_protocol.json # Generated replay protocol
├── architecture.md     # Architecture documentation
├── api_contracts.yaml # API contract definitions
├── tests.md          # Test coverage information
└── debug_logs/       # Debug logs from failed attempts
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql+asyncpg://schemawiki:schemawiki@localhost:5433/schemawiki` |
| `FEATURES_DATA_PATH` | Path for feature files | `/data/features` |
| `API_HOST` | API host | `0.0.0.0` |
| `API_PORT` | API port | `8080` |

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .
```

## Architecture

- **FastAPI**: REST API server
- **PostgreSQL**: Metadata storage
- **SQLAlchemy**: ORM with async support
- **GitPython**: Git operations
- **sentence-transformers**: Semantic search (Phase 4)

## MCP Server - AI Agent Activity Recording

The MCP server records AI agent activities during software development, capturing the **why** behind every step.

### Running the MCP Server

#### Option 1: Docker (Recommended)
```bash
cd docker
docker-compose up -d
```

#### Option 2: Local
```bash
python mcp_server.py
```

### MCP Tools

The server provides these tools for Claude Code:

| Tool | Description |
|------|-------------|
| `create_feature` | Create a new feature with name, description, version, tags |
| `record_step` | Record an implementation step with reasoning and trigger |
| `record_event` | Record events (lint_error, test_failed, bug_fix, etc.) |
| `update_implementation` | Update implementation documentation |
| `add_debug_log` | Log errors with root cause analysis |
| `get_feature` | Get full feature details |
| `generate_wiki` | Generate markdown/HTML wiki page |
| `list_features` | List all recorded features |
| `search_features` | Search features by query |

### Understanding the "Why" Tracking

Every step and event captures:

- **`why`**: The reasoning behind the action
- **`trigger`**: What initiated this (user_request, error, test_failure, lint_error, missing_code, bug_fix)
- **`context`**: Additional background information
- **`files_modified`**: Which files were changed

### Event Types

Use these event types with `record_event`:

| Event | Description |
|-------|-------------|
| `feature_coded` | Feature implementation completed |
| `service_restarted` | Service was restarted |
| `change_pushed` | Code pushed to repository |
| `missing_code` | Discovered missing functionality |
| `lint_error` | Linting error occurred |
| `test_passed` | Tests passed |
| `test_failed` | Tests failed |
| `bug_fix` | Bug was fixed |
| `code_review` | Code review performed |
| `refactor` | Code was refactored |
| `dependency_added` | New dependency added |
| `config_changed` | Configuration changed |
| `api_contract_change` | API contract modified |
| `db_migration` | Database migration applied |

### Example Workflow

1. **Create a feature:**
```python
create_feature(
    name="user-auth",
    description="JWT authentication system",
    version="1.0.0",
    why="Users need secure authentication"
)
```

2. **Record implementation steps:**
```python
record_step(
    feature_name="user-auth",
    step="Create User model",
    why="Need to store user credentials securely",
    trigger="user_request",
    command="python -m flask db create",
    files_modified=["models/user.py", "schemas/user.yaml"]
)
```

3. **Record events:**
```python
record_event(
    feature_name="user-auth",
    event_type="lint_error",
    why="Discovered unused import in user model",
    details="Removed unused 'os' import",
    files=["models/user.py"]
)
```

4. **Add debug logs:**
```python
add_debug_log(
    feature_name="user-auth",
    attempt=2,
    error="JWT token expired immediately",
    why_failed="Token expiry not set in config",
    fix_applied="Added 'expire_minutes': 60 to config"
)
```

5. **Generate wiki:**
```python
generate_wiki(
    feature_name="user-auth",
    format="markdown"  # or "html"
)
```

### Wiki Output

The generated wiki includes:

- **Why the feature exists** - Business justification
- **Plan and implementation** - Technical details
- **Development events** - Key milestones with reasoning
- **Implementation steps** - Each step with why/trigger
- **Debug logs** - Root cause analysis from failures

This gives future developers complete context on why decisions were made.

### REST API

The MCP server also exposes REST endpoints on port 8081:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/features` | POST | Create feature |
| `/steps` | POST | Record step |
| `/events` | POST | Record event |
| `/features/{name}` | GET | Get feature |
| `/wiki/{name}` | GET | Generate wiki (saves to disk) |
| `/wikis` | GET | List all saved wikis |
| `/wikis/{name}` | GET | Get saved wiki content |
| `/wikis/{name}/download` | GET | Download wiki file |

### Accessing Wiki Pages

Wikis are saved to `/data/wikis/` (or `WIKI_DATA_PATH` env var). Humans can access them via:

1. **REST API** (http://localhost:8081):
   ```bash
   # List all wikis
   curl http://localhost:8081/wikis

   # Get wiki content
   curl http://localhost:8081/wikis/user-auth

   # Download as file
   curl http://localhost:8081/wikis/user-auth/download -o user-auth.md
   ```

2. **Direct File Access** (Docker):
   ```bash
   # Mounted volume location
   docker volume ls | grep wikis
   docker run --rm -it -v schemawiki_wikis_data:/data/wikis alpine cat /data/wikis/user-auth.md
   ```

3. **Browser** (if serving static files):
   - Markdown: View raw file at `/wikis/{name}`
   - HTML: Generate with `format=html` parameter

The wiki path is returned in the response and stored in the feature's `wiki_path` field.

### Pushing Wikis to GitHub

You can automatically push generated wikis to a GitHub repository:

1. Set environment variables:
   ```bash
   GITHUB_REPO=owner/repo        # e.g., vkolyvas/SchemaWiki
   GITHUB_TOKEN=ghp_xxx         # GitHub personal access token
   WIKI_BRANCH=main             # Branch to push to (default: main)
   ```

2. Generate wiki with push:
   ```python
   generate_wiki(
       feature_name="user-auth",
       format="markdown",
       push_to_github=True
   )
   ```

   Or set env vars and it will auto-push:
   ```bash
   export GITHUB_REPO=vkolyvas/SchemaWiki
   export GITHUB_TOKEN=ghp_xxx
   # Now any generate_wiki call will push to GitHub
   ```

3. Wiki files are saved in the repo under `SchemaWiki/{feature-name}.md`

4. The GitHub URL is stored in `feature["github_wiki_url"]`

**GitHub Token Setup:**
- Go to GitHub Settings > Developer settings > Personal access tokens
- Generate new token (Fine-grained)
- Permissions: Contents: Read/Write

**Accessing GitHub Wikis:**
- View online: `https://github.com/{owner}/{repo}/blob/{branch}/SchemaWiki/{feature-name}.md`
- Raw: `https://raw.githubusercontent.com/{owner}/{repo}/{branch}/SchemaWiki/{feature-name}.md`

### Configuration for Claude Code

Add to your Claude Code settings:

```json
{
  "mcpServers": {
    "schemawiki": {
      "command": "python",
      "args": ["/path/to/SchemaWiki/mcp_server.py"]
    }
  }
}
```

## License

MIT
