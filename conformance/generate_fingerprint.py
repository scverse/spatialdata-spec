"""Generate a spec-level fingerprint of what the installed ``spatialdata`` writes and exposes.

The fingerprint captures only what the specification constrains, so that a difference between two
fingerprints means "the spec may need an update", not "a dependency changed a chunk size":

- on-disk: every Zarr group's attributes and, for arrays, shape, dtype and attributes; Parquet
  schemas and spec-relevant key/value metadata (GeoParquet ``geo`` minus the ``creator``); for both
  the current container format and container 0.1;
- ``spatialdata._io.format``: every format class with its versions and NGFF strings, the
  container/element compatibility, the current defaults;
- in-memory (Python): public exports of ``spatialdata``, ``spatialdata.models``,
  ``spatialdata.transformations``; model dims; ``parse`` signatures; the ``attrs`` layout of each
  fixture element.

Usage::

    python conformance/generate_fingerprint.py -o new.json
    python conformance/generate_fingerprint.py --write-baseline   # overwrite fingerprints/baseline.json

Licensed under BSD-3-Clause like the rest of the repository tooling.
"""

from __future__ import annotations

import argparse
import inspect
import json
import sys
import tempfile
import warnings
from importlib.metadata import version as pkg_version
from pathlib import Path
from typing import Any

warnings.simplefilter("ignore")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fixture import build_fixture  # noqa: E402

# Zarr array metadata keys that the spec does not constrain.
ARRAY_KEYS_DROPPED = {
    "chunks",
    "chunk_grid",
    "chunk_key_encoding",
    "codecs",
    "compressor",
    "filters",
    "fill_value",
    "order",
    "dimension_separator",
    "storage_transformers",
    "dimension_names",
    "zarr_format",
    "node_type",
}
GROUP_KEYS_DROPPED = {"zarr_format", "node_type", "consolidated_metadata"}


def _normalise_attrs(attrs: Any) -> Any:
    """Replace values that legitimately differ between runs or environments."""
    if isinstance(attrs, dict):
        out = {}
        for k, v in attrs.items():
            if k == "spatialdata_software_version":
                out[k] = "<spatialdata version>"
            else:
                out[k] = _normalise_attrs(v)
        return out
    if isinstance(attrs, list):
        return [_normalise_attrs(v) for v in attrs]
    return attrs


def _normalise_arrow_type(type_name: str) -> str:
    """``large_string``/``large_binary`` vs ``string``/``binary`` is a pyarrow/pandas choice, not a format one."""
    return type_name.replace("large_string", "string").replace("large_binary", "binary")


_PUBLIC_TYPES: list[tuple[str, str]] = [
    ("xarray", "DataArray"),
    ("xarray", "DataTree"),
    ("geopandas", "GeoDataFrame"),
    ("dask.dataframe", "DataFrame"),
    ("anndata", "AnnData"),
]


def _public_type_name(obj: Any) -> str:
    """Name an object by the public class it is an instance of, not by the private module path."""
    import importlib

    for module_name, class_name in _PUBLIC_TYPES:
        cls = getattr(importlib.import_module(module_name), class_name, None)
        if cls is not None and isinstance(obj, cls):
            return f"{module_name}.{class_name}"
    return type(obj).__module__ + "." + type(obj).__name__


def _normalise_annotation(text: str) -> str:
    """Strip quotes and module paths from a signature string so that only names matter."""
    import re

    text = text.replace("'", "").replace('"', "")
    return re.sub(r"\b(?:[A-Za-z_][\w]*\.)+([A-Za-z_]\w*)", r"\1", text)


def _read_json(path: Path) -> Any:
    with path.open() as fh:
        return json.load(fh)


