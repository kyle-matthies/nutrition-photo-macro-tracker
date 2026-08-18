# Privacy and threat model

## Data inventory

| Data | Local SQLite | Supabase | Vision provider |
|---|---:|---:|---:|
| Raw meal photo | No | No | Yes, for live analysis |
| Reviewed macros | Yes | Optional | Produced by provider |
| Optional user note | Yes | Optional | Yes, as analysis context |
| Confidence and assumptions | Yes | Optional | Produced by provider |
| Email/password | No | Supabase Auth | No |

The browser or Streamlit runtime may hold the current upload in memory for the active session. MacroLens does not write it to disk.

## Trust boundaries

1. The user's device and local SQLite file.
2. The configured model provider, which receives the image and optional note.
3. The user's Supabase project, when cloud sync is enabled.
4. The public source repository, which must contain no real user data or credentials.

## Primary threats and controls

### Credential disclosure

- `.env` and local database files are ignored.
- The OpenAI key stays local/server-side.
- The app accepts only a Supabase publishable key.
- The repository contains no project URL, user UUID, access token, or service-role key.

### Cross-user data access

- Every cloud row has a non-null `user_id` linked to `auth.users`.
- RLS is enabled before authenticated grants are useful.
- SELECT, INSERT, UPDATE, and DELETE policies compare `(select auth.uid())` with `user_id`.
- UPDATE includes both `USING` and `WITH CHECK`.
- An index covers the ownership predicate and common sort.

### Sensitive image retention

- No photo column or Storage bucket is created.
- Images are converted to an in-memory data URL only for the model request.
- A future persistence feature must be opt-in, private-bucket-only, encrypted where appropriate, and covered by retention/deletion tests.

### False confidence

- Three confidence dimensions remain visible.
- The app presents assumptions and an optional clarification question.
- Generated fields are editable before save.
- The UI and documentation state that estimates are educational and can be materially wrong.

## Operator responsibilities

- Review current model-provider data controls before using sensitive photos.
- Keep Supabase Auth, Data API exposure, and RLS settings aligned.
- Use synthetic data in development, issues, and pull requests.
- Rotate any exposed credential immediately.
- Do not treat this project as a HIPAA-ready system without a separate compliance assessment.
