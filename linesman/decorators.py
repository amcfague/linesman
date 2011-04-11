import functools


try:
    from cProfile import Profile
except ImportError:
    from profile import Profile


def profiler(func):
    def wrapper(*args, **kwargs):
        _locals = locals()
        _globals = globals()

        prof = Profile()
        prof.runctx("result = func(args, kwargs)",
                    _globals, _locals)

        stats = prof.getstats()
        session = ProfilingSession(stats)

        # TODO Need to actually USE the profiling session for something...
        return _locals['result']

    return functools.update_wrapper(wrapper, func)
