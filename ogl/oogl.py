import ctypes

import numpy as np
from OpenGL import GL
from OpenGL.GL import *

class _MissingImport(object):
    def __init__(self, name):
        self.name = name

    def __getattr__(self, attr):
        raise ImportError(self.name)

try:
    import pygame
except ImportError:
    pygame = _MissingImport('pygame')

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

    @classmethod
    def enable(cls, *feats):
        for feat in feats:
            glEnable(feat)

    @classmethod
    def disable(cls, *feats):
        for feat in feats:
            glDisable(feat)

    @classmethod
    def blend_func(cls, src_func, dst_func):
        glBlendFunc(src_func, dst_func)

    @classproperty
    def shader_storage(cls):
        return ShaderStorageBindings.instance

    @classproperty
    def draw_framebuffer(cls):
        return Framebuffer(glGetInteger(GL_DRAW_FRAMEBUFFER_BINDING))

    @classproperty
    def read_framebuffer(cls):
        return Framebuffer(glGetInteger(GL_READ_FRAMEBUFFER_BINDING))

    @classproperty
    def texture_units(cls):
        return TextureUnits.instance

    @classproperty
    def texture_unit(cls):
        return TextureUnit(glGetInteger(GL_ACTIVE_TEXTURE))

    @classproperty
    def array_buffer(cls):
        return Buffer(glGetInteger(GL_ARRAY_BUFFER_BINDING))

    @classproperty
    def element_array_buffer(cls):
        return Buffer(glGetInteger(GL_ELEMENT_ARRAY_BUFFER_BINDING))

    @classproperty
    def max_color_attachments(cls):
        return glGetInteger(GL_MAX_COLOR_ATTACHMENTS)

class ShaderStorageBindings(object):
    def __getitem__(self, i):
        return ShaderStorageBinding(i)

ShaderStorageBindings.instance = ShaderStorageBindings()

class ShaderStorageBinding(object):
    def __init__(self, idx):
        self.idx = idx

    def __repr__(self):
        return 'ShaderStorageBinding({})'.format(self.idx)

    def bind(self, buf, offset=0, size=None):
        if isinstance(buf, int):
            buf = Buffer(buf)

        if size is None:
            size = buf.size - offset

        glBindBufferRange(GL_SHADER_STORAGE_BUFFER, self.idx, buf.obj, offset, size)

class TextureUnits(object):
    def _getitem__(self, i):
        return TextureUnit(i)

TextureUnits.instance = TextureUnits()

class TextureUnit(object):
    def __init__(self, idx):
        self.idx = idx

    def activate(self):
        glActiveTexture(GL_TEXTURE0 + self.idx)

    @property
    def texture_1d(self):
        return Texture(
            glGetInteger(GL_TEXTURE_BINDING_1D),
            self, GL_TEXTURE_1D,
        )

    @property
    def texture_2d(self):
        return Texture(
            glGetInteger(GL_TEXTURE_BINDING_2D),
            self, GL_TEXTURE_2D,
        )

    @property
    def texture_3d(self):
        return Texture(
            glGetInteger(GL_TEXTURE_BINDING_3D),
            self, GL_TEXTURE_3D,
        )

    @property
    def texture_1d_array(self):
        return Texture(
            glGetInteger(GL_TEXTURE_BINDING_1D_ARRAY),
            self, GL_TEXTURE_1D_ARRAY,
        )

    @property
    def texture_2d_array(self):
        return Texture(
            glGetInteger(GL_TEXTURE_BINDING_2D_ARRAY),
            self, GL_TEXTURE_2D_ARRAY,
        )

    @property
    def texture_rectangle(self):
        return Texture(
            glGetInteger(GL_TEXTURE_BINDING_RECTANGLE),
            self, GL_TEXTURE_RECTANGLE,
        )

    @property
    def texture_2d_multisample(self):
        return Texture(
            glGetInteger(GL_TEXTURE_BINDING_2D_MULTISAMPLE),
            self, GL_TEXTURE_2D_MULTISAMPLE,
        )

    @property
    def texture_2d_multisample_array(self):
        return Texture(
            glGetInteger(GL_TEXTURE_BINDING_2D_MULTISAMPLE_ARRAY),
            self, GL_TEXTURE_2D_MULTISAMPLE_ARRAY,
        )

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

        if isinstance(values[0], Texture):
            values = (values[0].activate().idx,)

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
    def type(self):
        self.vao.bind()
        return glGetVertexAttribiv(self.attr.location, GL_VERTEX_ATTRIB_ARRAY_TYPE)[0]

    @property
    def type_size(self):
        return C_SIZE.get(self.type, 1)

    @property
    def actual_stride(self):
        stride = self.stride
        if stride == 0:
            return self.size * self.type_size

    @property
    def offset(self):
        self.vao.bind()
        return glGetVertexAttribPointerv(self.attr.location, GL_VERTEX_ATTRIB_ARRAY_POINTER)

