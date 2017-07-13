import sys, os
sys.path.append(os.path.normpath(os.path.join(os.getcwd(), '..')))

import glfw
import numpy as np
from OpenGL.GL import *

import procon

if not glfw.init():
    exit()

data = procon.get('fft')
SAMPLES = int(len(data) / 4)
shader_defines = '#define SAMPLES {}\n'.format(SAMPLES)

glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
win = glfw.create_window(640, 480, "Test", None, None)
if not win:
    glfw.terminate()

glfw.make_context_current(win)

print('Renderer:', glGetString(GL_RENDERER))
print('Version:', glGetString(GL_VERSION))

quad = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, quad)
quad_verts = np.array([
    -1.0, -1.0,
    1.0, -1.0,
    1.0, 1.0,
    -1.0, 1.0,
], dtype=np.float32)
glBufferData(GL_ARRAY_BUFFER, quad_verts, GL_STATIC_DRAW)

vs = glCreateShader(GL_VERTEX_SHADER)
glShaderSource(vs, open('vertex/trivial.vs').read().replace('@SHADER_DEFINES@', shader_defines))
glCompileShader(vs)
stat = glGetShaderiv(vs, GL_COMPILE_STATUS)
if not stat:
    sts = glGetShaderInfoLog(vs)
    print(sts)
    exit()

fs = glCreateShader(GL_FRAGMENT_SHADER)
glShaderSource(fs, open('fragment/render/spectrum.fs').read().replace('@SHADER_DEFINES@', shader_defines))
glCompileShader(fs)
stat = glGetShaderiv(fs, GL_COMPILE_STATUS)
if not stat:
    sts = glGetShaderInfoLog(fs)
    print(sts)
    exit()

prog = glCreateProgram()
glAttachShader(prog, vs)
glAttachShader(prog, fs)
#glBindFragDataLocation(prog, 0, "FragColor")
glLinkProgram(prog)
stat = glGetProgramiv(prog, GL_LINK_STATUS)
if not stat:
    sts = glGetProgramInfoLog(prog)
    print(sts)
    exit()

vao = glGenVertexArrays(1)
glBindVertexArray(vao)
glUseProgram(prog)
vPosition = glGetAttribLocation(prog, "vPosition")
#vTexCoord = glGetAttribLocation(prog, "vTexCoord")
glBindBuffer(GL_ARRAY_BUFFER, quad)
glEnableVertexAttribArray(vPosition)
glVertexAttribPointer(vPosition, 2, GL_FLOAT, GL_FALSE, 0, None)
uSpectrum = glGetUniformLocation(prog, "uSpectrum")
uWinSize = glGetUniformLocation(prog, "uWinSize")

while not glfw.window_should_close(win):

    glfw.make_context_current(win)

    #print('winsz:', glfw.get_window_size(win))
    winsz = glfw.get_window_size(win)
    glViewport(0, 0, *winsz)

    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glUseProgram(prog)
    data_array = np.frombuffer(data[:], dtype=np.float32)
    glUniform1fv(uSpectrum, 513, data_array)
    glUniform2f(uWinSize, *winsz)
    glBindVertexArray(vao)
    glDrawArrays(GL_TRIANGLE_FAN, 0, 4)

    glfw.swap_buffers(win)

    glfw.poll_events()
    
    #print('Frame')

glfw.terminate()
