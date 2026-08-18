# Product decisions

## Product thesis

A meal photo is valuable evidence, but it is not enough evidence for precise portion measurement. The product should reduce logging friction without converting model confidence into false nutritional certainty.

The core job is: **help me turn a photo into a useful first draft that I can correct quickly and trust later because I reviewed it.**

## Target user

MacroLens is for adults who already understand that macro tracking is approximate and want a faster capture workflow. It is not designed for clinical nutrition, eating-disorder treatment, pediatric use, or emergency decisions.

## MVP workflow

| Stage | User value | Product control |
|---|---|---|
| Upload | Lower capture friction | Supported image validation and 10 MB app limit |
| Estimate | A usable first draft | Structured output and explicit model name |
| Understand | Know what could be wrong | Identity, portion, and nutrition confidence are separate |
| Correct | Apply human context | All macro fields remain editable before save |
| Retain | Build history | Local SQLite by default; optional user-owned Supabase |

## Deliberate non-goals

- Medical recommendations, diagnosis, or treatment.
- Silent automatic logging.
- Exact nutrient claims from a single photo.
- Automatic body-weight or calorie-target changes.
- Public photo hosting or community feeds.
- Service-role access in the application.

## Key tradeoffs

### Review friction over fake precision

The extra confirmation step may reduce completion rate, but it is the primary trust mechanism. A successful result is not merely generated; it is reviewed and saved.

### No raw-photo persistence by default

Keeping photos only in the current process reduces breach impact and makes the open-source default safer. It also means estimates cannot be independently re-audited later. An opt-in encrypted evidence store belongs in a later, explicitly threat-modeled release.

### Local-first with optional cloud history

SQLite makes the project useful with one API key and no backend account. Supabase adds cross-device history and demonstrates a multi-user security model without becoming a requirement for the core experience.

## Suggested success metrics

- Reviewed-save rate: percentage of generated estimates that users review and save.
- Median correction magnitude by macro: a proxy for where the model needs better context.
- Clarification usefulness: percentage of asked questions that materially change a saved value.
- Repeat logging time: time from upload to saved review for returning users.
- Confidence calibration: relationship between model confidence and user correction size.

The project intentionally does not optimize for number of model calls or unreviewed estimates generated.

## Roadmap

1. Capture anonymous correction deltas locally to assess calibration.
2. Add a nutrition-label mode with OCR-specific prompts and higher image detail.
3. Introduce a provider interface for local and hosted multimodal models.
4. Add optional, encrypted photo evidence with explicit retention controls.
5. Evaluate range estimates and uncertainty visualization with user research.
