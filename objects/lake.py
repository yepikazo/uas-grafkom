"""
Animated lake surface shaped like Lake Motosu — large scale.
"""
import numpy as np
import math
from OpenGL.GL import *
from core.terrain_height import (lake_distance, LAKE_WATER_LEVEL,
                                  LAKE_CENTER_X, LAKE_CENTER_Z,
                                  LAKE_SEMI_MAJOR, LAKE_SEMI_MINOR)


class Lake:
    """Lake Motosu-shaped water mesh with wave animation."""

    def __init__(self):
        self.vao = None
        self.vbo = None
        self.ebo = None
        self.index_count = 0
        self._generate()

    def _generate(self):
        """Generate lake mesh covering the large organic Motosu shape."""
        # Bounding box with margin
        x_min = LAKE_CENTER_X - LAKE_SEMI_MAJOR - 5
        x_max = LAKE_CENTER_X + LAKE_SEMI_MAJOR + 5
        z_min = LAKE_CENTER_Z - LAKE_SEMI_MINOR - 5
        z_max = LAKE_CENTER_Z + LAKE_SEMI_MINOR + 5

        # Higher resolution for larger lake
        res_x = 200
        res_z = 100
        dx = (x_max - x_min) / res_x
        dz = (z_max - z_min) / res_z

        grid = {}
        vertices = []
        vert_count = 0

        for iz in range(res_z + 1):
            for ix in range(res_x + 1):
                x = x_min + dx * ix
                z = z_min + dz * iz
                ld = lake_distance(x, z)

                if ld <= 0.15:
                    grid[(ix, iz)] = vert_count
                    u = ix / res_x
                    v = iz / res_z
                    vertices.extend([x, LAKE_WATER_LEVEL, z,
                                     0.0, 1.0, 0.0, u, v])
                    vert_count += 1

        indices = []
        for iz in range(res_z):
            for ix in range(res_x):
                keys = [(ix, iz), (ix+1, iz), (ix, iz+1), (ix+1, iz+1)]
                if all(k in grid for k in keys):
                    tl, tr = grid[keys[0]], grid[keys[1]]
                    bl, br = grid[keys[2]], grid[keys[3]]
                    indices.extend([tl, bl, tr, tr, bl, br])

        vertices = np.array(vertices, dtype=np.float32)
        indices = np.array(indices, dtype=np.uint32)
        self.index_count = len(indices)

        print(f"  Lake vertices: {vert_count}, triangles: {self.index_count//3}")

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
