"""Check that the on-disk specification is consistent with ``spatialdata._io.format``.

``format.py`` in scverse/spatialdata is the source of truth for every on-disk format version:
which versions exist per component, which NGFF version string raster elements carry, which Zarr
format a container version implies, and which element versions a container version allows.
This script reads those facts from the installed ``spatialdata`` and checks that the prose in
``spec/on-disk/versions.md`` and ``spec/on-disk/images.md`` states the same.

Run from the repository root with a Python environment that has ``spatialdata`` installed::

    python tools/check_format_versions.py

Exit code 0 means consistent; 1 lists the mismatches. Licensed under BSD-3-Clause like the rest of
the repository tooling.
"""

from __future__ import annotations

import re
import sys
import warnings
from pathlib import Path

warnings.simplefilter("ignore")

import spatialdata  # noqa: E402
import spatialdata._io.format as fmt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
VERSIONS_MD = (ROOT / "spec" / "on-disk" / "versions.md").read_text()
IMAGES_MD = (ROOT / "spec" / "on-disk" / "images.md").read_text()

errors: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


# 1. Every element format version has a row in the element table: "| raster | 0.1 |" (bold allowed).
component_formats = {
    "raster": fmt.RasterFormats,
    "shapes": fmt.ShapesFormats,
    "points": fmt.PointsFormats,
    "tables": fmt.TablesFormats,
}
for component, formats in component_formats.items():
    for version in formats:
        pattern = rf"\|\s*{component}\s*\|\s*\**{re.escape(version)}\**\s*\|"
        check(re.search(pattern, VERSIONS_MD) is not None, f"versions.md: no row for {component} {version}")

# 2. Current versions are the bold ones.
current = fmt._parse_formats(None)
for component, formats in component_formats.items():
    current_version = current[component].spatialdata_format_version
    pattern = rf"\|\s*{component}\s*\|\s*\*\*{re.escape(current_version)}\*\*\s*\|"
    check(
        re.search(pattern, VERSIONS_MD) is not None,
        f"versions.md: current {component} version {current_version} is not the bold row",
    )
    for version in formats:
        if version != current_version:
            pattern = rf"\|\s*{component}\s*\|\s*\*\*{re.escape(version)}\*\*\s*\|"
            check(
                re.search(pattern, VERSIONS_MD) is None, f"versions.md: {component} {version} is bold but not current"
            )

# 3. Container versions: Zarr format and allowed element versions.
class_to_component = {
    "RasterFormat": "raster",
    "ShapesFormat": "shapes",
    "PointsFormat": "points",
    "TablesFormat": "tables",
}
for container_version, container in fmt.SpatialDataContainerFormats.items():
    allowed_names = fmt.ContainerFormatValidElements[str(container)]
    allowed: dict[str, list[str]] = {c: [] for c in class_to_component.values()}
    for name in allowed_names:
        prefix = name.rstrip("0123456789").removesuffix("V")
        component = class_to_component[prefix]
        allowed[component].append(getattr(fmt, name)().spatialdata_format_version)
    expected = " · ".join(f"{c} {', '.join(v)}" for c, v in allowed.items())
    check(expected in VERSIONS_MD, f"versions.md: container {container_version} should allow '{expected}'")
    zarr = f"v{container.zarr_format}"
    pattern = rf"\|\s*\**{re.escape(container_version)}\**[^|]*\|\s*{zarr}\s*\|"
    check(
        re.search(pattern, VERSIONS_MD) is not None,
        f"versions.md: container {container_version} should be listed with Zarr {zarr}",
    )

current_container = current["SpatialData"].spatialdata_format_version
check(
    re.search(rf"\|\s*\*\*{re.escape(current_container)}\*\*\s*\(current\)", VERSIONS_MD) is not None,
    f"versions.md: container {current_container} should be marked '**{current_container}** (current)'",
)

# 4. Default element versions when writing container 0.1.
defaults = {c: f.spatialdata_format_version for c, f in fmt.ContainerV01DefaultTypes.items()}
expected_defaults = " · ".join(f"{c} {v}" for c, v in defaults.items())
check(expected_defaults in VERSIONS_MD, f"versions.md: container 0.1 defaults should read '{expected_defaults}'")

# 5. NGFF version strings written by raster formats appear in versions.md and images.md.
for raster in fmt.RasterFormats.values():
    string = f'"{raster.version}"'
    check(
        string in VERSIONS_MD, f"versions.md: raster {raster.spatialdata_format_version} NGFF string {string} missing"
    )
    check(string in IMAGES_MD, f"images.md: NGFF string {string} missing")

# 6. Mapping NGFF version string -> ome-zarr Format (Zarr 2 vs 3) agrees with raster formats.
for string, ome_format in fmt.sdata_zarr_version_to_ome_zarr_format.items():
    raster = fmt.sdata_zarr_version_to_raster_format[string]
    check(
        ome_format.zarr_format == raster.zarr_format,
        f"format.py internal: {string} maps to Zarr {ome_format.zarr_format} but raster format says {raster.zarr_format}",
    )

print(
    f"spatialdata {spatialdata.__version__}; format classes checked: {len(fmt.RasterFormats) + len(fmt.ShapesFormats) + len(fmt.PointsFormats) + len(fmt.TablesFormats) + len(fmt.SpatialDataContainerFormats)}"
)
if errors:
    print("Mismatches between format.py and the specification:")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)
print("OK: spec/on-disk/versions.md and images.md are consistent with spatialdata._io.format")
