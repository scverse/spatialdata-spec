(data-model-versions)=
# Data model version history

The abstract data model is versioned as `MAJOR.MINOR`. A minor version adds concepts that older
readers can safely ignore; a major version removes or changes a concept. Each
{ref}`storage format version <storage-versions>` encodes one data model version, which is
therefore not written to stores. Corrections to the text change no version.

| Data model | Storage formats | Status |
|------------|-----------------|--------|
| **1.0** | 0.1, 0.2, 0.3, 0.4, **0.5** | current: what `spatialdata` has written so far |

Data model 1.0 is the model as `spatialdata` has implemented it up to 0.8, described in
{doc}`data-model`; all storage formats so far encode it.

(data-model-next)=
## Next version

The next data model version is opened by the first accepted RFC that changes the data model:
*1.1 (draft)* for an additive change, *2.0 (draft)* otherwise. RFCs that would change it are listed
with their targets on the {doc}`RFC page <rfcs>`; none is accepted yet. It is released together
with the first storage format version that encodes it (see {ref}`storage-next`).
