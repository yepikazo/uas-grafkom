"""
Window management using Pygame with OpenGL context.
"""
import pygame
from pygame.locals import *
from OpenGL.GL import *


class Window:
    """Creates and manages the Pygame/OpenGL window."""

    def __init__(self, width=1280, height=720, title="Yuru Camp - Lakeside Night Scene"):
        self.width = width
        self.height = height
        self.title = title
        self.running = True

        pygame.init()
        pygame.display.set_caption(self.title)

        # Set OpenGL attributes using pygame constants
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)

        self.screen = pygame.display.set_mode(
            (self.width, self.height),
            DOUBLEBUF | OPENGL | RESIZABLE
        )

        self.clock = pygame.time.Clock()

    def get_aspect_ratio(self):
        return self.width / self.height

    def handle_resize(self, width, height):
        self.width = width
        self.height = height
        glViewport(0, 0, width, height)

    def swap(self):
        pygame.display.flip()

    def tick(self, fps=60):
        return self.clock.tick(fps) / 1000.0  # Return delta time in seconds

    def destroy(self):
        pygame.quit()
