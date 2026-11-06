# The USD Working Group's assets for PartCAD

Serves the assets of [github.com/usd-wg/assets](https://github.com/usd-wg/assets), the Academy
Software Foundation USD Working Group's repository of sample and test assets - one of the "Additional
Assets" [openusd.org's Downloads page](https://openusd.org/release/dl_downloads.html) lists - as
PartCAD parts, published as `//pub/collection/openusd/usd-wg/assets`:

| Package | What it is | Parts |
| --- | --- | --- |
| `assets/full-assets` | The complete assets | `OpenChessSet` and its `King`, `Queen`, `Bishop`, `Knight`, `Rook`, `Pawn` and `Chessboard`; `Teapot`, `UtahTeapot`, `FancyTeapot`; the Mini Car Kit's vehicles (`van`, `tractor`, ... and `van_body` without its wheels), wheels and their variant sets; `CarbonFrameBike`, `ElephantWithMonochord`, `McUsd`, `StandardShaderBall`, `Pyramid`, `SpinningPyramids`, `UsdCookie` |
| `assets/test-assets` | The test assets: a part per layer of each test, named by where it is | `foundation_stage_composition_purpose`, `USDZ_DamagedHelmet`, `USDZ_BrainStem`, ... (137) |
| `assets/intent-vfx` | The `intent-vfx` example | `simpleAsset`, `teapot`, and its scenes |

```shell
pc list parts //pub/collection/openusd/usd-wg/assets/full-assets
pc search parts -P '//pub/collection/openusd/usd-wg/assets...' -k teapot
pc inspect //pub/collection/openusd/usd-wg/assets/full-assets:Teapot
pc render -t png //pub/collection/openusd/usd-wg/assets/full-assets:van
pc render -t png --style shaded //pub/collection/openusd/usd-wg/assets/full-assets:OpenChessSet
```

**Each part carries its asset's licence**, as its readme gives it: CC0 (the Teapots, the Mini Car Kit),
CC BY 4.0 (the Open Chess Set, the Standard Shader Ball), CC BY-SA 4.0 (the bike, the elephant) - and
**CC BY-NC-SA 4.0 for McUsd**, which is not for commercial use. What no readme licenses is the
repository's, Apache-2.0. `pc info` of a part shows its `license`.

**No geometry is vendored.** Every asset is fetched from GitHub the first time a part of it is built,
and kept by PartCAD from then on.

**Nothing here is manufacturable.** These are props, scenes and renderer tests made to be looked at;
the package says `manufacturable: false`, and so does the plugin of what it serves.

Requires PartCAD 0.9.6 or newer: the first release whose `//builtin` has the `usd` part type.

## Which assets

The repository lists nothing as an asset, so the complete assets are named in the plugin, layer by
layer, as their readmes describe them (`FULL_ASSETS` in `usd_wg_repo.py`); the Mini Car Kit's vehicles
and wheels, the test assets and the intent-vfx ones are found by where they are, so one added is a
part too. Every one is checked against the repository's tree: one that is gone is left out, saying
so.

The tree is GitHub's API's, at the commit the branch is at: the plugin asks which commit `main` is at
once a week, and that commit's tree once, and fetches every file from raw.githubusercontent.com at
that commit - so a part's files never change under it, and a week after the branch moves, its parts
do. Set `ref` to a commit to pin them for good. GitHub lets anybody ask its API 60 times an hour; the
plugin asks twice a week, and when GitHub refuses, it answers from the tree it kept.

## Listing, searching, building

**Listing and searching download no asset.** `pc list parts` and `pc search parts` are answered from
the repository's tree, which GitHub's API lists in one answer of about 190 KB, and the readmes that
give the assets' licences. What a part is made of is fetched when the part is built - by `pc inspect`,
`pc render`, `pc export`, or an assembly that places it - and then only that asset's own files, and
kept.

`pc search parts -k <words>` is answered by the plugin, from the same catalog: a part matches when
every word is in its name, its description, its author, its tags or its package's name, and the ones
whose name matches come first. Each package answers with at most 20, or what `--limit` says (up to
100); search a package and every one below it with `-P '<package>...'`.

## What a part is

Every part here is `type: usd`: PartCAD's own part type for OpenUSD, in its `//builtin`, which reads a
stage with Pixar's USD library (`usd-core`), installed into the sandbox that builds the part and
nowhere else. The plugin's part is the file, and the part type makes the shape of it.

- **The file.** A part's file is a USDZ package of the asset, which the plugin makes when the part is
  built. An asset published as a `.usdz` is served as it is. One published as `.usd`, `.usda` or
  `.usdc` layers is a root layer that names others by relative path - sublayers, references,
  payloads - and the plugin follows those names (in a text layer its `@asset paths@`, in a binary one
  its token table) and packs the root and everything it reaches into a USDZ, root first, as the format
  wants it. Of the files that are not layers, it carries what the part's look is read from (the
  plugin's `looks`): the shaders the layers name, and the images of the colour, roughness and
  metalness - a smaller copy of each where the source keeps one, else each of up to 8 MB - and not
  the normal, height or occlusion maps. `textures` carries every one, as it is. A file an asset names
  that the source does not have is reported, and the asset is served without it.
- **The shape.** What is built is the stage's default prim - what a reference to the asset brings
  in - and every mesh it shows: through native instancing and point instancers, of the purpose asked
  for, visible ones only, in millimetres (by the stage's `metersPerUnit`) with Z up. A cube, sphere,
  cylinder, cone or capsule is meshed; curves, points and volumes are not surfaces, and are left out
  and counted. Up to 20 000 triangles, each triangle is a face, and two that share an edge share it:
  the part is drawn as lines, written to STEP, and made the solid it bounds where it closes. Past
  that, the triangles of each look are one mesh: fast at any size, drawn shaded (`pc render --style
  shaded`) and written as STL, 3MF or glTF, but with no edges for a line drawing. The part is a
  surface as USD describes it - what a renderer draws - and PartCAD says so when it is not a solid.
- **The look.** Each face is in the colour, roughness and metalness its material says - the material
  bound to its mesh, or to the subset of its faces - and as see-through: a colour a texture gives is
  read off the image where the face lies on it. `UsdPreviewSurface`, MaterialX and NVIDIA's OmniPBR,
  OmniGlass and OmniSurface are read, an MDL preset calling one included; a face with no material, or
  none of those, is in its `displayColor`. Each is stated under PartCAD's `usd` convention by the
  material's name, so a package of yours can claim one with a colour, material or finish of its own
  (`ids: {usd: Ceramic}`); one nothing claims is drawn as the stage says, and is display-only. A shaded
  `pc render` draws the roughness and metalness too.
- **The size.** It is what the asset says it is, by its `metersPerUnit`: an asset authored in the
  wrong units comes out as large, or as small, as it says.
- **The other reader.** `reader=cadmpeg` reads the same file with cadmpeg instead, PartCAD's
  converter for CAD formats, which reads USD from its 0.6.8 release on: what a render shows, at the
  stage's static values. It does no point instancer (the City Set's buildings, the chess set's pawns
  are left out), no `purpose` but `render` and no `time` but `default`, and a prim it reads as an
  exact surface (a cube, a sphere) is counted and left out rather than meshed. It is there as a
  second opinion and a fallback; `usd-core` is the reader to use.

Every part takes the part type's parameters, in its name (`King;purpose=proxy`) or in the `with` of
an enrich of it:

| Parameter | Default | What it is |
| --- | --- | --- |
| `reader` | `usd-core` | What reads the stage: `usd-core`, or `cadmpeg` (see above). |
| `prim` | the default prim | Build only what is under this prim; `/` is the whole stage. |
| `purpose` | `render` | `render`: what a final render draws; `proxy`: the stand-ins a viewer draws; `all`: both, and guides. |
| `surface` | `auto` | `faces`: a face per triangle; `mesh`: a mesh per colour; `auto`: `faces` up to 20 000 triangles. |
| `time` | `default` | The time code to read animated geometry at, skinning a character to it. `default` is what a viewer opens the stage at (its start time code, else its earliest sample), unposed. |
| `maxTriangles` | 5000000 | The most triangles the part may be: a scene of more is refused, saying so. |

PartCAD's own documentation of the part type is
[the `usd` part type](https://partcad.readthedocs.io/en/latest/config_parts.html#usd-files).

Sizes are as each asset states them: the Mini Car Kit says its units are metres and is modelled in
what are clearly centimetres, so its van is 210 m long; the elephant, the other way, is a millimetre.

## Parameters of the plugin

| Parameter | Default | What it is |
| --- | --- | --- |
| `ref` | `main` | The branch, tag or commit of usd-wg/assets to serve. |
| `looks` | `true` | Whether a part's USDZ carries what its look is read from: its shaders, and the images of its colour, roughness and metalness, each of up to 8 MB (the chess pieces' are 0.4 MB). PartCAD colours each face from them. |
| `textures` | `false` | Whether a part's USDZ carries every texture its layers name, normal maps and all, each as it is: to open it complete in another USD application. |
| `max_size_mb` | `512` | The most a part's USDZ may be, in MB. |
| `github_token` | empty | A GitHub token, for more than 60 API requests an hour; rarely needed. `GITHUB_TOKEN` gives it too. Yours alone: set it in `~/.partcad/config.yaml`. |

Each is yours to set without touching this package, in your own `~/.partcad/config.yaml`, by the
plugin's name:

```yaml
parameters:
  "//pub/collection/openusd/usd-wg:usd_wg_repo":
    ref: 091bb5c6f8eb665ad4cf9d6c10025cecc07eda88
```

and all but the token in a package of your own, as an enrich of the plugin and a package it serves:

```yaml
repositories:
  pinned_repo:
    type: enrich
    source: //pub/collection/openusd/usd-wg:usd_wg_repo
    with:
      ref: 091bb5c6f8eb665ad4cf9d6c10025cecc07eda88
dependencies:
  usd_wg_pinned:
    type: external
    plugin: :pinned_repo
```

## Caching

The plugin keeps what GitHub answered under `~/.cache/partcad-openusd-usd-wg/` (or
`$PARTCAD_OPENUSD_USD_WG_CACHE`): which commit the branch is at, for a week; a commit's tree and its
files, for good, since they cannot change. Delete the directory to start over. PartCAD keeps every
answer the plugin gives, files included.

Every request says what it is: `User-Agent: Mozilla/5.0 (compatible; PartCAD-openusd-usd-wg/<version>;
+https://github.com/partcad/partcad-collection-openusd-usd-wg)`.

## Status

Run against GitHub at commit `091bb5c` of `main`: listing the three packages reads the tree (191 KB)
and the readmes that give licences (280 KB in all, and no asset); the files of the Teapot, the Open
Chess Set, the bike, the van, the vehicles' variant set, the Standard Shader Ball, the elephant, the
DamagedHelmet test and the intent-vfx teapot scene were fetched from raw.githubusercontent.com,
packed, and read back by the part type.

Drawn in their looks (`pc render --style shaded`): the Open Chess Set in its MaterialX materials -
which the part type reads itself, since the usd-core wheel composes no MaterialX - the bike, the cookie
and the DamagedHelmet in their textures, and the Teapot in the green its `displayColor` gives. The
Standard Shader Ball's box is textured in EXR, which PartCAD does not read, and its ball has no
material: both are drawn in no colour of their own.

Through PartCAD's own `usd` part type, run from the change that adds it to `//builtin` before its
release, with all six `partcad-collection-openusd-*` packages in one workspace: `pc list packages -r`
listed their 17 packages, and `pc search parts -P '<workspace>...'` answered across all of them in
about two seconds, each collection searching its own catalog; `pc info` of the Teapot built it (305 by
491 by 230 mm). GitHub's API itself could not be reached from where this was written (a proxy refused
it), so the tree was the one `git ls-tree` gives at that commit, in the API's shape; asking the API is
the standard `git/trees/<sha>?recursive=1`.