class Texture(object):
    def __init__(self, obj=None, unit=0, target=GL_TEXTURE_2D):
        if obj is None:
            obj = glGenTextures(1)

        if isinstance(unit, int):
            unit = TextureUnit(unit)

        self.obj = obj
        self.unit = unit
        self.target = target

    def free(self):
        glDeleteTextures(1, [obj])

    def bind(self):
        glBindTexture(self.target, self.obj)

    def activate(self, unit=None):
        if unit is None:
            unit = self.unit

        if isinstance(unit, int):
            unit = TextureUnit(unit)

        unit.activate()
        self.bind()

        return unit

    @property
    def min_filter(self):
        self.bind()
        return glGetTexParameteriv(self.target, GL_TEXTURE_MIN_FILTER)

    @min_filter.setter
    def min_filter(self, v):
        self.bind()
        glTexParameter(self.target, GL_TEXTURE_MIN_FILTER, v)

    @property
    def mag_filter(self):
        self.bind()
        return glGetTexParameteriv(self.target, GL_TEXTURE_MAG_FILTER)

    @mag_filter.setter
    def mag_filter(self, v):
        self.bind()
        glTexParameter(self.target, GL_TEXTURE_MAG_FILTER, v)

    @property
    def wrap_s(self):
        self.bind()
        return glGetTexParameteriv(self.target, GL_TEXTURE_WRAP_S)

    @wrap_s.setter
    def wrap_s(self, v):
        self.bind()
        glTexParameter(self.target, GL_TEXTURE_WRAP_S, v)

    @property
    def wrap_t(self):
        self.bind()
        return glGetTexParameteriv(self.target, GL_TEXTURE_WRAP_T)

    @wrap_t.setter
    def wrap_t(self, v):
        self.bind()
        glTexParameter(self.target, GL_TEXTURE_WRAP_T, v)

    @property
    def wrap_r(self):
        self.bind()
        return glGetTexParameteriv(self.target, GL_TEXTURE_WRAP_R)

    @wrap_r.setter
    def wrap_r(self, v):
        self.bind()
        glTexParameter(self.target, GL_TEXTURE_WRAP_R, v)

    def image_2d(self, data, width, height, format=GL_RGBA, type=GL_UNSIGNED_BYTE, intformat=GL_RGBA8, level=0):
        self.bind()
        glTexImage2D(self.target, level, intformat,
            width, height, 0, format, type, data,
        )
        return self

    def load_surface(self, surf):
        return self.image_2d(
            pygame.image.tostring(surf, 'RGBA', True),
            *surf.get_size(),
        )

class Framebuffer(_GLManagedObject):
    gl_ctor = glGenFramebuffers
    gl_dtor = glDeleteFramebuffers
    gl_bind = glBindFramebuffer

    def __enter__(self):
        self._prev_draw = Context.draw_framebuffer
        self._prev_read = Context.read_framebuffer
        self.bind(GL_FRAMEBUFFER)

    def __exit__(self, *exc):
        self._prev_draw.bind(GL_DRAW_FRAMEBUFFER)
        self._prev_read.bind(GL_READ_FRAMEBUFFER)

    @classproperty
    def default(cls):
        return cls(0)

    @property
    def attachments(self):
        return FramebufferAttachments(self)

    @property
    def status(self):
        with self:
            return glCheckFramebufferStatus(GL_FRAMEBUFFER)

    def blit_from(self, source, sx, sy, sw, sh, dx, dy, dw, dh, bits=GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT|GL_STENCIL_BUFFER_BIT, filter=GL_NEAREST):
        if isinstance(source, int):
            source = Framebuffer(source)

        with self.fb:
            source.bind(GL_READ_FRAMEBUFFER)
            glBlitFramebuffer(sx, sy, sx+sw, sy+sh, dx, dy, dx+dw, dy+dh, bits, filter)

