"""Validated domain models shared by analysis, review, and persistence."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class FoodItem(BaseModel):
    """A visible or inferred component of the meal."""

    name: str = Field(min_length=1, max_length=120)
    portion: str = Field(min_length=1, max_length=120)


class MacroEstimate(BaseModel):
    """Structured model output that keeps uncertainty visible."""

    meal_name: str = Field(min_length=1, max_length=160)
    foods: list[FoodItem] = Field(default_factory=list, max_length=20)
    calories: float = Field(ge=0, le=10_000)
    protein_g: float = Field(ge=0, le=1_000)
    carbs_g: float = Field(ge=0, le=2_000)
    fat_g: float = Field(ge=0, le=1_000)
    identity_confidence: float = Field(ge=0, le=1)
    portion_confidence: float = Field(ge=0, le=1)
    nutrition_confidence: float = Field(ge=0, le=1)
    assumptions: list[str] = Field(default_factory=list, max_length=12)
    clarification_question: str | None = Field(default=None, max_length=300)
    source_summary: str = Field(min_length=1, max_length=500)

    @field_validator("meal_name", "source_summary")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("clarification_question")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class MealRecord(BaseModel):
    """The user-reviewed record stored locally and optionally in Supabase."""

    id: UUID = Field(default_factory=uuid4)
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    meal_name: str = Field(min_length=1, max_length=160)
    calories: float = Field(ge=0, le=10_000)
    protein_g: float = Field(ge=0, le=1_000)
    carbs_g: float = Field(ge=0, le=2_000)
    fat_g: float = Field(ge=0, le=1_000)
    identity_confidence: float = Field(ge=0, le=1)
    portion_confidence: float = Field(ge=0, le=1)
    nutrition_confidence: float = Field(ge=0, le=1)
    foods: list[FoodItem] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    source_summary: str = Field(min_length=1, max_length=500)
    user_note: str | None = Field(default=None, max_length=500)
    model_name: str = Field(min_length=1, max_length=120)
    user_confirmed: bool = True

    @classmethod
    def from_estimate(
        cls,
        estimate: MacroEstimate,
        *,
        meal_name: str,
        calories: float,
        protein_g: float,
        carbs_g: float,
        fat_g: float,
        user_note: str | None,
        model_name: str,
    ) -> MealRecord:
        return cls(
            meal_name=meal_name,
            calories=calories,
            protein_g=protein_g,
            carbs_g=carbs_g,
            fat_g=fat_g,
            identity_confidence=estimate.identity_confidence,
            portion_confidence=estimate.portion_confidence,
            nutrition_confidence=estimate.nutrition_confidence,
            foods=estimate.foods,
            assumptions=estimate.assumptions,
            source_summary=estimate.source_summary,
            user_note=user_note.strip() if user_note and user_note.strip() else None,
            model_name=model_name,
        )

    def persistence_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "observed_at": self.observed_at.isoformat(),
            "meal_name": self.meal_name,
            "calories": self.calories,
            "protein_g": self.protein_g,
            "carbs_g": self.carbs_g,
            "fat_g": self.fat_g,
            "identity_confidence": self.identity_confidence,
            "portion_confidence": self.portion_confidence,
            "nutrition_confidence": self.nutrition_confidence,
            "foods": [item.model_dump() for item in self.foods],
            "assumptions": self.assumptions,
            "source_summary": self.source_summary,
            "user_note": self.user_note,
            "model_name": self.model_name,
            "user_confirmed": self.user_confirmed,
        }
