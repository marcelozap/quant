from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "unity" / "GREEN_MACHINE_WORLD_SECTION.md"


def test_world_section_documents_required_zones_and_paths():
    text = DOC.read_text(encoding="utf-8")

    for phrase in [
        "Green Gate",
        "Evidence Trail",
        "Risk Wall",
        "Receipt Ledger",
        "Archive Garden",
        "Rosco",
        "unity/LocalState/xiv_intents.jsonl",
        "unity/LocalState/receipts.jsonl",
    ]:
        assert phrase in text


def test_world_section_pins_required_boundary_copy():
    text = DOC.read_text(encoding="utf-8")

    for phrase in [
        "System proposes; never executes trades.",
        "Educational research only.",
        "Missing data stays UNKNOWN.",
        "Failed gate means no execution payload.",
        "GATE BARRED",
        "NO EXECUTION PAYLOAD",
    ]:
        assert phrase in text


def test_world_section_keeps_safe_language_replacements():
    text = DOC.read_text(encoding="utf-8")

    for phrase in [
        "Execution Agent | **Simulation Recorder**",
        "Trading Signal | **Research Card**",
        "Auto Execution | **Auto Review**",
        "Proceed | **Paper Review Ready**",
        "Target Price | **Scenario Level**",
        "P&L | **Simulated Outcome** / **Replay Outcome**",
        "Buy / Sell | **Scenario A** / **Scenario B**",
        "Trade Alert | **Review Prompt**",
    ]:
        assert phrase in text


def test_world_section_keeps_python_unity_write_boundary():
    text = DOC.read_text(encoding="utf-8")

    assert "Python writes" in text
    assert "Unity writes" in text
    assert "Python never touches scenes, builds, assets" in text
    assert "Unity never reads private account data" in text
