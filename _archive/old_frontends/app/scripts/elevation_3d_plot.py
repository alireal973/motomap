"""Generate advanced 3D elevation plots from MOTOMAP NPZ data."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import matplotlib
import numpy as np
from matplotlib.tri import Triangulation

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import scienceplots  # noqa: E402,F401


def _local_xy_meters(node_x, node_y):
    lon = node_x.astype(float)
    lat = node_y.astype(float)
    lon0 = float(np.nanmean(lon))
    lat0 = float(np.nanmean(lat))
    x_m = (lon - lon0) * 111320.0 * math.cos(math.radians(lat0))
    y_m = (lat - lat0) * 110540.0
    return x_m, y_m


def render_3d(npz_path: Path, png_path: Path, pdf_path: Path):
    data = np.load(npz_path, allow_pickle=True)
    node_x = data["node_x"].astype(float)
    node_y = data["node_y"].astype(float)
    node_elevation = data["node_elevation"].astype(float)

    mask = np.isfinite(node_x) & np.isfinite(node_y) & np.isfinite(node_elevation)
    x_m, y_m = _local_xy_meters(node_x[mask], node_y[mask])
    z_m = node_elevation[mask]

    tri = Triangulation(x_m, y_m)

    plt.style.use(["science", "grid"])
    plt.rcParams.update(
        {
            "text.usetex": True,
            "font.family": "serif",
            "axes.unicode_minus": False,
        }
    )

    fig = plt.figure(figsize=(14, 8), dpi=300)
    ax = fig.add_subplot(111, projection="3d")

    surf = ax.plot_trisurf(
        tri,
        z_m,
        cmap="terrain",
        linewidth=0.05,
        antialiased=True,
        alpha=0.97,
    )

    ax.set_title(r"\textbf{MOTOMAP 3D Y\"ukselti Y\"uzeyi}", fontsize=15, pad=18)
    ax.set_xlabel(r"$x\,(m)$", labelpad=10)
    ax.set_ylabel(r"$y\,(m)$", labelpad=10)
    ax.set_zlabel(r"$z\,(m)$", labelpad=10)
    ax.view_init(elev=45, azim=-135)
    ax.set_box_aspect((1.0, 1.0, 0.23))

    cbar = fig.colorbar(surf, ax=ax, shrink=0.60, pad=0.08)
    cbar.set_label(r"$\mathrm{elevation}\,(m)$", fontsize=10)

    meta = json.loads(str(data["metadata_json"]))
    text = (
        rf"$\mathrm{{Place}}:\ {meta.get('place', 'N/A')}$" + "\n"
        rf"$|V|={meta.get('node_count', 0)},\ |E|={meta.get('edge_count', 0)}$" + "\n"
        rf"$z_{{min}}={float(np.nanmin(z_m)):.2f}\,\mathrm{{m}},\ "
        rf"z_{{max}}={float(np.nanmax(z_m)):.2f}\,\mathrm{{m}}$"
    )
    ax.text2D(
        0.02,
        0.02,
        text,
        transform=ax.transAxes,
        fontsize=10,
        bbox={"facecolor": "white", "edgecolor": "black", "alpha": 0.85, "pad": 6},
    )

    png_path.parent.mkdir(parents=True, exist_ok=True)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png_path, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Render 3D elevation from NPZ.")
    parser.add_argument("--npz", required=True, help="Input NPZ path.")
    parser.add_argument(
        "--png-output",
        required=True,
        help="Output PNG path.",
    )
    parser.add_argument(
        "--pdf-output",
        required=True,
        help="Output PDF path.",
    )
    args = parser.parse_args()

    render_3d(
        npz_path=Path(args.npz),
        png_path=Path(args.png_output),
        pdf_path=Path(args.pdf_output),
    )
    print(f"3D PNG saved: {args.png_output}")
    print(f"3D PDF saved: {args.pdf_output}")


if __name__ == "__main__":
    main()
