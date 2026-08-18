"""Streamlit interface for the review-first MacroLens workflow."""

from __future__ import annotations

import os
from typing import Any

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from macro_lens.analyzer import (
    AnalysisConfigurationError,
    ImageValidationError,
    analyze_photo,
)
from macro_lens.models import MealRecord
from macro_lens.storage import LocalMealStore, SupabaseMealStore

load_dotenv()
st.set_page_config(page_title="MacroLens", page_icon="🥗", layout="wide")


def main() -> None:
    st.title("MacroLens")
    st.caption("Review-first macro estimates from meal photos")
    st.warning(
        "Educational estimate only—not medical advice. Photos are weak evidence for portion size, "
        "and every result should be reviewed before saving."
    )

    configure_cloud_sidebar()
    capture_tab, history_tab, about_tab = st.tabs(["Analyze", "History", "How it works"])
    with capture_tab:
        render_capture()
    with history_tab:
        render_history()
    with about_tab:
        render_about()


def configure_cloud_sidebar() -> None:
    st.sidebar.header("Optional cloud history")
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
    if not url or not key:
        st.sidebar.caption("Local-only mode. Add Supabase settings to `.env` to enable sync.")
        return

    if st.session_state.get("cloud_store"):
        st.sidebar.success("Signed in; new records will sync with Supabase.")
        if st.sidebar.button("Disconnect cloud session"):
            try:
                st.session_state.cloud_store.sign_out()
            except Exception:
                pass
            st.session_state.pop("cloud_store", None)
            st.rerun()
        return

    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Sign in", disabled=not (email and password)):
        try:
            st.session_state.cloud_store = SupabaseMealStore.sign_in(url, key, email, password)
            st.rerun()
        except Exception as exc:
            st.sidebar.error(f"Sign-in failed: {exc}")


def render_capture() -> None:
    left, right = st.columns([1, 1], gap="large")
    with left:
        uploaded = st.file_uploader(
            "Meal photo",
            type=["jpg", "jpeg", "png", "webp", "gif"],
            help="The app keeps the photo in memory for this session and does not save it.",
        )
        note = st.text_area(
            "Optional context",
            max_chars=500,
            placeholder="Example: chicken bowl; dressing on the side",
        )
        if os.getenv("MACRO_LENS_DEMO", "0") == "1":
            st.info(
                "Demo mode is on. The displayed result will not be based on the uploaded image."
            )
        analyze_clicked = st.button(
            "Analyze photo",
            type="primary",
            disabled=uploaded is None,
            use_container_width=True,
        )
        if uploaded is not None:
            st.image(uploaded, caption="Session-only preview", width="stretch")

    if analyze_clicked and uploaded is not None:
        try:
            with st.spinner("Building a rough estimate..."):
                estimate = analyze_photo(uploaded.getvalue(), uploaded.type, note)
            st.session_state.estimate = estimate
            st.session_state.estimate_note = note
        except (ImageValidationError, AnalysisConfigurationError) as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Could not analyze this photo: {exc}")

    with right:
        estimate = st.session_state.get("estimate")
        if estimate is None:
            st.info("Upload a photo to generate an editable estimate.")
            return
        render_review_form(estimate, st.session_state.get("estimate_note", ""))


def render_review_form(estimate: Any, note: str) -> None:
    st.subheader("Review before saving")
    if estimate.clarification_question:
        st.info(estimate.clarification_question)

    with st.form("review-estimate"):
        meal_name = st.text_input("Meal", value=estimate.meal_name, max_chars=160)
        cols = st.columns(4)
        calories = cols[0].number_input("Calories", min_value=0.0, value=estimate.calories)
        protein = cols[1].number_input("Protein (g)", min_value=0.0, value=estimate.protein_g)
        carbs = cols[2].number_input("Carbs (g)", min_value=0.0, value=estimate.carbs_g)
        fat = cols[3].number_input("Fat (g)", min_value=0.0, value=estimate.fat_g)

        confidence_cols = st.columns(3)
        confidence_cols[0].metric("Identity confidence", f"{estimate.identity_confidence:.0%}")
        confidence_cols[1].metric("Portion confidence", f"{estimate.portion_confidence:.0%}")
        confidence_cols[2].metric("Nutrition confidence", f"{estimate.nutrition_confidence:.0%}")

        st.write("**Model assumptions**")
        for assumption in estimate.assumptions:
            st.write(f"- {assumption}")
        if estimate.foods:
            st.caption(
                "Detected components: "
                + ", ".join(f"{item.name} ({item.portion})" for item in estimate.foods)
            )

        saved = st.form_submit_button("Save reviewed estimate", type="primary")

    if saved:
        model_name = (
            "demo-not-image-analysis"
            if os.getenv("MACRO_LENS_DEMO", "0") == "1"
            else os.getenv("OPENAI_MODEL", "gpt-5.6")
        )
        record = MealRecord.from_estimate(
            estimate,
            meal_name=meal_name,
            calories=calories,
            protein_g=protein,
            carbs_g=carbs,
            fat_g=fat,
            user_note=note,
            model_name=model_name,
        )
        LocalMealStore().save(record)
        cloud_store = st.session_state.get("cloud_store")
        if cloud_store:
            try:
                cloud_store.save(record)
                st.success("Saved locally and synced to Supabase.")
            except Exception as exc:
                st.warning(f"Saved locally, but cloud sync failed: {exc}")
        else:
            st.success("Saved locally.")


def render_history() -> None:
    source = st.radio("History source", ["Local", "Supabase"], horizontal=True)
    if source == "Supabase":
        store = st.session_state.get("cloud_store")
        if store is None:
            st.info("Sign in from the sidebar to view Supabase history.")
            return
    else:
        store = LocalMealStore()

    try:
        rows = store.list_recent(100)
    except Exception as exc:
        st.error(f"Could not load history: {exc}")
        return
    if not rows:
        st.info("No reviewed estimates saved yet.")
        return

    frame = pd.DataFrame(rows)
    st.dataframe(frame, hide_index=True, width="stretch")
    totals = frame[["calories", "protein_g", "carbs_g", "fat_g"]].sum()
    cols = st.columns(4)
    cols[0].metric("Calories shown", f"{totals['calories']:.0f}")
    cols[1].metric("Protein shown", f"{totals['protein_g']:.1f}g")
    cols[2].metric("Carbs shown", f"{totals['carbs_g']:.1f}g")
    cols[3].metric("Fat shown", f"{totals['fat_g']:.1f}g")
    st.caption("Totals cover the displayed rows, not necessarily a complete day or diet.")


def render_about() -> None:
    st.markdown(
        """
        MacroLens separates three questions that photo nutrition tools often collapse:

        - **Identity:** What foods are probably present?
        - **Portion:** How much of each food is probably present?
        - **Nutrition:** Given those assumptions, what macro range is plausible?

        The app stores only the reviewed record. Raw photos are not written to SQLite or Supabase.
        Live analysis sends the photo to the configured model provider; review that provider's data
        policy before using sensitive images.
        """
    )


if __name__ == "__main__":
    main()
