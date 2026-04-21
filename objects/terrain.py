"""
Terrain with procedural mountains surrounding a lake basin.
"""
import numpy as np
import math
from OpenGL.GL import *


class Terrain:
    """Generates a terrain mesh with mountains and a lake basin."""

    def __init__(self):
        self.vao = None
        self.vbo = None
        self.ebo = None
        self.index_count = 0
        self._generate()

    def _height_at(self, x, z):
        """Calculate terrain height at a given (x, z) position."""
        # Distance from center (lake area)
        dist = math.sqrt(x * x + z * z)

        # Lake basin - flat and low in center
        if dist < 3.5:
            return -0.05

        # Shore transition
        shore = max(0.0, (dist - 3.5) / 2.0)
        shore = min(shore, 1.0)

        # Base terrain elevation
        height = shore * 0.3

        # Mountain ridges using layered sine waves
        # Main mountain range (background)
        ridge1 = math.sin(x * 0.3 + 1.0) * math.cos(z * 0.2 + 0.5)
        ridge2 = math.sin(x * 0.5 + z * 0.3) * 0.6
        ridge3 = math.sin(x * 0.15 - 0.7) * math.cos(z * 0.15 + 0.3) * 1.5

        # Noise for detail
        noise1 = math.sin(x * 1.2 + z * 0.8) * 0.15
        noise2 = math.cos(x * 0.9 - z * 1.1) * 0.1
        noise3 = math.sin(x * 2.1 + z * 1.7) * 0.05

        mountain = (ridge1 + ridge2 + ridge3 + noise1 + noise2 + noise3)

        # Scale mountains by distance from center (taller further away)
        mountain_scale = max(0.0, (dist - 5.0) / 8.0)
        mountain_scale = min(mountain_scale, 1.0)
        mountain *= mountain_scale * 3.5

        # Ensure mountains rise at edges
        edge_rise = max(0.0, (dist - 10.0) / 5.0)
        edge_rise = min(edge_rise, 1.0)
        height += edge_rise * 2.0

        height += max(0.0, mountain)

        return height

    def _generate(self):
        """Generate terrain mesh."""
        size = 30.0
        resolution = 120
        half = size / 2.0
        step = size / resolution

        vertices = []
        indices = []

        for iz in range(resolution + 1):
            for ix in range(resolution + 1):
                x = -half + ix * step
                z = -half + iz * step
                y = self._height_at(x, z)

                # Calculate normal using finite differences
                hL = self._height_at(x - step, z)
                hR = self._height_at(x + step, z)
                hD = self._height_at(x, z - step)
                hU = self._height_at(x, z + step)

                nx = hL - hR
                ny = 2.0 * step
                nz = hD - hU
                length = math.sqrt(nx * nx + ny * ny + nz * nz)
                if length > 0:
                    nx /= length
                    ny /= length
                    nz /= length

                # Texture coordinates
                u = ix / resolution
                v = iz / resolution

                vertices.extend([x, y, z, nx, ny, nz, u, v])

        for iz in range(resolution):
            for ix in range(resolution):
                top_left = iz * (resolution + 1) + ix
                top_right = top_left + 1
                bottom_left = (iz + 1) * (resolution + 1) + ix
                bottom_right = bottom_left + 1

                indices.extend([top_left, bottom_left, top_right])
                indices.extend([top_right, bottom_left, bottom_right])

        vertices = np.array(vertices, dtype=np.float32)
        indices = np.array(indices, dtype=np.uint32)
        self.index_count = len(indices)

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)

        glBindVertexArray(self.vao)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        stride = 8 * 4  # 8 floats * 4 bytes
        # Position
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        # Normal
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)
        # TexCoord
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
