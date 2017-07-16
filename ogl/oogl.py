import ctypes

import numpy as np
from OpenGL import GL
from OpenGL.GL import *

class _OOGLConfig(object):
    AUTO_FREE = False

ELEMS_PER_TYPE = {
    GL_FLOAT_VEC2: 2,
    GL_INT_VEC2: 2,
    GL_UNSIGNED_INT_VEC2: 2,
    GL_DOUBLE_VEC2: 2,
    GL_FLOAT_VEC3: 3,
    GL_INT_VEC3: 3,
    GL_UNSIGNED_INT_VEC3: 3,
    GL_DOUBLE_VEC3: 3,
    GL_FLOAT_VEC4: 4,
    GL_INT_VEC4: 4,
    GL_UNSIGNED_INT_VEC4: 4,
    GL_DOUBLE_VEC4: 4,
}

BASE_TYPE = {
    GL_FLOAT: GL_FLOAT,
    GL_FLOAT_VEC2: GL_FLOAT,
    GL_FLOAT_VEC3: GL_FLOAT,
    GL_FLOAT_VEC4: GL_FLOAT,
    GL_INT: GL_INT,
    GL_INT_VEC2: GL_INT,
    GL_INT_VEC3: GL_INT,
    GL_INT_VEC4: GL_INT,
    GL_UNSIGNED_INT: GL_UNSIGNED_INT,
    GL_UNSIGNED_INT_VEC2: GL_UNSIGNED_INT,
    GL_UNSIGNED_INT_VEC3: GL_UNSIGNED_INT,
    GL_UNSIGNED_INT_VEC4: GL_UNSIGNED_INT,
    GL_DOUBLE: GL_DOUBLE,
    GL_DOUBLE_VEC2: GL_DOUBLE,
    GL_DOUBLE_VEC3: GL_DOUBLE,
    GL_DOUBLE_VEC4: GL_DOUBLE,
}

C_SIZE = {
    GL_BYTE: 1,
    GL_UNSIGNED_BYTE: 1,
    GL_SHORT: 2,
    GL_UNSIGNED_SHORT: 2,
    GL_INT: 4,
    GL_UNSIGNED_INT: 4,
    GL_FLOAT: 4,
    GL_DOUBLE: 8,
}

class classproperty(object):
    def __init__(self, getter, doc=None):
        self._getter = getter
        self.__doc__ = doc

    def getter(self, fn):
        self._getter = fn
        return fn

    def __get__(self, inst, cls):
        return self._getter(cls)

class Context(object):
    @classproperty
    def version(cls):
        return glGetString(GL_VERSION)

    @classproperty
    def renderer(cls):
        return glGetString(GL_RENDERER)

    @classproperty
    def max_vertex_attribs(cls):
        return glGetInteger(GL_MAX_VERTEX_ATTRIBS)

    @classproperty
    def current_program(cls):
        return Program(glGetInteger(GL_CURRENT_PROGRAM))

    @classmethod
    def viewport(cls, x, y, w, h):
        glViewport(x, y, w, h)

    @classmethod
    def clear(cls, bits=GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT):
        glClear(bits)

    @classmethod
    def clear_color(cls, r=0.0, g=0.0, b=0.0, a=1.0):
        glClearColor(r, g, b, a)

class _GLManagedObject(object):
    gl_ctor = None
    gl_dtor = None
    gl_bind = None

    def __new__(cls, obj=None):
        if obj in (GL_INVALID_INDEX, -1):
            return None
        return super().__new__(cls)

    def __init__(self, obj=None):
        if obj is None:
            obj = self.gl_ctor(1)
        self.obj = obj

    @classmethod
    def create_many(cls, num):
        if num == 1:
            return cls()
        return map(cls, cls.gl_ctor(num))

    def free(self):
        self.gl_dtor(1, arrays.GLuintArray.asArray([self.obj]))

    def __del__(self):
        if _OOGLConfig.AUTO_FREE:
            self.free()

    def bind(self, *args):
        if self.gl_bind is None:
            raise TypeError('{} cannot be bound'.format(self))

        self.gl_bind(*(args + (self.obj,)))
        return self

class Buffer(_GLManagedObject):
    gl_ctor = glGenBuffers
    gl_dtor = glDeleteBuffers
    gl_bind = glBindBuffer

    def set(self, data=None, size=None, usage=GL_STATIC_DRAW):
        if size is None and data is None:
            size = 0

        self.bind(GL_ARRAY_BUFFER)
        if size is None:
            glBufferData(GL_ARRAY_BUFFER, data, usage)
        else:
            glBufferData(GL_ARRAY_BUFFER, size, data, usage)

        return self

    def update(self, data, offset=0, size=None):
        self.bind(GL_ARRAY_BUFFER)
        print(data, self.size, size)
        if size is None:
            glBufferSubData(GL_ARRAY_BUFFER, offset, data)
        else:
            glBufferSubData(GL_ARRAY_BUFFER, offset, size, data)

        return self

    @property
    def size(self):
        self.bind(GL_ARRAY_BUFFER)
        return glGetBufferParameteriv(GL_ARRAY_BUFFER, GL_BUFFER_SIZE)

