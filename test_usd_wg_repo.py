#
# partcad-openusd-usd-wg, 2026
#
# Licensed under Apache License, Version 2.0.
#
"""Tests of the USD Working Group plugin, with GitHub answered from a table.

The tree has the shape GitHub's API gives, of a repository laid out as
usd-wg/assets is, with made-up layers in it. Nothing here touches the network.
"""

import base64
import importlib.util
import io
import json
import os
import re
import runpy
import zipfile

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_PLUGIN = os.path.join(_HERE, "usd_wg_repo.py")
_SPEC = importlib.util.spec_from_file_location("usd_wg_repo_under_test", _PLUGIN)
plugin = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(plugin)
ua = plugin.ua

COMMIT = "0123456789abcdef0123456789abcdef01234567"
CARS = "full_assets/Vehicles/USD_Mini_Car_Kit/assets/"


def _usda(text=""):
    return ("#usda 1.0\n" + text).encode()


FILES = {
    "full_assets/Teapot/Teapot.usd": _usda('def "Teapot" ( payload = @./Teapot_Payload.usd@ ) {}\n'),
    "full_assets/Teapot/Teapot_Payload.usd": _usda("( subLayers = [@./geo/UtahTeapot.usd@] )\n"),
    "full_assets/Teapot/geo/UtahTeapot.usd": _usda(),
    "full_assets/Teapot/geo/FancyTeapot.usd": _usda(),
    "full_assets/Teapot/README.md": b"## License\n\nPublic Domain - CC0\n",
    "full_assets/McUsd/McUsd.usdz": ua.write_usdz([("McUsd.usda", _usda())]),
    CARS + "vehicles/van/asset/vanFullAsset.usda": _usda('def "van" ( references = @../geo/vanGeo.usd@ ) {}\n'),
    CARS + "vehicles/van/asset/vanBodyAsset.usda": _usda(),
    CARS + "vehicles/van/geo/vanGeo.usd": _usda(),
    CARS + "wheels/wheelRed/asset/wheelRedAsset.usda": _usda(),
    "test_assets/USDZ/BrainStem/BrainStem.usdz": ua.write_usdz([("BrainStem.usdc", _usda())]),
    "test_assets/foundation/stage_composition/purpose.usda": _usda(),
    "test_assets/foundation/stage_composition/payload/_children/_child_stage.usda": _usda(),
    "test_assets/RoughnessTest/RoughnessTest.usda": _usda(),
    "test_assets/RoughnessTest/README.md": b"Licensed CC0\n",
    "intent-vfx/assets/teapot/teapot.usd": _usda(),
    "intent-vfx/assets/teapot/geo.usd": _usda(),
    "intent-vfx/scenes/teapotScene.usda": _usda(),
}


class Wire:
    def __init__(self, table):
        self.table = dict(table)
        self.asked = []

    def __call__(self, url, headers=None, method=None, timeout=120):
        self.asked.append((url, dict(headers or {})))
        if url not in self.table:
            return ua.Response(404, {}, b"", url)
        status, body = self.table[url]
        return ua.Response(status, {}, body if isinstance(body, bytes) else json.dumps(body).encode(), url)


def _table():
    table = {
        plugin.API + "/commits/main": (200, {"sha": COMMIT}),
        plugin.API
        + "/git/trees/%s?recursive=1"
        % COMMIT: (
            200,
            {"truncated": False, "tree": [{"path": p, "type": "blob", "size": len(d)} for p, d in FILES.items()]},
        ),
    }
    for path, data in FILES.items():
        table[plugin.RAW + COMMIT + "/" + path] = (200, data)
    return table


@pytest.fixture
def usd_wg(tmp_path, monkeypatch):
    monkeypatch.setenv("PARTCAD_OPENUSD_USD_WG_CACHE", str(tmp_path))
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    def make(**parameters):
        made = plugin.UsdWg({"parameters": parameters})
        made.http.request = Wire(_table())
        return made

    return make


