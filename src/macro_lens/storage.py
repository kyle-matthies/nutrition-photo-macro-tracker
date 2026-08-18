"""Local-first storage plus optional authenticated Supabase sync."""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from macro_lens.models import MealRecord

SCHEMA = """
create table if not exists meal_estimates (
    id text primary key,
    observed_at text not null,
    meal_name text not null,
    calories real not null check (calories >= 0),
    protein_g real not null check (protein_g >= 0),
    carbs_g real not null check (carbs_g >= 0),
    fat_g real not null check (fat_g >= 0),
    identity_confidence real not null check (identity_confidence between 0 and 1),
    portion_confidence real not null check (portion_confidence between 0 and 1),
    nutrition_confidence real not null check (nutrition_confidence between 0 and 1),
    foods_json text not null default '[]',
    assumptions_json text not null default '[]',
    source_summary text not null,
    user_note text,
    model_name text not null,
    user_confirmed integer not null default 1 check (user_confirmed in (0, 1)),
    created_at text not null default current_timestamp
);
create index if not exists meal_estimates_observed_at_idx
    on meal_estimates (observed_at desc);
"""


class LocalMealStore:
    def __init__(self, path: str | Path | None = None) -> None:
        configured = path or os.getenv("MACRO_LENS_DB_PATH", "data/macro_lens.sqlite")
        self.path = Path(configured)

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.executescript(SCHEMA)
        return connection

    def save(self, record: MealRecord) -> None:
        payload = record.persistence_payload()
        with self.connect() as connection:
            connection.execute(
                """
                insert into meal_estimates (
                    id, observed_at, meal_name, calories, protein_g, carbs_g, fat_g,
                    identity_confidence, portion_confidence, nutrition_confidence,
                    foods_json, assumptions_json, source_summary, user_note,
                    model_name, user_confirmed
                ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                on conflict(id) do update set
                    observed_at = excluded.observed_at,
                    meal_name = excluded.meal_name,
                    calories = excluded.calories,
                    protein_g = excluded.protein_g,
                    carbs_g = excluded.carbs_g,
                    fat_g = excluded.fat_g,
                    identity_confidence = excluded.identity_confidence,
                    portion_confidence = excluded.portion_confidence,
                    nutrition_confidence = excluded.nutrition_confidence,
                    foods_json = excluded.foods_json,
                    assumptions_json = excluded.assumptions_json,
                    source_summary = excluded.source_summary,
                    user_note = excluded.user_note,
                    model_name = excluded.model_name,
                    user_confirmed = excluded.user_confirmed
                """,
                (
                    payload["id"],
                    payload["observed_at"],
                    payload["meal_name"],
                    payload["calories"],
                    payload["protein_g"],
                    payload["carbs_g"],
                    payload["fat_g"],
                    payload["identity_confidence"],
                    payload["portion_confidence"],
                    payload["nutrition_confidence"],
                    json.dumps(payload["foods"]),
                    json.dumps(payload["assumptions"]),
                    payload["source_summary"],
                    payload["user_note"],
                    payload["model_name"],
                    int(bool(payload["user_confirmed"])),
                ),
            )

    def list_recent(self, limit: int = 50) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                select id, observed_at, meal_name, calories, protein_g, carbs_g, fat_g,
                       nutrition_confidence, model_name
                from meal_estimates
                order by observed_at desc
                limit ?
                """,
                (max(1, min(limit, 500)),),
            ).fetchall()
        return [dict(row) for row in rows]


class SupabaseMealStore:
    """A user-session client; RLS remains the authorization boundary."""

    def __init__(self, client: Any, user_id: str) -> None:
        self.client = client
        self.user_id = user_id

    @classmethod
    def sign_in(cls, url: str, publishable_key: str, email: str, password: str):
        from supabase import create_client

        client = create_client(url, publishable_key)
        response = client.auth.sign_in_with_password({"email": email, "password": password})
        user = response.user
        if user is None:
            raise RuntimeError("Supabase sign-in did not return a user.")
        return cls(client, str(user.id))

    def save(self, record: MealRecord) -> None:
        payload = record.persistence_payload()
        payload["user_id"] = self.user_id
        self.client.table("meal_estimates").upsert(payload).execute()

    def sign_out(self) -> None:
        self.client.auth.sign_out()

    def list_recent(self, limit: int = 50) -> list[dict[str, Any]]:
        response = (
            self.client.table("meal_estimates")
            .select(
                "id,observed_at,meal_name,calories,protein_g,carbs_g,fat_g,"
                "nutrition_confidence,model_name"
            )
            .order("observed_at", desc=True)
            .limit(max(1, min(limit, 500)))
            .execute()
        )
        return list(response.data or [])
