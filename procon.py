import mmap, os

DEFAULT_BASE='/dev/shm/render'

def get(name, base=DEFAULT_BASE, size=None):
    if not os.path.exists(base):
        os.makedirs(base)
    fullpath = os.path.join(base, name)
    if not os.path.exists(fullpath) and size is None:
        raise ValueError('No file {}; did you start the producer, and is the base correct?'.format(fullpath))
    elif size is not None:
        f = open(fullpath, 'wb')
        f.write(b'\0' * size)
        f.close()
    fd = os.open(fullpath, os.O_RDWR)
    if size is None:
        size = 0
    return mmap.mmap(fd, size)
