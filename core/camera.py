"""
Camera system with orbital/free-look controls.
"""
import glm
import math


class Camera:
    """Third-person orbital camera for viewing the scene."""

    def __init__(self, position=None, target=None):
        self.position = position or glm.vec3(8.0, 6.0, 12.0)
        self.target = target or glm.vec3(0.0, 1.0, 0.0)
        self.up = glm.vec3(0.0, 1.0, 0.0)

        # Orbital parameters
        self.yaw = -45.0
        self.pitch = -25.0
        self.distance = 18.0
        self.min_distance = 5.0
        self.max_distance = 50.0

        # Mouse state
        self.last_x = 0
        self.last_y = 0
        self.is_dragging = False

        # Auto-rotate
        self.auto_rotate = True
        self.auto_rotate_speed = 3.0  # degrees per second

        self._update_position()

    def _update_position(self):
        """Update camera position based on orbital parameters."""
        rad_yaw = math.radians(self.yaw)
        rad_pitch = math.radians(self.pitch)

        x = self.distance * math.cos(rad_pitch) * math.sin(rad_yaw)
        y = self.distance * math.sin(rad_pitch)
        z = self.distance * math.cos(rad_pitch) * math.cos(rad_yaw)

        self.position = self.target + glm.vec3(x, y, z)

    def get_view_matrix(self):
        return glm.lookAt(self.position, self.target, self.up)

    def get_projection_matrix(self, aspect_ratio, fov=45.0, near=0.1, far=200.0):
        return glm.perspective(glm.radians(fov), aspect_ratio, near, far)

    def process_mouse_button(self, button, pressed, x, y):
        """Handle mouse button events for orbital control."""
        if button == 1:  # Left button
            self.is_dragging = pressed
            self.last_x = x
            self.last_y = y
            if pressed:
                self.auto_rotate = False

    def process_mouse_motion(self, x, y):
        """Handle mouse motion for orbital rotation."""
        if self.is_dragging:
            dx = x - self.last_x
            dy = y - self.last_y
            self.last_x = x
            self.last_y = y

            self.yaw += dx * 0.3
            self.pitch -= dy * 0.3
            self.pitch = max(-80.0, min(80.0, self.pitch))
            self._update_position()

    def process_scroll(self, scroll_y):
        """Handle mouse scroll for zoom."""
        self.distance -= scroll_y * 1.5
        self.distance = max(self.min_distance, min(self.max_distance, self.distance))
        self._update_position()

    def update(self, delta_time):
        """Update auto-rotation."""
        if self.auto_rotate:
            self.yaw += self.auto_rotate_speed * delta_time
            self._update_position()
