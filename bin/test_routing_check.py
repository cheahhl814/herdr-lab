#!/usr/bin/env python3
"""Self-check for check_routing: python3 bin/test_routing_check.py"""
import datetime
import importlib.util
import json
import os
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("caps", os.path.join(here, "herdr-capabilities.py"))
caps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(caps)

report = {"harnesses": [
    {"kind": "pi", "installed": True, "models": ["ollama-cloud:glm-5.3", "ollama-cloud:kimi-k3.1-pro"]},
    {"kind": "opencode", "installed": True, "models": ["ollama-cloud/glm-5.3"]},
    {"kind": "claude", "installed": True, "models": None},
    {"kind": "gone", "installed": False, "models": None},
]}
profile = {
    "_updated": "2026-01-01",
    "T0": {"harness": "pi", "provider": "ollama-cloud", "model_pattern": "glm-5.3"},
    "T1": {"harness": "pi", "provider": "ollama-cloud", "model_pattern": "delisted"},
    "T2": {"harness": "gone", "provider": "x", "model_pattern": "default"},
    "T3": {"harness": "claude", "provider": "anthropic-native", "model_pattern": "opus*"},
}
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "routing.json")
    assert caps.check_routing(report, path) is None

    with open(path, "w") as fh:
        json.dump(profile, fh)
    out = caps.check_routing(report, path, datetime.date(2026, 3, 1))
    assert {t: e["status"] for t, e in out["tiers"].items()} == {
        "T0": "ok", "T1": "no-model", "T2": "no-harness", "T3": "unverified"}
    assert out["stale"] is False  # exactly 59 days
    assert caps.check_routing(report, path, datetime.date(2026, 3, 3))["stale"] is True

    with open(path, "w") as fh:
        json.dump({"T0": {"harness": "opencode", "provider": "ollama-cloud",
                          "model_pattern": "glm-*"}}, fh)
    out = caps.check_routing(report, path)
    assert out["tiers"]["T0"]["status"] == "ok"  # glob + provider/model form
    assert out["stale"] is True  # undated

    with open(path, "w") as fh:
        fh.write("{broken")
    assert caps.check_routing(report, path)["error"]
print("ok")