## Layout

| Path | Purpose |
| --- | --- |
| `partcad.yaml` | `//pub/collection/openusd/usd-wg`; the `assets` external dependency and the `usd_wg_repo` repository that serves it. |
| `usd_wg_repo.py` | The repository plugin: where the USD Working Group keeps its assets. |
| `usd_assets.py` | What every OpenUSD collection plugin shares, byte for byte: following a USD asset's layers, packing a USDZ, reading remote archives, buckets and listings a piece at a time, searching a catalog, the keys PartCAD asks. |
| `shared.sha256` | The digests of the shared files and their tests. They are the same in every `partcad-collection-openusd-*` repository - pixar, usd-wg, apple, nvidia, aswf-dpel and disney-moana - and a test fails when one here differs: change them in all of them. |
| `test_*.py` | The tests. Nothing in them touches the network. |

```shell
python -m pytest
```

When what the plugin answers changes - here or in `usd_assets.py` - raise `CACHE_VERSION` in
`usd_wg_repo.py`: PartCAD keys everything it caches of this package on it, and an unchanged version
is answered from what it cached before.

## Licensing

The code here is Apache-2.0 (`LICENSE`). The assets are the USD Working Group's contributors', each
under the licence its readme gives (above), and the rest under the repository's Apache-2.0. Nothing of
them is in this repository.
