class Playfield(object):
    def __init__(self):
        self.store = {}
        self.default = ' '
        self.min_x = None
        self.min_y = None
        self.max_x = None
        self.max_y = None

    def set(self, x, y, value):
        if self.min_x is None or self.min_x > x:
            self.min_x = x
        if self.max_x is None or self.max_x < x:
            self.max_x = x
        if self.min_y is None or self.min_y > y:
            self.min_y = x
        if self.max_y is None or self.max_y < y:
            self.max_y = y
        self.store[(x, y)] = value

    def get(self, x, y):
        return self.store.get((x, y), self.default)
