# RFCs

An RFC (request for comments) is a written proposal for a large feature or a big breaking change of
the SpatialData data model, the storage format, or several in-memory formats at once. It is
discussed and refined in the open before anything is decided. Smaller changes go through an issue
and a pull request alone; see {doc}`contributing_to_the_spec`.

## When to write an RFC

- The change adds a concept to the abstract data model, or changes the meaning of an existing one.
- The change needs a new storage format version and affects several element types, or affects
  readers and writers in more than one language.
- There are several reasonable designs, and the choice needs input from the community.

## Process

1. **Propose.** Open a pull request that adds the RFC as a Markdown file `rfcs/<number>-<name>.md`
   (numbers are sequential in order of proposal, assigned when an RFC is listed below, and never
   reused, e.g. `rfcs/0001-transformations.md`),
   based on the template below. An RFC that started elsewhere (a discussion, a fork) is listed
   here with a link and moves into `rfcs/` when it is formally presented for review.
2. **Discuss.** Comments go to the pull request. The RFC is revised until the discussion converges.
3. **Decide.** Decisions follow the consensus-seeking process of the
   [scverse governance](https://github.com/scverse/governance/blob/main/roles.md#decision-making-process).
   The decision and its reasons are recorded in the RFC, which is then merged with the status
   *accepted* or *rejected*, so that the record stays.
4. **Implement.** An accepted RFC lands in the specification as tabs of the next storage version
   (*container-format-0.3 (draft)*, see {doc}`spec/on-disk/next`) and in the implementations. Its
   status becomes *implemented* with the release that writes the new version.

Statuses: *planned* (agreed to be written) · *idea* (a discussion, not yet written up) · *draft* · *under review* · *accepted* ·
*rejected* · *withdrawn* · *implemented*.

## RFCs

| No. | RFC | Scope | Proposed by | Status |
|-----|-----|-------|-------------|--------|
| 1 | Coordinate systems and transformations: adopt NGFF 0.6 ([RFC-5](https://ngff.openmicroscopy.org/rfc/5/)) for all spatial elements (see {doc}`spec/on-disk/ngff-compatibility` and {doc}`spec/on-disk/next`) | data model; storage format (new container version); implementations | spatialdata core team | planned |
| 2 | [Instance-level linking (mulink-compatible)](https://github.com/LucaMarconato/spatialdata/blob/2619c4ff31a5e6e0a98047be17025d96210c15d0/rfcs/links.md) | data model; storage format (new container version); Python | Luca Marconato | draft (in a fork of `spatialdata`) |
| 3 | [Spatial tiling of vector data](https://github.com/scverse/spatialdata/discussions/1251) | storage format; implementations | [@cornhundred](https://github.com/cornhundred) | idea ([discussion](https://github.com/scverse/spatialdata/discussions/1251), September 2026) |

## Template

```text
# RFC: <title>

## Authors and acknowledgements
## Summary            one paragraph: what changes, for whom
## Motivation         the problem, with concrete use cases
## Proposal
### Data model        new or changed concepts, in plain language
### Storage format    the bytes that change; new container version
### In-memory formats per language, where affected
## Compatibility      reading old stores, writing new ones, migration
## Alternatives       designs considered and why they were not chosen
## Open questions
## Decision           filled in when the RFC is accepted or rejected
## References
```
