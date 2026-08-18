from macro_lens.models import MacroEstimate, MealRecord
from macro_lens.storage import LocalMealStore


def test_local_round_trip(tmp_path) -> None:
    estimate = MacroEstimate(
        meal_name="Soup",
        calories=240,
        protein_g=14,
        carbs_g=28,
        fat_g=8,
        identity_confidence=0.8,
        portion_confidence=0.5,
        nutrition_confidence=0.55,
        assumptions=["Bowl size is estimated."],
        source_summary="Photo plus user context.",
    )
    record = MealRecord.from_estimate(
        estimate,
        meal_name="Soup",
        calories=240,
        protein_g=14,
        carbs_g=28,
        fat_g=8,
        user_note="medium bowl",
        model_name="test-model",
    )
    store = LocalMealStore(tmp_path / "history.sqlite")

    store.save(record)
    rows = store.list_recent()

    assert len(rows) == 1
    assert rows[0]["id"] == str(record.id)
    assert rows[0]["meal_name"] == "Soup"
    assert rows[0]["nutrition_confidence"] == 0.55
