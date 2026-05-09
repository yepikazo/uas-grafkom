"""
Tent, camping accessories, and scattered trees around Lake Motosu.
Revised: 3 tents (Olive Green, Navy Blue, Khaki Brown), more background forest trees.
"""
import numpy as np
import math
import random
from OpenGL.GL import *
from core.terrain_height import height_at, lake_distance, CAMP_X, CAMP_Z
from core.terrain_height import LAKE_SEMI_MAJOR, LAKE_SEMI_MINOR


class Tent:
    """A-frame camping tents with chairs, camping props, lantern, and forest trees."""

    def __init__(self):
        self.position = (CAMP_X, height_at(CAMP_X, CAMP_Z), CAMP_Z)
        self.rotation = math.pi * 1.5  # Face toward lake (north, -Z)
        self.vao = None
        self.vbo = None
        self.ebo = None
        self.index_count = 0
        self._generate()

    def _add_box(self, verts, idxs, cx, cy, cz, hw, hh, hd, color):
        b = len(verts) // 9
        for sy in [-1, 1]:
            for sz in [-1, 1]:
                for sx in [-1, 1]:
                    n = 0.577
                    verts.extend([cx+sx*hw, cy+sy*hh, cz+sz*hd,
                                  sx*n, sy*n, sz*n, *color])
        i = b
        idxs.extend([i,i+1,i+3, i,i+3,i+2, i+4,i+7,i+5, i+4,i+6,i+7,
                     i,i+4,i+1, i+1,i+4,i+5, i+2,i+3,i+6, i+3,i+7,i+6,
                     i,i+2,i+4, i+2,i+6,i+4, i+1,i+5,i+3, i+3,i+5,i+7])

    def _add_rotated_box(self, verts, idxs, cx, cy, cz, hw, hh, hd, rotation, color):
        """Add a box rotated around Y. Local +Z is the facing direction."""
        cr, sr = math.cos(rotation), math.sin(rotation)
        b = len(verts) // 9

        for sy in [-1, 1]:
            for sz in [-1, 1]:
                for sx in [-1, 1]:
                    lx, ly, lz = sx * hw, sy * hh, sz * hd
                    wx = cx + lx * cr + lz * sr
                    wz = cz - lx * sr + lz * cr

                    n = 0.577
                    nx = sx * n * cr + sz * n * sr
                    nz = -sx * n * sr + sz * n * cr
                    verts.extend([wx, cy + ly, wz, nx, sy * n, nz, *color])

        i = b
        idxs.extend([i,i+1,i+3, i,i+3,i+2, i+4,i+7,i+5, i+4,i+6,i+7,
                     i,i+4,i+1, i+1,i+4,i+5, i+2,i+3,i+6, i+3,i+7,i+6,
                     i,i+2,i+4, i+2,i+6,i+4, i+1,i+5,i+3, i+3,i+5,i+7])

    def _look_rotation(self, cx, cz, tx, tz):
        """Return a Y rotation where local +Z points toward target."""
        return math.atan2(tx - cx, tz - cz)

    def _add_simple_chair(self, verts, idxs, cx, cz, rotation, fabric_color):
        """Add the original simple chair model."""
        cy = height_at(cx, cz)
        frame_color = [0.18, 0.18, 0.17]
        sw, sh, sd = 0.3, 0.35, 0.3
        cr, sr = math.cos(rotation), math.sin(rotation)

        def chair_vertex(lx, ly, lz, nx, ny, nz):
            wx = cx + lx * cr + lz * sr
            wz = cz - lx * sr + lz * cr
            wnx = nx * cr + nz * sr
            wnz = -nx * sr + nz * cr
            return [wx, cy + ly, wz, wnx, ny, wnz]

        def chair_leg(lx, lz):
            leg_x = cx + lx * cr + lz * sr
            leg_z = cz - lx * sr + lz * cr
            self._add_box(verts, idxs, leg_x, cy + sh/2, leg_z,
                          0.015, sh/2, 0.015, frame_color)

        b = len(verts) // 9
        for vertex in [
            chair_vertex(-sw, sh, -sd, 0, 1, 0),
            chair_vertex( sw, sh, -sd, 0, 1, 0),
            chair_vertex( sw, sh,  sd, 0, 1, 0),
            chair_vertex(-sw, sh,  sd, 0, 1, 0),
        ]:
            verts.extend([*vertex, *fabric_color])
        idxs.extend([b, b+1, b+2, b, b+2, b+3])

        b = len(verts) // 9
        for vertex in [
            chair_vertex(-sw, sh,       sd, 0, 0, 1),
            chair_vertex( sw, sh,       sd, 0, 0, 1),
            chair_vertex( sw, sh+0.45,  sd, 0, 0, 1),
            chair_vertex(-sw, sh+0.45,  sd, 0, 0, 1),
        ]:
            verts.extend([*vertex, *fabric_color])
        idxs.extend([b, b+1, b+2, b, b+2, b+3])

        for dx in [-sw+0.05, sw-0.05]:
            for dz in [-sd+0.05, sd-0.05]:
                chair_leg(dx, dz)

    def _add_camping_props(self, verts, idxs, fire_x, fire_z):
        """Add small camping items around the fire without entering tent/fire space."""
        wood = [0.30, 0.18, 0.08]
        metal = [0.42, 0.42, 0.38]
        dark = [0.08, 0.08, 0.075]
        red = [0.42, 0.07, 0.05]
        cream = [0.82, 0.78, 0.62]
        blanket = [0.50, 0.08, 0.06]

        table_x, table_z = fire_x + 1.55, fire_z + 1.35
        table_y = height_at(table_x, table_z)
        table_rot = self._look_rotation(table_x, table_z, fire_x, fire_z)
        self._add_rotated_box(verts, idxs, table_x, table_y + 0.42, table_z,
                              0.55, 0.045, 0.32, table_rot, wood)
        for lx in [-0.45, 0.45]:
            for lz in [-0.23, 0.23]:
                leg_x = table_x + lx * math.cos(table_rot) + lz * math.sin(table_rot)
                leg_z = table_z - lx * math.sin(table_rot) + lz * math.cos(table_rot)
                self._add_box(verts, idxs, leg_x, table_y + 0.22, leg_z,
                              0.025, 0.22, 0.025, dark)

        # Cooking pot and two mugs on the table.
        self._add_box(verts, idxs, table_x - 0.05, table_y + 0.54, table_z,
                      0.18, 0.08, 0.18, metal)
        self._add_box(verts, idxs, table_x - 0.05, table_y + 0.64, table_z,
                      0.20, 0.02, 0.20, dark)
        self._add_box(verts, idxs, table_x + 0.32, table_y + 0.55, table_z - 0.12,
                      0.07, 0.09, 0.07, red)
        self._add_box(verts, idxs, table_x + 0.34, table_y + 0.55, table_z + 0.14,
                      0.07, 0.09, 0.07, cream)

        cooler_x, cooler_z = fire_x - 3.45, fire_z - 1.65
        cooler_y = height_at(cooler_x, cooler_z)
        cooler_rot = self._look_rotation(cooler_x, cooler_z, fire_x, fire_z)
        self._add_rotated_box(verts, idxs, cooler_x, cooler_y + 0.22, cooler_z,
                              0.42, 0.22, 0.28, cooler_rot, [0.70, 0.72, 0.68])
        self._add_rotated_box(verts, idxs, cooler_x, cooler_y + 0.46, cooler_z,
                              0.44, 0.035, 0.30, cooler_rot, [0.12, 0.18, 0.28])

        mat_x, mat_z = fire_x - 1.00, fire_z + 3.00
        mat_y = height_at(mat_x, mat_z)
        mat_rot = self._look_rotation(mat_x, mat_z, fire_x, fire_z)
        self._add_rotated_box(verts, idxs, mat_x, mat_y + 0.04, mat_z,
                              0.48, 0.025, 0.95, mat_rot, blanket)

    def _add_tree(self, verts, idxs, tx, tz, scale=1.0):
        """Add a pine tree at world position."""
        ty = height_at(tx, tz)
        if ty < -0.1:  # Skip if underwater
            return
        if ty >= 15.0:  # Skip if on white/snowy mountain soil
            return
        trunk_h = 0.6 * scale
        trunk_c = [0.12, 0.07, 0.03]
        self._add_box(verts, idxs, tx, ty + trunk_h, tz,
                      0.08 * scale, trunk_h, 0.08 * scale, trunk_c)
        for layer in range(3):
            ly = ty + trunk_h * 1.5 + layer * 0.55 * scale
            s = (0.7 - layer * 0.15) * scale
            lc = [0.04 + layer * 0.01, 0.12 + layer * 0.02, 0.03]
            b = len(verts) // 9
            verts.extend([
                tx - s, ly, tz - s, 0, -1, 0, *lc,
                tx + s, ly, tz - s, 0, -1, 0, *lc,
                tx + s, ly, tz + s, 0, -1, 0, *lc,
                tx - s, ly, tz + s, 0, -1, 0, *lc,
                tx, ly + 0.8 * scale, tz, 0, 1, 0, *lc,
            ])
            idxs.extend([b, b+1, b+4, b+1, b+2, b+4,
                         b+2, b+3, b+4, b+3, b, b+4])

    def _add_tent(self, verts, idxs, px, py, pz, rotation, tent_color, side_color, floor_color):
        """Add a single A-frame tent at the given position."""
        cr, sr = math.cos(rotation), math.sin(rotation)

        def rot(x, z):
            return x * cr - z * sr, x * sr + z * cr

        def av(lx, ly, lz, nx, ny, nz, r, g, b):
            rx, rz = rot(lx, lz)
            rnx, rnz = rot(nx, nz)
            verts.extend([px + rx, py + ly, pz + rz, rnx, ny, rnz, r, g, b])

        tw, th, td = 0.9, 1.1, 1.3

        # Front face
        b = len(verts) // 9
        av(-tw, 0, td, 0, 0, 1, *tent_color)
        av( tw, 0, td, 0, 0, 1, *tent_color)
        av(  0, th, td, 0, 0, 1, *tent_color)
        idxs.extend([b, b+1, b+2])

        # Back face
        b = len(verts) // 9
        av( tw, 0, -td, 0, 0, -1, *tent_color)
        av(-tw, 0, -td, 0, 0, -1, *tent_color)
        av(  0, th, -td, 0, 0, -1, *tent_color)
        idxs.extend([b, b+1, b+2])

        # Side panels
        nl = math.sqrt(th * th + tw * tw)
        for side in [-1, 1]:
            b = len(verts) // 9
            av(side*tw, 0,  td, side*th/nl, tw/nl, 0, *side_color)
            av(       0, th, td, side*th/nl, tw/nl, 0, *side_color)
            av(side*tw, 0, -td, side*th/nl, tw/nl, 0, *side_color)
            av(       0, th, -td, side*th/nl, tw/nl, 0, *side_color)
            if side == -1:
                idxs.extend([b, b+1, b+2, b+1, b+3, b+2])
            else:
                idxs.extend([b, b+2, b+1, b+1, b+2, b+3])

        # Floor
        b = len(verts) // 9
        av(-tw, 0.01,  td, 0, 1, 0, *floor_color)
        av( tw, 0.01,  td, 0, 1, 0, *floor_color)
        av( tw, 0.01, -td, 0, 1, 0, *floor_color)
        av(-tw, 0.01, -td, 0, 1, 0, *floor_color)
        idxs.extend([b, b+1, b+2, b, b+2, b+3])

    def _add_small_campsite(self, verts, idxs, center_x, center_z, colors, scale=1.0):
        """Add a quiet secondary campsite to make the lakeside feel inhabited."""
        fire_x, fire_z = center_x, center_z
        offsets = [(-3.7 * scale, 0.55 * scale), (3.5 * scale, 0.35 * scale)]

        for i, (ox, oz) in enumerate(offsets):
            tx = fire_x + ox
            tz = fire_z + oz
            ty = height_at(tx, tz)
            rot = self._look_rotation(tx, tz, fire_x, fire_z)
            tent_color, side_color = colors[i]
            floor_color = [0.07, 0.07, 0.06]
            self._add_tent(verts, idxs, tx, ty, tz, rot,
                           tent_color=tent_color,
                           side_color=side_color,
                           floor_color=floor_color)

        chair_x, chair_z = fire_x, fire_z - 2.4 * scale
        chair_rot = self._look_rotation(chair_x, chair_z, fire_x, fire_z) + math.pi
        self._add_simple_chair(verts, idxs, chair_x, chair_z, chair_rot, [0.16, 0.18, 0.28])

        mat_x, mat_z = fire_x - 0.4 * scale, fire_z + 2.8 * scale
        mat_y = height_at(mat_x, mat_z)
        mat_rot = self._look_rotation(mat_x, mat_z, fire_x, fire_z)
        self._add_rotated_box(verts, idxs, mat_x, mat_y + 0.04, mat_z,
                              0.42 * scale, 0.025, 0.85 * scale,
                              mat_rot, [0.34, 0.18, 0.12])

        lantern_x, lantern_z = fire_x - 2.4 * scale, fire_z - 1.7 * scale
        lantern_y = height_at(lantern_x, lantern_z)
        self._add_box(verts, idxs, lantern_x, lantern_y + 0.10, lantern_z,
                      0.04, 0.10, 0.04, [0.18, 0.18, 0.18])
        self._add_box(verts, idxs, lantern_x, lantern_y + 0.13, lantern_z,
                      0.035, 0.07, 0.035, [0.75, 0.62, 0.20])

        cooler_x, cooler_z = fire_x + 2.7 * scale, fire_z - 1.8 * scale
        cooler_y = height_at(cooler_x, cooler_z)
        cooler_rot = self._look_rotation(cooler_x, cooler_z, fire_x, fire_z)
        self._add_rotated_box(verts, idxs, cooler_x, cooler_y + 0.18, cooler_z,
                              0.34 * scale, 0.18, 0.22 * scale,
                              cooler_rot, [0.62, 0.65, 0.62])

    def _generate(self):
        verts = []
        idxs = []

        # =========================================================
        # === 3 TENTS around the campfire ===
        # Campfire is at approximately (CAMP_X - 2.0, _, CAMP_Z + 1.5)
        # =========================================================
        fire_x = CAMP_X - 2.0
        fire_z = CAMP_Z + 1.5
        CLEAR_RADIUS = 6.0  # No trees within this radius of camp

        # --- Tent 1: Olive Green — left side of campfire ---
        t1x = fire_x - 4.5
        t1z = fire_z + 0.5
        t1y = height_at(t1x, t1z)
        # Face toward the fire
        t1_rot = math.atan2(fire_x - t1x, fire_z - t1z)
        self._add_tent(verts, idxs, t1x, t1y, t1z, t1_rot,
                       tent_color=[0.26, 0.30, 0.14],
                       side_color=[0.28, 0.32, 0.15],
                       floor_color=[0.08, 0.08, 0.06])

        # --- Tent 2: Navy Blue — right side of campfire ---
        t2x = fire_x + 4.5
        t2z = fire_z + 0.0
        t2y = height_at(t2x, t2z)
        t2_rot = math.atan2(fire_x - t2x, fire_z - t2z)
        self._add_tent(verts, idxs, t2x, t2y, t2z, t2_rot,
                       tent_color=[0.08, 0.12, 0.30],
                       side_color=[0.09, 0.13, 0.32],
                       floor_color=[0.06, 0.07, 0.10])

        # --- Tent 3: Khaki Brown — slightly behind campfire ---
        t3x = fire_x + 0.5
        t3z = fire_z + 5.5
        t3y = height_at(t3x, t3z)
        t3_rot = math.atan2(fire_x - t3x, fire_z - t3z)
        self._add_tent(verts, idxs, t3x, t3y, t3z, t3_rot,
                       tent_color=[0.40, 0.33, 0.18],
                       side_color=[0.42, 0.35, 0.19],
                       floor_color=[0.08, 0.07, 0.05])

        # === Chairs and small camping interior ===
        chair_specs = [
            (fire_x - 2.10, fire_z - 1.15, [0.13, 0.20, 0.36]),
            (fire_x + 2.10, fire_z - 1.05, [0.34, 0.12, 0.08]),
            (fire_x + 0.35, fire_z + 2.25, [0.22, 0.28, 0.14]),
        ]
        for cpx, cpz, color in chair_specs:
            crot = self._look_rotation(cpx, cpz, fire_x, fire_z) + math.pi
            self._add_simple_chair(verts, idxs, cpx, cpz, crot, color)

        self._add_camping_props(verts, idxs, fire_x, fire_z)

        # === Lantern ===
        lx, lz = CAMP_X - 1.5, CAMP_Z - 0.5
        ly = height_at(lx, lz)
        self._add_box(verts, idxs, lx, ly+0.12, lz, 0.05, 0.12, 0.05, [0.2, 0.2, 0.2])
        self._add_box(verts, idxs, lx, ly+0.15, lz, 0.04, 0.08, 0.04, [0.8, 0.7, 0.2])

        # === Secondary campsites so the lakeside feels less empty ===
        campsite_centers = [
            (CAMP_X - 18.0, CAMP_Z + 9.0, 5.5),
            (CAMP_X + 17.0, CAMP_Z + 8.0, 5.5),
        ]
        self._add_small_campsite(
            verts, idxs,
            center_x=campsite_centers[0][0],
            center_z=campsite_centers[0][1],
            colors=[
                ([0.36, 0.22, 0.10], [0.42, 0.27, 0.12]),
                ([0.12, 0.25, 0.22], [0.14, 0.30, 0.25]),
            ],
            scale=0.95
        )
        self._add_small_campsite(
            verts, idxs,
            center_x=campsite_centers[1][0],
            center_z=campsite_centers[1][1],
            colors=[
                ([0.32, 0.16, 0.20], [0.38, 0.20, 0.24]),
                ([0.20, 0.24, 0.36], [0.24, 0.28, 0.42]),
            ],
            scale=0.9
        )

        # =========================================================
        # === FOREST TREES ===
        # =========================================================
        random.seed(42)
        tree_count = 0

        def is_near_camp(tx, tz):
            """Return True if too close to camp tents or fire — keep open space."""
            if abs(tx - fire_x) < CLEAR_RADIUS and abs(tz - fire_z) < CLEAR_RADIUS:
                return True
            for cx, cz, radius in campsite_centers:
                if abs(tx - cx) < radius and abs(tz - cz) < radius:
                    return True
            return False

        # --- Scattered trees near camp but not blocking it ---
        for _ in range(40):
            tx = CAMP_X + random.uniform(-25, 25)
            tz = CAMP_Z + random.uniform(-8, 30)
            if is_near_camp(tx, tz):
                continue
            if lake_distance(tx, tz) < 0.8:
                continue
            self._add_tree(verts, idxs, tx, tz, random.uniform(0.8, 1.5))
            tree_count += 1

        # --- Dense background forest (far behind campsite, away from lake) ---
        for _ in range(120):
            tx = CAMP_X + random.uniform(-60, 60)
            tz = CAMP_Z + random.uniform(20, 100)  # Far south/behind camp
            if is_near_camp(tx, tz):
                continue
            if lake_distance(tx, tz) < 0.5:
                continue
            if abs(tx) > 185 or abs(tz) > 185:
                continue
            scale = random.uniform(1.0, 2.5)  # Taller background trees
            self._add_tree(verts, idxs, tx, tz, scale)
            tree_count += 1

        # --- East and west flanking forest ---
        for _ in range(80):
            side = random.choice([-1, 1])
            tx = CAMP_X + side * random.uniform(15, 70)
            tz = CAMP_Z + random.uniform(-20, 60)
            if is_near_camp(tx, tz):
                continue
            if lake_distance(tx, tz) < 0.6:
                continue
            if abs(tx) > 185 or abs(tz) > 185:
                continue
            self._add_tree(verts, idxs, tx, tz, random.uniform(0.9, 2.0))
            tree_count += 1

        # --- Trees along lakeshore (all around the lake) ---
        for angle_deg in range(0, 360, 5):
            angle = math.radians(angle_deg)
            for ring in range(4):
                base_r = 1.05 + ring * 0.18
                tx = LAKE_SEMI_MAJOR * base_r * math.cos(angle) + random.uniform(-3, 3)
                tz = LAKE_SEMI_MINOR * base_r * math.sin(angle) + random.uniform(-3, 3)
                if is_near_camp(tx, tz):
                    continue
                if lake_distance(tx, tz) < 0.3:
                    continue
                if abs(tx) > 185 or abs(tz) > 185:
                    continue
                self._add_tree(verts, idxs, tx, tz, random.uniform(0.6, 2.0))
                tree_count += 1

        print(f"  Trees placed: {tree_count}")

        vertices = np.array(verts, dtype=np.float32)
        indices_arr = np.array(idxs, dtype=np.uint32)
        self.index_count = len(indices_arr)

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices_arr.nbytes, indices_arr, GL_STATIC_DRAW)
        stride = 9 * 4
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))
        glEnableVertexAttribArray(2)
        glBindVertexArray(0)

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, self.index_count, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    def destroy(self):
        glDeleteVertexArrays(1, [self.vao])
        glDeleteBuffers(1, [self.vbo])
        glDeleteBuffers(1, [self.ebo])
