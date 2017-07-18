import sys, os, ctypes
sys.path.append(os.path.normpath(os.path.join(os.getcwd(), '..')))

import glfw
import numpy as np

import procon
from oogl import *

if not glfw.init():
    exit()

data = procon.get('fft')
sig = procon.get('win')
DATA_SAMPLES = int(len(data) / 4)
data_type = ctypes.c_float * DATA_SAMPLES
data_ptr = data_type.from_buffer(data)
SIG_SAMPLES = int(len(sig) / 4)
sig_type = ctypes.c_float * SIG_SAMPLES
sig_ptr = sig_type.from_buffer(sig)

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
    -1.0, -1.0,
    1.0, 1.0,
    -1.0, 1.0,
], dtype=np.float32))

uvs = Buffer().set(np.array([
    0.0, 0.0,
    1.0, 0.0,
    1.0, 1.0,
    0.0, 0.0,
    1.0, 1.0,
    0.0, 1.0,
], dtype=np.float32))

spectrum = Buffer().set(data_ptr, usage=GL_STREAM_DRAW)
signal = Buffer().set(sig_ptr, usage=GL_STREAM_DRAW)
lin = Buffer().set(np.linspace(-1.0, 1.0, SIG_SAMPLES, False, dtype=np.float32))

prog = Program().attach(
    Shader(GL_VERTEX_SHADER).source(
        #open('vertex/freq_scale.vs').read(),
        open('vertex/trivial.vs').read(),
    ).compile(),
    Shader(GL_FRAGMENT_SHADER).source(
        open('fragment/render/spectrum.fs').read(),
    ).compile(),
).link()

prog.storage_blocks[1].bind(spectrum)

prog_bkgd = Program().attach(
    Shader(GL_VERTEX_SHADER).source(
        open('vertex/freq_scale.vs').read(),
    ).compile(),
    Shader(GL_FRAGMENT_SHADER).source(
        open('fragment/render/checkers.fs').read(),
    ).compile(),
).link()

prog_bkgd.storage_blocks[1].bind(spectrum)

prog_scope = Program().attach(
    Shader(GL_VERTEX_SHADER).source(
        open('vertex/function.vs').read(),
    ).compile(),
    Shader(GL_FRAGMENT_SHADER).source(
        open('fragment/render/solid.fs').read(),
    ).compile(),
).link()

prog.use()
vao = VertexArrayObject()
vao[prog.attributes.vPosition].bind(quad)
vao[prog.attributes.vTexCoord].bind(uvs)

prog_bkgd.use()
vao_bkgd = VertexArrayObject()
vao_bkgd[prog_bkgd.attributes.vPosition].bind(quad)
vao_bkgd[prog_bkgd.attributes.vTexCoord].bind(uvs)

prog_scope.use()
vao_scope = VertexArrayObject()
vao_scope[prog_scope.attributes.vX].bind(lin)
vao_scope[prog_scope.attributes.vY].bind(signal)
prog_scope.uniforms.uColor.set([0.0, 1.0, 0.0, 1.0])

while not glfw.window_should_close(win):
    glfw.make_context_current(win)

    winsz = glfw.get_window_size(win)
    Context.viewport(0, 0, *winsz)

    Context.clear_color()
    Context.clear()

    Context.blend_func(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    Context.enable(GL_BLEND)

    spectrum.update(data_ptr)
    signal.update(sig_ptr)

    #prog_bkgd.use()
    #vao_bkgd.draw(GL_TRIANGLES)

    prog_scope.use()
    vao_scope.draw(GL_LINE_STRIP)

    prog.use()
    #prog.uniforms.uWinSize.set(*winsz, type='f')
    vao.draw(GL_TRIANGLES)

    glfw.swap_buffers(win)

    glfw.poll_events()

glfw.terminate()
