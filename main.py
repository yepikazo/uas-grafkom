"""
Yuru Camp - Lakeside Night Scene
A 3D OpenGL scene depicting a nighttime lakeside camping scene.
Features: mountains, animated lake, starry sky with moon, campfire with particles,
tent and camping accessories. cek notif

Controls:
  - Left mouse drag: Rotate camera
  - Mouse scroll: Zoom in/out
  - V: Toggle cinematic camera
  - R: Reset/toggle auto-rotation
  - ESC: Exit
"""
import os
import sys
import math
import time as time_module

import pygame
from pygame.locals import *
from OpenGL.GL import *
import glm
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.window import Window
from core.camera import Camera
from core.shader import Shader
from core.terrain_height import height_at, CAMP_X, CAMP_Z
from objects.terrain import Terrain
from objects.lake import Lake
from objects.campfire import Campfire
from objects.tent import Tent
from objects.skybox import Skybox
from objects.firefly import Firefly


class Scene:
    """Main scene manager for the Yuru Camp lakeside night scene."""

    def __init__(self):
        # Create window
        self.window = Window(1280, 720, "Yuru Camp ⛺ - Lakeside Night Scene")

        # Print OpenGL info
        print(f"OpenGL Version: {glGetString(GL_VERSION).decode()}")
        print(f"GLSL Version: {glGetString(GL_SHADING_LANGUAGE_VERSION).decode()}")
        print(f"Renderer: {glGetString(GL_RENDERER).decode()}")

        # OpenGL settings
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_MULTISAMPLE)
        glClearColor(0.01, 0.015, 0.04, 1.0)  # Very dark blue night sky

        # Shader directory
        shader_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shaders")

        # Load shaders
        self.terrain_shader = Shader(
            os.path.join(shader_dir, "terrain.vert"),
            os.path.join(shader_dir, "terrain.frag")
        )
        self.lake_shader = Shader(
            os.path.join(shader_dir, "lake.vert"),
            os.path.join(shader_dir, "lake.frag")
        )
        self.campfire_shader = Shader(
            os.path.join(shader_dir, "campfire.vert"),
            os.path.join(shader_dir, "camfire.frag")
        )
        self.skybox_shader = Shader(
            os.path.join(shader_dir, "skybox.vert"),
            os.path.join(shader_dir, "skybox.frag")
        )
        self.object_shader = Shader(
            os.path.join(shader_dir, "object.vert"),
            os.path.join(shader_dir, "object.frag")
        )
        self.firefly_shader = Shader(
            os.path.join(shader_dir, "firefly.vert"),
            os.path.join(shader_dir, "firefly.frag")
        )

        # Camp and fire positions
        camp_y = height_at(CAMP_X, CAMP_Z)
        fire_x, fire_z = CAMP_X - 2.0, CAMP_Z + 1.5
        fire_y = height_at(fire_x, fire_z) + 0.3

        # Create camera — first-person, seated at camp looking toward fire & lake
        chair_x, chair_z = CAMP_X + 2.5, CAMP_Z - 1.5
        chair_y = height_at(chair_x, chair_z)
        eye_height = 1.2  # seated eye level
        self.camera = Camera(
            position=glm.vec3(chair_x, chair_y + eye_height, chair_z),
            target=glm.vec3(fire_x, fire_y + 0.5, fire_z - 15.0)
        )

        # Create scene objects
        print("Generating terrain...")
        self.terrain = Terrain()
        print("Generating lake...")
        self.lake = Lake()
        print("Generating campfires...")
        secondary_fire_specs = [
            (CAMP_X - 18.0, CAMP_Z + 9.0),
            (CAMP_X + 17.0, CAMP_Z + 8.0),
        ]
        self.campfires = [Campfire(position=(fire_x, fire_y - 0.1, fire_z))]
        self.fire_light_positions = [glm.vec3(fire_x, fire_y, fire_z)]
        for sx, sz in secondary_fire_specs:
            sy = height_at(sx, sz) + 0.3
            self.campfires.append(Campfire(position=(sx, sy - 0.1, sz)))
            self.fire_light_positions.append(glm.vec3(sx, sy, sz))
        self.campfire = self.campfires[0]
        print("Generating tent and accessories...")
        self.tent = Tent()
        print("Generating skybox...")
        self.skybox = Skybox()
        print("Generating fireflies...")
        self.firefly = Firefly()
        print("Scene ready!")

        # Scene parameters
        self.time = 0.0
        self.fire_pos = self.fire_light_positions[0]
        self.fire_color = glm.vec3(1.0, 0.6, 0.15)
        self.fire_intensity = 3.0
        # Moon close to Mount Fuji, slightly above and to the right of the summit.
        self.moon_dir = glm.normalize(glm.vec3(0.16, 0.34, -0.93))
        self.moon_color = glm.vec3(0.7, 0.75, 1.0)
        self.cinematic_enabled = False
        self.cinematic_time = 0.0
        self.cinematic_duration = 56.0

    def _cinematic_point(self, x, z, eye_height):
        """Create a camera point lifted above the terrain."""
        return glm.vec3(x, height_at(x, z) + eye_height, z)

    def _smoothstep(self, value):
        value = max(0.0, min(1.0, value))
        return value * value * (3.0 - 2.0 * value)

    def _lerp_vec3(self, a, b, t):
        return a * (1.0 - t) + b * t

    def _set_fire_uniforms(self, shader):
        """Upload all campfire light sources to a shader."""
        fire_count = min(len(self.fire_light_positions), 3)
        shader.set_int("fireCount", fire_count)
        for i in range(fire_count):
            pos = self.fire_light_positions[i]
            shader.set_vec3(f"firePositions[{i}]", pos.x, pos.y, pos.z)
            shader.set_vec3(f"fireColors[{i}]", self.fire_color.x, self.fire_color.y, self.fire_color.z)
            shader.set_float(f"fireIntensities[{i}]", self.fire_intensity)

    def _sample_cinematic_path(self):
        """Return smoothly interpolated camera and target positions."""
        fire_x, fire_y, fire_z = self.fire_pos.x, self.fire_pos.y, self.fire_pos.z
        tent_focus = glm.vec3(fire_x + 0.3, height_at(fire_x + 0.3, fire_z + 2.6) + 1.1, fire_z + 2.6)
        lake_focus = glm.vec3(0.0, 1.0, -18.0)
        fuji_focus = glm.vec3(0.0, 18.0, -135.0)
        moon_focus = glm.vec3(10.0, 31.0, -88.0)
        horizon_focus = glm.vec3(2.0, 5.5, -45.0)

        shots = [
            # Tents in the foreground, lake and Fuji behind them.
            (self._cinematic_point(-8.0, 62.0, 2.4), horizon_focus),
            (self._cinematic_point(0.0, 64.0, 2.2), fuji_focus),
            (self._cinematic_point(8.0, 61.0, 2.5), moon_focus),

            # Slow side drift keeps the campsite visible while revealing the lake.
            (self._cinematic_point(13.0, 55.0, 3.2), lake_focus),
            (self._cinematic_point(-13.0, 55.0, 3.2), lake_focus),

            # Closer campsite composition before looping back to the wide view.
            (self._cinematic_point(-5.0, 57.0, 1.6), tent_focus),
            (self._cinematic_point(5.0, 58.0, 1.8), horizon_focus),
        ]

        phase = (self.cinematic_time % self.cinematic_duration) / self.cinematic_duration
        scaled = phase * len(shots)
        index = int(scaled) % len(shots)
        next_index = (index + 1) % len(shots)
        local_t = self._smoothstep(scaled - int(scaled))

        cam_a, target_a = shots[index]
        cam_b, target_b = shots[next_index]
        camera_pos = self._lerp_vec3(cam_a, cam_b, local_t)
        target_pos = self._lerp_vec3(target_a, target_b, local_t)

        # Gentle handheld-like drift, subtle enough for presentation.
        camera_pos.y += math.sin(self.cinematic_time * 0.45) * 0.18
        target_pos.x += math.sin(self.cinematic_time * 0.22) * 0.35
        return camera_pos, target_pos

    def update_cinematic_camera(self, dt):
        """Advance the cinematic camera loop."""
        self.cinematic_time += dt
        camera_pos, target_pos = self._sample_cinematic_path()
        self.camera.set_view(camera_pos, target_pos)

    def handle_events(self):
        """Process input events."""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.window.running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.window.running = False
                elif event.key == K_r:
                    self.camera.auto_rotate = not self.camera.auto_rotate
                elif event.key == K_c:
                    self.cinematic_enabled = False
                    self.camera.toggle_mode()
                    print(f"Camera mode: {self.camera.mode}")
                elif event.key == K_v:
                    self.cinematic_enabled = not self.cinematic_enabled
                    self.camera.auto_rotate = False
                    print(f"Cinematic camera: {'ON' if self.cinematic_enabled else 'OFF'}")
            elif event.type == VIDEORESIZE:
                self.window.handle_resize(event.w, event.h)
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.cinematic_enabled = False
                    self.camera.process_mouse_button(1, True, *event.pos)
                elif event.button == 4:
                    self.camera.process_scroll(1)
                elif event.button == 5:
                    self.camera.process_scroll(-1)
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    self.camera.process_mouse_button(1, False, *event.pos)
            elif event.type == MOUSEMOTION:
                self.camera.process_mouse_motion(*event.pos)
            elif event.type == MOUSEWHEEL:
                self.camera.process_scroll(event.y)

    def update(self, dt):
        """Update scene state."""
        self.time += dt
        
        # Handle keyboard movement
        keys = pygame.key.get_pressed()
        if self.cinematic_enabled:
            self.update_cinematic_camera(dt)
        else:
            self.camera.process_keyboard(keys, dt)
            self.camera.update(dt)

        for campfire in self.campfires:
            campfire.update(dt)
        self.firefly.update(dt, self.camera.position)

        # Animate fire intensity
        self.fire_intensity = 5 + 1.2 * math.sin(self.time * 3.0) + 0.5 * math.sin(self.time * 7.0)

    def render(self):
        """Render the complete scene."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        aspect = self.window.get_aspect_ratio()
        view = self.camera.get_view_matrix()
        projection = self.camera.get_projection_matrix(aspect)

        # Convert glm matrices to flat arrays for OpenGL
        view_data = np.array(view.to_list(), dtype=np.float32).flatten()
        proj_data = np.array(projection.to_list(), dtype=np.float32).flatten()
        model = glm.mat4(1.0)
        model_data = np.array(model.to_list(), dtype=np.float32).flatten()

        cam_pos = self.camera.position

        # --- Draw Skybox first ---
        self.skybox_shader.use()
        self.skybox_shader.set_mat4("view", view_data)
        self.skybox_shader.set_mat4("projection", proj_data)
        self.skybox_shader.set_float("time", self.time)
        self.skybox_shader.set_vec3("moonDir", self.moon_dir.x, self.moon_dir.y, self.moon_dir.z)
        self.skybox.draw()

        # --- Draw Terrain ---
        self.terrain_shader.use()
        self.terrain_shader.set_mat4("model", model_data)
        self.terrain_shader.set_mat4("view", view_data)
        self.terrain_shader.set_mat4("projection", proj_data)
        self._set_fire_uniforms(self.terrain_shader)
        self.terrain_shader.set_vec3("moonDir", self.moon_dir.x, self.moon_dir.y, self.moon_dir.z)
        self.terrain_shader.set_vec3("moonColor", self.moon_color.x, self.moon_color.y, self.moon_color.z)
        self.terrain_shader.set_float("time", self.time)
        self.terrain.draw()

        # --- Draw Tent and accessories ---
        self.object_shader.use()
        self.object_shader.set_mat4("model", model_data)
        self.object_shader.set_mat4("view", view_data)
        self.object_shader.set_mat4("projection", proj_data)
        self._set_fire_uniforms(self.object_shader)
        self.object_shader.set_vec3("moonDir", self.moon_dir.x, self.moon_dir.y, self.moon_dir.z)
        self.object_shader.set_vec3("moonColor", self.moon_color.x, self.moon_color.y, self.moon_color.z)
        self.object_shader.set_float("time", self.time)
        self.tent.draw()

        # --- Draw Campfire logs ---
        for campfire in self.campfires:
            campfire.draw_logs()

        # --- Draw Lake (transparent, after opaque objects) ---
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.lake_shader.use()
        self.lake_shader.set_mat4("model", model_data)
        self.lake_shader.set_mat4("view", view_data)
        self.lake_shader.set_mat4("projection", proj_data)
        self.lake_shader.set_vec3("viewPos", cam_pos.x, cam_pos.y, cam_pos.z)
        self._set_fire_uniforms(self.lake_shader)
        self.lake_shader.set_vec3("moonDir", self.moon_dir.x, self.moon_dir.y, self.moon_dir.z)
        self.lake_shader.set_vec3("moonColor", self.moon_color.x, self.moon_color.y, self.moon_color.z)
        self.lake_shader.set_float("time", self.time)
        self.lake.draw()

        # --- Draw Campfire particles (additive blending) ---
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)  # Additive blending for fire glow
        self.campfire_shader.use()
        self.campfire_shader.set_mat4("model", model_data)
        self.campfire_shader.set_mat4("view", view_data)
        self.campfire_shader.set_mat4("projection", proj_data)
        self.campfire_shader.set_float("time", self.time)
        for campfire in self.campfires:
            campfire.draw_particles()

        # --- Draw Fireflies (additive blending for natural glow) ---
        self.firefly_shader.use()
        self.firefly_shader.set_mat4("model", model_data)
        self.firefly_shader.set_mat4("view", view_data)
        self.firefly_shader.set_mat4("projection", proj_data)
        self.firefly.draw()

        # Reset blend mode
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def run(self):
        """Main loop."""
        print("\n=== Yuru Camp - Lakeside Night Scene ===")
        print("Controls:")
        print("  Mouse drag  : Rotate camera")
        print("  Scroll      : Zoom (Orbital) / Move Speed (Free)")
        print("  WASD        : Move (Free mode)")
        print("  Space/Shift : Up/Down (Free mode)")
        print("  C           : Toggle Camera Mode (Free/Orbital)")
        print("  V           : Toggle Cinematic Camera")
        print("  R           : Toggle Auto-rotation (Orbital mode)")
        print("  ESC         : Exit")
        print("========================================\n")

        while self.window.running:
            dt = self.window.tick(60)
            self.handle_events()
            self.update(dt)
            self.render()
            self.window.swap()

        self.cleanup()

    def cleanup(self):
        """Clean up resources."""
        self.terrain.destroy()
        self.lake.destroy()
        for campfire in self.campfires:
            campfire.destroy()
        self.tent.destroy()
        self.skybox.destroy()
        self.firefly.destroy()
        self.terrain_shader.destroy()
        self.lake_shader.destroy()
        self.campfire_shader.destroy()
        self.skybox_shader.destroy()
        self.object_shader.destroy()
        self.firefly_shader.destroy()
        self.window.destroy()


if __name__ == "__main__":
    scene = Scene()
    scene.run()
