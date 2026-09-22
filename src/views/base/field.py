class Field:
    def __init__(self, getter, default=None):
        self._getter = getter
        self.default = default

    def value(self):
        v = self._getter()
        v = v.strip() if isinstance(v, str) else v
        return v if v else self.default