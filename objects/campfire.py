"""
Campfire with particle system for flames and embers.
"""
import numpy as np
import math
import random
from OpenGL.GL import *


class Campfire:
    """Particle-based campfire with logs, flames, and ember particles."""

    def __init__(self, position=(4.0, 0.3, 3.0)):
        self.position = position
        self.max_particles = 400
        self.particles = []
        self.log_vao = None
        self.log_vbo = None
        self.log_ebo = None
        self.log_index_count = 0
        self.particle_vao = None
        self.particle_vbo = None

        self._init_particles()
        self._generate_logs()
        self._setup_particle_buffer()

    def _init_particles(self):
        """Initialize particle pool."""
        for _ in range(self.max_particles):
            self.particles.append(self._new_particle())

    def _new_particle(self):
        """Create a new fire/ember particle."""
        px, py, pz = self.position

        # Random spread from fire center
        spread = 0.3
        x = px + random.uniform(-spread, spread)
        z = pz + random.uniform(-spread, spread)
        y = py + random.uniform(0.0, 0.1)

        # Velocity - mostly upward with some spread
        vx = random.uniform(-0.1, 0.1)
        vy = random.uniform(0.5, 2.0)
        vz = random.uniform(-0.1, 0.1)

        # Life
        life = random.uniform(0.5, 1.0)
        max_life = life

        # Color based on particle type
        r = random.random()
        if r < 0.4:
            # Bright flame core
            color = [1.0, 0.8, 0.2]
        elif r < 0.7:
            # Orange flame
            color = [1.0, 0.4, 0.05]
        elif r < 0.9:
            # Red-orange
            color = [0.9, 0.2, 0.02]
        else:
            # Ember/spark
            color = [1.0, 0.6, 0.1]
            vy = random.uniform(1.5, 3.0)
            vx = random.uniform(-0.4, 0.4)
            vz = random.uniform(-0.4, 0.4)

        return {
            'pos': [x, y, z],
            'vel': [vx, vy, vz],
            'color': color,
            'life': life,
            'max_life': max_life
        }

    def _generate_logs(self):
        """Generate log geometry for the campfire base."""
        vertices = []
        indices = []

        px, py, pz = self.position

        def add_cylinder(cx, cy, cz, radius, length, angle_y, segments=8):
            """Add a cylinder (log) at the given position and rotation."""
            cos_a = math.cos(angle_y)
            sin_a = math.sin(angle_y)
            base_idx = len(vertices) // 9  # 9 floats per vertex (pos + normal + color)

            # Log color (dark brown)
            color = [0.15, 0.08, 0.03]

            for end in range(2):
                offset = -length / 2 + end * length
                for i in range(segments):
                    theta = 2.0 * math.pi * i / segments
                    # Local coordinates
                    lx = offset
                    ly = radius * math.cos(theta)
                    lz = radius * math.sin(theta)

                    # Rotate around Y axis
                    wx = cx + lx * cos_a - lz * sin_a
                    wy = cy + ly
                    wz = cz + lx * sin_a + lz * cos_a

                    # Normal
                    nx = 0.0
                    ny = math.cos(theta)
                    nz = math.sin(theta)
                    wnx = nx * cos_a - nz * sin_a
                    wnz = nx * sin_a + nz * cos_a

                    vertices.extend([wx, wy, wz, wnx, ny, wnz, *color])

            # Side indices
            for i in range(segments):
                i0 = base_idx + i
                i1 = base_idx + (i + 1) % segments
                i2 = base_idx + segments + i
                i3 = base_idx + segments + (i + 1) % segments
                indices.extend([i0, i2, i1, i1, i2, i3])

        # Create logs in a teepee/crossed arrangement
        log_radius = 0.06
        log_length = 0.8

        # Log 1 - angled
        add_cylinder(px, py, pz, log_radius, log_length, 0.0)
        # Log 2 - crossed
        add_cylinder(px, py, pz, log_radius, log_length, math.pi / 3)
        # Log 3 - third crossing
        add_cylinder(px, py, pz, log_radius, log_length, 2 * math.pi / 3)
        # Log 4 - slightly raised
        add_cylinder(px, py + 0.08, pz, log_radius * 0.8, log_length * 0.7, math.pi / 6)

        # Stone ring around fire
        stone_color = [0.2, 0.2, 0.18]
        num_stones = 10
        stone_radius = 0.5
        for i in range(num_stones):
            angle = 2.0 * math.pi * i / num_stones
            sx = px + stone_radius * math.cos(angle)
            sz = pz + stone_radius * math.sin(angle)
            sy = py - 0.05

            # Simple cube-ish stone
            s = 0.08 + random.uniform(-0.02, 0.02)
            base_idx = len(vertices) // 9

            # 8 corners of a box
            for dy in [-s, s]:
                for dz2 in [-s, s]:
                    for dx2 in [-s, s]:
                        nx2 = dx2 / abs(dx2) if dx2 != 0 else 0
                        ny2 = dy / abs(dy) if dy != 0 else 0
                        nz2 = dz2 / abs(dz2) if dz2 != 0 else 0
                        ln = math.sqrt(nx2*nx2 + ny2*ny2 + nz2*nz2)
                        if ln > 0:
                            nx2 /= ln; ny2 /= ln; nz2 /= ln
                        sc = [c + random.uniform(-0.03, 0.03) for c in stone_color]
                        vertices.extend([sx + dx2, sy + dy, sz + dz2, nx2, ny2, nz2, *sc])

            # Box faces (6 faces, 2 triangles each)
            # Bottom: 0,1,2,3  Top: 4,5,6,7
            b = base_idx
            indices.extend([
                b+0,b+1,b+3, b+0,b+3,b+2,  # bottom
                b+4,b+7,b+5, b+4,b+6,b+7,  # top
                b+0,b+4,b+1, b+1,b+4,b+5,  # front
                b+2,b+3,b+6, b+3,b+7,b+6,  # back
                b+0,b+2,b+4, b+2,b+6,b+4,  # left
                b+1,b+5,b+3, b+3,b+5,b+7,  # right
            ])

        vertices = np.array(vertices, dtype=np.float32)
        indices = np.array(indices, dtype=np.uint32)
        self.log_index_count = len(indices)

        self.log_vao = glGenVertexArrays(1)
        self.log_vbo = glGenBuffers(1)
        self.log_ebo = glGenBuffers(1)

        glBindVertexArray(self.log_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.log_vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.log_ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        stride = 9 * 4
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))
        glEnableVertexAttribArray(2)

        glBindVertexArray(0)

    def _setup_particle_buffer(self):
        """Setup VBO/VAO for particle rendering."""
        self.particle_vao = glGenVertexArrays(1)
        self.particle_vbo = glGenBuffers(1)

        glBindVertexArray(self.particle_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.particle_vbo)

        # Allocate buffer (pos:3 + color:3 + life:1 = 7 floats per particle)
        max_size = self.max_particles * 7 * 4
        glBufferData(GL_ARRAY_BUFFER, max_size, None, GL_DYNAMIC_DRAW)

        stride = 7 * 4
        # Position
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        # Color
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)
        # Life
        glVertexAttribPointer(2, 1, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))
        glEnableVertexAttribArray(2)

        glBindVertexArray(0)

    def update(self, delta_time):
        """Update all particles."""
        for i, p in enumerate(self.particles):
            p['life'] -= delta_time * 0.8
            if p['life'] <= 0:
                self.particles[i] = self._new_particle()
                continue

            # Update position
            p['pos'][0] += p['vel'][0] * delta_time
            p['pos'][1] += p['vel'][1] * delta_time
            p['pos'][2] += p['vel'][2] * delta_time

            # Slow down horizontal movement
            p['vel'][0] *= 0.98
            p['vel'][2] *= 0.98

            # Slight upward acceleration (hot air)
            p['vel'][1] += 0.5 * delta_time

            # Wind effect
            p['vel'][0] += math.sin(p['pos'][1] * 2.0) * 0.1 * delta_time

    def draw_logs(self):
        """Draw the log geometry."""
        glBindVertexArray(self.log_vao)
        glDrawElements(GL_TRIANGLES, self.log_index_count, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    def draw_particles(self):
        """Upload particle data and draw."""
        data = []
        alive_count = 0
        for p in self.particles:
            if p['life'] > 0:
                life_ratio = p['life'] / p['max_life']
                data.extend(p['pos'])
                data.extend(p['color'])
                data.append(life_ratio)
                alive_count += 1

        if alive_count == 0:
            return

        particle_data = np.array(data, dtype=np.float32)

        glBindVertexArray(self.particle_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.particle_vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, particle_data.nbytes, particle_data)

        glEnable(GL_PROGRAM_POINT_SIZE)
        glDrawArrays(GL_POINTS, 0, alive_count)
        glDisable(GL_PROGRAM_POINT_SIZE)

        glBindVertexArray(0)

    def destroy(self):
        glDeleteVertexArrays(1, [self.log_vao])
        glDeleteBuffers(1, [self.log_vbo])
        glDeleteBuffers(1, [self.log_ebo])
        glDeleteVertexArrays(1, [self.particle_vao])
        glDeleteBuffers(1, [self.particle_vbo])
