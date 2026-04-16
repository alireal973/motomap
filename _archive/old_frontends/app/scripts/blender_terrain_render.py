"""Render a 4K terrain scene from MOTOMAP NPZ using Blender.

Usage example:
    blender -b -P scripts/blender_terrain_render.py -- \
      --npz outputs/dem_api/moda_kadikoy_dem_api_map.npz \
      --output outputs/dem_api/moda_kadikoy_dem_api_3d_4k.png
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy
import numpy as np


def _parse_args():
    raw = sys.argv
    if "--" in raw:
        raw = raw[raw.index("--") + 1 :]
    else:
        raw = []

    parser = argparse.ArgumentParser(description="Blender 4K terrain renderer")
    parser.add_argument("--npz", required=True, help="Input NPZ file path")
    parser.add_argument("--output", required=True, help="Output image path (PNG)")
    parser.add_argument("--grid-size", type=int, default=220, help="Terrain grid size")
    parser.add_argument(
        "--z-scale", type=float, default=85.0, help="Vertical exaggeration"
    )
    return parser.parse_args(raw)


def _prepare_height_grid(node_x, node_y, node_elev, grid_size: int):
    lon = node_x.astype(float)
    lat = node_y.astype(float)
    elev = node_elev.astype(float)

    mask = np.isfinite(lon) & np.isfinite(lat) & np.isfinite(elev)
    lon, lat, elev = lon[mask], lat[mask], elev[mask]
    if lon.size < 50:
        raise ValueError("Not enough valid nodes for terrain mesh.")

    lon0 = float(np.mean(lon))
    lat0 = float(np.mean(lat))
    x_m = (lon - lon0) * 111320.0 * math.cos(math.radians(lat0))
    y_m = (lat - lat0) * 110540.0
    z_m = elev - float(np.nanmin(elev))

    x_min, x_max = float(np.min(x_m)), float(np.max(x_m))
    y_min, y_max = float(np.min(y_m)), float(np.max(y_m))
    xr = max(1e-6, x_max - x_min)
    yr = max(1e-6, y_max - y_min)

    accum = np.zeros((grid_size, grid_size), dtype=float)
    counts = np.zeros((grid_size, grid_size), dtype=float)
    ix = np.clip(((x_m - x_min) / xr * (grid_size - 1)).astype(int), 0, grid_size - 1)
    iy = np.clip(((y_m - y_min) / yr * (grid_size - 1)).astype(int), 0, grid_size - 1)
    np.add.at(accum, (iy, ix), z_m)
    np.add.at(counts, (iy, ix), 1.0)

    height = np.full_like(accum, np.nan)
    valid = counts > 0
    height[valid] = accum[valid] / counts[valid]

    # Fill gaps with iterative neighborhood averaging.
    for _ in range(12):
        nan_mask = ~np.isfinite(height)
        if not np.any(nan_mask):
            break

        filled = height.copy()
        changed = False
        for y in range(grid_size):
            y0 = max(0, y - 1)
            y1 = min(grid_size, y + 2)
            for x in range(grid_size):
                if np.isfinite(height[y, x]):
                    continue
                x0 = max(0, x - 1)
                x1 = min(grid_size, x + 2)
                patch = height[y0:y1, x0:x1]
                vals = patch[np.isfinite(patch)]
                if vals.size:
                    filled[y, x] = float(np.mean(vals))
                    changed = True
        height = filled
        if not changed:
            break

    # Final fallback for any remaining NaN.
    if np.any(~np.isfinite(height)):
        height[~np.isfinite(height)] = float(np.nanmean(height))

    # Smoothing pass.
    for _ in range(2):
        p = np.pad(height, 1, mode="edge")
        height = (
            p[0:-2, 0:-2]
            + p[0:-2, 1:-1]
            + p[0:-2, 2:]
            + p[1:-1, 0:-2]
            + 2.0 * p[1:-1, 1:-1]
            + p[1:-1, 2:]
            + p[2:, 0:-2]
            + p[2:, 1:-1]
            + p[2:, 2:]
        ) / 10.0

    x_axis = np.linspace(x_min, x_max, grid_size)
    y_axis = np.linspace(y_min, y_max, grid_size)
    return x_axis, y_axis, height


def _build_mesh(x_axis, y_axis, height, z_scale: float):
    vertices = []
    faces = []
    ny, nx = height.shape
    z_max = float(np.max(height)) if np.max(height) > 0 else 1.0

    for j in range(ny):
        for i in range(nx):
            z = float(height[j, i] / z_max) * z_scale
            vertices.append((float(x_axis[i]), float(y_axis[j]), z))

    for j in range(ny - 1):
        for i in range(nx - 1):
            a = j * nx + i
            b = a + 1
            c = a + nx + 1
            d = a + nx
            faces.append((a, b, c, d))

    mesh = bpy.data.meshes.new("MotoMapTerrain")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    obj = bpy.data.objects.new("MotoMapTerrain", mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth()
    return obj


def _setup_material(obj, z_scale: float):
    mat = bpy.data.materials.new(name="TerrainMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new(type="ShaderNodeOutputMaterial")
    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    geom = nodes.new(type="ShaderNodeNewGeometry")
    sep_xyz = nodes.new(type="ShaderNodeSeparateXYZ")
    map_range = nodes.new(type="ShaderNodeMapRange")
    ramp = nodes.new(type="ShaderNodeValToRGB")

    map_range.inputs["From Min"].default_value = 0.0
    map_range.inputs["From Max"].default_value = max(1.0, z_scale)
    map_range.inputs["To Min"].default_value = 0.0
    map_range.inputs["To Max"].default_value = 1.0

    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.10, 0.26, 0.54, 1.0)
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = (0.95, 0.93, 0.86, 1.0)
    mid1 = ramp.color_ramp.elements.new(0.35)
    mid1.color = (0.15, 0.55, 0.30, 1.0)
    mid2 = ramp.color_ramp.elements.new(0.68)
    mid2.color = (0.48, 0.34, 0.21, 1.0)

    bsdf.inputs["Roughness"].default_value = 0.72
    bsdf.inputs["Specular IOR Level"].default_value = 0.03

    links.new(geom.outputs["Position"], sep_xyz.inputs["Vector"])
    links.new(sep_xyz.outputs["Z"], map_range.inputs["Value"])
    links.new(map_range.outputs["Result"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def _setup_scene(obj, output_path: Path):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 64
    scene.render.resolution_x = 3840
    scene.render.resolution_y = 2160
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(output_path.resolve())

    # Clean default camera/light if present
    for name in ("Camera", "Light"):
        if name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

    # Add camera
    bpy.ops.object.camera_add()
    cam = bpy.context.object
    scene.camera = cam

    # Place camera based on object bounds
    bbox = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
    xs = [v.x for v in bbox]
    ys = [v.y for v in bbox]
    zs = [v.z for v in bbox]
    cx = (min(xs) + max(xs)) / 2.0
    cy = (min(ys) + max(ys)) / 2.0
    cz = (min(zs) + max(zs)) / 2.0
    span = max(max(xs) - min(xs), max(ys) - min(ys))
    dist = span * 1.6

    cam.location = (cx - dist, cy - dist, cz + dist * 0.95)
    cam.data.lens = 42
    cam.data.clip_start = 0.1
    cam.data.clip_end = max(100000.0, dist * 20.0)

    # Track camera to terrain center for robust framing.
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(cx, cy, cz))
    target = bpy.context.object
    track = cam.constraints.new(type="TRACK_TO")
    track.target = target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    # Sun + fill light
    bpy.ops.object.light_add(
        type="SUN", location=(cx + dist, cy - dist, cz + dist * 1.3)
    )
    sun = bpy.context.object
    sun.data.energy = 5.0
    sun.rotation_euler = (math.radians(40.0), math.radians(8.0), math.radians(35.0))

    bpy.ops.object.light_add(
        type="AREA", location=(cx - dist * 0.4, cy + dist * 0.3, cz + dist * 0.6)
    )
    area = bpy.context.object
    area.data.energy = 420.0
    area.data.size = span * 0.7

    if scene.world is None:
        scene.world = bpy.data.worlds.new("MotoMapWorld")
    world = scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.015, 0.02, 0.03, 1.0)
        bg.inputs[1].default_value = 0.85


def main():
    # Delay import until Blender runtime is fully available.
    global mathutils
    import mathutils  # noqa: PLC0415

    args = _parse_args()
    npz_path = Path(args.npz)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Reset scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    data = np.load(npz_path, allow_pickle=True)
    x_axis, y_axis, height = _prepare_height_grid(
        data["node_x"],
        data["node_y"],
        data["node_elevation"],
        grid_size=args.grid_size,
    )
    terrain_obj = _build_mesh(x_axis, y_axis, height, z_scale=args.z_scale)
    _setup_material(terrain_obj, z_scale=args.z_scale)
    _setup_scene(terrain_obj, output_path=output_path)

    bpy.ops.render.render(write_still=True)
    print(f"4K render saved: {output_path}")


if __name__ == "__main__":
    main()
