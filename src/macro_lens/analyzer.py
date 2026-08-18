"""Meal-photo analysis using structured OpenAI vision output."""

from __future__ import annotations

import base64
import os
from typing import Any

from openai import OpenAI
from PIL import Image
from pydantic import ValidationError

from macro_lens.models import FoodItem, MacroEstimate

SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMAGE_BYTES = 10 * 1024 * 1024
PIL_FORMAT_TO_MIME = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
    "GIF": "image/gif",
}

SYSTEM_PROMPT = """You estimate nutrition from meal photos for an educational tracking tool.
Return a rough, reviewable estimate, never medical advice. Identify visible foods and plausible
portions. Account for uncertainty from hidden oils, sauces, ingredients, and scale. Do not invent
brand or recipe certainty. Use confidence values from 0 to 1, with portion confidence usually the
lowest for a photo-only meal. List material assumptions. Ask at most one short clarification
question when one answer could materially improve the estimate. The user will review and edit all
values before saving them."""


class AnalysisConfigurationError(RuntimeError):
    """Raised when live analysis is requested without valid configuration."""


class ImageValidationError(ValueError):
    """Raised when an upload is unsafe or unsupported."""


def validate_image(image_bytes: bytes, mime_type: str) -> None:
    if mime_type not in SUPPORTED_IMAGE_TYPES:
        raise ImageValidationError("Use a JPEG, PNG, WEBP, or non-animated GIF image.")
    if not image_bytes:
        raise ImageValidationError("The uploaded image is empty.")
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise ImageValidationError("Images must be 10 MB or smaller.")

    from io import BytesIO

    try:
        with Image.open(BytesIO(image_bytes)) as image:
            detected_mime = PIL_FORMAT_TO_MIME.get(image.format or "")
            if detected_mime != mime_type:
                raise ImageValidationError(
                    "The image contents do not match the declared file type."
                )
            if getattr(image, "is_animated", False):
                raise ImageValidationError("Animated images are not supported.")
            image.verify()
    except ImageValidationError:
        raise
    except Exception as exc:
        raise ImageValidationError("The upload could not be decoded as an image.") from exc


def analyze_photo(
    image_bytes: bytes,
    mime_type: str,
    note: str | None = None,
    *,
    model: str | None = None,
    client: Any | None = None,
) -> MacroEstimate:
    """Analyze an in-memory image without persisting the photo."""

    validate_image(image_bytes, mime_type)
    note = (note or "").strip()[:500]

    if os.getenv("MACRO_LENS_DEMO", "0") == "1" and client is None:
        return demo_estimate(note)

    if client is None and not os.getenv("OPENAI_API_KEY"):
        raise AnalysisConfigurationError(
            "Set OPENAI_API_KEY for live analysis, or MACRO_LENS_DEMO=1 for a labeled demo."
        )

    selected_model = model or os.getenv("OPENAI_MODEL", "gpt-5.6")
    api = client or OpenAI()
    encoded = base64.b64encode(image_bytes).decode("ascii")
    context = note or "No additional context was provided."

    try:
        response = api.responses.parse(
            model=selected_model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": f"Estimate this meal. User context: {context}",
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:{mime_type};base64,{encoded}",
                            "detail": "high",
                        },
                    ],
                },
            ],
            text_format=MacroEstimate,
        )
    except ValidationError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Photo analysis failed: {exc}") from exc

    if response.output_parsed is None:
        raise RuntimeError("The model did not return a structured estimate.")
    return response.output_parsed


def demo_estimate(note: str | None = None) -> MacroEstimate:
    """Return a deterministic, conspicuously labeled UI demo result."""

    context = f" Context supplied: {note.strip()}." if note and note.strip() else ""
    return MacroEstimate(
        meal_name="Demo grain bowl",
        foods=[
            FoodItem(name="grain", portion="about 1 cup"),
            FoodItem(name="roasted vegetables", portion="about 1 cup"),
            FoodItem(name="protein", portion="about 4 oz"),
        ],
        calories=610,
        protein_g=34,
        carbs_g=70,
        fat_g=22,
        identity_confidence=0.62,
        portion_confidence=0.35,
        nutrition_confidence=0.38,
        assumptions=[
            "Demo data: the uploaded image was not analyzed.",
            "One tablespoon of cooking oil or dressing is assumed.",
        ],
        clarification_question="Was the sauce or dressing served on the side?",
        source_summary="Deterministic demo estimate for interface testing only." + context,
    )
