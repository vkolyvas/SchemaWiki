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

## License

MIT
