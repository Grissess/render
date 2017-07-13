def memoized(f):
    def inner(*args):
        if args in inner.cache:
            return inner.cache[args]
        res = f(*args)
        inner.cache[args] = res
        return res
    inner.cache = {}
    return inner
