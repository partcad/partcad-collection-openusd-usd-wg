#
# partcad-openusd-usd-wg, 2026
#
# Licensed under Apache License, Version 2.0.
#
"""A PartCAD 'basic' repository plugin that serves the USD Working Group's assets as parts.

Published as ``//pub/collection/openusd/usd-wg/assets``. The assets are those of
https://github.com/usd-wg/assets, the Academy Software Foundation USD Working
Group's repository of sample and test assets, which openusd.org's Downloads
page lists among its "Additional Assets":

    full-assets    the complete assets - the Open Chess Set and each of its
                   pieces, the Teapots, the Mini Car Kit's vehicles and wheels,
                   the Carbon Frame Bike, McUsd, the Standard Shader Ball, ...
    test-assets    the test assets, a part per layer at the top of each test's
                   folder: renderer tests, mostly spheres and planes
    intent-vfx     the 'intent-vfx' example: its assets and its scenes

The repository lists nothing as an asset, so which layers of 'full_assets' are
what is named here (see FULL_ASSETS); the test assets and the intent-vfx ones
are found by where they are. Every one is checked against the repository's
tree, which GitHub's API lists, at a commit the branch was resolved to: the
files are then fetched from raw.githubusercontent.com at that commit, and never
change under a part.

GitHub lets an unauthenticated client ask its API 60 times an hour; the plugin
asks twice a week (the branch's commit, and that commit's tree), and a
'github_token' - or GITHUB_TOKEN - raises the limit. Should GitHub refuse, the
tree kept from an earlier run is used.

PartCAD runs this script once per key (via runpy) with the key in
``request["key"]``; the answer goes in ``output``.
"""

import importlib.util
import os
import posixpath
import re
import sys
import urllib.parse

# When this plugin's answers stopped meaning what they meant before. PartCAD
# keys everything it caches of this package on it, so raise it with any change
# to what is answered - here, or in usd_assets.py.
#
# v1: full assets, test assets and intent-vfx, as PartCAD 'usd' parts.
# v2: with the files a part's look is read from - its shaders, and its colour and finish
#     images, a smaller copy where the source keeps one ('looks').
CACHE_VERSION = 2


def _shared():
    """usd_assets.py, beside this script, under a name of this plugin's own."""
    name = "_partcad_openusd_usd_wg_usd_assets"
    if name not in sys.modules:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usd_assets.py")
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


ua = _shared()

REPOSITORY = "usd-wg/assets"
WEB = "https://github.com/" + REPOSITORY
API = "https://api.github.com/repos/" + REPOSITORY
RAW = "https://raw.githubusercontent.com/" + REPOSITORY + "/"

# The repository's own licence, for everything an asset's readme does not
# license otherwise.
REPOSITORY_LICENSE = "Apache-2.0"

# The complete assets, as each readme describes and licenses them:
# (part name, root layer, what it is, licence, author). An asset the tree no
# longer has is left out, saying so.
_CHESS = "full_assets/OpenChessSet/"
_CARS = "full_assets/Vehicles/USD_Mini_Car_Kit/assets/"
_CHESS_BY = "Moeen Sayed and Mujtaba Sayed (SideFX), for the Academy Software Foundation"
_CARS_BY = "Kenney (kenney.nl); made into USD by Robin-Yann Storm"
_TEAPOTS_BY = "James Ray Cook, Jurita Burger and Rico Cilliers (Poly Haven); the Utah teapot after Martin Newell"
_CHESS_PIECES = ("Chessboard", "King", "Queen", "Bishop", "Knight", "Rook", "Pawn")
FULL_ASSETS = (
    [("OpenChessSet", _CHESS + "chess_set.usda", "The Open Chess Set: a board and its 32 pieces.", "CC-BY-4.0",
      _CHESS_BY)]
    + [
        (piece, _CHESS + "assets/%s/%s.usd" % (piece, piece), "The Open Chess Set's %s." % piece.lower(), "CC-BY-4.0",
         _CHESS_BY)
        for piece in _CHESS_PIECES
    ]
    + [
        ("Teapot", "full_assets/Teapot/Teapot.usd", "A teapot, with variants: the Utah teapot and a fancy one.",
         "CC0-1.0", _TEAPOTS_BY),
        ("UtahTeapot", "full_assets/Teapot/geo/UtahTeapot.usd", "The Utah teapot.", "CC0-1.0", _TEAPOTS_BY),
        ("FancyTeapot", "full_assets/Teapot/geo/FancyTeapot.usd", "A fancy teapot, of Poly Haven's tea set.",
         "CC0-1.0", _TEAPOTS_BY),
        ("CarbonFrameBike", "full_assets/CarbonFrameBike/CarbonFrameBike.usdz", "A carbon frame bike.",
         "CC-BY-SA-4.0", "Robert Schweier and prefrontal cortex"),
        ("ElephantWithMonochord", "full_assets/ElephantWithMonochord/SoC-ElephantWithMonochord.usdc",
         "Songs of Cultures: a Vietnamese elephant with a monochord.", "CC-BY-SA-4.0",
         "A.MUSE - Interactive Design Studio"),
        ("McUsd", "full_assets/McUsd/McUsd.usdz", "A small Minecraft scene, exported with Mineways.",
         "CC-BY-NC-SA-4.0", "Eric Haines"),
        ("McUsd_10cm", "full_assets/McUsd/McUsd_10cm.usdz", "McUsd, at 10 cm a block.", "CC-BY-NC-SA-4.0",
         "Eric Haines"),
        ("StandardShaderBall", "full_assets/StandardShaderBall/standard_shader_ball_scene.usda",
         "The Standard Shader Ball: a scene to test materials on.", "CC-BY-4.0", "Academy Software Foundation"),
        ("SpinningPyramids", "full_assets/SubdivisionSurfaces/Creases_SpinningPyramids.usda",
         "Subdivision surface creases, on spinning pyramids (read as their control meshes).", REPOSITORY_LICENSE,
         None),
        ("Pyramid", "full_assets/SubdivisionSurfaces/Pyramid/Pyramid.usd",
         "A subdivision surface pyramid (read as its control mesh).", REPOSITORY_LICENSE, None),
        ("UsdCookie", "full_assets/UsdCookie/UsdCookie.usdz", "A cookie.", REPOSITORY_LICENSE, None),
        ("Vehicles", _CARS + "vehicles/vehicleVariants.usda", "The Mini Car Kit's vehicles, as variants of one.",
         "CC0-1.0", _CARS_BY),
        ("Wheels", _CARS + "wheels/wheelVariants.usda", "The Mini Car Kit's wheels, as variants of one.", "CC0-1.0",
         _CARS_BY),
    ]
)  # fmt: skip

