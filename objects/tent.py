"""
Tent, camping accessories, and scattered trees around Lake Motosu.
"""
import numpy as np
import math
import random
from OpenGL.GL import *
from core.terrain_height import height_at, lake_distance, CAMP_X, CAMP_Z
from core.terrain_height import LAKE_SEMI_MAJOR, LAKE_SEMI_MINOR


class Tent:
    """A-frame camping tent with chair, lantern, and forest trees."""

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

    def _add_tree(self, verts, idxs, tx, tz, scale=1.0):
        """Add a tree at world position."""
        ty = height_at(tx, tz)
        if ty < -0.1:  # Skip if underwater
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

    def _generate(self):
        verts = []
        idxs = []
        px, py, pz = self.position
        cr, sr = math.cos(self.rotation), math.sin(self.rotation)

        def rot(x, z):
            return x * cr - z * sr, x * sr + z * cr

        def av(lx, ly, lz, nx, ny, nz, r, g, b):
            rx, rz = rot(lx, lz)
            rnx, rnz = rot(nx, nz)
            verts.extend([px + rx, py + ly, pz + rz, rnx, ny, rnz, r, g, b])

        # === Tent ===
        tw, th, td = 0.9, 1.1, 1.3
        tc = [0.2, 0.25, 0.12]
        b = len(verts) // 9
        av(-tw, 0, td, 0, 0, 1, *tc); av(tw, 0, td, 0, 0, 1, *tc); av(0, th, td, 0, 0, 1, *tc)
        idxs.extend([b, b+1, b+2])
        b = len(verts) // 9
        av(tw, 0, -td, 0, 0, -1, *tc); av(-tw, 0, -td, 0, 0, -1, *tc); av(0, th, -td, 0, 0, -1, *tc)
        idxs.extend([b, b+1, b+2])
        nl = math.sqrt(th * th + tw * tw)
        ts = [0.22, 0.27, 0.13]
        for side in [-1, 1]:
            b = len(verts) // 9
            av(side*tw, 0, td, side*th/nl, tw/nl, 0, *ts)
            av(0, th, td, side*th/nl, tw/nl, 0, *ts)
            av(side*tw, 0, -td, side*th/nl, tw/nl, 0, *ts)
            av(0, th, -td, side*th/nl, tw/nl, 0, *ts)
            if side == -1:
                idxs.extend([b, b+1, b+2, b+1, b+3, b+2])
            else:
                idxs.extend([b, b+2, b+1, b+1, b+2, b+3])
        b = len(verts) // 9
        fc = [0.08, 0.08, 0.06]
        av(-tw, 0.01, td, 0, 1, 0, *fc); av(tw, 0.01, td, 0, 1, 0, *fc)
        av(tw, 0.01, -td, 0, 1, 0, *fc); av(-tw, 0.01, -td, 0, 1, 0, *fc)
        idxs.extend([b, b+1, b+2, b, b+2, b+3])

        # === Chair ===
        cc = [0.15, 0.2, 0.35]
        cpx, cpz = CAMP_X + 3.0, CAMP_Z - 2.0  # North side of camp (toward lake)
        cpy = height_at(cpx, cpz)
        sw, sh, sd = 0.3, 0.35, 0.3
        b = len(verts) // 9
        verts.extend([cpx-sw, cpy+sh, cpz-sd, 0,1,0, *cc,
                      cpx+sw, cpy+sh, cpz-sd, 0,1,0, *cc,
                      cpx+sw, cpy+sh, cpz+sd, 0,1,0, *cc,
                      cpx-sw, cpy+sh, cpz+sd, 0,1,0, *cc])
        idxs.extend([b, b+1, b+2, b, b+2, b+3])
        b = len(verts) // 9
        verts.extend([cpx-sw, cpy+sh, cpz+sd, 0,0,1, *cc,
                      cpx+sw, cpy+sh, cpz+sd, 0,0,1, *cc,
                      cpx+sw, cpy+sh+0.45, cpz+sd, 0,0,1, *cc,
                      cpx-sw, cpy+sh+0.45, cpz+sd, 0,0,1, *cc])
        idxs.extend([b, b+1, b+2, b, b+2, b+3])
        fc2 = [0.25, 0.25, 0.25]
        for dx in [-sw+0.05, sw-0.05]:
            for dz in [-sd+0.05, sd-0.05]:
                self._add_box(verts, idxs, cpx+dx, cpy+sh/2, cpz+dz, 0.015, sh/2, 0.015, fc2)

        # === Lantern ===
        lx, lz = CAMP_X - 1.5, CAMP_Z - 0.5
        ly = height_at(lx, lz)
        self._add_box(verts, idxs, lx, ly+0.12, lz, 0.05, 0.12, 0.05, [0.2,0.2,0.2])
        self._add_box(verts, idxs, lx, ly+0.15, lz, 0.04, 0.08, 0.04, [0.8,0.7,0.2])

        # === Forest Trees ===
        random.seed(42)
        tree_count = 0

        # Trees near camp area
        for _ in range(30):
            tx = CAMP_X + random.uniform(-20, 20)
            tz = CAMP_Z + random.uniform(-10, 25)
            if abs(tx - CAMP_X) < 4 and abs(tz - CAMP_Z) < 4:
                continue
            if lake_distance(tx, tz) < 0.8:
                continue
            self._add_tree(verts, idxs, tx, tz, random.uniform(0.8, 1.5))
            tree_count += 1

        # Trees scattered along lakeshore (all around the lake)
        for angle_deg in range(0, 360, 6):
            angle = math.radians(angle_deg)
            for ring in range(3):
                base_r = 1.05 + ring * 0.15
                tx = LAKE_SEMI_MAJOR * base_r * math.cos(angle) + random.uniform(-3, 3)
                tz = LAKE_SEMI_MINOR * base_r * math.sin(angle) + random.uniform(-3, 3)
                if lake_distance(tx, tz) < 0.3:
                    continue
                if abs(tx) > 185 or abs(tz) > 185:
                    continue
                self._add_tree(verts, idxs, tx, tz, random.uniform(0.6, 1.8))
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
