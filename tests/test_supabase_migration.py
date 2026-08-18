from pathlib import Path

MIGRATION = next(
    (Path(__file__).resolve().parents[1] / "supabase" / "migrations").glob(
        "*_create_meal_estimates.sql"
    )
)


def test_migration_enables_rls_and_scopes_every_operation() -> None:
    sql = MIGRATION.read_text().lower()

    assert "enable row level security" in sql
    assert "revoke all on table public.meal_estimates from anon" in sql
    assert "to authenticated" in sql
    assert sql.count("(select auth.uid()) = user_id") == 5
    assert "for select" in sql
    assert "for insert" in sql
    assert "for update" in sql
    assert "for delete" in sql
    assert "with check" in sql
    assert "service_role" in sql
