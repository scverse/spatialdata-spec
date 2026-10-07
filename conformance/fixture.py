"""Deterministic SpatialData fixture covering every element type and transformation type.

Used by ``generate_fingerprint.py`` to detect on-disk and in-memory drift between ``spatialdata``
versions, and reusable as a small example dataset for other implementations. Licensed under
BSD-3-Clause like the rest of the repository tooling.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def build_fixture():  # type: ignore[no-untyped-def]
    """Return a SpatialData object with fixed content (no randomness, tiny arrays)."""
    import geopandas as gpd
    from anndata import AnnData
    from shapely.geometry import MultiPolygon, Point, Polygon
    from spatialdata import SpatialData
    from spatialdata.models import (
        Image2DModel,
        Image3DModel,
        Labels2DModel,
        Labels3DModel,
        PointsModel,
        ShapesModel,
        TableModel,
    )
    from spatialdata.transformations import Affine, Identity, MapAxis, Scale, Sequence, Translation

    rng = np.random.default_rng(0)

    image2d = Image2DModel.parse(
        rng.integers(0, 255, size=(2, 8, 10), dtype=np.uint8),
        c_coords=["DAPI", "CD3"],
        transformations={
            "global": Identity(),
            "scaled": Scale([0.5, 2.0], axes=("y", "x")),
            "shifted": Translation([10.0, -3.0], axes=("y", "x")),
            "affine": Affine(
                np.array([[1.0, 0.0, 5.0], [0.0, 2.0, 6.0], [0.0, 0.0, 1.0]]),
                input_axes=("x", "y"),
                output_axes=("x", "y"),
            ),
            "sequence": Sequence([Scale([2.0, 2.0], axes=("x", "y")), Translation([1.0, 1.0], axes=("x", "y"))]),
        },
    )
    image2d_multiscale = Image2DModel.parse(
        rng.integers(0, 255, size=(3, 16, 16), dtype=np.uint8),
        c_coords=["r", "g", "b"],
        scale_factors=[2, 2],
    )
    image3d = Image3DModel.parse(rng.integers(0, 4000, size=(1, 2, 8, 10), dtype=np.uint16))
    labels2d = Labels2DModel.parse(np.array([[0, 1, 1, 2], [0, 1, 2, 2], [3, 3, 0, 0]], dtype=np.uint16))
    labels2d_multiscale = Labels2DModel.parse(
        np.kron(np.arange(1, 5, dtype=np.uint32).reshape(2, 2), np.ones((8, 8), dtype=np.uint32)),
        scale_factors=[2, 2],
    )
    labels3d = Labels3DModel.parse(
        np.arange(2 * 4 * 5, dtype=np.int32).reshape(2, 4, 5) % 3,
        transformations={"global": Scale([1.0, 0.5, 0.5], axes=("z", "y", "x"))},
    )

    circles = ShapesModel.parse(
        gpd.GeoDataFrame({"geometry": [Point(1.0, 1.0), Point(2.5, 3.0)], "radius": [1.5, 2.5]}, index=["a", "b"]),
        transformations={"global": MapAxis({"x": "y", "y": "x"})},
    )
    square = Polygon([(0, 0), (0, 2), (2, 2), (2, 0)])
    polygons = ShapesModel.parse(
        gpd.GeoDataFrame({"geometry": [square, Polygon([(3, 3), (3, 5), (5, 5)])], "kind": ["sq", "tri"]})
    )
    multipolygons = ShapesModel.parse(
        gpd.GeoDataFrame({"geometry": [MultiPolygon([square, Polygon([(3, 3), (3, 5), (5, 5)])])]})
    )

    points2d = PointsModel.parse(
        pd.DataFrame(
            {
                "x": [1.0, 2.0, 3.0],
                "y": [3.0, 4.0, 5.0],
                "gene": pd.Categorical(["a", "b", "a"]),
                "cell": [1, 2, 1],
            }
        ),
        feature_key="gene",
        instance_key="cell",
    )
    points3d = PointsModel.parse(
        pd.DataFrame({"x": [1, 2], "y": [3, 4], "z": [0, 1], "intensity": [0.5, 0.75]}),
        transformations={"global": Identity(), "micron": Scale([0.2, 0.2, 1.0], axes=("x", "y", "z"))},
    )

    # one table annotating two regions: integer label values and the integer row index of `polygons`
    obs = pd.DataFrame(
        {
            "region": pd.Categorical(["labels2d", "labels2d", "polygons"]),
            "instance_id": np.array([1, 2, 0], dtype=np.int64),
            "cluster": pd.Categorical(["c1", "c2", "c1"]),
        },
        index=["r0", "r1", "r2"],
    )
    table = TableModel.parse(
        AnnData(X=np.arange(6, dtype=np.float64).reshape(3, 2), obs=obs, var=pd.DataFrame(index=["g1", "g2"])),
        region=["labels2d", "polygons"],
        region_key="region",
        instance_key="instance_id",
    )
    table_plain = AnnData(X=np.ones((2, 2), dtype=np.float32), obs=pd.DataFrame(index=["o1", "o2"]))

    sdata = SpatialData(
        images={"image2d": image2d, "image2d_multiscale": image2d_multiscale, "image3d": image3d},
        labels={"labels2d": labels2d, "labels2d_multiscale": labels2d_multiscale, "labels3d": labels3d},
        shapes={"circles": circles, "polygons": polygons, "multipolygons": multipolygons},
        points={"points2d": points2d, "points3d": points3d},
        tables={"table": table, "table_plain": table_plain},
        attrs={"fixture": {"purpose": "spec drift detection", "version": 1}},
    )
    return sdata


if __name__ == "__main__":
    print(build_fixture())
