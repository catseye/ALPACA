# encoding: UTF-8

class AST(object):
    children_attrs = ()
    child_attrs = ()
    value_attrs = ()

    def __init__(self, **kwargs):
        self.attrs = {}
        for attr in self.children_attrs:
            self.attrs[attr] = kwargs.pop(attr, [])
            for child in self.attrs[attr]:
                assert isinstance(child, AST), \
                  "child %r of %r is not an AST node" % (child, self)        
        for attr in self.child_attrs:
            self.attrs[attr] = kwargs.pop(attr, None)
            child = self.attrs[attr]
            assert isinstance(child, AST), \
              "child %r of %r is not an AST node" % (child, self)        
        for attr in self.value_attrs:
            self.attrs[attr] = kwargs.pop(attr, None)
        assert (not kwargs), "extra arguments supplied to {} node: {}".format(self.type, kwargs)

    @property
    def type(self):
        return self.__class__.__name__

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.attrs)

    def __getattr__(self, name):
        if name in self.attrs:
            return self.attrs[name]
        raise AttributeError(name)

    def all_children(self):
        for attr in self.children_attrs:
            for child in self.attrs(attr):
                yield child
                for subchild in child.all_children():
                    yield subchild
        for attr in self.child_attrs:
            yield child
            for subchild in child.all_children():
                yield subchild


class Alpaca(AST):
    children_attrs = ('defns',)
    child_attrs = ('playfield',)


class Neighbourhood(AST):
    children_attrs = ('children',)


class Playfield(AST):
    pass


class CharRepr(AST):
    value_attrs = ('value',)


class MembershipDecls(AST):
    children_attrs = ('children',)


class StateDefn(AST):
    pass

class ClassDecl(AST):
    pass

class ClassDefn(AST):
    pass

class NbhdDefn(AST):
    pass

class Rules(AST):
    pass

class Rule(AST):
    pass


class StateRefEq(AST):
    value_attrs = ('value',)


class StateRefRel(AST):
    value_attrs = ('value',)


class NbhdRef(AST):
    pass

class Adjacency(AST):
    child_attrs = ('lhs', 'rhs',)
    value_attrs = ('value',)


class Relational(AST):
    pass

class Not(AST):
    pass

class BoolOp(AST):
    pass


class BoolLit(AST):
    value_attrs = ('value',)
