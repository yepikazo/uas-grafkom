"""
Tent and camping accessories.
"""
import numpy as np
import math
from OpenGL.GL import *


class Tent:
    """A-frame camping tent with chair and lantern."""

    def __init__(self, position=(5.5, 0.3, 1.5), rotation=math.pi * 0.75):
        self.position = position
        self.rotation = rotation
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

    def _generate(self):
        verts = []
        idxs = []
        px, py, pz = self.position
        cr, sr = math.cos(self.rotation), math.sin(self.rotation)

        def rot(x, z):
            return x*cr - z*sr, x*sr + z*cr

        def av(lx, ly, lz, nx, ny, nz, r, g, b):
            rx, rz = rot(lx, lz)
            rnx, rnz = rot(nx, nz)
            verts.extend([px+rx, py+ly, pz+rz, rnx, ny, rnz, r, g, b])

        tw, th, td = 0.9, 1.1, 1.3
        tc = [0.2, 0.25, 0.12]

        # Front triangle
        b = len(verts)//9
        av(-tw,0,td, 0,0,1, *tc); av(tw,0,td, 0,0,1, *tc); av(0,th,td, 0,0,1, *tc)
        idxs.extend([b, b+1, b+2])

        # Back triangle
        b = len(verts)//9
        av(tw,0,-td, 0,0,-1, *tc); av(-tw,0,-td, 0,0,-1, *tc); av(0,th,-td, 0,0,-1, *tc)
        idxs.extend([b, b+1, b+2])

        # Left slope
        nl = math.sqrt(th*th + tw*tw)
        b = len(verts)//9
        ts = [0.22, 0.27, 0.13]
        av(-tw,0,td, -th/nl,tw/nl,0, *ts); av(0,th,td, -th/nl,tw/nl,0, *ts)
        av(-tw,0,-td, -th/nl,tw/nl,0, *ts); av(0,th,-td, -th/nl,tw/nl,0, *ts)
        idxs.extend([b,b+1,b+2, b+1,b+3,b+2])

        # Right slope
        b = len(verts)//9
        av(tw,0,td, th/nl,tw/nl,0, *ts); av(0,th,td, th/nl,tw/nl,0, *ts)
        av(tw,0,-td, th/nl,tw/nl,0, *ts); av(0,th,-td, th/nl,tw/nl,0, *ts)
        idxs.extend([b,b+2,b+1, b+1,b+2,b+3])

        # Floor
        b = len(verts)//9
        fc = [0.08, 0.08, 0.06]
        av(-tw,0.01,td, 0,1,0, *fc); av(tw,0.01,td, 0,1,0, *fc)
        av(tw,0.01,-td, 0,1,0, *fc); av(-tw,0.01,-td, 0,1,0, *fc)
        idxs.extend([b,b+1,b+2, b,b+2,b+3])

        # Chair near fire
        cc = [0.15, 0.2, 0.35]
        cpx, cpz = 3.2, 4.0
        # Seat
        b = len(verts)//9
        sw, sh, sd = 0.3, 0.35, 0.3
        verts.extend([cpx-sw,py+sh,cpz-sd, 0,1,0, *cc,
                      cpx+sw,py+sh,cpz-sd, 0,1,0, *cc,
                      cpx+sw,py+sh,cpz+sd, 0,1,0, *cc,
                      cpx-sw,py+sh,cpz+sd, 0,1,0, *cc])
        idxs.extend([b,b+1,b+2, b,b+2,b+3])
        # Back
        b = len(verts)//9
        verts.extend([cpx-sw,py+sh,cpz-sd, 0,0,-1, *cc,
                      cpx+sw,py+sh,cpz-sd, 0,0,-1, *cc,
                      cpx+sw,py+sh+0.45,cpz-sd, 0,0,-1, *cc,
                      cpx-sw,py+sh+0.45,cpz-sd, 0,0,-1, *cc])
        idxs.extend([b,b+1,b+2, b,b+2,b+3])
        # Legs
        fc2 = [0.25, 0.25, 0.25]
        for dx in [-sw+0.05, sw-0.05]:
            for dz in [-sd+0.05, sd-0.05]:
                self._add_box(verts, idxs, cpx+dx, py+sh/2, cpz+dz, 0.015, sh/2, 0.015, fc2)

        # Lantern
        self._add_box(verts, idxs, 5.0, py+0.12, 3.0, 0.05, 0.12, 0.05, [0.2,0.2,0.2])
        self._add_box(verts, idxs, 5.0, py+0.15, 3.0, 0.04, 0.08, 0.04, [0.8,0.7,0.2])

        # Trees (simple cone + cylinder trunks)
        tree_positions = [(-6,0,-5), (-8,0,-3), (-7,0,2), (7,0,-6), (8,0,-4), (-5,0,7), (9,0,3)]
        for tx, _, tz in tree_positions:
            th2 = self._get_ground_y(tx, tz)
            trunk_c = [0.12, 0.07, 0.03]
            self._add_box(verts, idxs, tx, th2+0.5, tz, 0.1, 0.5, 0.1, trunk_c)
            # Foliage layers (stacked cones approximated as pyramids)
            for layer in range(3):
                ly = th2 + 0.8 + layer * 0.6
                s = 0.7 - layer * 0.15
                leaf_c = [0.04+layer*0.01, 0.12+layer*0.02, 0.03]
                b = len(verts)//9
                verts.extend([
                    tx-s, ly, tz-s, 0,-1,0, *leaf_c,
                    tx+s, ly, tz-s, 0,-1,0, *leaf_c,
                    tx+s, ly, tz+s, 0,-1,0, *leaf_c,
                    tx-s, ly, tz+s, 0,-1,0, *leaf_c,
                    tx, ly+0.8, tz, 0,1,0, *leaf_c,
                ])
                idxs.extend([b,b+1,b+4, b+1,b+2,b+4, b+2,b+3,b+4, b+3,b,b+4])

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

    def _get_ground_y(self, x, z):
        dist = math.sqrt(x*x + z*z)
        if dist < 3.5: return -0.05
        shore = min(max(0.0, (dist-3.5)/2.0), 1.0)
        h = shore * 0.3
        r1 = math.sin(x*0.3+1)*math.cos(z*0.2+0.5)
        r2 = math.sin(x*0.5+z*0.3)*0.6
        r3 = math.sin(x*0.15-0.7)*math.cos(z*0.15+0.3)*1.5
        n1 = math.sin(x*1.2+z*0.8)*0.15
        n2 = math.cos(x*0.9-z*1.1)*0.1
        m = (r1+r2+r3+n1+n2)
        ms = min(max(0.0,(dist-5.0)/8.0),1.0)
        m *= ms * 3.5
        er = min(max(0.0,(dist-10.0)/5.0),1.0)
        h += er*2.0 + max(0.0, m)
        return h

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, self.index_count, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    def destroy(self):
        glDeleteVertexArrays(1, [self.vao])
        glDeleteBuffers(1, [self.vbo])
        glDeleteBuffers(1, [self.ebo])
