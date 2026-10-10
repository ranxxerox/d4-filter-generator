from pathlib import Path

import pytest

from d4filter.cli import describe, main
from d4filter.fetcher import cache_dir, fetch_cached
from d4filter.maxroll import parse_maxroll_guide, parse_remix_context

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "maxroll_hell_fracture_warlock_guide.html"


@pytest.fixture(scope="module")
def spec():
    return parse_maxroll_guide(FIXTURE.read_text(encoding="utf-8"), source_url="fixture.html")


def test_parses_title_class_season(spec):
    assert spec.title == "Hell Fracture Warlock Endgame Guide"
    assert spec.game_class == "Warlock"
    assert spec.season == 15
    assert "Endgame" in spec.profile_names


def test_extracts_named_skills(spec):
    assert "Hell Fracture" in spec.skills
    assert "Sigil of Chaos" in spec.skills


def test_extracts_skill_bar_ids(spec):
    assert any("Warlock_Fissure" in s for s in spec.skill_ids)


def test_extracts_important_stats(spec):
    joined = " | ".join(spec.stat_lines)
    assert "Attack Speed" in joined
    assert "Critical Strike Chance" in joined
    assert "Maximum Life" in joined


def test_extracts_guide_filter_codes(spec):
    names = [name for name, _ in spec.guide_filter_codes]
    assert names == ["Maxroll Light", "Maxroll Medium", "Maxroll Strict"]
    for _, code in spec.guide_filter_codes:
        assert len(code) > 500


def test_parse_requires_remix_context():
    with pytest.raises(ValueError):
        parse_maxroll_guide("<html><script>window._other = {}</script></html>")


def test_remix_context_parses_json():
    html = '<script>window.__remixContext = {"state": {"ok": true}}</script>'
    assert parse_remix_context(html) == {"state": {"ok": True}}


def test_cli_describe_output(spec):
    out = describe(spec)
    assert "Class:    Warlock" in out
    assert "mappable: Hell Fracture" in out
    assert "Maxroll Light" in out


def test_cli_file_mode(capsys):
    assert main(["--file", str(FIXTURE)]) == 0
    out = capsys.readouterr().out
    assert "Season 15" in out


def test_cli_print_guide_filter(capsys):
    assert main(["--file", str(FIXTURE), "--print-guide-filter", "maxroll light"]) == 0
    code = capsys.readouterr().out.strip()
    assert len(code) > 500


def test_fetcher_caches(monkeypatch, tmp_path):
    monkeypatch.setattr("d4filter.fetcher.cache_dir", lambda: tmp_path)
    calls = []

    def fake_urlopen(request, timeout):
        class R:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return None

            def read(self):
                calls.append(True)
                return b"<html>payload</html>"

        return R()

    urllib_mod = __import__("urllib.request", fromlist=["urlopen"])
    monkeypatch.setattr(urllib_mod, "urlopen", fake_urlopen)
    monkeypatch.setattr("urllib.request.Request", lambda url, headers=None: (url, headers))

    first = fetch_cached("https://example.com/guide")
    second = fetch_cached("https://example.com/guide")
    assert first == second == "<html>payload</html>"
    assert len(calls) == 1  # second call served from cache
    from d4filter import fetcher as fetcher_mod

    assert list(fetcher_mod.cache_dir().glob("*.json"))
