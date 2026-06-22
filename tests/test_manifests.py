import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def _load(p):
    return json.loads((ROOT / p).read_text())

def test_marketplace_manifest():
    m = _load(".claude-plugin/marketplace.json")
    assert m["name"] == "feedforward"
    plugins = {p["name"]: p for p in m["plugins"]}
    assert "vendor-review" in plugins
    assert plugins["vendor-review"]["source"] == "./plugins/vendor-review"

def test_claude_plugin_manifest():
    p = _load("plugins/vendor-review/.claude-plugin/plugin.json")
    assert p["name"] == "vendor-review"
    assert "version" in p and "description" in p

def test_codex_plugin_manifest():
    p = _load("plugins/vendor-review/.codex-plugin/plugin.json")
    assert p["name"] == "vendor-review"
    assert p["skills"] == "./skills/"
    assert p["interface"]["displayName"] == "Feedforward Vendor Review"
