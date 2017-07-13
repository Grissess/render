import sys

import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *

glutInitDisplayMode(GLUT_RGB | GLUT_DEPTH | GLUT_DOUBLE)
glutInit(sys.argv)
glutCreateWindow('Test')
glutFullScreen()

print('Renderer:', glGetString(GL_RENDERER))
print('Version:', glGetString(GL_VERSION))

quad = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, quad)
quad_verts = np.array([
    -0.5, -0.5, 0.0,
    0.5, -0.5, 0.0,
    0.5, 0.5, 0.0,
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
glEnableVertexAttribArray(vPosition)
glVertexAttribPointer(vPosition, 3, GL_FLOAT, GL_FALSE, 0, 0)

def render():
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glViewport(0, 0, glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT))

    glUseProgram(prog)
    glBindVertexArray(vao)
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

    glutSwapBuffers()

glutDisplayFunc(render)

glutMainLoop()

exit()
