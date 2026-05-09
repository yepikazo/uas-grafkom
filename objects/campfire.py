"""Campfire with particle system for flames and embers."""
import numpy as np
import math
import random
from OpenGL.GL import *

_rnd = random.uniform
_PI2 = 2 * math.pi

# Decay & buoyancy tables
_DECAY  = {'core': 1.6, 'flame': 1.1, 'outer': 1.3, 'ember': 0.7, 'smoke': 0.45}
_BUOY   = {'core': 1.2, 'flame': 0.9, 'outer': 0.6, 'ember': 0.3, 'smoke': 0.15}


def _lerp(a, b, t):
    return [a[i] + (b[i] - a[i]) * t for i in range(3)]


class Campfire:
    """Particle-based campfire with logs, flames, and ember particles."""

    def __init__(self, position=(4.0, 0.3, 3.0)):
        self.position = position
        self.max_particles = 600
        self.particles = []
        self.log_vao = self.log_vbo = self.log_ebo = None
        self.log_index_count = 0
        self.particle_vao = self.particle_vbo = None
        self._time = 0.0

        self._init_particles()
        self._generate_logs()
        self._setup_particle_buffer()

    # ------------------------------------------------------------------ spawn

    def _init_particles(self):
        for _ in range(self.max_particles):
            self.particles.append(self._new_particle())

    def _new_particle(self, ptype=None):
        px, py, pz = self.position

        if ptype is None:
            r = random.random()
            if   r < 0.30: ptype = 'core'
            elif r < 0.60: ptype = 'flame'
            elif r < 0.82: ptype = 'outer'
            elif r < 0.93: ptype = 'ember'
            else:          ptype = 'smoke'

        def gs(s):
            """Gaussian-distributed spawn offset."""
            return np.random.normal(0, s * 0.5)

        if ptype == 'core':
            s = 0.10
            x, z = px + gs(s), pz + gs(s)
            y    = py + _rnd(0.0, 0.05)
            vx, vz = _rnd(-0.06, 0.06), _rnd(-0.06, 0.06)
            vy   = _rnd(1.0, 2.2)
            life = _rnd(0.6, 1.0)
            col  = [1.0, _rnd(0.9, 1.0), _rnd(0.7, 0.9)]
            sm   = 1.3

        elif ptype == 'flame':
            s = 0.18
            x, z = px + gs(s), pz + gs(s)
            y    = py + _rnd(0.0, 0.08)
            vx, vz = _rnd(-0.12, 0.12), _rnd(-0.12, 0.12)
            vy   = _rnd(0.7, 1.8)
            life = _rnd(0.5, 0.9)
            col  = [1.0, _rnd(0.8, 1.0), _rnd(0.4, 0.6)]
            sm   = 1.0

        elif ptype == 'outer':
            s = 0.22
            x, z = px + gs(s), pz + gs(s)
            y    = py + _rnd(0.05, 0.15)
            vx, vz = _rnd(-0.18, 0.18), _rnd(-0.18, 0.18)
            vy   = _rnd(0.5, 1.4)
            life = _rnd(0.4, 0.8)
            col  = [1.0, _rnd(0.6, 0.8), _rnd(0.1, 0.3)]
            sm   = 0.85

        elif ptype == 'ember':
            s     = 0.12
            x, z  = px + gs(s), pz + gs(s)
            y     = py + _rnd(0.05, 0.2)
            angle = _rnd(0, _PI2)
            spd   = _rnd(0.3, 0.7)
            vx, vz = math.cos(angle) * spd, math.sin(angle) * spd
            vy    = _rnd(1.8, 3.2)
            life  = _rnd(0.4, 0.9)
            col   = [1.0, _rnd(0.7, 0.9), _rnd(0.2, 0.4)]
            sm    = 0.55

        else:  # smoke
            s = 0.20
            x, z = px + gs(s), pz + gs(s)
            y    = py + _rnd(0.3, 0.6)
            vx, vz = _rnd(-0.08, 0.08), _rnd(-0.08, 0.08)
            vy   = _rnd(0.3, 0.7)
            life = _rnd(0.1, 0.2)
            col  = [1.0, 1.0, 1.0]
            sm   = 1.6

        return {
            'pos':      [x, y, z],
            'vel':      [vx, vy, vz],
            'color':    col,
            'life':     life,
            'max_life': life,
            'type':     ptype,
            'size_mult': sm,
            'phase':    _rnd(0, _PI2),
        }

    # ------------------------------------------------------------------ logs

    def _generate_logs(self):
        vertices, indices = [], []
        px, py, pz = self.position

        def add_cylinder(cx, cy, cz, radius, length, angle_y, seg=8):
            ca, sa = math.cos(angle_y), math.sin(angle_y)
            bi  = len(vertices) // 9
            col = [0.15, 0.08, 0.03]
            for end in range(2):
                off = -length / 2 + end * length
                for i in range(seg):
                    th = _PI2 * i / seg
                    lx = off
                    ly = radius * math.cos(th)
                    lz = radius * math.sin(th)
                    wx = cx + lx * ca - lz * sa
                    wy = cy + ly
                    wz = cz + lx * sa + lz * ca
                    nx, ny, nz = 0.0, math.cos(th), math.sin(th)
                    wnx = nx * ca - nz * sa
                    wnz = nx * sa + nz * ca
                    vertices.extend([wx, wy, wz, wnx, ny, wnz, *col])
            for i in range(seg):
                i0 = bi + i
                i1 = bi + (i + 1) % seg
                i2 = bi + seg + i
                i3 = bi + seg + (i + 1) % seg
                indices.extend([i0, i2, i1, i1, i2, i3])

        lr, ll = 0.06, 0.8
        add_cylinder(px, py,        pz, lr,        ll,        0.0)
        add_cylinder(px, py,        pz, lr,        ll,        math.pi / 3)
        add_cylinder(px, py,        pz, lr,        ll,        _PI2 / 3)
        add_cylinder(px, py + 0.08, pz, lr * 0.8,  ll * 0.7,  math.pi / 6)

        sc_base = [0.2, 0.2, 0.18]
        for i in range(10):
            angle = _PI2 * i / 10
            sx = px + 0.5 * math.cos(angle)
            sz = pz + 0.5 * math.sin(angle)
            sy = py - 0.05
            s  = 0.08 + _rnd(-0.02, 0.02)
            bi = len(vertices) // 9
            for dy in [-s, s]:
                for dz2 in [-s, s]:
                    for dx2 in [-s, s]:
                        nx2 = (dx2 / abs(dx2)) if dx2 else 0
                        ny2 = (dy  / abs(dy))  if dy  else 0
                        nz2 = (dz2 / abs(dz2)) if dz2 else 0
                        ln  = math.sqrt(nx2**2 + ny2**2 + nz2**2)
                        if ln: nx2 /= ln; ny2 /= ln; nz2 /= ln
                        sc = [c + _rnd(-0.03, 0.03) for c in sc_base]
                        vertices.extend([sx+dx2, sy+dy, sz+dz2, nx2, ny2, nz2, *sc])
            b = bi
            indices.extend([
                b+0,b+1,b+3, b+0,b+3,b+2,
                b+4,b+7,b+5, b+4,b+6,b+7,
                b+0,b+4,b+1, b+1,b+4,b+5,
                b+2,b+3,b+6, b+3,b+7,b+6,
                b+0,b+2,b+4, b+2,b+6,b+4,
                b+1,b+5,b+3, b+3,b+5,b+7,
            ])

        verts = np.array(vertices, dtype=np.float32)
        idxs  = np.array(indices,  dtype=np.uint32)
        self.log_index_count = len(idxs)

        self.log_vao = glGenVertexArrays(1)
        self.log_vbo = glGenBuffers(1)
        self.log_ebo = glGenBuffers(1)

        glBindVertexArray(self.log_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.log_vbo)
        glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.log_ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, idxs.nbytes, idxs, GL_STATIC_DRAW)

        stride = 9 * 4
        for loc, offset in [(0, 0), (1, 12), (2, 24)]:
            glVertexAttribPointer(loc, 3, GL_FLOAT, GL_FALSE, stride,
                                  ctypes.c_void_p(offset))
            glEnableVertexAttribArray(loc)
        glBindVertexArray(0)

    # -------------------------------------------------------- particle buffer

    def _setup_particle_buffer(self):
        self.particle_vao = glGenVertexArrays(1)
        self.particle_vbo = glGenBuffers(1)

        glBindVertexArray(self.particle_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.particle_vbo)
        glBufferData(GL_ARRAY_BUFFER, self.max_particles * 8 * 4,
                     None, GL_DYNAMIC_DRAW)

        stride = 8 * 4
        specs = [(0, 3, 0), (1, 3, 12), (2, 1, 24), (3, 1, 28)]
        for loc, size, off in specs:
            glVertexAttribPointer(loc, size, GL_FLOAT, GL_FALSE, stride,
                                  ctypes.c_void_p(off))
            glEnableVertexAttribArray(loc)
        glBindVertexArray(0)

    # ----------------------------------------------------------------- update

    def update(self, dt):
        self._time += dt
        t = self._time

        # Slow drifting wind
        wind_x = math.sin(t * 0.3) * 0.15
        wind_z = math.cos(t * 0.25) * 0.08

        # Fire color ramp: white-hot → yellow → orange → deep red
        _WHITE  = [1.0, 1.0, 0.9]
        _YELLOW = [1.0, 0.9, 0.2]
        _ORANGE = [1.0, 0.45, 0.05]
        _RED    = [0.8, 0.1, 0.2]
        _DARK   = [0.25, 0.05, 0.0]

        for i, p in enumerate(self.particles):
            ptype = p['type']

            p['life'] -= dt * _DECAY.get(ptype, 1.0)
            if p['life'] <= 0:
                self.particles[i] = self._new_particle()
                continue

            lr = p['life'] / p['max_life']   # 1.0 = fresh, 0.0 = dying

            # -- Realistic color evolution (hot → cool) --------------------
            if ptype in ('core', 'flame', 'outer'):
                if   lr > 0.75: col = _lerp(_WHITE,  _YELLOW, (1 - lr) / 0.25)
                elif lr > 0.45: col = _lerp(_YELLOW, _ORANGE, (0.75 - lr) / 0.30)
                elif lr > 0.15: col = _lerp(_ORANGE, _RED,    (0.45 - lr) / 0.30)
                else:           col = _lerp(_RED,    _DARK,   (0.15 - lr) / 0.15)
                p['color'] = col

            elif ptype == 'ember':
                if lr > 0.15:
                    p['color'] = _lerp(_YELLOW, _RED, 1 - lr)
                else:
                    # Flicker and die
                    flk = abs(math.sin(t * 20.0 + p['phase']))
                    p['color'] = [flk, flk * 0.25, 0.0]

            # smoke stays gray (handled by shader via low life value)

            # -- Dynamic size: bell curve (swell then shrink) --------------
            bell = 1.0 + math.sin(lr * math.pi) * 0.8
            p['size_mult'] = p.get('base_sm', p['size_mult']) * bell
            if 'base_sm' not in p:
                p['base_sm'] = p['size_mult']

            # -- Position update -------------------------------------------
            p['pos'][0] += p['vel'][0] * dt
            p['pos'][1] += p['vel'][1] * dt
            p['pos'][2] += p['vel'][2] * dt

            # -- Drag ---------------------------------------------------------
            drag = 0.94 if ptype == 'ember' else 0.97
            p['vel'][0] *= drag
            p['vel'][2] *= drag

            # -- Buoyancy -----------------------------------------------------
            p['vel'][1] += _BUOY.get(ptype, 0.5) * dt

            # -- Wind + turbulence -------------------------------------------
            phase  = p['phase']
            height = p['pos'][1] - self.position[1]
            swirl  = 0.18 * (1.0 + height * 0.4)
            p['vel'][0] += (math.sin(t * 4.5 + phase + height * 2.5) * swirl
                            + wind_x) * dt
            p['vel'][2] += (math.cos(t * 3.8 + phase + height * 2.1) * swirl
                            + wind_z) * dt

            # -- Gravity on embers -------------------------------------------
            if ptype == 'ember':
                p['vel'][1] -= 1.5 * dt

    # ------------------------------------------------------------------ draw

    def draw_logs(self):
        glBindVertexArray(self.log_vao)
        glDrawElements(GL_TRIANGLES, self.log_index_count, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    def draw_particles(self):
        data, alive = [], 0
        for p in self.particles:
            if p['life'] > 0:
                lr = p['life'] / p['max_life']
                data.extend(p['pos'])
                data.extend(p['color'])
                data.append(lr)
                data.append(p.get('size_mult', 1.0))
                alive += 1

        if not alive:
            return

        arr = np.array(data, dtype=np.float32)
        glBindVertexArray(self.particle_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.particle_vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, arr.nbytes, arr)
        glEnable(GL_PROGRAM_POINT_SIZE)
        glDrawArrays(GL_POINTS, 0, alive)
        glDisable(GL_PROGRAM_POINT_SIZE)
        glBindVertexArray(0)

    def destroy(self):
        glDeleteVertexArrays(1, [self.log_vao])
        glDeleteBuffers(1, [self.log_vbo])
        glDeleteBuffers(1, [self.log_ebo])
        glDeleteVertexArrays(1, [self.particle_vao])
        glDeleteBuffers(1, [self.particle_vbo])