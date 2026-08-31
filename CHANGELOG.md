# Changelog

All notable changes to this project are documented in this file.

Entries are split into two categories:

- **Specification** — changes to the specification text under `spec/` and to the on-disk
  format it describes.
- **Repository** — changes to tooling, CI, documentation infrastructure, and project
  scaffolding that do not affect the specification.

Within each category, the [Keep a Changelog][] subheadings apply
(_Added_, _Changed_, _Deprecated_, _Removed_, _Fixed_, _Security_).

[keep a changelog]: https://keepachangelog.com/

## [Unreleased]

### Specification

_Nothing yet — the specification text has not been written._

### Repository

#### Changed

- Re-scoped from the scverse package template to a specification repository: removed the
  Python package scaffolding, package build/release CI, and API documentation.

#### Added

- `spec/` directory (CC-BY-4.0) to hold the specification prose.
- `docs/contributing_to_the_spec.md` placeholder for the specification contribution workflow.
