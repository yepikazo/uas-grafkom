"""
Shader compilation and program management for OpenGL.
"""
import os
from OpenGL.GL import *


class Shader:
    """Compiles vertex and fragment shaders, links them into a program."""

    def __init__(self, vertex_path, fragment_path):
        self.program = glCreateProgram()

        vertex_src = self._load_source(vertex_path)
        fragment_src = self._load_source(fragment_path)

        vs = self._compile(vertex_src, GL_VERTEX_SHADER)
        fs = self._compile(fragment_src, GL_FRAGMENT_SHADER)

        glAttachShader(self.program, vs)
        glAttachShader(self.program, fs)
        glLinkProgram(self.program)

        # Check link status
        if not glGetProgramiv(self.program, GL_LINK_STATUS):
            info = glGetProgramInfoLog(self.program).decode()
            raise RuntimeError(f"Shader link error:\n{info}")

        glDeleteShader(vs)
        glDeleteShader(fs)

    def _load_source(self, path):
        with open(path, 'r') as f:
            return f.read()

    def _compile(self, source, shader_type):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            info = glGetShaderInfoLog(shader).decode()
            raise RuntimeError(f"Shader compile error:\n{info}")
        return shader

    def use(self):
        glUseProgram(self.program)

    def set_float(self, name, value):
        loc = glGetUniformLocation(self.program, name)
        glUniform1f(loc, value)

    def set_int(self, name, value):
        loc = glGetUniformLocation(self.program, name)
        glUniform1i(loc, value)

    def set_vec3(self, name, x, y, z):
        loc = glGetUniformLocation(self.program, name)
        glUniform3f(loc, x, y, z)

    def set_vec4(self, name, x, y, z, w):
        loc = glGetUniformLocation(self.program, name)
        glUniform4f(loc, x, y, z, w)

    def set_mat4(self, name, matrix):
        loc = glGetUniformLocation(self.program, name)
        glUniformMatrix4fv(loc, 1, GL_FALSE, matrix)

    def destroy(self):
        glDeleteProgram(self.program)
