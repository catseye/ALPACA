class Playfield(object):
    def __init__(self, default):
        self.store = {}
        self.default = default
        self.recalculate_limits()

    def recalculate_limits(self):
        self.min_x = None
        self.min_y = None
        self.max_x = None
        self.max_y = None
        if len(self.store) == 0:
            return
        for (x, y) in self.store:
            if self.store[(x, y)] == self.default:
                continue
            if self.min_x is None or self.min_x > x:
                self.min_x = x
            if self.max_x is None or self.max_x < x:
                self.max_x = x
            if self.min_y is None or self.min_y > y:
                self.min_y = y
            if self.max_y is None or self.max_y < y:
                self.max_y = y
        #print "(%s,%s)-(%s,%s)" % (self.min_x, self.min_y, self.max_x, self.max_y)
          
    def set(self, x, y, value):
        """Does not recalculate limits."""
        if value == self.default:
            if (x, y) in self.store:
                del self.store[(x, y)]
        else:
            self.store[(x, y)] = value

    def get(self, x, y):
        return self.store.get((x, y), self.default)

    def represent(self, name):
        # XXX hardcoded
        if name == 'Alive':
            return '*'
        return ' '

    def __str__(self):
        s = ''
        y = self.min_y
        while y <= self.max_y:
            x = self.min_x
            while x <= self.max_x:
                s += self.represent(self.get(x, y))
                x += 1
            y += 1
            s += '\n'
        return s
