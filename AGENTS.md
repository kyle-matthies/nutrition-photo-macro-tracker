# Contributor and agent guidance

- Treat meal photos, notes, body metrics, and nutrition history as sensitive data.
- Never commit photos, databases, environment files, credentials, or real user records.
- Preserve uncertainty. A photo-only estimate must not be presented as precise nutrition data.
- Keep the review step explicit: generated estimates are editable before they are saved.
- Do not add diagnosis, treatment, medication, or prescriptive medical advice.
- Use a publishable Supabase key with user-authenticated RLS. Never expose a secret or service-role key.
- When schema fields change, update the migration, storage adapter, tests, and data dictionary together.

Run before submitting changes:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```
