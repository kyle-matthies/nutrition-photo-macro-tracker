from io import BytesIO
from types import SimpleNamespace

import pytest
from PIL import Image

from macro_lens.analyzer import ImageValidationError, analyze_photo
from macro_lens.models import FoodItem, MacroEstimate


def image_bytes() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (8, 8), "green").save(buffer, format="PNG")
    return buffer.getvalue()


class FakeResponses:
    def __init__(self, estimate: MacroEstimate) -> None:
        self.estimate = estimate
        self.request = None

    def parse(self, **kwargs):
        self.request = kwargs
        return SimpleNamespace(output_parsed=self.estimate)


class FakeClient:
    def __init__(self, estimate: MacroEstimate) -> None:
        self.responses = FakeResponses(estimate)


def test_analyzer_uses_structured_image_request_without_persisting() -> None:
    expected = MacroEstimate(
        meal_name="Test meal",
        foods=[FoodItem(name="vegetables", portion="1 cup")],
        calories=300,
        protein_g=20,
        carbs_g=30,
        fat_g=10,
        identity_confidence=0.7,
        portion_confidence=0.3,
        nutrition_confidence=0.4,
        assumptions=["Cooking oil is unknown."],
        source_summary="Rough photo-based estimate.",
    )
    client = FakeClient(expected)

    result = analyze_photo(
        image_bytes(), "image/png", "vegetable bowl", client=client, model="test-model"
    )

    assert result == expected
    request = client.responses.request
    assert request["text_format"] is MacroEstimate
    image_part = request["input"][1]["content"][1]
    assert image_part["type"] == "input_image"
    assert image_part["image_url"].startswith("data:image/png;base64,")
    assert image_part["detail"] == "high"


def test_analyzer_rejects_declared_type_mismatch() -> None:
    with pytest.raises(ImageValidationError, match="do not match"):
        analyze_photo(image_bytes(), "image/jpeg", client=FakeClient(None))
