"""
Animated lake surface with wave displacement.
"""
import numpy as np
import math
from OpenGL.GL import *


class Lake:
    """Circular lake mesh rendered with transparency and wave animation."""

    def __init__(self, radius=3.5, segments=80):
        self.vao = None
        self.vbo = None
        self.ebo = None
        self.index_count = 0
        self._generate(radius, segments)

    def _generate(self, radius, segments):
        """Generate a circular disc mesh for the lake surface."""
        vertices = []
        indices = []

        # Center vertex
        vertices.extend([0.0, 0.0, 0.0,  # position
                         0.0, 1.0, 0.0,   # normal
                         0.5, 0.5])        # texcoord

        # Ring vertices
        for ring in range(1, segments + 1):
            r = radius * ring / segments
            num_verts = max(8, int(ring * 6))
            for i in range(num_verts):
                angle = 2.0 * math.pi * i / num_verts
                x = r * math.cos(angle)
                z = r * math.sin(angle)

                u = 0.5 + 0.5 * x / radius
                v = 0.5 + 0.5 * z / radius

                vertices.extend([x, 0.0, z,
                                 0.0, 1.0, 0.0,
                                 u, v])

        vertices = np.array(vertices, dtype=np.float32)

        # Generate indices (triangle fan from center, then rings)
        # Simple approach: create a flat disc with triangle fan
        # Re-generate with simpler grid approach
        vertices2 = []
        indices2 = []

        res = segments
        for iz in range(res + 1):
            for ix in range(res + 1):
                x = -radius + 2.0 * radius * ix / res
                z = -radius + 2.0 * radius * iz / res

                # Clip to circle
                dist = math.sqrt(x * x + z * z)
                if dist > radius:
                    scale = radius / dist
                    x *= scale
                    z *= scale

                u = 0.5 + 0.5 * x / radius
                v = 0.5 + 0.5 * z / radius

                vertices2.extend([x, 0.0, z,
                                  0.0, 1.0, 0.0,
                                  u, v])

        for iz in range(res):
            for ix in range(res):
                tl = iz * (res + 1) + ix
                tr = tl + 1
                bl = (iz + 1) * (res + 1) + ix
                br = bl + 1

                # Only add triangles inside the circle
                indices2.extend([tl, bl, tr])
                indices2.extend([tr, bl, br])

        vertices2 = np.array(vertices2, dtype=np.float32)
        indices2 = np.array(indices2, dtype=np.uint32)
        self.index_count = len(indices2)

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)

        glBindVertexArray(self.vao)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices2.nbytes, vertices2, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices2.nbytes, indices2, GL_STATIC_DRAW)

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
