import inspect


def make_timer():
    registry = []

    def reg(interval):
        def inner(func):
            registry.append((func, interval))
            return func

        reg.all = registry
        return inner

    reg.all = reg.all if hasattr(reg, 'all') else []

    return reg


def generator(func):
    def wrapper(*a, **ka):
        if not inspect.isgeneratorfunction(func):
            func(*a, **ka)
            yield
        else:
            yield from func(*a, **ka)
    return wrapper
