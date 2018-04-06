class Playfield(object):
    def __init__(self, default, map):
        self.store = {}
        self.default = default
        self.recalculate_limits()
        self.repr_to_state = map
        self.state_to_repr = dict([(v, k) for (k, v) in map.iteritems()])

    def iteritems(self):
        y = self.min_y
        while y <= self.max_y:
            x = self.min_x
            while x <= self.max_x:
                c = self.get(x, y)
                if c != self.default:
                    yield (x, y, c)
                x += 1
            y += 1
        raise StopIteration

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
                self.set(x, y, self.repr_to_state[c])
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
        return self.state_to_repr[name]

    def to_str(self, min_x, min_y, max_x, max_y):
        s = ''
        y = min_y
        if y is None:
            return ''
        while y <= max_y:
            x = min_x
            while x <= max_x:
                s += self.represent(self.get(x, y))
                x += 1
            y += 1
            s += '\n'
        return s

    def __str__(self):
        return self.to_str(self.min_x, self.min_y, self.max_x, self.max_y)

    def to_svg(self, min_x, min_y, max_x, max_y, stylesheet=None):
        if stylesheet is None:
            stylesheet = 'rect { fill: white } .{} { fill: black }'.format(self.default)
        rects = []
        y = min_y
        while y is not None and y <= max_y:
            x = min_x
            while x <= max_x:
                state = self.get(x, y)
                rects.append(
                    '<rect class="{}" x="{}" y="{}" width="1" height="1" />'.format(state, x, y)
                )
                x += 1
            y += 1
        return """\
<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg viewBox="{} {} {} {}" version="1.1">
  <style type="text/css">
    {}
  </style>
  {}
</svg>""".format(min_x, min_y, max_x-min_x, max_y-min_y, stylesheet, '\n  '.join(rects))
