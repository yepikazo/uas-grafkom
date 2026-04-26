"""
Terrain with procedural mountains surrounding Lake Motosu.
"""
import numpy as np
import math
from OpenGL.GL import *
from core.terrain_height import height_at


class Terrain:
    """Generates a large terrain mesh with Lake Motosu basin and surrounding hills."""

    def __init__(self):
        self.vao = None
        self.vbo = None
        self.ebo = None
        self.index_count = 0
        self._generate()

    def _generate(self):
        """Generate terrain mesh covering 400x400 unit area."""
        size = 400.0
        resolution = 200
        half = size / 2.0
        step = size / resolution

        print(f"  Grid: {resolution}x{resolution}, step={step:.1f}")

        vertices = []
        indices = []

        for iz in range(resolution + 1):
            for ix in range(resolution + 1):
                x = -half + ix * step
                z = -half + iz * step
                y = height_at(x, z)

                # Normal via finite differences
                hL = height_at(x - step, z)
                hR = height_at(x + step, z)
                hD = height_at(x, z - step)
                hU = height_at(x, z + step)

                nx = hL - hR
                ny = 2.0 * step
                nz = hD - hU
                length = math.sqrt(nx * nx + ny * ny + nz * nz)
                if length > 0:
                    nx /= length
                    ny /= length
                    nz /= length

                u = ix / resolution
                v = iz / resolution
                vertices.extend([x, y, z, nx, ny, nz, u, v])

        for iz in range(resolution):
            for ix in range(resolution):
                tl = iz * (resolution + 1) + ix
                tr = tl + 1
                bl = (iz + 1) * (resolution + 1) + ix
                br = bl + 1
                indices.extend([tl, bl, tr, tr, bl, br])

        vertices = np.array(vertices, dtype=np.float32)
        indices = np.array(indices, dtype=np.uint32)
        self.index_count = len(indices)

        print(f"  Vertices: {len(vertices)//8}, Triangles: {self.index_count//3}")

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        stride = 8 * 4
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))
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
