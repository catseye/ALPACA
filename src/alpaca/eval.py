"""
Direct evaluator of ALPACA AST nodes.

XXX move some of these out into alpaca.analysis

"""

from alpaca.ast import AST
from alpaca.playfield import Playfield


def eval_state_ref(playfield, x, y, ast):
    if ast.type == 'StateRefEq':
        return ast.value
    elif ast.type == 'StateRefRel':
        return playfield.get(x + ast.value[0], y + ast.value[1])
    else:
        raise NotImplementedError


def eval_expr(playfield, x, y, ast):
    """Given a playfield and a position within it, and a boolean expression,
    return what the expression evaluates to at that position.
    
    """
    if ast.type == 'BoolOp':
        lhs = eval_expr(playfield, x, y, ast.children[0])
        rhs = eval_expr(playfield, x, y, ast.children[1])
        op = ast.value
        if op == 'and':
            return lhs and rhs
        elif op == 'or':
            return lhs or rhs
        elif op == 'xor':
            return not (lhs == rhs)
    elif ast.type == 'Not':
        return not eval_expr(playfield, x, y, ast.children[0])
    elif ast.type == 'Adjacency':
        state = eval_state_ref(playfield, x, y, ast.children[0])
        nb = ast.children[1]
        assert nb.type, 'Neighbourhood'
        nb = set([node.value for node in nb.children])
        count = 0
        for (dx, dy) in nb:
            if playfield.get(x + dx, y + dy) == state:
                count += 1
        #print "(%d,%d) has %d neighbours that are %s" % (x, y, count, state)
        return count >= int(ast.value)
    elif ast.type == 'Relational':
        raise NotImplementedError
    elif ast.type == 'BoolLit':
        if ast.value == 'true':
            return True
        elif ast.value == 'false':
            return False
        elif ast.value == 'guess':
            return False  # XXX randomly true or false
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError


def eval_rules(playfield, x, y, ast):
    """Given a playfield and a position within it, and a set of rules,
    return the "to" state for the rule that applies.
    
    """
    assert ast.type == 'Rules'
    for rule in ast.children:
        assert rule.type == 'Rule'
        s = rule.children[0]
        e = rule.children[1]
        if eval_expr(playfield, x, y, e):
            return eval_state_ref(playfield, x, y, s)
    return playfield.get(x, y)


def find_state_defn(state_id, ast):
    assert isinstance(state_id, basestring), \
      "why is %r not a string?" % state_id
    assert ast.type == 'Alpaca'
    defns = ast.children[0]
    assert defns.type == 'Definitions'
    for defn in defns.children:
        if defn.type == 'StateDefn':
            if state_id == defn.value:
                return defn
    raise KeyError, "No such state '%s'" % state_sym


def construct_representation_map(ast):
    map = {}
    assert ast.type == 'Alpaca'
    defns = ast.children[0]
    assert defns.type == 'Definitions'
    for defn in defns.children:
        if defn.type == 'StateDefn':
            repr = defn.children[0]
            assert repr.type == 'CharRepr'
            map[repr.value] = defn.value
    return map


def get_default_state(ast):
    assert ast.type == 'Alpaca'
    defns = ast.children[0]
    assert defns.type == 'Definitions'
    for defn in defns.children:
        if defn.type == 'StateDefn':
            return defn.value


def get_defined_playfield(ast):
    assert ast.type == 'Alpaca'
    playast = ast.children[1]
    assert playast.type == 'Playfield'
    repr_map = construct_representation_map(ast)
    pf = Playfield(get_default_state(ast), repr_map)
    for (x, y, ch) in playast.value:
        pf.set(x, y, repr_map[ch])
    pf.recalculate_limits()
    return pf


def evolve_playfield(playfield, new_pf, ast):
    # XXX TODO + 1, - 1's in here should reflect the maximum
    # neighbourhood used by any rule
    if playfield.min_y is None:
        return
    y = playfield.min_y - 1
    while y <= playfield.max_y + 1:
        x = playfield.min_x - 1
        while x <= playfield.max_x + 1:
            state_id = playfield.get(x, y)
            #print "state at (%d,%d): %s" % (x, y, state_id)
            state_ast = find_state_defn(state_id, ast)
            #print " => %r" % state_ast
            new_state_id = eval_rules(playfield, x, y, state_ast.children[3])
            #print "new state: %s" % new_state_id
            new_pf.set(x, y, new_state_id)
            x += 1
        y += 1
