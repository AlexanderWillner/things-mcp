#!/usr/bin/env -S just --justfile

set dotenv-load

TAG := `git describe --tags --abbrev=0 2>/dev/null || echo "0.0.0-alpha.0"`
VERSION := `echo ${VERSION:-0.0.0-alpha.0}`
COMMIT := `git rev-parse --short HEAD 2>/dev/null||echo c0ffee1`

# Show help
help:
	@just --list

# Show variables
show-vars:
	@echo "VERSION: {{VERSION}}"
	@echo "COMMIT: {{COMMIT}}"
	@echo "TAG: {{TAG}}"

# Run MCP Server
run:
	uv run --no-dev python3 -c "import sys; sys.path.insert(0, 'src'); from things_mcp.mcp import main; main()"

# Upgrade python packages
upgrade:
	uv lock --upgrade

# Build python package
build: prepare clean
	uv build

# Publish python package
publish: build
	uv publish -u token -p "${PYPI_PASSWORD}" dist/*.whl

# Give feedback
give-feedback:
	@python3 -m webbrowser "mailto:alex@willner.ws"

# Sync the project's dependencies
sync:
	uv sync --locked --no-dev --no-cache

# Run all pre-commit hooks
pre-commit: prepare
	pre-commit run -a

# Lint the code
lint:
	uv run ruff format src tests
	uv run ruff check --fix --unsafe-fixes src tests
	uv run bandit -q -r src
	uv run ty check src tests

# Run the tests
test:
	uv run --extra test pytest tests/ --cov=src/things_mcp --cov-report=term-missing --cov-report=xml

# Run GitHub Actions workflow locally using act
test-ci job-name="":
	act --pull=false -j "{{job-name}}"

# Clean the project
clean:
	rm -rf htmlcov .coverage coverage.xml .pytest_cache .ruff_cache .tox build dist logs .DS_Store .gitlab-ci-local **/*.egg-info **/__pycache__ __pycache__ && find . -type d \( -name .mypy_cache -o -name __pycache__ \) -exec rm -rf {} +

# Prune the project (also delete venv)
prune: clean
	rm -rf .venv

prepare:
	uv tool run --from=toml-cli toml set --toml-path=pyproject.toml project.version {{VERSION}}

# Tag a new version
tag:
	#!/bin/bash
	set -euo pipefail
	# Ensure working directory is clean
	if [ -n "$(git status --porcelain)" ]; then
		echo "Error: Working directory is not clean. Commit or stash your changes before tagging." >&2
		exit 1
	fi
	# Ensure remote exists
	if ! git remote | grep -q '^origin$'; then
		echo "Error: Remote 'origin' does not exist." >&2
		exit 1
	fi
	# Get latest tag or default
	LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "0.0.0")
	# Always initialize NEW_TAG
	NEW_TAG=""
	# Parse version and increment patch (only X.Y.Z supported)
	if echo "$LATEST_TAG" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$'; then
		NEW_TAG=$(echo "$LATEST_TAG" | awk -F. '{printf "%d.%d.%d", $1, $2, $3+1}')
	else
		NEW_TAG="0.0.1"
	fi
	# Check if tag already exists
	if git tag | grep -qx "$NEW_TAG"; then
		echo "Error: Tag $NEW_TAG already exists." >&2
		exit 1
	fi
	echo "Tagging version $NEW_TAG"
	uv tool run --from=toml-cli toml set --toml-path=pyproject.toml project.version $NEW_TAG
	uv build
	uv lock
	git add pyproject.toml uv.lock
	# Only commit if there are changes
	if ! git diff --cached --quiet; then
		git commit -m "Release $NEW_TAG" pyproject.toml uv.lock
	fi
	git tag -a $NEW_TAG -m "Release $NEW_TAG"
	git push --follow-tags origin HEAD

# Install the CLI as an executable in the system
install:
	pip install --break-system-packages .
