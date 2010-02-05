def cache_method(func):
    def wrapper(self, *args, **kw):
        cache_key = (args, kw)
        if not hasattr(self, '_method_cache'):
            self._method_cache = {}
        if cache_key in self._method_cache:
            return self._method_cache[cache_key]
        self._method_cache = func(self, *args, **kw)
    return wrapper 