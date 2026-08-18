# Data dictionary

`meal_estimates` stores the user-reviewed output. Raw photos are intentionally absent.

| Field | Meaning |
|---|---|
| `id` | Client-generated UUID shared by local and cloud copies |
| `user_id` | Supabase Auth owner; cloud only |
| `observed_at` | Timestamp associated with the meal record |
| `meal_name` | User-editable meal label |
| `calories` | Reviewed calorie estimate |
| `protein_g` | Reviewed protein estimate in grams |
| `carbs_g` | Reviewed carbohydrate estimate in grams |
| `fat_g` | Reviewed fat estimate in grams |
| `identity_confidence` | Model confidence in recognized foods, from 0 to 1 |
| `portion_confidence` | Model confidence in estimated quantities, from 0 to 1 |
| `nutrition_confidence` | Overall confidence in the resulting macro estimate, from 0 to 1 |
| `foods` | Structured list of food names and estimated portions |
| `assumptions` | Material assumptions that may affect the estimate |
| `source_summary` | Short explanation of the estimate's evidence and limits |
| `user_note` | Optional user-provided analysis context |
| `model_name` | Model or demo identifier that produced the draft |
| `user_confirmed` | Whether the values passed through the explicit review step |
| `created_at` | Cloud creation timestamp |
