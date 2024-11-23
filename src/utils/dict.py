## Version 1.0
# class CaseInsensitiveDict(dict):
#     """
#     A case-insensitive dictionary wrapper.
#     Example:
#         >>> d = CaseInsensitiveDict({'Hello': 1, 'World': 2})
#         >>> d['hello']  # Returns 1
#         >>> d['HELLO']  # Returns 1
#         >>> d['unknown']  # Raises KeyError
#     """
#     def __getitem__(self, key: str):
#         try:
#             # Search for a key that matches in a case-insensitive manner
#             return next(
#                 value for k, value in self.items() 
#                 if k.lower() == key.lower()
#             )
#         except StopIteration:
#             # Raise KeyError to match behavior of dict
#             raise KeyError(key)

#     def get(self, key: str, default=None):
#         # Attempt to retrieve the key, return default if not found
#         try:
#             return self[key]
#         except KeyError:
#             return default

# Version 2.0
class CaseInsensitiveDict:
    def __init__(self, *args, **kwargs):
        self._store = {}
        self.update(*args, **kwargs)

    def _lower_key(self, key):
        return key.lower() if isinstance(key, str) else key

    def __setitem__(self, key, value):
        lower_key = self._lower_key(key)
        self._store[lower_key] = (key, value)

    def __getitem__(self, key):
        lower_key = self._lower_key(key)
        if lower_key in self._store:
            return self._store[lower_key][1]
        raise KeyError(key)

    def __delitem__(self, key):
        lower_key = self._lower_key(key)
        if lower_key in self._store:
            del self._store[lower_key]
        else:
            raise KeyError(key)

    def get(self, key, default=None):
        return self._store.get(self._lower_key(key), (None, default))[1]

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v

    def __contains__(self, key):
        return self._lower_key(key) in self._store

    def keys(self):
        return (original_key for original_key, _ in self._store.values())

    def items(self):
        return ((original_key, value) for original_key, value in self._store.values())

    def values(self):
        return (value for _, value in self._store.values())

    def __repr__(self):
        return f"{self.__class__.__name__}({dict(self.items())})"