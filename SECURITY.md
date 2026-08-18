# Security policy

## Supported versions

Security fixes are applied to the latest release and the `main` branch.

## Reporting a vulnerability

Please use GitHub's private vulnerability reporting for this repository. Do not open a public issue containing exploit details, credentials, personal nutrition data, or meal photos.

## Secrets and data

- Keep `OPENAI_API_KEY` local/server-side.
- Use only a Supabase publishable key in the app; never use a secret or service-role key.
- The included policies require an authenticated user and enforce row ownership.
- Local SQLite files and environment files are ignored by Git.
- Raw uploaded photos are not persisted by MacroLens.

If a credential is accidentally committed, revoke it first, then remove it from history and report the incident privately.
