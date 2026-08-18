from macro_lens.models import FoodItem, MacroEstimate, MealRecord


def estimate() -> MacroEstimate:
    return MacroEstimate(
        meal_name="Rice bowl",
        foods=[FoodItem(name="rice", portion="1 cup")],
        calories=500,
        protein_g=30,
        carbs_g=60,
        fat_g=15,
        identity_confidence=0.8,
        portion_confidence=0.4,
        nutrition_confidence=0.5,
        assumptions=["Oil is not visible."],
        source_summary="Photo-only rough estimate.",
    )


def test_reviewed_values_replace_model_draft() -> None:
    record = MealRecord.from_estimate(
        estimate(),
        meal_name="Corrected bowl",
        calories=550,
        protein_g=35,
        carbs_g=62,
        fat_g=17,
        user_note="extra chicken",
        model_name="test-model",
    )

    assert record.meal_name == "Corrected bowl"
    assert record.calories == 550
    assert record.user_confirmed is True
    assert record.assumptions == ["Oil is not visible."]


def test_persistence_payload_contains_no_photo_field() -> None:
    record = MealRecord.from_estimate(
        estimate(),
        meal_name="Rice bowl",
        calories=500,
        protein_g=30,
        carbs_g=60,
        fat_g=15,
        user_note=None,
        model_name="test-model",
    )

    payload = record.persistence_payload()
    assert not any("photo" in key or "image" in key for key in payload)
