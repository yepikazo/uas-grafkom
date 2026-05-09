#!/usr/bin/env python3
"""
Diagnostic script to check system OpenGL capabilities and version info.
"""
import sys
import os

print("=" * 60)
print("SYSTEM DIAGNOSTIC REPORT")
print("=" * 60)

# Check Python version
print(f"\n[Python]")
print(f"  Version: {sys.version}")
print(f"  Executable: {sys.executable}")

# Check pygame
print(f"\n[pygame]")
try:
    import pygame
    print(f"  Version: {pygame.version.ver}")
    print(f"  Status: ✓ Installed")
except ImportError as e:
    print(f"  Status: ✗ NOT INSTALLED - {e}")

# Check PyOpenGL
print(f"\n[PyOpenGL]")
try:
    from OpenGL import GL, version
    print(f"  Version: {version.__version__}")
    print(f"  Status: ✓ Installed")
except ImportError as e:
    print(f"  Status: ✗ NOT INSTALLED - {e}")

# Check numpy
print(f"\n[numpy]")
try:
    import numpy
    print(f"  Version: {numpy.__version__}")
    print(f"  Status: ✓ Installed")
except ImportError as e:
    print(f"  Status: ✗ NOT INSTALLED - {e}")

# Check glm
print(f"\n[PyGLM]")
try:
    import glm
    print(f"  Version: {glm.__version__}")
    print(f"  Status: ✓ Installed")
except ImportError as e:
    print(f"  Status: ✗ NOT INSTALLED - {e}")

# Try to initialize Pygame and check OpenGL
print(f"\n[OpenGL Context]")
try:
    pygame.init()
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
    
    screen = pygame.display.set_mode((800, 600), pygame.DOUBLEBUF | pygame.OPENGL)
    
    from OpenGL.GL import glGetString, GL_VERSION, GL_RENDERER, GL_VENDOR, GL_SHADING_LANGUAGE_VERSION
    
    vendor = glGetString(GL_VENDOR).decode() if glGetString(GL_VENDOR) else "Unknown"
    renderer = glGetString(GL_RENDERER).decode() if glGetString(GL_RENDERER) else "Unknown"
    version = glGetString(GL_VERSION).decode() if glGetString(GL_VERSION) else "Unknown"
    glsl = glGetString(GL_SHADING_LANGUAGE_VERSION).decode() if glGetString(GL_SHADING_LANGUAGE_VERSION) else "Unknown"
    
    print(f"  ✓ Context created successfully")
    print(f"  Vendor: {vendor}")
    print(f"  Renderer: {renderer}")
    print(f"  OpenGL Version: {version}")
    print(f"  GLSL Version: {glsl}")
    
    pygame.quit()
    
except Exception as e:
    print(f"  ✗ FAILED TO CREATE CONTEXT: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("END DIAGNOSTIC REPORT")
print("=" * 60)