# What the Mini Car Kit is besides: a vehicle, with and without its wheels, and
# each wheel. Found by name in the tree, so that a vehicle added is a part too.
_CAR = re.compile(r"^full_assets/Vehicles/USD_Mini_Car_Kit/assets/vehicles/([^/]+)/asset/\1(Full|Body)Asset\.usda$")
_WHEEL = re.compile(r"^full_assets/Vehicles/USD_Mini_Car_Kit/assets/wheels/([^/]+)/asset/\1Asset\.usda$")

COLLECTIONS = {
    "full-assets": (
        "The USD Working Group's complete assets: each licensed as its readme says.",
        WEB + "/tree/main/full_assets",
    ),
    "test-assets": (
        "The USD Working Group's test assets: a part per layer of each test.",
        WEB + "/tree/main/test_assets",
    ),
    "intent-vfx": (
        "The USD Working Group's 'intent-vfx' example: its assets and its scenes.",
        WEB + "/tree/main/intent-vfx",
    ),
}


# Where each child package's assets are in the repository.
FOLDERS = {"full-assets": "full_assets", "test-assets": "test_assets", "intent-vfx": "intent-vfx"}


def _layer(path):
    return posixpath.splitext(path)[1].lower() in (".usd", ".usda", ".usdc", ".usdz")


