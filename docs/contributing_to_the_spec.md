# Contributing to the specification

Contributions to SpatialData specifications are very welcome:
Simply open an issue or a pull request on GitHub until a formal specification process is established.

Contributions to the repository tooling are also highly appreciated, please see {doc}`contributing` for guidelines.

## Licensing

The repository is dual-licensed:

- Everything under [`spec/`](https://github.com/scverse/spatialdata-spec/tree/main/spec)
  is **prose only** and licensed under **CC-BY-4.0** (`spec/LICENSE`).
- All other content — repository tooling, documentation build, and any future schemas,
  examples, and conformance code — is licensed under **BSD-3-Clause** (`LICENSE`).

Do not add code, JSON Schemas, or example files under `spec/`: keeping that directory
prose-only avoids CC-BY attribution overhead for downstream implementations.
