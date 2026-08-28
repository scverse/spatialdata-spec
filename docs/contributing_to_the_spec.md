# Contributing to the specification

:::{warning}
**TODO — this page is a placeholder.**
The workflow for proposing and reviewing changes to the SpatialData specification
has not been defined yet. It will be written in a dedicated pull request.
:::

## Scope

This page will describe how to contribute to the **specification text** that lives in
the [`spec/`](https://github.com/scverse/spatialdata-spec/tree/main/spec) directory,
as opposed to the repository tooling covered in {doc}`contributing`.

Topics to cover:

- How to propose a change: issue → discussion → pull request.
- How specification versions are cut and how the on-disk format version relates to them.
- The RFC / decision process for non-trivial changes.
- Backwards-compatibility expectations.

## Licensing

The repository is dual-licensed:

- Everything under [`spec/`](https://github.com/scverse/spatialdata-spec/tree/main/spec)
  is **prose only** and licensed under **CC-BY-4.0** (`spec/LICENSE`).
- All other content — repository tooling, documentation build, and any future schemas,
  examples, and conformance code — is licensed under **BSD-3-Clause** (`LICENSE`).

Do not add code, JSON Schemas, or example files under `spec/`: keeping that directory
prose-only avoids CC-BY attribution overhead for downstream implementations.
