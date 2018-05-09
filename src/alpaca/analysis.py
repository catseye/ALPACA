"""
Functions for discovering certain things about an ALPACA description
given its AST.

"""

from alpaca.playfield import Playfield


def find_defn(alpaca, type, id):
    assert isinstance(id, basestring)
    for defn in alpaca.defns:
        if defn.type == type and defn.id == id:
            return defn
    raise KeyError, "No such %s '%s'" % (type, id)


def find_state_defn(alpaca, state_id):
    return find_defn(alpaca, 'StateDefn', state_id)


def find_class_defn(alpaca, class_id):
    return find_defn(alpaca, 'ClassDefn', class_id)


def find_nbhd_defn(alpaca, nbhd_id):
    return find_defn(alpaca, 'NbhdDefn', nbhd_id)


def state_defn_is_a(alpaca, state_ast, class_id, verbose=False):
    for class_decl in state_ast.classes:
        if verbose:
            print " ===> checking for {} in {}".format(class_id, repr(class_decl))
        assert class_decl.type == 'ClassDecl'
        if class_id == class_decl.id:
            return True
        class_ast = find_class_defn(alpaca, class_decl.id)
        if class_defn_is_a(alpaca, class_ast, class_id, verbose=verbose):
            return True
    return False


def class_defn_is_a(alpaca, class_ast, class_id, verbose=False):
    if class_ast.id == class_id:
        return True
    for class_decl in class_ast.classes:
        assert class_decl.type == 'ClassDecl'
        if class_id == class_decl.id:
            return True
        parent_class_ast = find_class_defn(alpaca, class_decl.id)
        if class_defn_is_a(alpaca, parent_class_ast, class_id, verbose=verbose):
            return True
    return False


def get_membership(alpaca, class_decls, membership):
    for class_decl in class_decls:
        assert class_decl.type == 'ClassDecl'
        if class_decl.id not in membership:
            membership.add(class_decl.id)
            get_class_membership(alpaca, class_decl.id, membership)


def get_state_membership(alpaca, state_id, membership):
    """Given a state ID, return a set of IDs of all classes of which that
    state is a member.

    """
    state_ast = find_state_defn(alpaca, state_id)
    get_membership(alpaca, state_ast.classes, membership)


def get_class_membership(alpaca, class_id, membership):
    """Given a class ID, return a set of IDs of all classes of which that
    class is a member.

    """
    class_ast = find_class_defn(alpaca, class_id)
    get_membership(alpaca, class_ast.classes, membership)


def get_class_map(alpaca):
    """Given an ALPACA description, return a dictionary where the keys are
    the IDs of classes and the values are the sets of IDs of states which are
    members of those classes.

    All classes are included in the map, even if they contain no states.

    """
    state_map = {}
    class_map = {}
    for defn in alpaca.defns:
        if defn.type == 'StateDefn':
            membership = set()
            get_state_membership(alpaca, defn.id, membership)
            state_map[defn.id] = membership
        if defn.type == 'ClassDefn':
            class_map[defn.id] = set()
    for (state_id, class_set) in state_map.iteritems():
        for class_id in class_set:
            class_map.setdefault(class_id, set()).add(state_id)
    return class_map


def construct_representation_map(alpaca):
    map_ = {}
    for defn in alpaca.defns:
        if defn.type == 'StateDefn':
            assert defn.char_repr.type == 'CharRepr'
            map_[defn.char_repr.value] = defn.id
    return map_


def get_default_state(alpaca):
    for defn in alpaca.defns:
        if defn.type == 'StateDefn':
            return defn.id


def get_defined_playfield(alpaca):
    assert alpaca.type == 'Alpaca'
    playast = alpaca.playfield
    assert playast.type == 'Playfield'
    if playast.value is None:
        return None
    repr_map = construct_representation_map(alpaca)
    pf = Playfield(get_default_state(alpaca), repr_map)
    for (x, y, ch) in playast.value:
        pf.set(x, y, repr_map[ch])
    pf.recalculate_limits()
    return pf


class BoundingBox(object):
    """
    
    >>> b = BoundingBox(-2, -3, 2, 3)
    >>> b
    BoundingBox(-2, -3, 2, 3)
    >>> b.expand_to_contain(4, 1)
    >>> b
    BoundingBox(-2, -3, 4, 3)
    >>> b.expand_to_contain(0, -4)
    >>> b
    BoundingBox(-2, -4, 4, 3)
    
    """
    def __init__(self, min_dx, min_dy, max_dx, max_dy):
        self.min_dx = min_dx
        self.min_dy = min_dy
        self.max_dx = max_dx
        self.max_dy = max_dy

    def expand_to_contain(self, dx, dy):
        if dx < self.min_dx:
            self.min_dx = dx
        if dx > self.max_dx:
            self.max_dx = dx
        if dy < self.min_dy:
            self.min_dy = dy
        if dy > self.max_dy:
            self.max_dy = dy

    def __repr__(self):
        return "BoundingBox(%d, %d, %d, %d)" % (
            self.min_dx, self.min_dy, self.max_dx, self.max_dy
        )


def fit_bounding_box(ast, bb):
    """Given an ALPACA AST, expand the given bounding box to
    encompass all relative references used within th AST.

    """
    if ast.type == 'StateRefRel':
        (dx, dy) = ast.value
        bb.expand_to_contain(dx, dy)
    for child in ast.all_children():
        fit_bounding_box(child, bb=bb)
