"""Guards for the Pages publishing workflow.

The workflow is the only path that publishes the site, so these checks keep
its triggers, permissions, and deploy steps from drifting.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "pages.yml"


def workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_workflow_exists():
    assert WORKFLOW.is_file()


def test_triggers_on_main_and_manual_dispatch():
    text = workflow_text()
    assert "branches: [main]" in text
    assert "workflow_dispatch:" in text


def test_token_permissions_are_least_privilege():
    text = workflow_text()
    assert "contents: read" in text
    assert "pages: write" in text
    assert "id-token: write" in text


def test_deployments_are_serialized():
    text = workflow_text()
    assert 'group: "pages"' in text
    assert "cancel-in-progress: false" in text


def test_deploy_steps_run_in_order():
    text = workflow_text()
    steps = [
        "actions/checkout@v4",
        "actions/configure-pages@v5",
        "actions/upload-pages-artifact@v5",
        "actions/deploy-pages@v5",
    ]
    positions = [text.index(step) for step in steps]
    assert positions == sorted(positions)


def test_publishes_repository_root():
    text = workflow_text()
    assert "path: '.'" in text


def test_deploy_environment_exposes_url():
    text = workflow_text()
    assert "name: github-pages" in text
    assert "steps.deployment.outputs.page_url" in text