class UsdWg(ua.Source):
    NAME = "openusd-usd-wg"
    TITLE = "the USD Working Group"
    URL = WEB
    DESC = (
        "The USD Working Group's assets (github.com/usd-wg/assets): its complete assets, its test assets and "
        "its 'intent-vfx' example, a child package each and a part per asset."
    )
    LICENSE = REPOSITORY_LICENSE
    VERSION = CACHE_VERSION
    REPOSITORY = "partcad-collection-openusd-usd-wg"
    PLUGIN = "//pub/collection/openusd/usd-wg:usd_wg_repo"

    def __init__(self, request=None):
        super().__init__(request)
        self.ref = str(self.parameters.get("ref") or "main").strip()
        token = ua.credential(self.request, "github_token", "GITHUB_TOKEN")
        self.api_headers = {"Accept": "application/vnd.github+json"}
        if token:
            self.api_headers["Authorization"] = "Bearer " + token
        self._store = None

    def collections(self):
        return {name: ua.Collection(name, desc, url) for name, (desc, url) in COLLECTIONS.items()}

    # -- the tree --

    def commit(self):
        """The commit 'ref' is at: a commit itself, else what GitHub says the branch or tag is at, kept a week."""
        if re.match(r"^[0-9a-f]{40}$", self.ref):
            return self.ref
        url = "%s/commits/%s" % (API, urllib.parse.quote(self.ref, safe=""))
        answer = self.http.json(url, "the commit %s is at" % self.ref, headers=self.api_headers, stale=True)
        sha = answer.get("sha") if isinstance(answer, dict) else None
        if not sha:
            raise ua.SourceError("%s: GitHub did not say which commit %s is at" % (self.NAME, self.ref))
        return sha

    def store(self):
        if self._store is None:
            commit = self.commit()
            url = "%s/git/trees/%s?recursive=1" % (API, commit)
            # A commit's tree never changes: kept for good.
            tree = self.http.json(url, "the tree of %s" % commit[:12], ttl=None, headers=self.api_headers)
            if tree.get("truncated"):
                ua.warn("%s: GitHub truncated the tree of %s; some assets may be missing" % (self.NAME, commit[:12]))
            listing = {
                entry["path"]: int(entry.get("size") or 0)
                for entry in tree.get("tree") or []
                if entry.get("type") == "blob" and entry.get("path")
            }
            self._store = ua.HttpStore(self.http, RAW + commit + "/", listing)
            self._store.commit = commit
        return self._store

    # -- the assets --

    def assets(self, collection):
        store = self.store()
        listing = store.listing()
        found = {}

        def add(id, root, desc, license=None, author=None):
            if root not in listing:
                ua.warn("%s: %s is not in %s at %s any more" % (self.NAME, root, REPOSITORY, store.commit[:12]))
                return
            asset = ua.Asset(
                id,
                store,
                root,
                desc=desc,
                url="%s/blob/%s/%s" % (WEB, store.commit, posixpath.dirname(root)),
                license=license or self._license_of(root),
                author=author,
            )
            found.setdefault(asset.id, asset)

        if collection != "full-assets":
            # The readmes the licences of these are read from, fetched together.
            top = FOLDERS[collection] + "/"
            store.prefetch([p for p in listing if p.startswith(top) and posixpath.basename(p).lower() == "readme.md"])
        if collection == "full-assets":
            for id, root, desc, license, author in FULL_ASSETS:
                add(id, root, desc, license, author)
            for path in sorted(listing):
                car = _CAR.match(path)
                if car:
                    which = "" if car.group(2) == "Full" else ", without its wheels"
                    id = car.group(1) + ("" if car.group(2) == "Full" else "_body")
                    add(id, path, "The Mini Car Kit's %s%s." % (car.group(1), which), "CC0-1.0", _CARS_BY)
                wheel = _WHEEL.match(path)
                if wheel:
                    add(wheel.group(1), path, "The Mini Car Kit's %s." % wheel.group(1), "CC0-1.0", _CARS_BY)
        elif collection == "test-assets":
            # Every layer of a test, named by where it is: 'foundation/stage_composition/purpose.usda' is
            # 'foundation_stage_composition_purpose', and 'USDZ/BrainStem/BrainStem.usdz' 'USDZ_BrainStem'. A
            # file or folder whose name starts with '_' is one a test's layers use, not a test.
            for path in sorted(listing):
                parts = path.split("/")
                if parts[0] != "test_assets" or len(parts) < 3 or not _layer(path):
                    continue
                if any(part.startswith("_") for part in parts[1:]):
                    continue
                names = parts[1:-1] + [posixpath.splitext(parts[-1])[0]]
                if names[-1] == names[-2]:
                    names.pop()
                add("_".join(names), path, "A layer of the USD Working Group's %s test." % "/".join(parts[1:-1]))
        elif collection == "intent-vfx":
            for path in sorted(listing):
                parts = path.split("/")
                if (
                    len(parts) == 4
                    and parts[:2] == ["intent-vfx", "assets"]
                    and posixpath.splitext(parts[3])[0] == parts[2]
                    and _layer(path)
                ):
                    add(parts[2], path, "intent-vfx's %s asset." % parts[2])
                elif len(parts) == 3 and parts[:2] == ["intent-vfx", "scenes"] and _layer(path):
                    add(
                        posixpath.splitext(parts[2])[0],
                        path,
                        "intent-vfx's %s scene." % posixpath.splitext(parts[2])[0],
                    )
        return found

    def _license_of(self, root):
        """The licence the readme nearest an asset gives, for an asset this plugin does not name.

        The repository's own, when no readme on the way up says.
        """
        store = self.store()
        listing = store.listing()
        folder = posixpath.dirname(root)
        while folder.count("/") >= 1:
            for name in ("README.md", "Readme.md", "readme.md"):
                path = folder + "/" + name
                if path not in listing:
                    continue
                try:
                    text = store.read(path).decode("utf-8", "replace")
                except ua.SourceError:
                    return REPOSITORY_LICENSE
                for pattern, spdx in _LICENSES:
                    if re.search(pattern, text, re.IGNORECASE):
                        return spdx
                return REPOSITORY_LICENSE
            folder = posixpath.dirname(folder)
        return REPOSITORY_LICENSE


# How a readme names its licence, most specific first.
_LICENSES = [
    (r"CC[- ]?(BY[- ]NC[- ]SA|NC[- ]BY[- ]SA)", "CC-BY-NC-SA-4.0"),
    (r"CC[- ]?BY[- ]SA|Attribution-ShareAlike", "CC-BY-SA-4.0"),
    (r"CC[- ]?BY\b|Attribution 4\.0", "CC-BY-4.0"),
    (r"CC0|Creative Commons Zero|Public Domain", "CC0-1.0"),
]


def get(key):
    return ua.serve(UsdWg(globals().get("request")), key)


# Last, so that everything above is defined when PartCAD runs this.
if __name__ == "get":
    output = {"result": get(request["key"])}  # noqa: F821 - injected by the runtime
else:
    output = {}
