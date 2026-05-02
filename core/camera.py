"""
Camera system with orbital and free-look (creative) controls.
"""
import glm
import math
import pygame


class Camera:
    """Flexible camera supporting orbital and free-look modes."""

    def __init__(self, position=None, target=None):
        self.position = position or glm.vec3(10.0, 6.0, 10.0)
        self.target = target or glm.vec3(2.0, 0.5, 2.0)
        self.up = glm.vec3(0.0, 1.0, 0.0)
        self.front = glm.normalize(self.target - self.position)
        self.right = glm.normalize(glm.cross(self.front, self.up))

        # Camera modes: 'orbital' or 'free'
        self.mode = 'free'  # Start in free mode as requested
        
        # Free-look parameters
        self.yaw = math.degrees(math.atan2(self.front.z, self.front.x))
        self.pitch = math.degrees(math.asin(self.front.y))
        self.movement_speed = 10.0
        self.mouse_sensitivity = 0.15

        # Orbital parameters
        self.distance = glm.length(self.position - self.target)
        self.min_distance = 2.0
        self.max_distance = 100.0

        # Mouse state
        self.last_x = 0
        self.last_y = 0
        self.is_dragging = False

        # Auto-rotate (only for orbital)
        self.auto_rotate = False
        self.auto_rotate_speed = 3.0

        self._update_vectors()

    def _update_vectors(self):
        """Calculate front, right, and up vectors from yaw and pitch."""
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)

        front = glm.vec3()
        front.x = math.cos(yaw_rad) * math.cos(pitch_rad)
        front.y = math.sin(pitch_rad)
        front.z = math.sin(yaw_rad) * math.cos(pitch_rad)
        
        self.front = glm.normalize(front)
        self.right = glm.normalize(glm.cross(self.front, glm.vec3(0.0, 1.0, 0.0)))
        self.up = glm.normalize(glm.cross(self.right, self.front))

        if self.mode == 'orbital':
            self.position = self.target - self.front * self.distance
        else:
            self.target = self.position + self.front

    def get_view_matrix(self):
        return glm.lookAt(self.position, self.target, glm.vec3(0.0, 1.0, 0.0))

    def get_projection_matrix(self, aspect_ratio, fov=45.0, near=0.1, far=300.0):
        return glm.perspective(glm.radians(fov), aspect_ratio, near, far)

    def set_view(self, position, target):
        """Set camera position and target directly, used by cinematic paths."""
        self.position = glm.vec3(position)
        self.target = glm.vec3(target)

        direction = self.target - self.position
        if glm.length(direction) <= 0.0001:
            return

        self.distance = glm.length(direction)
        self.front = glm.normalize(direction)
        self.right = glm.normalize(glm.cross(self.front, glm.vec3(0.0, 1.0, 0.0)))
        self.up = glm.normalize(glm.cross(self.right, self.front))
        self.yaw = math.degrees(math.atan2(self.front.z, self.front.x))
        self.pitch = math.degrees(math.asin(self.front.y))

    def process_mouse_button(self, button, pressed, x, y):
        """Handle mouse button events."""
        if button == 1:  # Left button
            self.is_dragging = pressed
            self.last_x = x
            self.last_y = y
            if pressed:
                self.auto_rotate = False

    def process_mouse_motion(self, x, y):
        """Handle mouse motion for rotation."""
        if self.is_dragging:
            dx = x - self.last_x
            dy = y - self.last_y
            self.last_x = x
            self.last_y = y

            self.yaw += dx * self.mouse_sensitivity
            self.pitch -= dy * self.mouse_sensitivity

            # Constrain pitch
            self.pitch = max(-89.0, min(89.0, self.pitch))
            self._update_vectors()

    def process_scroll(self, scroll_y):
        """Handle mouse scroll for zoom or speed."""
        if self.mode == 'orbital':
            self.distance -= scroll_y * 1.5
            self.distance = max(self.min_distance, min(self.max_distance, self.distance))
            self._update_vectors()
        else:
            self.movement_speed += scroll_y * 2.0
            self.movement_speed = max(1.0, min(50.0, self.movement_speed))

    def process_keyboard(self, keys, dt):
        """Handle keyboard movement (Minecraft style)."""
        if self.mode != 'free':
            return

        velocity = self.movement_speed * dt
        
        # Forward/Backward (ignore Y for horizontal movement if desired, but Minecraft creative flies)
        if keys[pygame.K_w]:
            self.position += self.front * velocity
        if keys[pygame.K_s]:
            self.position -= self.front * velocity
            
        # Strafe Left/Right
        if keys[pygame.K_a]:
            self.position -= self.right * velocity
        if keys[pygame.K_d]:
            self.position += self.right * velocity
            
        # Up/Down (Space/Shift)
        if keys[pygame.K_SPACE]:
            self.position += glm.vec3(0.0, 1.0, 0.0) * velocity
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.position -= glm.vec3(0.0, 1.0, 0.0) * velocity
            
        self.target = self.position + self.front

    def toggle_mode(self):
        """Switch between orbital and free-look modes."""
        if self.mode == 'orbital':
            self.mode = 'free'
            # Reset yaw/pitch based on current view
            dir = glm.normalize(self.target - self.position)
            self.yaw = math.degrees(math.atan2(dir.z, dir.x))
            self.pitch = math.degrees(math.asin(dir.y))
        else:
            self.mode = 'orbital'
            self.distance = glm.length(self.position - self.target)
            
        self._update_vectors()

    def update(self, delta_time):
        """Update auto-rotation if in orbital mode."""
        if self.mode == 'orbital' and self.auto_rotate:
            self.yaw += self.auto_rotate_speed * delta_time
            self._update_vectors()
