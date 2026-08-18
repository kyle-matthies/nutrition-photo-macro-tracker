# Contributing

Thanks for helping improve MacroLens.

## Development setup

```bash
uv sync --all-groups
cp .env.example .env
uv run streamlit run app.py
```

Run the quality gates before opening a pull request:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

## Pull requests

- Keep changes focused and explain the user problem they address.
- Add or update tests for behavior changes.
- Update schema, storage adapters, tests, and documentation together when fields change.
- Preserve the editable review step and uncertainty fields.
- Use synthetic examples only. Do not include real photos, notes, credentials, database rows, or health information.

## Product boundaries

MacroLens estimates nutrition; it does not diagnose, treat, or prescribe. Features that imply medical certainty or silently turn a rough estimate into a saved fact are out of scope.
