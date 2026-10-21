(data-model-versions)=
# Data model version history

The abstract data model is versioned on its own, as `MAJOR.MINOR`. A minor version adds concepts
that readers of an earlier minor version can ignore; a major version removes a concept or changes
its meaning. Each {ref}`storage format version <storage-versions>` encodes exactly one data model
version, so a change to the data model always comes with a new storage format version.

| Data model | Storage formats | Status |
|------------|-----------------|--------|
| **1.0** | 0.1, 0.2, 0.3, 0.4, **0.5** | current: what `spatialdata` has written so far |

Data model 1.0 is the model as `spatialdata` has implemented it up to 0.8, described in
{doc}`data-model`; all storage formats so far encode it.
