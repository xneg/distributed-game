import inspect


def generator(func):
    def wrapper(*a, **ka):
        if not inspect.isgeneratorfunction(func):
            func(*a, **ka)
            yield
        else:
            yield from func(*a, **ka)
    return wrapper


def make_timer():
    registry = {}

    def reg(interval):
        def inner(func):
            class_name = f"{func.__module__}.{func.__qualname__.split('.')[0]}"
            if class_name not in registry:
                registry[class_name] = []
            registry[class_name].append((generator(func), interval))
            return generator(func)

        reg.all = registry
        return inner

    reg.all = reg.all if hasattr(reg, 'all') else {}

    return reg


def make_endpoint():
    registry = {}

    def reg(message_type):
        def inner(func):
            class_name = f"{func.__module__}.{func.__qualname__.split('.')[0]}"
            if class_name not in registry:
                registry[class_name] = {}
            registry[class_name][message_type] = generator(func)
            return generator(func)

        reg.all = registry
        return inner

    reg.all = reg.all if hasattr(reg, 'all') else {}

    return reg
