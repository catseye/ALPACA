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
            for child in self.attrs[attr]:
                yield child
                for subchild in child.all_children():
                    yield subchild
        for attr in self.child_attrs:
            child = self.attrs[attr]
            yield child
            for subchild in child.all_children():
                yield subchild


class Alpaca(AST):
    children_attrs = ('defns',)
    child_attrs = ('playfield',)


class Neighbourhood(AST):
    children_attrs = ('children',)


class Playfield(AST):
    value_attrs = ('value',)


class CharRepr(AST):
    value_attrs = ('value',)


class StateDefn(AST):
    children_attrs = ('rules', 'classes',)
    child_attrs = ('char_repr',)
    value_attrs = ('id',)


class ClassDecl(AST):
    value_attrs = ('id',)


class ClassDefn(AST):
    children_attrs = ('rules', 'classes',)
    value_attrs = ('id',)


class NbhdDefn(AST):
    children_attrs = ('children',)
    value_attrs = ('id',)


class Rule(AST):
    child_attrs = ('expr', 'state_ref',)


class StateRefEq(AST):
    value_attrs = ('id',)


class StateRefRel(AST):
    value_attrs = ('value',)


class NbhdRef(AST):
    value_attrs = ('id',)


class Adjacency(AST):
    child_attrs = ('rel', 'nbhd',)
    value_attrs = ('count',)


class Relational(AST):
    child_attrs = ('lhs', 'rhs',)


class Not(AST):
    child_attrs = ('expr',)


class BoolOp(AST):
    child_attrs = ('lhs', 'rhs',)
    value_attrs = ('op',)


class BoolLit(AST):
    value_attrs = ('value',)