def fingerprint_store(root: Path) -> dict[str, Any]:
    """Walk a Zarr store (v2 or v3) and collect spec-relevant metadata per node path."""
    import pyarrow.parquet as pq

    nodes: dict[str, Any] = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        name = path.name
        node_path = str(rel.parent).replace("\\", "/")
        node_path = "" if node_path == "." else node_path
        if name == "zarr.json":
            meta = _read_json(path)
            entry: dict[str, Any] = {"kind": meta.get("node_type")}
            if meta.get("node_type") == "array":
                entry["shape"] = meta.get("shape")
                entry["dtype"] = meta.get("data_type")
            entry["attributes"] = _normalise_attrs(meta.get("attributes", {}))
            nodes[node_path] = entry
        elif name == ".zgroup":
            nodes.setdefault(node_path, {"kind": "group"})
        elif name == ".zarray":
            meta = _read_json(path)
            entry = nodes.setdefault(node_path, {})
            entry.update({"kind": "array", "shape": meta.get("shape"), "dtype": meta.get("dtype")})
        elif name == ".zattrs":
            entry = nodes.setdefault(node_path, {})
            entry["attributes"] = _normalise_attrs(_read_json(path))
        elif name.endswith(".parquet") and path.is_file():
            md = pq.read_metadata(path)
            schema = md.schema.to_arrow_schema()
            fields = []
            for field in schema:
                fmeta = {k.decode(): v.decode() for k, v in (field.metadata or {}).items()}
                fields.append({"name": field.name, "type": _normalise_arrow_type(str(field.type)), "metadata": fmeta})
            kv = {k.decode(): v.decode() for k, v in (md.metadata or {}).items()}
            parquet_entry: dict[str, Any] = {"kind": "parquet", "fields": fields, "num_rows": md.num_rows}
            if "geo" in kv:
                geo = json.loads(kv["geo"])
                geo.pop("creator", None)
                parquet_entry["geo"] = geo
            if "pandas" in kv:
                pandas_meta = json.loads(kv["pandas"])
                # pandas_type/numpy_type depend on the pandas release (e.g. "unicode" vs "object"), not on the format
                parquet_entry["pandas"] = {
                    "index_columns": pandas_meta.get("index_columns"),
                    "columns": [c.get("name") for c in pandas_meta.get("columns", [])],
                }
            nodes[str(rel).replace("\\", "/")] = parquet_entry
    return nodes


def fingerprint_format_module() -> dict[str, Any]:
    import spatialdata._io.format as fmt

    classes: dict[str, Any] = {}
    for name in sorted(n for n in dir(fmt) if n.endswith(tuple("0123456789")) and "Format" in n and n[0].isupper()):
        obj = getattr(fmt, name)
        if not isinstance(obj, type):
            continue
        instance = obj()
        classes[name] = {
            "spatialdata_format_version": getattr(instance, "spatialdata_format_version", None),
            "ngff_version_string": getattr(instance, "version", None),
            "zarr_format": getattr(instance, "zarr_format", None),
        }
    current = {k: type(v).__name__ for k, v in fmt._parse_formats(None).items()}
    return {
        "classes": classes,
        "current": current,
        "container_valid_elements": fmt.ContainerFormatValidElements,
        "container_v01_default_elements": {k: type(v).__name__ for k, v in fmt.ContainerV01DefaultTypes.items()},
        "ngff_version_to_zarr_format": {k: v.zarr_format for k, v in fmt.sdata_zarr_version_to_ome_zarr_format.items()},
    }


def _signature(obj: Any) -> str:
    try:
        return _normalise_annotation(str(inspect.signature(obj)))
    except (TypeError, ValueError):
        return "<unavailable>"


