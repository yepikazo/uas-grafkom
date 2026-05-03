"""
Shared terrain height calculation for Danau Motosu scene.
Layout: Camp (south) → Lake (center) → Fuji (north) — all aligned on Z axis.
"""
import math

# === Scene Layout (aligned along Z axis) ===

# Lake Motosu — MUCH larger, elongated east-west
LAKE_CENTER_X = 0.0
LAKE_CENTER_Z = 0.0
LAKE_SEMI_MAJOR = 80.0    # X axis (east-west), ~160 units wide
LAKE_SEMI_MINOR = 40.0    # Z axis (north-south), ~80 units deep
LAKE_WATER_LEVEL = -0.3

# Mount Fuji — due NORTH of lake (negative Z in skybox)
FUJI_DIR_X = 0.0
FUJI_DIR_Z = -1.0

# Camping spot — due SOUTH of lake center
CAMP_X = 0.0
CAMP_Z = 48.0


def lake_distance(x, z):
    """Signed distance to lake boundary. Negative = inside lake."""
    lx = x - LAKE_CENTER_X
    lz = z - LAKE_CENTER_Z

    nx = lx / LAKE_SEMI_MAJOR
    nz = lz / LAKE_SEMI_MINOR

    # Western end narrower, eastern wider (like real Motosu)
    width_mod = 1.0 + 0.12 * nx
    nz_adj = nz / max(width_mod, 0.4)

    # Organic perturbation for natural shoreline
    angle = math.atan2(nz_adj, nx)
    perturb = (0.05 * math.sin(angle * 3.0 + 0.5) +
               0.03 * math.sin(angle * 5.0 + 2.0) +
               0.02 * math.cos(angle * 7.0 + 1.0))

    r = math.sqrt(nx * nx + nz_adj * nz_adj)
    return r + perturb - 1.0


def terrain_noise(x, z):
    """Multi-octave procedural noise for terrain hills."""
    n = 0.0
    n += math.sin(x * 0.04 + 1.3) * math.cos(z * 0.035 + 0.8) * 1.0
    n += math.sin(x * 0.07 + z * 0.06 + 2.1) * 0.6
    n += math.cos(x * 0.05 - z * 0.07 + 0.3) * 0.8
    n += math.sin(x * 0.15 + z * 0.12 + 1.5) * 0.3
    n += math.cos(x * 0.12 - z * 0.18 + 0.7) * 0.25
    n += math.sin(x * 0.3 + z * 0.25 + 3.0) * 0.1
    return n


def height_at(x, z):
    """Calculate terrain height at world position (x, z)."""
    lake_d = lake_distance(x, z)

    # Deep inside lake — lake bed
    if lake_d < -0.3:
        return LAKE_WATER_LEVEL - 3.0

    # Shore transition zone
    if lake_d < 0.0:
        t = max(0.0, (lake_d + 0.3) / 0.3)
        bed_h = LAKE_WATER_LEVEL - 3.0
        return bed_h * (1.0 - t)

    # Land terrain — hills scale with distance from shore
    shore_factor = min(lake_d / 1.5, 1.0)
    shore_factor *= shore_factor
    base_h = shore_factor * 2.0

    # Hills from noise
    noise = terrain_noise(x, z)
    hill_factor = min(lake_d / 2.5, 1.0)
    hills_h = max(0.0, noise) * hill_factor * 12.0

    # Distant terrain rises (surrounding mountains)
    dist = math.sqrt(x * x + z * z)
    far_rise = min(max(0.0, (dist - 100.0) / 60.0), 1.0)
    far_h = far_rise * 15.0

    # Mountain ridges far from lake
    if dist > 60.0:
        ridge = (math.sin(x * 0.06 + 0.5) * math.cos(z * 0.05 + 1.0) *
                 math.sin(x * 0.025 + z * 0.03) * 10.0)
        ridge_factor = min((dist - 60.0) / 40.0, 1.0)
        hills_h += max(0.0, ridge) * ridge_factor

    height = base_h + hills_h + far_h

    # Edge rise to hide terrain boundary
    edge_dist = min(200.0 - abs(x), 200.0 - abs(z))
    if edge_dist < 30.0:
        edge_rise = ((30.0 - edge_dist) / 30.0) ** 1.5
        height = max(height, edge_rise * 25.0)

    return height