def test_a_child_package_per_part_of_the_repository(usd_wg):
    assert usd_wg().get("deps") == ["full-assets", "intent-vfx", "test-assets"]


def test_the_complete_assets_are_named_and_found(usd_wg, capsys):
    parts = usd_wg().get("full-assets/objects/part")
    assert {"Teapot", "UtahTeapot", "FancyTeapot", "McUsd", "van", "van_body", "wheelRed"} <= set(parts)
    assert parts["Teapot"]["license"] == "CC0-1.0"
    assert parts["McUsd"]["license"] == "CC-BY-NC-SA-4.0"
    assert parts["Teapot"]["url"] == "%s/blob/%s/full_assets/Teapot" % (plugin.WEB, COMMIT)
    # An asset the plugin names and the tree has not got is left out, saying so.
    assert "OpenChessSet" not in parts
    assert "chess_set.usda is not in usd-wg/assets" in capsys.readouterr().err


def test_a_test_asset_is_named_by_where_it_is_and_licensed_by_its_readme(usd_wg):
    parts = usd_wg().get("test-assets/objects/part")
    assert sorted(parts) == ["RoughnessTest", "USDZ_BrainStem", "foundation_stage_composition_purpose"]
    assert parts["RoughnessTest"]["license"] == "CC0-1.0"
    assert parts["USDZ_BrainStem"]["license"] == "Apache-2.0"


def test_intent_vfx_is_its_assets_and_its_scenes(usd_wg):
    assert sorted(usd_wg().get("intent-vfx/objects/part")) == ["teapot", "teapotScene"]


def test_an_asset_is_fetched_at_the_commit_the_branch_is_at(usd_wg):
    made = usd_wg()
    data = base64.b64decode(made.get("full-assets/files/Teapot.usdz"))
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        assert z.namelist() == ["Teapot.usd", "Teapot_Payload.usd", "geo/UtahTeapot.usd"]
    raw = [url for url, _ in made.http.request.asked if url.startswith(plugin.RAW)]
    assert raw and all(url.startswith(plugin.RAW + COMMIT + "/") for url in raw)


def test_a_commit_is_used_as_it_is_and_a_token_is_sent_to_the_api(usd_wg):
    made = usd_wg(ref=COMMIT, github_token="t0k3n")
    made.get("full-assets/objects/part")
    asked = made.http.request.asked
    assert not any(url.endswith("/commits/main") for url, _ in asked)
    assert all(headers.get("Authorization") == "Bearer t0k3n" for url, headers in asked if url.startswith(plugin.API))
    assert not any("Authorization" in headers for url, headers in asked if url.startswith(plugin.RAW))


def test_a_rate_limited_api_is_answered_from_the_tree_kept(usd_wg, capsys):
    usd_wg().get("full-assets/objects/part")
    made = usd_wg()
    made.http.request.table[plugin.API + "/commits/main"] = (403, {"message": "API rate limit exceeded"})
    # A week later: what was kept is old, and GitHub says no.
    for folder, _, names in os.walk(made.http.root):
        for name in names:
            os.utime(os.path.join(folder, name), (0, 0))
    assert "Teapot" in made.get("full-assets/objects/part")
    assert "answering from what was kept" in capsys.readouterr().err


def test_the_plugin_is_named_as_the_package_declares_it():
    with open(os.path.join(_HERE, "partcad.yaml")) as f:
        text = f.read()
    name = re.search(r"^name: (\S+)", text, re.M).group(1)
    assert re.search(r"^  usd_wg_repo:\n    type: basic\n    path: usd_wg_repo.py", text, re.M)
    assert plugin.UsdWg.PLUGIN == name + ":usd_wg_repo"


def test_partcad_runs_it_and_reads_the_answer_from_output(tmp_path, monkeypatch):
    monkeypatch.setenv("PARTCAD_OPENUSD_USD_WG_CACHE", str(tmp_path))
    result = runpy.run_path(_PLUGIN, init_globals={"request": {"key": "meta", "parameters": {}}}, run_name="get")
    assert result["output"]["result"]["manufacturable"] is False
