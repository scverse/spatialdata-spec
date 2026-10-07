# Conformance and drift detection

Tooling (BSD-3-Clause) that keeps the specification honest against what `spatialdata` actually
writes and exposes.

| File | Purpose |
|------|---------|
| `fixture.py` | Deterministic `SpatialData` object with every element type, both single- and multiscale rasters, every transformation type, tables annotating several regions, and user `attrs`. |
| `generate_fingerprint.py` | Writes the fixture with the installed `spatialdata` (current container format and container 0.1), then records only what the spec constrains: Zarr group attributes, array shapes and dtypes, Parquet schemas and GeoParquet metadata, the `format.py` version facts, and the Python in-memory layout (exports, model dims, `attrs` keys, element types, round trip). |
| `compare_fingerprints.py` | Diffs two fingerprints and prints a Markdown report grouped by section, with the spec pages to check. Exit code 1 on drift. |
| `fingerprints/baseline.json` | Fingerprint of the `spatialdata` version the specification currently describes. Regenerate it (`--write-baseline`) only when the spec has been updated to that version. |
| `../tools/check_format_versions.py` | Checks the version tables in the spec against `spatialdata._io.format`. |

## Why fingerprints instead of an agent

A fingerprint diff is exact, cheap, and free of false positives from dependency noise (chunking,
codecs and library versions are excluded). It answers "did anything the spec constrains change?"
deterministically. Only when it says yes is there something to interpret, and that is where an
agent, or a maintainer, adds value: reading the diff and the `spatialdata` changelog and drafting
the spec edits. The GitHub workflow `spec-drift.yml` implements this two-stage design.

## Running locally

```bash
hatch run drift:check                # check_format_versions + fingerprint + compare against baseline
hatch run drift:fingerprint -o new.json
hatch run drift:compare conformance/fingerprints/baseline.json new.json
hatch run drift:baseline             # regenerate baseline after updating the spec
```

The `drift` environment installs `spatialdata` from PyPI. To test against `spatialdata` `main`:

```bash
hatch run drift:pip install --force-reinstall "git+https://github.com/scverse/spatialdata@main"
hatch run drift:check
```

## What counts as drift

- Any change in `spatialdata._io.format`: new or removed format classes, version strings, container
  compatibility, defaults.
- Any change in group attributes of any node of the fixture store (both container formats).
- Any change in array shapes or dtypes, Parquet field names/types, GeoParquet `geo` metadata
  (except `creator`), pandas index metadata.
- Any change in public exports, model dims, `parse` signatures, element types, `attrs` keys or
  transformation classes in memory, before or after a read.

Not drift (normalised away): chunking, codecs, compression levels, consolidated metadata,
dependency versions, `spatialdata_software_version`, Arrow `large_string` vs `string`, pandas
`pandas_type` names, private module paths in type names (`anndata._core.anndata.AnnData` vs
`anndata.AnnData`), quoting and module prefixes in signature annotations, dtypes of free
(unconstrained) columns.

## Validation of the detector

Comparing a `spatialdata` 0.6.0 environment with 0.8.0 (September 2026) reported, after
normalisation, exactly the substantive differences: pyramid arrays renamed `0` → `s0`, a per-level
`translation` added, `multiscales[0].name` changed, `image-label` added to multiscale labels in Zarr
v2 stores, AnnData 0.13 `nullable-string-array` indices, and the changed public exports. None of
these bumped a format version; all are now recorded in `spec/on-disk/versions.md`. Two runs on the
same environment produce identical fingerprints.

## Keeping the baseline

The baseline pins the spec to a `spatialdata` version. Workflow:

1. Drift is reported for a new `spatialdata` version.
2. Update the spec pages listed in the report (manually or from the agent's draft PR).
3. Run `hatch run drift:baseline` with that `spatialdata` version installed and commit the new
   baseline together with the spec changes.
