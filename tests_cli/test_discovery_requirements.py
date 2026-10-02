from pathlib import Path

from scrumaidev import __version__

from scrumaidev.runtime_ops import configure, doctor, workflow_names

NEW_WORKFLOWS = ("scope-idea", "discover", "requirements")


def test_new_workflows_are_part_of_the_runtime():
    names = workflow_names()
    for name in NEW_WORKFLOWS:
        assert name in names
    # The old AI-DLC-flavored name must not resurface.
    assert "start" not in names
    assert "stories" not in names


def test_config_installs_new_workflows_and_adapters(tmp_path: Path):
    configure(tmp_path, "opencode", __version__)
    for name in NEW_WORKFLOWS:
        assert (tmp_path / f".agents/workflows/{name}.md").exists()
        assert (tmp_path / f".opencode/commands/{name}.md").exists()
    assert (tmp_path / "docs/work_classification.md").exists()
    assert (tmp_path / "docs/discovery_requirements.md").exists()
    assert (tmp_path / "templates/work_classification.md").exists()
    assert (tmp_path / "templates/discovery.md").exists()
    assert (tmp_path / "templates/requirements.md").exists()
    assert doctor(tmp_path)["status"] == "ok"


def test_adapters_do_not_override_model(tmp_path: Path):
    configure(tmp_path, "opencode", __version__)
    for name in NEW_WORKFLOWS:
        text = (tmp_path / f".opencode/commands/{name}.md").read_text(encoding="utf-8")
        assert "model:" not in text
        assert "does not override the model" in text


def test_review_and_adjust_is_explicit_in_new_workflows():
    root = Path(__file__).resolve().parents[1] / "src/scrumaidev/runtime/core/agents/workflows"
    for name in ("discover", "requirements"):
        text = (root / f"{name}.md").read_text(encoding="utf-8")
        assert "REVIEW & ADJUST" in text


def test_create_user_story_absorbs_backlog_mode_instead_of_a_separate_stories_command():
    root = Path(__file__).resolve().parents[1] / "src/scrumaidev/runtime/core/agents/workflows"
    text = (root / "create-user-story.md").read_text(encoding="utf-8")
    assert "Modo Backlog" in text
    assert not (root / "stories.md").exists()


def test_scope_idea_is_distinct_from_init_project():
    root = Path(__file__).resolve().parents[1] / "src/scrumaidev/runtime/core/agents/workflows"
    text = (root / "scope-idea.md").read_text(encoding="utf-8")
    assert "init-project" in text
    assert not (root / "start.md").exists()


def test_maturity_and_classification_are_documented_as_separate_axes():
    root = Path(__file__).resolve().parents[1]
    text = (root / "docs/work_classification.md").read_text(encoding="utf-8")
    assert "LIGHT" in text and "NORMAL" in text and "HEAVY" in text
    assert "maturidade" in text.lower()