def fingerprint_python_api(sdata: Any) -> dict[str, Any]:
    import spatialdata
    import spatialdata.models as models
    import spatialdata.transformations as transformations
    from spatialdata.transformations import get_transformation

    model_names = [
        "Image2DModel",
        "Image3DModel",
        "Labels2DModel",
        "Labels3DModel",
        "ShapesModel",
        "PointsModel",
        "TableModel",
    ]
    model_info = {}
    for name in model_names:
        model = getattr(models, name)
        dims = getattr(model, "dims", None)
        dims = getattr(dims, "dims", dims)  # spatialdata <= 0.6 wraps dims in an xarray-schema DimsSchema
        model_info[name] = {
            "dims": [str(d) for d in dims] if dims is not None else None,
            "parse_signature": _signature(model.parse),
            "class_attributes": {
                k: v for k, v in vars(model).items() if k.isupper() and isinstance(v, str | int | tuple)
            },
        }

    def element_layout(element: Any) -> dict[str, Any]:
        info: dict[str, Any] = {"type": _public_type_name(element)}
        attrs = getattr(element, "attrs", None)
        if attrs is not None:
            info["attrs_keys"] = sorted(str(k) for k in dict(attrs).keys())
            spatialdata_attrs = dict(attrs).get("spatialdata_attrs")
            if isinstance(spatialdata_attrs, dict):
                info["spatialdata_attrs_keys"] = sorted(spatialdata_attrs)
        if hasattr(element, "dims"):
            info["dims"] = [str(d) for d in element.dims]
            info["coords"] = sorted(str(c) for c in element.coords)
            info["name"] = element.name
        if type(element).__name__ == "DataTree":
            children = list(dict(element).keys())
            info["children"] = children
            first = element[children[0]]
            info["data_vars"] = sorted(first.data_vars)
            info["tree_attrs_keys"] = sorted(element.attrs)
            var = first[info["data_vars"][0]]
            info["dims"] = [str(d) for d in var.dims]
            info["level1_transform_type"] = type(
                dict(get_transformation(element[children[1]][info["data_vars"][0]], get_all=True))["global"]
            ).__name__
        if hasattr(element, "columns") and not hasattr(element, "obs"):
            info["columns"] = [str(c) for c in element.columns]
            # only dtypes the spec constrains: coordinates, radius, geometry, feature/instance keys
            constrained = {"x", "y", "z", "radius", "geometry"}
            spatialdata_attrs = dict(attrs or {}).get("spatialdata_attrs") or {}
            constrained |= {v for k, v in spatialdata_attrs.items() if k in ("feature_key", "instance_key")}
            info["dtypes"] = {str(k): str(v) for k, v in element.dtypes.items() if str(k) in constrained}
            if hasattr(element, "npartitions"):
                info["npartitions"] = element.npartitions
        if hasattr(element, "obs"):
            info["uns_keys"] = sorted(element.uns)
            table_attrs = element.uns.get("spatialdata_attrs")
            info["spatialdata_attrs"] = table_attrs
            keys = {table_attrs.get("region_key"), table_attrs.get("instance_key")} if table_attrs else set()
            info["obs_dtypes"] = {k: str(v) for k, v in element.obs.dtypes.items() if k in keys}
        if hasattr(element, "attrs") and "transform" in dict(attrs or {}):
            info["transform_types"] = {k: type(v).__name__ for k, v in dict(attrs)["transform"].items()}
        return info

    elements = {}
    for element_type, name, element in sdata.gen_elements():
        elements[f"{element_type}/{name}"] = element_layout(element)

    return {
        "exports": {
            "spatialdata": sorted(spatialdata.__all__),
            "spatialdata.models": sorted(models.__all__),
            "spatialdata.transformations": sorted(transformations.__all__),
        },
        "models": model_info,
        "spatialdata_signature": _signature(spatialdata.SpatialData.__init__),
        "write_signature": _signature(spatialdata.SpatialData.write),
        "coordinate_systems": sorted(sdata.coordinate_systems),
        "elements": elements,
    }


def generate() -> dict[str, Any]:
    import spatialdata
    from spatialdata._io.format import SpatialDataContainerFormatV01

    sdata = build_fixture()
    stores: dict[str, Any] = {}
    with tempfile.TemporaryDirectory() as tmp:
        current_path = Path(tmp) / "current.zarr"
        sdata.write(current_path)
        stores["container_current"] = fingerprint_store(current_path)
        legacy_path = Path(tmp) / "legacy.zarr"
        sdata.write(legacy_path, sdata_formats=SpatialDataContainerFormatV01())
        stores["container_0.1"] = fingerprint_store(legacy_path)
        # round trip: what comes back after read must match what went in (element layout)
        reread = spatialdata.read_zarr(current_path)
        roundtrip = fingerprint_python_api(reread)["elements"]

    def dep(name: str) -> str:
        try:
            return pkg_version(name)
        except Exception:  # noqa: BLE001
            return "<not installed>"

    return {
        "fingerprint_version": 1,
        "environment": {
            "spatialdata": spatialdata.__version__,
            "dependencies": {
                n: dep(n) for n in ["zarr", "ome-zarr", "anndata", "xarray", "dask", "geopandas", "pyarrow", "shapely"]
            },
            "python": sys.version.split()[0],
        },
        "format_module": fingerprint_format_module(),
        "on_disk": stores,
        "python_api": fingerprint_python_api(sdata),
        "python_api_after_read": roundtrip,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-o", "--output", type=Path, help="where to write the fingerprint JSON")
    parser.add_argument("--write-baseline", action="store_true", help="overwrite fingerprints/baseline.json")
    args = parser.parse_args()
    if not args.output and not args.write_baseline:
        parser.error("pass -o FILE or --write-baseline")
    data = generate()
    targets = []
    if args.output:
        targets.append(args.output)
    if args.write_baseline:
        targets.append(HERE / "fingerprints" / "baseline.json")
    for target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
        print(f"wrote {target} (spatialdata {data['environment']['spatialdata']})")


if __name__ == "__main__":
    main()
