import sys, os, ctypes, colorsys, time
sys.path.append(os.path.normpath(os.path.join(os.getcwd(), '..')))

import glfw
import numpy as np
import pygame

import procon
from oogl import *

if not glfw.init():
    exit()

base_time = time.time()

def real_time():
    return time.time() - base_time

def scaled_time(f):
    return f * real_time()

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
glfw.window_hint(glfw.SAMPLES, 4)
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

Context.shader_storage[1].bind(spectrum)

prog = Program().attach(
    Shader(GL_VERTEX_SHADER).source(
        #open('vertex/freq_scale.vs').read(),
        open('vertex/trivial.vs').read(),
    ).compile(),
    Shader(GL_FRAGMENT_SHADER).source(
        open('fragment/render/spectrum.fs').read(),
    ).compile(),
).link()

prog_bkgd = Program().attach(
    Shader(GL_VERTEX_SHADER).source(
        open('vertex/freq_scale.vs').read(),
    ).compile(),
    Shader(GL_FRAGMENT_SHADER).source(
        open('fragment/render/checkers.fs').read(),
    ).compile(),
).link()

prog_scope = Program().attach(
    Shader(GL_VERTEX_SHADER).source(
        open('vertex/function.vs').read(),
    ).compile(),
    Shader(GL_FRAGMENT_SHADER).source(
        open('fragment/render/solid.fs').read(),
    ).compile(),
).link()

prog_img = Program().attach(
    Shader(GL_VERTEX_SHADER).source(
        open('vertex/freq_scale.vs').read(),
    ).compile(),
    Shader(GL_FRAGMENT_SHADER).source(
        open('fragment/render/texture.fs').read(),
    ).compile(),
).link()

prog_pproc = Program().attach(
    Shader(GL_VERTEX_SHADER).source(
        open('vertex/trivial.vs').read(),
    ).compile(),
    Shader(GL_FRAGMENT_SHADER).source(
        open('fragment/postproc/wavy.fs').read(),
    ).compile(),
).link()

tex_img = Texture().load_surface(
    pygame.image.load('/home/grissess/Documents/trollface.png'),
)
tex_img.wrap_s = GL_REPEAT
tex_img.wrap_t = GL_REPEAT
tex_img.min_filter = GL_NEAREST
tex_img.mag_filter = GL_NEAREST

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

prog_img.use()
vao_img = VertexArrayObject()
vao_img[prog_img.attributes.vPosition].bind(quad)
vao_img[prog_img.attributes.vTexCoord].bind(uvs)
prog_img.uniforms.uColor.set([1.0, 0.0, 0.0, 0.5])
prog_img.uniforms.uMinFactor.set(0.5)
IMG_DIVISIONS = 8
IMG_MIN_F = 0.003
IMG_MAX_F = 0.7

prog_pproc.use()
vao_pproc = VertexArrayObject()
vao_pproc[prog_pproc.attributes.vPosition].bind(quad)
vao_pproc[prog_pproc.attributes.vTexCoord].bind(uvs)

last_size = None
fb = Framebuffer()
fb_tex = Texture()
fb_tex.wrap_s = GL_REPEAT
fb_tex.wrap_t = GL_REPEAT
fb_tex.min_filter = GL_NEAREST
fb_tex.mag_filter = GL_NEAREST
fb_ds = Renderbuffer()

while not glfw.window_should_close(win):
    glfw.make_context_current(win)

    winsz = glfw.get_window_size(win)
    Context.viewport(0, 0, *winsz)

    if last_size != winsz:
        print('Resizing FB to', winsz)

        fb_tex.image_2d(None, *winsz)
        fb_ds.storage(GL_DEPTH24_STENCIL8, *winsz)

        fb.attachments.colors[0].attach(fb_tex)
        fb.attachments.depth_stencil.attach(fb_ds)

        if fb.status != GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError(fb.status)

        last_size = winsz

    Context.clear_color()

    with fb:
        Context.clear()

        Context.blend_func(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        Context.enable(GL_BLEND)

        spectrum.update(data_ptr)
        signal.update(sig_ptr)

        prog_bkgd.use()
        vao_bkgd.draw(GL_TRIANGLES)

        prog_img.use()
        prog_img.uniforms.uTex.set(tex_img)
        for i in range(IMG_DIVISIONS):
            prog_img.uniforms.uColor.set(
                list(
                    colorsys.hls_to_rgb(
                        0.66 * i, 0.5, 1,
                    ),
                ) + [0.2],
            )
            prog_img.uniforms.uSampF.set(
                IMG_MIN_F + (i / IMG_DIVISIONS) * (IMG_MAX_F - IMG_MIN_F),
            )
            vao_img.draw(GL_TRIANGLES)

        glEnable(GL_MULTISAMPLE)
        prog_scope.use()
        vao_scope.draw(GL_LINE_STRIP)
        glDisable(GL_MULTISAMPLE)

        prog.use()
        #prog.uniforms.uWinSize.set(*winsz, type='f')
        vao.draw(GL_TRIANGLES)

    Context.clear()

    prog_pproc.use()
    prog_pproc.uniforms.uColor.set([1.0, 1.0, 1.0, 1.0])
    prog_pproc.uniforms.uFB.set(fb_tex)
    prog_pproc.uniforms.uPhaseOff.set(scaled_time(1.0))
    prog_pproc.uniforms.uAngle.set(scaled_time(8.0))
    vao_pproc.draw(GL_TRIANGLES)

    glfw.swap_buffers(win)

    glfw.poll_events()

glfw.terminate()