class Shader(object):
    def __init__(self, type):
        self.obj = glCreateShader(type)

    def source(self, source):
        glShaderSource(self.obj, source)
        return self

    def compile(self):
        glCompileShader(self.obj)
        stat = glGetShaderiv(self.obj, GL_COMPILE_STATUS)
        if not stat:
            raise RuntimeError(glGetShaderInfoLog(self.obj))
        return self

class Program(object):
    def __init__(self, obj=None):
        if obj is None:
            obj = glCreateProgram()
        self.obj = obj

    def __repr__(self):
        return 'Program({})'.format(self.obj)

    def attach(self, *shds):
        for shd in shds:
            if not isinstance(shd, int):
                shd = shd.obj

            glAttachShader(self.obj, shd)
        return self

    def link(self):
        glLinkProgram(self.obj)
        stat = glGetProgramiv(self.obj, GL_LINK_STATUS)
        if not stat:
            raise RuntimeError(glGetProgramInfoLog(self.obj))
        return self

    def use(self):
        glUseProgram(self.obj)
        return self

    @property
    def uniforms(self):
        return ProgramUniforms(self)

    @property
    def uniform_blocks(self):
        return ProgramUniformBlocks(self)

    @property
    def attributes(self):
        return ProgramAttributes(self)

    @property
    def attrib_name_max_len(self):
        return int(glGetProgramiv(self.obj, GL_ACTIVE_ATTRIBUTE_MAX_LENGTH))

c_char_p_p = ctypes.POINTER(ctypes.POINTER(ctypes.c_char))

class ProgramUniforms(object):
    def __init__(self, prog):
        self.prog = prog

    def __len__(self):
        return glGetProgramiv(self.prog.obj, GL_ACTIVE_UNIFORMS)

    def __getitem__(self, i):
        if i >= len(self) or i < 0:
            raise IndexError(i)
        return ProgramUniform(self.prog, i, *glGetActiveUniform(self.prog.obj, i))

    def __getattr__(self, name):
        nm = ctypes.c_char_p(name.encode('utf8'))
        ar = arrays.GLuintArray.zeros(1)
        glGetUniformIndices(self.prog.obj, 1,
            ctypes.cast(ctypes.pointer(nm), c_char_p_p),
            ar,
        )
        return self[ar[0]]

class ProgramUniform(object):
    def __init__(self, prog, idx, name, len, type):
        self.prog = prog
        self.idx = idx
        self.name = name
        self.len = len
        self.type = type

    def __len__(self):
        return self.len

    def __repr__(self):
        return '<Uniform {}:{} {}[{}] of {}>'.format(
            self.idx, self.type, self.name, self.len,
            self.prog,
        )

    @property
    def location(self):
        return glGetUniformLocation(self.prog.obj, self.name)

    def set(self, *values, type=None):
        if isinstance(values[0], np.ndarray):
            values = values[0]

        count = len(values)
        try:
            cs = len(values[0])
            if type is None:
                if isinstance(values[0][0], int):
                    type = 'i'
                else:
                    type = 'f'
        except (TypeError, ValueError):
            cs = 1
            if len(values) <= 4:
                cs = len(values)
                count = 1
            if type is None:
                if isinstance(values[0], int):
                    type = 'i'
                else:
                    type = 'f'

        if not 1 <= cs <= 4:
            raise ValueError('component size expected to be in [1, 4], not {}'.format(cs))

        self.prog.use()
        getattr(GL, 'glUniform{}{}v'.format(cs, type))(self.location, count, values)

class ProgramUniformBlocks(object):
    def __init__(self, prog):
        self.prog = prog

    def __len__(self):
        return glGetProgramiv(self.prog.obj, GL_ACTIVE_UNIFORM_BLOCKS)

    def __getitem__(self, i):
        if i >= len(self) or i < 0:
            raise IndexError(i)
        return ProgramUniformBlock(self.prog, i)

    def __getattr__(self, name):
        return self[glGetUniformBlockIndex(self.prog.obj, name)]

class ProgramUniformBlock(object):
    def __init__(self, prog, idx):
        self.prog = prog
        self.idx = idx

    def __repr__(self, prog, idx):
        return '<Uniform block {} of {}>'.format(
            self.idx, self.prog,
        )

    def bind(self, buf, offset=0, size=None):
        if isinstance(buf, int):
            buf = Buffer(buf)

        if size is None:
            size = buf.size - offset

        glBindBufferRange(GL_UNIFORM_BUFFER, self.idx, buf.obj, offset, size)

    @property
    def size(self):
        return glGetActiveUniformBlockiv(self.prog.obj, self.idx,
            GL_UNIFORM_BLOCK_DATA_SIZE,
        )

    @property
    def buffer(self):
        return Buffer(glGetActiveUniformBlockiv(self.prog.obj, self.idx,
            GL_UNIFORM_BLOCK_BINDING,
        ))

    @property
    def uniforms(self):
        num = glGetActiveUniformBlockiv(self.prog.obj, self.idx,
            GL_UNIFORM_BLOCK_ACTIVE_UNIFORMS,
        )
        indices = arrays.GLintArray.zeros(num)
        glGetActiveUniformBlockiv(self.prog.obj, self.idx,
            GL_UNIFORM_BLOCK_ACTIVE_UNIFORMS_INDICES,
            indices,
        )
        return [self.prog.uniforms[i] for i in indices]

    @property
    def is_in_vertex(self):
        return glGetActiveUniformBlockiv(self.prog.obj, self.idx,
            GL_UNIFORM_BLOCK_REFERENCED_BY_VERTEX_SHADER,
        )

    @property
    def is_in_geometry(self):
        return glGetActiveUniformBlockiv(self.prog.obj, self.idx,
            GL_UNIFORM_BLOCK_REFERENCED_BY_GEOMETRY_SHADER,
        )

    @property
    def is_in_fragment(self):
        return glGetActiveUniformBlockiv(self.prog.obj, self.idx,
            GL_UNIFORM_BLOCK_REFERENCED_BY_FRAGMENT_SHADER,
        )

