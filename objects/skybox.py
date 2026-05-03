"""
Skybox cube for the night sky background.
"""
import numpy as np
from OpenGL.GL import *


class Skybox:
    """A large cube rendered with the sky shader, always surrounding the camera."""

    def __init__(self):
        self.vao = None
        self.vbo = None
        self._generate()

    def _generate(self):
        # Skybox cube vertices (positions only)
        s = 500.0
        vertices = np.array([
            # Back face
            -s, -s, -s,  s, -s, -s,  s,  s, -s,
             s,  s, -s, -s,  s, -s, -s, -s, -s,
            # Front face
            -s, -s,  s,  s,  s,  s,  s, -s,  s,
            -s, -s,  s, -s,  s,  s,  s,  s,  s,
            # Left face
            -s,  s,  s, -s, -s, -s, -s,  s, -s,
            -s,  s,  s, -s, -s,  s, -s, -s, -s,
            # Right face
             s,  s,  s,  s,  s, -s,  s, -s, -s,
             s, -s, -s,  s, -s,  s,  s,  s,  s,
            # Bottom face
            -s, -s, -s, -s, -s,  s,  s, -s,  s,
             s, -s,  s,  s, -s, -s, -s, -s, -s,
            # Top face
            -s,  s, -s,  s,  s,  s, -s,  s,  s,
            -s,  s, -s,  s,  s, -s,  s,  s,  s,
        ], dtype=np.float32)

        self.vertex_count = 36

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glBindVertexArray(0)

    def draw(self):
        glDepthFunc(GL_LEQUAL)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        glBindVertexArray(0)
        glDepthFunc(GL_LESS)

    def destroy(self):
        glDeleteVertexArrays(1, [self.vao])
        glDeleteBuffers(1, [self.vbo])
