---
rfc: N  # the next free number; the file is rfcs/NNNN-name.md
title: "Title"
authors: "First Author ([@first-author](https://github.com/first-author)), Second Author; input from Third Person ([@third-person](https://github.com/third-person)), Fourth Person"  # names, no email addresses; GitHub handles optional
status: "draft"  # planned, idea, draft, under review, accepted, specified, rejected, withdrawn or implemented
type: "data model; storage format; discussion"  # keep what applies: data model and/or storage format; or discussion alone, when the RFC changes neither
created: YYYY-MM-DD
---

# RFC N: Title

## Abstract

One paragraph: what changes, why, and for whom.

## Description

The problem, with concrete use cases, and the scope of the proposal. Together with the two sections
below, it is self-sufficient: a reader can fully understand and implement the proposal from them.
Plain language, with figures, pseudocode or examples on top where they help.

## Data model

The changes to the abstract data model: new or changed concepts, independent of how they are stored.
Leave this section out when the data model does not change. A change to the data model always also
changes the storage format, since each storage format version encodes one data model version.

## Storage format

How the proposal is stored on disk: the files, their organization and metadata, and the use of Zarr
or Parquet; then compatibility: reading old stores, writing new ones, migration.

## Related work

Other formats, standards and implementations that address the same problem, and the designs that
were considered, with the reasons they were not chosen.

## Implementation

The implementations that read and write the proposal, with links to their pull requests, and the
pull request with the changes to the specification.

## Discussion

Links to where the RFC is discussed (an issue, a Zulip topic, a GitHub discussion, or elsewhere),
and the open questions. When the RFC is accepted or rejected, the decision and its reasons.

## References

Links and citations.