class ProgramAttributes(object):
    def __init__(self, prog):
        self.prog = prog

    def __len__(self):
        return glGetProgramiv(self.prog.obj, GL_ACTIVE_ATTRIBUTES)

    def __getitem__(self, i):
        if i >= len(self) or i < 0:
            raise IndexError(i)
        olen = constants.GLsizei(0)
        osize = constants.GLint(0)
        otype = constants.GLenum(0)
        namebuf = ctypes.create_string_buffer(self.prog.attrib_name_max_len)

        glGetActiveAttrib(self.prog.obj, i, len(namebuf),
            ctypes.pointer(olen), ctypes.pointer(osize),
            ctypes.pointer(otype), namebuf,
        )

        return ProgramAttribute(self.prog, i,
            namebuf.value, osize.value, otype.value,
        )

    def __getattr__(self, name):
        if isinstance(name, str):
            name = name.encode('utf8')
        for attr in self:
            if attr.name == name:
                return attr
        raise AttributeError(name)

class ProgramAttribute(object):
    def __init__(self, prog, idx, name, size, type):
        self.prog = prog
        self.idx = idx
        self.name = name
        self.size = size
        self.type = type

    def __repr__(self):
        return '<Attr {}:{} {}[{}] of {}>'.format(
            self.idx, self.type, self.name, self.size,
            self.prog,
        )

    @property
    def elements(self):
        return ELEMS_PER_TYPE.get(self.type, 1)

    @property
    def base_type(self):
        return BASE_TYPE.get(self.type, GL_FLOAT)

    @property
    def base_size(self):
        return C_SIZE.get(self.base_type, 1)

    @property
    def elem_size(self):
        return self.base_size * self.elements

    @property
    def location(self):
        return glGetAttribLocation(self.prog.obj, self.name)

class VertexArrayObject(_GLManagedObject):
    gl_ctor = glGenVertexArrays
    gl_dtor = glDeleteVertexArrays
    gl_bind = glBindVertexArray

    def __getitem__(self, i):
        if isinstance(i, int):
            prog = Context.current_program
            i = prog.attributes[i]

        return VertexArrayBinding(self, i)


    def draw(self, prim, start=0, count=None):
        self.bind()

        if count is None:
            end = 0
            for i in range(Context.max_vertex_attribs):
                try:
                    attr = self[i]
                except IndexError:
                    continue
                buf = attr.buffer
                if buf is not None:
                    end = max((end, (buf.size - attr.offset) // attr.actual_stride))
            count = int(end - start)

        glDrawArrays(prim, start, count)

class VertexArrayBinding(object):
    def __init__(self, vao, attr):
        self.vao = vao
        self.attr = attr

    def bind(self, buffer=None, type=None, stride=0, offset=0, norm=False):
        self.vao.bind()

        if buffer is not None:
            buffer.bind(GL_ARRAY_BUFFER)

        if type is None:
            type = self.attr.base_type

        glVertexAttribPointer(self.attr.location, self.attr.elements,
            type, norm, 0, ctypes.c_void_p(offset),
        )
        glEnableVertexAttribArray(self.attr.location)

    def disable(self):
        self.vao.bind()
        glDisableVertexAttribArray(self.attr.location)

    @property
    def is_enabled(self):
        self.vao.bind()
        return glGetVertexAttribiv(self.attr.location, GL_VERTEX_ATTRIB_ARRAY_ENABLED)[0]

    @property
    def buffer(self):
        self.vao.bind()
        return Buffer(glGetVertexAttribiv(self.attr.location, GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING)[0])

    @property
    def size(self):
        self.vao.bind()
        return glGetVertexAttribiv(self.attr.location, GL_VERTEX_ATTRIB_ARRAY_SIZE)[0]

    @property
    def stride(self):
        self.vao.bind()
        return glGetVertexAttribiv(self.attr.location, GL_VERTEX_ATTRIB_ARRAY_STRIDE)[0]

    @property
    def actual_stride(self):
        stride = self.stride
        if stride == 0:
            return self.size

    @property
    def offset(self):
        self.vao.bind()
        return glGetVertexAttribPointerv(self.attr.location, GL_VERTEX_ATTRIB_ARRAY_POINTER)
