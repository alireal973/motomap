"""Build DEM/API-enriched map outputs and export NPZ + PDF/SVG artifacts.

This script performs:
1) OSM graph fetch (API/network call)
2) Elevation fetch via Google Elevation API or Open Topo Data fallback
3) Grade and travel-time enrichment
4) Export of numeric arrays to .npz
5) SciencePlots/LaTeX-rendered PDF and SVG map
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
import numpy as np
import osmnx as ox
from matplotlib import colors
from matplotlib.collections import LineCollection

from motomap import motomap_graf_olustur
from motomap.algorithm import TRAVEL_TIME_ATTR, add_travel_time_to_graph, is_toll_edge
from motomap.config import GOOGLE_MAPS_API_KEY

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import scienceplots  # noqa: E402,F401


def _edge_segments_and_values(edges_gdf):
    segments = []
    grade_values_pct = []
    toll_segments = []

    for _, row in edges_gdf.iterrows():
        grade_pct = float(row.get("grade_abs", 0.0) or 0.0) * 100.0
        toll_flag = is_toll_edge(row.to_dict())
        geometry = row.geometry

        if geometry.geom_type == "LineString":
            xy = np.column_stack(geometry.xy)
            segments.append(xy)
            grade_values_pct.append(grade_pct)
            if toll_flag:
                toll_segments.append(xy)
            continue

        if geometry.geom_type == "MultiLineString":
            for part in geometry.geoms:
                xy = np.column_stack(part.xy)
                segments.append(xy)
                grade_values_pct.append(grade_pct)
                if toll_flag:
                    toll_segments.append(xy)

    return segments, np.asarray(grade_values_pct, dtype=float), toll_segments


def _export_npz(graph, output_path: Path, place: str) -> Path:
    node_rows = list(graph.nodes(data=True))
    edge_rows = list(graph.edges(keys=True, data=True))

    node_ids = np.asarray([int(node_id) for node_id, _ in node_rows], dtype=np.int64)
    node_x = np.asarray(
        [float(data.get("x", np.nan)) for _, data in node_rows], dtype=float
    )
    node_y = np.asarray(
        [float(data.get("y", np.nan)) for _, data in node_rows], dtype=float
    )
    node_elevation = np.asarray(
        [float(data.get("elevation", np.nan)) for _, data in node_rows],
        dtype=float,
    )

    edge_u = np.asarray([int(u) for u, _, _, _ in edge_rows], dtype=np.int64)
    edge_v = np.asarray([int(v) for _, v, _, _ in edge_rows], dtype=np.int64)
    edge_key = np.asarray([int(k) for _, _, k, _ in edge_rows], dtype=np.int64)
    edge_length_m = np.asarray(
        [float(data.get("length", np.nan)) for _, _, _, data in edge_rows],
        dtype=float,
    )
    edge_grade = np.asarray(
        [float(data.get("grade", np.nan)) for _, _, _, data in edge_rows],
        dtype=float,
    )
    edge_grade_abs = np.asarray(
        [float(data.get("grade_abs", np.nan)) for _, _, _, data in edge_rows],
        dtype=float,
    )
    edge_travel_time_s = np.asarray(
        [float(data.get(TRAVEL_TIME_ATTR, np.nan)) for _, _, _, data in edge_rows],
        dtype=float,
    )
    edge_toll = np.asarray(
        [1 if is_toll_edge(data) else 0 for _, _, _, data in edge_rows],
        dtype=np.uint8,
    )

    metadata = {
        "place": place,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "node_count": int(graph.number_of_nodes()),
        "edge_count": int(graph.number_of_edges()),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output_path,
        node_ids=node_ids,
        node_x=node_x,
        node_y=node_y,
        node_elevation=node_elevation,
        edge_u=edge_u,
        edge_v=edge_v,
        edge_key=edge_key,
        edge_length_m=edge_length_m,
        edge_grade=edge_grade,
        edge_grade_abs=edge_grade_abs,
        edge_travel_time_s=edge_travel_time_s,
        edge_toll=edge_toll,
        metadata_json=np.asarray(json.dumps(metadata), dtype="<U2048"),
    )
    return output_path


def _plot_science_map(
    graph,
    place: str,
    pdf_output_path: Path,
    svg_output_path: Path,
) -> tuple[Path, Path]:
    projected_graph = ox.project_graph(graph)
    nodes_gdf, edges_gdf = ox.graph_to_gdfs(projected_graph)

    segments, grade_values_pct, toll_segments = _edge_segments_and_values(edges_gdf)
    if grade_values_pct.size == 0:
        raise ValueError("No plottable edge geometry found.")

    # SciencePlots + LaTeX rendering.
    plt.style.use(["science", "grid"])
    plt.rcParams.update(
        {
            "text.usetex": True,
            "font.family": "serif",
            "axes.unicode_minus": False,
        }
    )

    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)

    upper = float(np.nanpercentile(grade_values_pct, 95))
    vmax = max(1.0, upper)
    lc = LineCollection(
        segments,
        cmap="viridis",
        norm=colors.Normalize(vmin=0.0, vmax=vmax),
        linewidths=1.2,
        alpha=0.95,
    )
    lc.set_array(grade_values_pct)
    ax.add_collection(lc)

    if toll_segments:
        toll_lc = LineCollection(
            toll_segments,
            colors="#d62728",
            linewidths=1.9,
            alpha=0.70,
        )
        ax.add_collection(toll_lc)

    elev_values = nodes_gdf["elevation"].astype(float).to_numpy()
    node_scatter = ax.scatter(
        nodes_gdf.geometry.x.to_numpy(),
        nodes_gdf.geometry.y.to_numpy(),
        c=elev_values,
        cmap="magma",
        s=5,
        alpha=0.35,
        linewidths=0,
        zorder=3,
    )

    ax.autoscale()
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title(
        r"\textbf{MOTOMAP DEM/API Haritasi}"
        + "\n"
        + rf"$|V|={graph.number_of_nodes()},\ |E|={graph.number_of_edges()}$",
        fontsize=14,
        pad=16,
    )

    cbar_grade = fig.colorbar(lc, ax=ax, fraction=0.03, pad=0.015)
    cbar_grade.set_label(r"$|\mathrm{grade}|\,(\%)$", fontsize=10)

    cbar_elev = fig.colorbar(node_scatter, ax=ax, fraction=0.03, pad=0.06)
    cbar_elev.set_label(r"$\mathrm{elevation}\,(m)$", fontsize=10)

    mean_grade_pct = float(np.nanmean(grade_values_pct))
    mean_tt_s = float(
        np.nanmean(
            [
                float(data.get(TRAVEL_TIME_ATTR, np.nan))
                for _, _, _, data in graph.edges(keys=True, data=True)
            ]
        )
    )
    text = (
        rf"$\mathrm{{Place}}:\ {place}$" + "\n"
        rf"$\overline{{|\mathrm{{grade}}|}}={mean_grade_pct:.2f}\%$" + "\n"
        rf"$\overline{{T_e}}={mean_tt_s:.2f}\ \mathrm{{s}}$"
    )
    ax.text(
        0.02,
        0.02,
        text,
        transform=ax.transAxes,
        fontsize=10,
        bbox={"facecolor": "white", "edgecolor": "black", "alpha": 0.85, "pad": 6},
    )

    pdf_output_path.parent.mkdir(parents=True, exist_ok=True)
    svg_output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(pdf_output_path, format="pdf", bbox_inches="tight")
    fig.savefig(svg_output_path, format="svg", bbox_inches="tight")
    plt.close(fig)
    return pdf_output_path, svg_output_path


def run(
    place: str,
    output_dir: Path,
    api_key: str | None,
    basename: str | None = None,
):
    resolved_key = api_key if api_key is not None else GOOGLE_MAPS_API_KEY
    graph = motomap_graf_olustur(place, api_key=resolved_key)
    add_travel_time_to_graph(graph)

    safe_name = place.lower().replace(",", "").replace(" ", "_").replace("/", "_")
    if basename:
        stem = basename
    else:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        stem = f"{safe_name}_{timestamp}"

    npz_path = output_dir / f"{stem}.npz"
    pdf_path = output_dir / f"{stem}.pdf"
    svg_path = output_dir / f"{stem}.svg"

    saved_npz = _export_npz(graph, npz_path, place=place)
    saved_pdf, saved_svg = _plot_science_map(
        graph,
        place=place,
        pdf_output_path=pdf_path,
        svg_output_path=svg_path,
    )
    return saved_npz, saved_pdf, saved_svg


def main():
    parser = argparse.ArgumentParser(
        description="Export DEM/API graph artifacts (NPZ + SciencePlots PDF)."
    )
    parser.add_argument(
        "--place",
        default="Moda, Kadikoy, Istanbul, Turkey",
        help="Geocodable area name for OSM graph download.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/dem_api",
        help="Output directory for NPZ and PDF files.",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="Google Elevation API key (optional).",
    )
    parser.add_argument(
        "--basename",
        default=None,
        help="Optional fixed output basename (without extension).",
    )
    args = parser.parse_args()

    npz_path, pdf_path, svg_path = run(
        place=args.place,
        output_dir=Path(args.output_dir),
        api_key=args.api_key,
        basename=args.basename,
    )
    print(f"NPZ saved: {npz_path}")
    print(f"PDF saved: {pdf_path}")
    print(f"SVG saved: {svg_path}")


if __name__ == "__main__":
    main()
