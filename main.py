"""
Yuru Camp - Lakeside Night Scene
A 3D OpenGL scene depicting a nighttime lakeside camping scene.
Features: mountains, animated lake, starry sky with moon, campfire with particles,
tent and camping accessories. cek notif

Controls:
  - Left mouse drag: Rotate camera
  - Mouse scroll: Zoom in/out
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

        # Camp and fire positions
        camp_y = height_at(CAMP_X, CAMP_Z)
        fire_x, fire_z = CAMP_X - 2.0, CAMP_Z + 1.5
        fire_y = height_at(fire_x, fire_z) + 0.3

        # Create camera near camp, looking NORTH toward lake and Fuji
        self.camera = Camera(
            position=glm.vec3(CAMP_X, camp_y + 3.0, CAMP_Z + 6.0),
            target=glm.vec3(CAMP_X, camp_y + 1.0, CAMP_Z - 30.0)
        )

        # Create scene objects
        print("Generating terrain...")
        self.terrain = Terrain()
        print("Generating lake...")
        self.lake = Lake()
        print("Generating campfire...")
        self.campfire = Campfire(position=(fire_x, fire_y - 0.1, fire_z))
        print("Generating tent and accessories...")
        self.tent = Tent()
        print("Generating skybox...")
        self.skybox = Skybox()
        print("Scene ready!")

        # Scene parameters
        self.time = 0.0
        self.fire_pos = glm.vec3(fire_x, fire_y, fire_z)
        self.fire_color = glm.vec3(1.0, 0.6, 0.15)
        self.fire_intensity = 3.0
        self.moon_dir = glm.normalize(glm.vec3(0.5, 0.6, -0.4))
        self.moon_color = glm.vec3(0.6, 0.65, 0.8)

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
                    self.camera.toggle_mode()
                    print(f"Camera mode: {self.camera.mode}")
            elif event.type == VIDEORESIZE:
                self.window.handle_resize(event.w, event.h)
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
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
        self.camera.process_keyboard(keys, dt)
        
        self.camera.update(dt)
        self.campfire.update(dt)

        # Animate fire intensity
        self.fire_intensity = 2.5 + 0.8 * math.sin(self.time * 3.0) + 0.3 * math.sin(self.time * 7.0)

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
        self.terrain_shader.set_vec3("firePos", self.fire_pos.x, self.fire_pos.y, self.fire_pos.z)
        self.terrain_shader.set_vec3("fireColor", self.fire_color.x, self.fire_color.y, self.fire_color.z)
        self.terrain_shader.set_float("fireIntensity", self.fire_intensity)
        self.terrain_shader.set_vec3("moonDir", self.moon_dir.x, self.moon_dir.y, self.moon_dir.z)
        self.terrain_shader.set_vec3("moonColor", self.moon_color.x, self.moon_color.y, self.moon_color.z)
        self.terrain_shader.set_float("time", self.time)
        self.terrain.draw()

        # --- Draw Tent and accessories ---
        self.object_shader.use()
        self.object_shader.set_mat4("model", model_data)
        self.object_shader.set_mat4("view", view_data)
        self.object_shader.set_mat4("projection", proj_data)
        self.object_shader.set_vec3("firePos", self.fire_pos.x, self.fire_pos.y, self.fire_pos.z)
        self.object_shader.set_vec3("fireColor", self.fire_color.x, self.fire_color.y, self.fire_color.z)
        self.object_shader.set_float("fireIntensity", self.fire_intensity)
        self.object_shader.set_vec3("moonDir", self.moon_dir.x, self.moon_dir.y, self.moon_dir.z)
        self.object_shader.set_vec3("moonColor", self.moon_color.x, self.moon_color.y, self.moon_color.z)
        self.object_shader.set_float("time", self.time)
        self.tent.draw()

        # --- Draw Campfire logs ---
        self.campfire.draw_logs()

        # --- Draw Lake (transparent, after opaque objects) ---
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.lake_shader.use()
        self.lake_shader.set_mat4("model", model_data)
        self.lake_shader.set_mat4("view", view_data)
        self.lake_shader.set_mat4("projection", proj_data)
        self.lake_shader.set_vec3("viewPos", cam_pos.x, cam_pos.y, cam_pos.z)
        self.lake_shader.set_vec3("firePos", self.fire_pos.x, self.fire_pos.y, self.fire_pos.z)
        self.lake_shader.set_vec3("fireColor", self.fire_color.x, self.fire_color.y, self.fire_color.z)
        self.lake_shader.set_float("fireIntensity", self.fire_intensity)
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
        self.campfire.draw_particles()

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
        self.campfire.destroy()
        self.tent.destroy()
        self.skybox.destroy()
        self.terrain_shader.destroy()
        self.lake_shader.destroy()
        self.campfire_shader.destroy()
        self.skybox_shader.destroy()
        self.object_shader.destroy()
        self.window.destroy()


if __name__ == "__main__":
    scene = Scene()
    scene.run()
