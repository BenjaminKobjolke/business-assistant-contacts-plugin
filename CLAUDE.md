# Business Assistant Contacts Plugin - Development Guide

## Project Overview

Google Contacts plugin for Business Assistant v2. Source code in `src/business_assistant_contacts/`.

## Commands

- `uv sync --all-extras` — Install dependencies
- `uv run pytest tests/ -v` — Run tests
- `uv run ruff check src/ tests/` — Lint
- `uv run mypy src/` — Type check

## Architecture

- `config.py` — ContactsSettings (extends GoogleAuthSettings, frozen dataclass)
- `constants.py` — Plugin-specific string constants
- `contacts_client.py` — GoogleContactsClient (extends GoogleAuthClient, People API)
- `contacts_service.py` — High-level contact operations (string-returning)
- `plugin.py` — Plugin registration + PydanticAI tool definitions
- `__init__.py` — Exposes `register()` as entry point

## Plugin Protocol

The plugin exposes `register(registry: PluginRegistry)` which:
1. Loads Google Contacts settings from env vars
2. Skips registration if GOOGLE_CONTACTS_CREDENTIALS_PATH not configured
3. Creates ContactsService and registers 6 PydanticAI tools

## Restarting the Bot

After making code changes, always restart the bot by creating the restart flag:

```bash
touch "D:/GIT/BenjaminKobjolke/business-assistant-v2/restart.flag"
```

The bot picks it up within 5 seconds and restarts with fresh plugins.

## Code Analysis

After implementing new features or making significant changes, run the code analysis:

```bash
powershell -Command "cd 'D:\GIT\BenjaminKobjolke\business-assistant-contacts-plugin'; cmd /c '.\tools\analyze_code.bat'"
```

Fix any reported issues before committing.

## Rules

- Use objects for related values (DTOs/Settings)
- Centralize string constants in `constants.py`
- Tests are mandatory — use pytest with mocked Google People API
- Use `spec=` with MagicMock
- Type hints on all public APIs
- Frozen dataclasses for settings
