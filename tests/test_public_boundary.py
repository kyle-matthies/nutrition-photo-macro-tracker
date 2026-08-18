from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_public_tree_has_no_personal_project_identifiers() -> None:
    forbidden = (
        "nlcbkxy" + "fngdhcgbcyfyx",
        "nutrition-remote-" + "dashboard.vercel.app",
        "/Users/" + "kylematthies/Documents",
        "NUTRITION_CLOUD_" + "SERVICE_ROLE_KEY",
        "Daily Turkey" + " Sandwich",
    )
    scanned = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or ".venv" in path.parts:
            continue
        if path.suffix.lower() not in {".py", ".md", ".toml", ".sql", ".yml", ".yaml", ".example"}:
            continue
        scanned.append(path)
        text = path.read_text(errors="replace")
        assert not any(value in text for value in forbidden), path
    assert scanned
