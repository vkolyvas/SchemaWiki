# SchemaWiki Claude Code Prompt

Use this prompt in any Claude Code session to record feature development with SchemaWiki.

---

## Quick Start

### 1. Ensure MCP Server is Running

The SchemaWiki MCP server must be running at `http://localhost:8081`. If not, start it:

```bash
cd /home/onchain3r/base/SchemaWiki/docker
docker-compose up -d mcp
```

### 2. Configure Claude Code MCP

Add to your `claude.json` settings:

```json
{
  "mcpServers": {
    "schemawiki": {
      "command": "curl",
      "args": ["-s", "http://localhost:8081"]
    }
  }
}
```

**Or use REST API directly** (no MCP needed):

```bash
export SCHEMAWIKI_URL=http://localhost:8081
```

---

## Available Tools

### Create Feature

Record a new feature with business justification:

```
Call create_feature with:
- name: "feature-name"
- description: "What it does"
- version: "1.0.0"
- why: "Why this feature exists (business reason)"
- tags: ["tag1", "tag2"]
```

### Record Step

Record each implementation step with reasoning:

```
Call record_step with:
- feature_name: "feature-name"
- step: "What you did"
- why: "Why you did it this way"
- trigger: "user_request | error | test_failure | lint_error | missing_code | bug_fix"
- command: "Command executed (optional)"
- files_modified: ["file1.py", "file2.py"]
- status: "completed | in_progress | failed"
- context: "Additional context (optional)"
```

### Record Event

Record significant development events:

```
Call record_event with:
- feature_name: "feature-name"
- event_type: "feature_coded | service_restarted | change_pushed | missing_code | lint_error | test_passed | test_failed | bug_fix | code_review | refactor | dependency_added | config_changed | api_contract_change | db_migration"
- why: "Why this happened"
- details: "What happened"
- files: ["affected files"]
- auto_wiki: true (optional - auto-generates wiki after feature_coded, change_pushed, service_restarted)
```

### Update Implementation

Add implementation details:

```
Call update_implementation with:
- feature_name: "feature-name"
- content: "Implementation details"
- why: "Why this implementation was chosen"
```

### Add Debug Log

Record errors with root cause analysis:

```
Call add_debug_log with:
- feature_name: "feature-name"
- attempt: 1
- error: "Error message"
- why_failed: "Root cause analysis"
- fix_applied: "How it was fixed"
- log: "Full debug log (optional)"
```

### Generate Wiki

Create human-readable wiki page:

```
Call generate_wiki with:
- feature_name: "feature-name"
- format: "markdown | html"
- push_to_github: true (optional - requires GITHUB_REPO and GITHUB_TOKEN env vars)
```

### List Features

```
Call list_features
```

### Search Features

```
Call search_features with:
- query: "search term"
```

---

## Example Workflow

### Start New Feature

```
create_feature(
    name="user-authentication",
    description="JWT-based authentication system",
    version="1.0.0",
    why="Users need secure authentication to access protected resources",
    tags=["auth", "security", "api"]
)
```

### During Implementation

```
# After creating a file
record_step(
    feature_name="user-authentication",
    step="Create User model",
    why="Need to store user credentials and profile data",
    trigger="feature_requirement",
    command="sqlacodegen users.db > models/user.py",
    files_modified=["models/user.py", "schemas/user.yaml"],
    status="completed"
)

# After fixing a bug
record_step(
    feature_name="user-authentication",
    step="Fix token expiration",
    why="Tokens were expiring immediately due to missing config",
    trigger="bug_fix",
    command="Update JWT config",
    files_modified=["config/jwt.yaml"],
    status="completed"
)

# After tests pass
record_event(
    feature_name="user-authentication",
    event_type="test_passed",
    why="All authentication tests passing",
    details="Login, logout, register, token refresh all working"
)
```

### Complete Feature

```
record_event(
    feature_name="user-authentication",
    event_type="change_pushed",
    why="Feature complete and ready for review",
    files=["models/user.py", "auth/jwt.py", "routes/auth.py"],
    auto_wiki=true
)
```

---

## REST API Alternative

If MCP is not configured, use curl directly:

```bash
# Create feature
curl -X POST http://localhost:8081/features \
  -H "Content-Type: application/json" \
  -d '{"name": "feature-name", "why": "Business reason"}'

# Record step
curl -X POST http://localhost:8081/steps \
  -H "Content-Type: application/json" \
  -d '{"feature_name": "feature-name", "step": "Did something", "why": "Why"}'

# Generate wiki
curl http://localhost:8081/wiki/feature-name
```

---

## Environment Variables

Set these for auto-wiki generation and GitHub push:

- `SCHEMAWIKI_URL` - API URL (default: http://localhost:8081)
- `GITHUB_REPO` - Repository for wiki push (e.g., `owner/repo`)
- `GITHUB_TOKEN` - GitHub personal access token
- `WIKI_BRANCH` - Branch to push to (default: main)

---

## Wiki Output

The generated wiki includes:

- **Why the feature exists** - Business justification
- **Description** - Feature details
- **Plan** - Original plan
- **Implementation** - Technical details
- **Development Events** - Key milestones with reasoning
- **Implementation Steps** - Each step with why/trigger
- **Debug Logs** - Root cause analysis from failures

Access wikis at:
- REST: `http://localhost:8081/wikis/{feature-name}`
- GitHub: `https://github.com/{owner}/{repo}/blob/{branch}/SchemaWiki/{feature-name}.md`