class FramebufferAttachments(object):
    def __init__(self, fb):
        self.fb = fb

    def __getitem__(self, i):
        return FramebufferAttachment(self.fb, i)

    @property
    def colors(self):
        return FramebufferColorAttachments(self)

    @property
    def depth(self):
        return self[GL_DEPTH_ATTACHMENT]

    @property
    def stencil(self):
        return self[GL_STENCIL_ATTACHMENT]

    @property
    def depth_stencil(self):
        return self[GL_DEPTH_STENCIL_ATTACHMENT]

class FramebufferColorAttachments(object):
    def __init__(self, at):
        self.at = at

    def __len__(self):
        return Context.max_color_attachments

    def __getitem__(self, i):
        if i >= len(self) or i < 0:
            raise IndexError(i)
        return self.at[GL_COLOR_ATTACHMENT0 + i]

class FramebufferAttachment(object):
    def __init__(self, fb, idx):
        self.fb = fb
        self.idx = idx

    @property
    def type(self):
        with self.fb:
            return glGetFramebufferAttachmentParameteriv(
                GL_FRAMEBUFFER, self.idx,
                GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE,
            )[0]

    @property
    def object_name(self):
        with self.fb:
            return glGetFramebufferAttachmentParameteriv(
                GL_FRAMEBUFFER, self.idx,
                GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME,
            )[0]

    @property
    def object(self):
        tp = self.type
        if tp in (GL_NONE, GL_DEFAULT_FRAMEBUFFER):
            return None
        else:
            nm = self.object_name
            if tp == GL_RENDERBUFFER:
                return Renderbuffer(nm)
            elif tp == GL_TEXTURE:
                return Texture(nm)
            else:
                raise ValueError(tp)

    def attach_texture(self, tex, level=0):
        if isinstance(tex, int):
            tex = Texture(tex)

        with self.fb:
            glFramebufferTexture(
                GL_FRAMEBUFFER, self.idx,
                tex.obj, level,
            )

    def attach_renderbuffer(self, rb):
        if isinstance(rb, int):
            rb = Renderbuffer(rb)

        with self.fb:
            glFramebufferRenderbuffer(
                GL_FRAMEBUFFER, self.idx,
                GL_RENDERBUFFER, rb.obj,
            )

    def attach(self, obj):
        if isinstance(obj, Texture):
            self.attach_texture(obj)
        elif isinstance(obj, Renderbuffer):
            self.attach_renderbuffer(obj)
        else:
            raise TypeError(obj)

class Renderbuffer(_GLManagedObject):
    gl_ctor = glGenRenderbuffers
    gl_dtor = glDeleteRenderbuffers
    gl_bind = glBindRenderbuffer

    def storage(self, format, width, height, samples=0):
        self.bind(GL_RENDERBUFFER)
        glRenderbufferStorageMultisample(
            GL_RENDERBUFFER, 0, format, width, height,
        )
        return self

    @property
    def width(self):
        self.bind(GL_RENDERBUFFER)
        return glGetRenderbufferParameteriv(
            GL_RENDERBUFFER, GL_RENDERBUFFER_WIDTH,
        )[0]

    @property
    def height(self):
        self.bind(GL_RENDERBUFFER)
        return glGetRenderbufferParameteriv(
            GL_RENDERBUFFER, GL_RENDERBUFFER_HEIGHT,
        )[0]

    @property
    def format(self):
        self.bind(GL_RENDERBUFFER)
        return glGetRenderbufferParameteriv(
            GL_RENDERBUFFER, GL_RENDERBUFFER_INTERNAL_FORMAT,
        )[0]

    @property
    def samples(self):
        self.bind(GL_RENDERBUFFER)
        return glGetRenderbufferParameteriv(
            GL_RENDERBUFFER, GL_RENDERBUFFER_SAMPLES,
        )[0]
