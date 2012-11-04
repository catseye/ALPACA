class Playfield(object):
    def __init__(self, default, map):
        self.store = {}
        self.default = default
        self.recalculate_limits()
        self.map = map
        self._inverted_map = dict([(v, k) for (k, v) in map.iteritems()])

    def copy(self, pf):
        y = pf.min_y
        while y <= pf.max_y:
            x = pf.min_x
            while x <= pf.max_x:
                self.set(x, y, pf.get(x, y))
                x += 1
            y += 1
        self.recalculate_limits()

    def equals(self, pf):
        if (self.min_y != pf.min_y or
            self.max_y != pf.max_y or
            self.min_x != pf.min_x or
            self.max_x != pf.max_x):
            return False
        y = pf.min_y
        while y <= pf.max_y:
            x = pf.min_x
            while x <= pf.max_x:
                if self.get(x, y) != pf.get(x, y):
                    return False
                x += 1
            y += 1
        return True

    def load(self, f):
        y = 0
        for line in f:
            x = 0
            for c in line.rstrip('\r\n'):
                self.set(x, y, self.map[c])
                x += 1
            y += 1
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
        return self._inverted_map[name]

    def __str__(self):
        s = ''
        y = self.min_y
        if y is None:
            return ''
        while y <= self.max_y:
            x = self.min_x
            while x <= self.max_x:
                s += self.represent(self.get(x, y))
                x += 1
            y += 1
            s += '\n'
        return s
