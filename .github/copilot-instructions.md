# Copilot Instructions

This project is a Python CLI application that runs
a Model Context Protocol (MCP) Server for Things 3,
enabling AI access to todos and projects.

## Coding Standards

- Focus on code readability
- Divide code into smaller, self-contained modules or functions for reusability and maintainability
- Identify inefficient algorithms or data structures and refactor for better performance
- Avoid security vulnerabilities such as SQL injection, XSS, CSRF, etc
- Use Conventional Commits for commit messages
- Use Best Coding Practices and Clean Code and idiomatic expressions
- Use semantic/meaningful method names and variables, the code should read like a well-written book
- Use types where appropriate
- Use English for variables, comments and documentation
- Use a logger instead of print statements when appropriate
- Use stderr for error messages
- Use constants for magic numbers
- Use a makefile or justfile with target to run, test, lint, clean, format the code and to add pre-commit hooks and to upgrade dependencies

## Language Specific

### Python

- Make use of astral-sh/uv, astral-sh/ruff, and astral-sh/ty with standard package structure for executing commands (e.g. use the shebang `#!/usr/bin/env -S uv run --script` and PEP 722 for executable scripts)
- Use f-strings for string formatting

## Communication

- Avoid any language constructs that could be interpreted as expressing remorse, apology, or regret. This includes any phrases containing words like 'sorry', 'apologies', 'regret', etc., even when used in a context that isn't expressing remorse, apology, or regret
- If events or information are beyond your scope or knowledge, provide a response stating 'I don't know' without elaborating on why the information is unavailable
- Keep responses unique and free of repetition
- Always focus on the key points in my questions to determine my intent
- If a mistake is made in a previous response, recognize and correct it
- Do not hallucinate
