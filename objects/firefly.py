"""
Firefly particle system — glowing yellow-green lights floating in the forest at night.
Each firefly follows a sinusoidal drift path and blinks independently.
"""
import numpy as np
import math
import random
from OpenGL.GL import *
from core.terrain_height import height_at, lake_distance, CAMP_X, CAMP_Z


class Firefly:
    """
    Animated firefly system using GL_POINTS with additive blending.
    Fireflies spawn in the forest area around the campsite,
    avoid the lake, and hover above the ground level.
    """

    NUM_FIREFLIES = 60

    def __init__(self):
        self.time    = 0.0
        self.fireflies = []  # list of dicts: base_pos, phase, freq, amplitude, height_offset
        self.vao     = None
        self.vbo     = None
        self._spawn_fireflies()
        self._setup_buffer()

    # ------------------------------------------------------------------ spawn
    def _spawn_fireflies(self):
        """Place fireflies close to camp — near tents, forest edge, and lake shore."""
        random.seed(99)
        fire_x, fire_z = CAMP_X - 2.0, CAMP_Z + 1.5
        placed = 0

        attempts = 0
        while placed < self.NUM_FIREFLIES and attempts < 2000:
            attempts += 1

            zone = random.random()
            if zone < 0.35:
                # Just behind tents — close forest edge (south/behind camp)
                tx = CAMP_X + random.uniform(-18, 18)
                tz = CAMP_Z + random.uniform(8, 22)
            elif zone < 0.55:
                # Left and right flanks of camp, close range
                side = random.choice([-1, 1])
                tx = CAMP_X + side * random.uniform(7, 20)
                tz = CAMP_Z + random.uniform(-5, 18)
            elif zone < 0.75:
                # Near lake shore edge (outside lake boundary)
                tx = CAMP_X + random.uniform(-25, 25)
                tz = CAMP_Z + random.uniform(-18, -5)
            else:
                # Scattered very close around camp perimeter
                tx = CAMP_X + random.uniform(-12, 12)
                tz = CAMP_Z + random.uniform(-10, 15)

            # Reject if inside camp clearing (keep open space around fire & tents)
            if abs(tx - fire_x) < 5.0 and abs(tz - fire_z) < 5.0:
                continue
            # Reject if too deep inside lake
            if lake_distance(tx, tz) < 0.5:
                continue
            # Reject if out of terrain bounds
            if abs(tx) > 170 or abs(tz) > 170:
                continue

            ty = height_at(tx, tz)
            if ty < 0.0:  # underwater
                continue

            self.fireflies.append({
                'base':         [tx, ty, tz],
                'move_phase_x': random.uniform(0, math.pi * 2),
                'move_phase_z': random.uniform(0, math.pi * 2),
                'blink_phase':  random.uniform(0, math.pi * 2),
                'blink_freq':   random.uniform(0.8, 2.5),
                'drift_speed':  random.uniform(0.3, 0.9),
                'hover_height': random.uniform(0.4, 2.0),
                'drift_r':      random.uniform(0.4, 1.5),
                'evasion_offset': [0.0, 0.0, 0.0],
            })
            placed += 1


    # ------------------------------------------------------------------ GPU buffer
    def _setup_buffer(self):
        """Allocate VAO/VBO for point sprite rendering.
        Each vertex: pos(3) + color(3) + brightness(1) = 7 floats.
        """
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        max_bytes = self.NUM_FIREFLIES * 7 * 4
        glBufferData(GL_ARRAY_BUFFER, max_bytes, None, GL_DYNAMIC_DRAW)

        stride = 7 * 4
        # position
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        # color
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)
        # brightness
        glVertexAttribPointer(2, 1, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))
        glEnableVertexAttribArray(2)

        glBindVertexArray(0)

    # ------------------------------------------------------------------ update
    def update(self, dt, camera_pos=None):
        self.time += dt
        
        if camera_pos:
            cx, cy, cz = camera_pos.x, camera_pos.y, camera_pos.z
            for ff in self.fireflies:
                bx, by, bz = ff['base']
                ex, ey, ez = ff['evasion_offset']
                
                # Current approx position (ignoring sine drift for collision)
                curr_x, curr_y, curr_z = bx + ex, by + ff['hover_height'] + ey, bz + ez
                
                dx, dy, dz = curr_x - cx, curr_y - cy, curr_z - cz
                dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                
                # If camera is closer than 4 meters, scatter!
                if dist < 4.0 and dist > 0.01:
                    push_force = (4.0 - dist) * 2.0  # Stronger push the closer it is
                    # Normalize and apply force
                    ff['evasion_offset'][0] += (dx / dist) * push_force * dt
                    ff['evasion_offset'][1] += (dy / dist) * push_force * dt
                    ff['evasion_offset'][2] += (dz / dist) * push_force * dt
                else:
                    # Slowly return to original base position
                    ff['evasion_offset'][0] -= ex * 1.5 * dt
                    ff['evasion_offset'][1] -= ey * 1.5 * dt
                    ff['evasion_offset'][2] -= ez * 1.5 * dt

    # ------------------------------------------------------------------ draw
    def draw(self):
        """Upload current positions/brightness and draw all fireflies."""
        t = self.time
        data = []
        count = 0

        for ff in self.fireflies:
            bx, by, bz = ff['base']
            ex, ey, ez = ff['evasion_offset']
            sp  = ff['drift_speed']
            dr  = ff['drift_r']
            hh  = ff['hover_height']
            mpx = ff['move_phase_x']
            mpz = ff['move_phase_z']
            bp  = ff['blink_phase']
            bf  = ff['blink_freq']

            # Sinusoidal hover drift + evasion offset
            x = bx + ex + math.sin(t * sp + mpx) * dr
            y = by + ey + hh + math.sin(t * sp * 0.7 + mpx + 1.0) * 0.25
            z = bz + ez + math.cos(t * sp + mpz) * dr

            # Blink: 0 (off) → 1 (on), with quick on & slow off (natural bioluminescence)
            raw_blink = math.sin(t * bf * math.pi * 2 + bp)
            brightness = max(0.0, raw_blink) ** 0.5   # bias toward bright

            # Slight color variation: warm yellow-green to cool green
            r = 0.55 + 0.20 * math.sin(bp)
            g = 0.95
            b = 0.30 + 0.20 * math.cos(bp * 1.3)

            data.extend([x, y, z, r, g, b, brightness])
            count += 1

        if count == 0:
            return

        arr = np.array(data, dtype=np.float32)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, arr.nbytes, arr)

        glEnable(GL_PROGRAM_POINT_SIZE)
        glDrawArrays(GL_POINTS, 0, count)
        glDisable(GL_PROGRAM_POINT_SIZE)

        glBindVertexArray(0)

    # ------------------------------------------------------------------ cleanup
    def destroy(self):
        glDeleteVertexArrays(1, [self.vao])
        glDeleteBuffers(1, [self.vbo])
