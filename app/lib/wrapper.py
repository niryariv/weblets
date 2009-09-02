# unused for now... might come handy sometime
# http://downgra.de/2009/05/16/python-monkey-patching/
def wrap(orig_func):
    """ decorator to wrap an existing method of a class.
        e.g.

        @wrap(Post.write)
        def verbose_write(forig, self):
            print 'generating post: %s (from: %s)' % (self.title,
                                                      self.filename)
            return forig(self)

        the first parameter of the new function is the the original,
        overwritten function ('forig').
    """

    # har, some funky python magic NOW!
    @functools.wraps(orig_func)
    def outer(new_func):
        def wrapper(*args, **kwargs):
            return new_func(orig_func, *args, **kwargs)
        if inspect.ismethod(orig_func):
            setattr(orig_func.im_class, orig_func.__name__, wrapper)
        return wrapper
    return outer
