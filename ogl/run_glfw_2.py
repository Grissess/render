import sys, os, ctypes
sys.path.append(os.path.normpath(os.path.join(os.getcwd(), '..')))

import glfw
import numpy as np

import procon
from oogl import *

if not glfw.init():
    exit()

data = procon.get('fft')
SAMPLES = int(len(data) / 4)
data_type = ctypes.c_float * SAMPLES
data_ptr = data_type.from_buffer(data)

glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
win = glfw.create_window(640, 480, "Test 2", None, None)
if not win:
    glfw.terminate()

glfw.make_context_current(win)

print('Renderer:', Context.renderer)
print('Version:', Context.version)

quad = Buffer().set(np.array([
    -1.0, -1.0,
    1.0, -1.0,
    1.0, 1.0,
    -1.0, 1.0,
], dtype=np.float32))

spectrum = Buffer().set(data_ptr)

prog = Program().attach(
    Shader(GL_VERTEX_SHADER).source(
        open('vertex/trivial.vs').read(),
    ).compile(),
    Shader(GL_FRAGMENT_SHADER).source(
        open('fragment/render/spectrum.fs').read(),
    ).compile(),
).link()

prog.storage_blocks[1].bind(spectrum)

vao = VertexArrayObject()
vao[prog.attributes.vPosition].bind(quad)

while not glfw.window_should_close(win):
    glfw.make_context_current(win)

    winsz = glfw.get_window_size(win)
    Context.viewport(0, 0, *winsz)

    Context.clear_color()
    Context.clear()

    prog.use()
    prog.uniforms.uWinSize.set(*winsz, type='f')
    spectrum.update(data_ptr)
    vao.draw(GL_TRIANGLE_FAN)

    glfw.swap_buffers(win)

    glfw.poll_events()

glfw.terminate()
