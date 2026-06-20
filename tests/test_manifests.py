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
    assert plugins["vendor-review"]["source"] == "./"

def test_plugin_manifest():
    p = _load(".claude-plugin/plugin.json")
    assert p["name"] == "vendor-review"
    assert "version" in p and "description" in p
