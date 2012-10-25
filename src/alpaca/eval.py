"""
Direct evaluator of ALPACA AST nodes.

"""

from alpaca.ast import AST


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
        #nb = ast.children[1]
        nb = set(((0, -1), (-1, -1), (1, -1), (-1, 0), (1, 0), (0, 1), (-1, 1), (1, 1)))
        count = 0
        for (dx, dy) in nb:
            if playfield.get(x + dx, y + dx) == state:
                count += 1
        print "(%d,%d) has %d neighbours that are %s" % (x, y, count, state)
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
    for defn in defns:
        if defn.type == 'StateDefn':
            if state_id == defn.value:
                return defn
    raise KeyError, "No such state '%s'" % state_sym


def evolve_playfield(playfield, new_pf, ast):
    # XXX TODO + 1, - 1's in here should reflect the maximum
    # neighbourhood used by any rule
    y = playfield.min_y - 1
    while y <= playfield.max_y + 1:
        x = playfield.min_x - 1
        while x <= playfield.max_x + 1:
            state_id = playfield.get(x, y)
            #print "state at (%d,%d): %s" % (x, y, state_id)
            state_ast = find_state_defn(state_id, ast)
            #print " => %r" % state_ast
            new_state_id = eval_rules(playfield, x, y, state_ast.children[3])
            print "new state: %s" % new_state_id
            new_pf.set(x, y, new_state_id)
            x += 1
        y += 1
