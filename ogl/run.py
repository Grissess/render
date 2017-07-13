import time

import pygame
import numpy as np
from OpenGL.GL import *

pygame.SDL_GL_CONTEXT_MAJOR_VERSION = 17
pygame.SDL_GL_CONTEXT_MINOR_VERSION = 18

pygame.init()

pygame.display.gl_set_attribute(pygame.SDL_GL_CONTEXT_MAJOR_VERSION, 3)
pygame.display.gl_set_attribute(pygame.SDL_GL_CONTEXT_MINOR_VERSION, 3)

dispinfo = pygame.display.Info()
disp = pygame.display.set_mode(
    (dispinfo.current_w, dispinfo.current_h),
    pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.OPENGL,
    #pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.OPENGL,
)

#print(glGetInteger(GL_MAJOR_VERSION))
#print(glGetInteger(GL_MINOR_VERSION))
#exit()

quad = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, quad)
quad_verts = np.array([
    -1.0, -1.0, 0.0,
    1.0, -1.0, 0.0,
    0.0, 1.0, 0.0,
    -0.5, 0.5, 0.0,
], dtype=np.float32)
glBufferData(GL_ARRAY_BUFFER, quad_verts, GL_STATIC_DRAW)

vs = glCreateShader(GL_VERTEX_SHADER)
glShaderSource(vs, open('vertex/trivial.vs').read())
glCompileShader(vs)
stat = glGetShaderiv(vs, GL_COMPILE_STATUS)
if not stat:
    sts = glGetShaderInfoLog(vs)
    print(sts)
    exit()

fs = glCreateShader(GL_FRAGMENT_SHADER)
glShaderSource(fs, open('fragment/render/trivial.fs').read())
glCompileShader(fs)
stat = glGetShaderiv(fs, GL_COMPILE_STATUS)
if not stat:
    sts = glGetShaderInfoLog(fs)
    print(sts)
    exit()

prog = glCreateProgram()
glAttachShader(prog, vs)
glAttachShader(prog, fs)
glLinkProgram(prog)
stat = glGetProgramiv(prog, GL_LINK_STATUS)
if not stat:
    sts = glGetProgramInfoLog(prog)
    print(sts)
    exit()

vao = glGenVertexArrays(1)
glUseProgram(prog)
glBindVertexArray(vao)
vPosition = glGetAttribLocation(prog, "vPosition")
vTexCoord = glGetAttribLocation(prog, "vTexCoord")
glBindBuffer(GL_ARRAY_BUFFER, quad)
#vPosition = 0
glEnableVertexAttribArray(vPosition)
glVertexAttribPointer(vPosition, 3, GL_FLOAT, GL_FALSE, 0, 0)
#glBindBuffer(GL_ARRAY_BUFFER, 0)
#glVertexAttribPointer(vPosition, 3, GL_FLOAT, GL_FALSE, 0, quad_verts)

while True:
    for ev in pygame.event.get():
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_q:
            exit()
        if ev.type == pygame.QUIT:
            exit()

    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glViewport(0, 0, *disp.get_size())

    glUseProgram(prog)
    glBindVertexArray(vao)
    #vPosition = 0
    glEnableVertexAttribArray(vPosition)
    glBindBuffer(GL_ARRAY_BUFFER, quad)
    glVertexAttribPointer(vPosition, 3, GL_FLOAT, GL_FALSE, 0, 0)
    glDrawArrays(GL_TRIANGLES, 0, 3)

    pygame.display.flip()
    print(time.time(), 'FRAME')
