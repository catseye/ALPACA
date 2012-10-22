class AST(object):
    def __init__(self, type, children=None, value=None):
        self.type = type
        self.value = value
        if children is not None:
            self.children = children
        else:
            self.children = []

    def add_child(self, item):
        self.children.append(item)

    def __repr__(self):
        if self.value is None:
            return 'AST(%r,%r)' % (self.type, self.children)
        if not self.children:
            return 'AST(%r,value=%r)' % (self.type, self.value)
        return 'AST(%r,%r,value=%r)' % (self.type, self.children, self.value)
