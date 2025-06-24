# Things MCP Server

A Python CLI MCP (Model Context Protocol) server for Things 3, enabling programmatic access to todos and projects, including filtering by due date. Designed for automation, scripting, and integration with other tools.

[![Build Status](https://github.com/your-org/things-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/things-mcp/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/your-org/things-mcp)](LICENSE)
[![Coverage Status](https://img.shields.io/badge/coverage-100%25-brightgreen)](coverage.xml)

## Features

- Query all todos and projects from Things 3
- Filter todos by project or due date (YYYY-MM-DD)
- Clean, type-safe, and test-driven codebase
- CLI installable and easy to run
- Automation via justfile (run, test, lint, format, upgrade, etc.)

## Installation

```sh
uv pip install --break-system-packages .
```

## Usage

Start the MCP server:

```sh
things-mcp
```

Or, for development:

```sh
just run
```

### Querying Todos

Example request to get all todos:

```json
{"method": "get-todos"}
```

Example request to get todos due today:

```json
{"method": "get-todos", "params": {"due_date": "2025-06-24"}}
```

### Querying Projects

```json
{"method": "get-projects"}
```

## Development

- Run tests: `just test`
- Lint: `just lint`
- Format: `just format`
- Upgrade deps: `just upgrade`
- Add pre-commit hooks: `just precommit`
- Clean: `just clean`

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. Please read our [Code of Conduct](CODE_OF_CONDUCT.md).

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.

## Security

See [SECURITY.md](SECURITY.md) for reporting vulnerabilities. Contact: [your-email@example.com]

## License

Apache License, Version 2.0. See [LICENSE](LICENSE).
