# SchemaWiki Data Directory

This directory contains persistent data for SchemaWiki.

## Directory Structure

- `features/` - Feature documentation and metadata
- `postgres/` - PostgreSQL data persistence (managed by Docker)

## Features Directory

Each feature is stored in its own subdirectory under `/data/features/{feature_name}/`.

Standard files in each feature directory:
- `plan.md` - Feature plan/specification
- `implementation.md` - Implementation details
- `agent_steps.yaml` - Step-by-step agent instructions
- `replay_protocol.json` - Generated replay protocol
- `architecture.md` - Architecture documentation
- `api_contracts.yaml` - API contract definitions
- `tests.md` - Test coverage information
- `debug_logs/` - Debug logs from failed attempts
