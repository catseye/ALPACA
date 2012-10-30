"""
Direct evaluator of ALPACA AST nodes.

"""

from alpaca.ast import AST
from alpaca.playfield import Playfield
from alpaca.analysis import (
    find_state_defn, find_class_defn, state_defn_is_a,
)


def eval_state_ref(playfield, x, y, ast):
    if ast.type == 'StateRefEq':
        return ast.value
    elif ast.type == 'StateRefRel':
        return playfield.get(x + ast.value[0], y + ast.value[1])
    else:
        raise NotImplementedError


def eval_expr(alpaca, playfield, x, y, ast):
    """Given a playfield and a position within it, and a boolean expression,
    return what the expression evaluates to at that position.
    
    """
    if ast.type == 'BoolOp':
        lhs = eval_expr(alpaca, playfield, x, y, ast.children[0])
        rhs = eval_expr(alpaca, playfield, x, y, ast.children[1])
        op = ast.value
        if op == 'and':
            return lhs and rhs
        elif op == 'or':
            return lhs or rhs
        elif op == 'xor':
            return not (lhs == rhs)
    elif ast.type == 'Not':
        return not eval_expr(alpaca, playfield, x, y, ast.children[0])
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
        state0 = eval_state_ref(playfield, x, y, ast.children[0])
        state1 = eval_state_ref(playfield, x, y, ast.children[1])
        return state0 == state1
    elif ast.type == 'RelationalClass':
        state_id = eval_state_ref(playfield, x, y, ast.children[0])
        state_ast = find_state_defn(alpaca, state_id)
        class_id = ast.children[1].value
        return state_defn_is_a(state_ast, class_id)
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


def eval_rules(alpaca, playfield, x, y, ast):
    """Given a playfield and a position within it, and a set of rules,
    return the "to" state for the rule that applies.

    If no rule applies, None is returned.

    """
    assert ast.type == 'Rules'
    for rule in ast.children:
        assert rule.type == 'Rule'
        s = rule.children[0]
        e = rule.children[1]
        if eval_expr(alpaca, playfield, x, y, e):
            return eval_state_ref(playfield, x, y, s)
    return None


def evolve_playfield(playfield, new_pf, alpaca):
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
            state_ast = find_state_defn(alpaca, state_id)
            #print " => %r" % state_ast
            new_state_id = eval_rules(alpaca, playfield, x, y, state_ast.children[3])
            class_decls = state_ast.children[2]
            assert class_decls.type == 'MembershipDecls'
            for class_decl in class_decls.children:
                assert class_decl.type == 'ClassDecl'
                if new_state_id is not None:
                    break
                class_id = class_decl.value
                class_ast = find_class_defn(alpaca, class_id)
                new_state_id = eval_rules(alpaca, playfield, x, y, class_ast.children[0])
            if new_state_id is None:
                new_state_id = playfield.get(x, y)
            #print "new state: %s" % new_state_id
            new_pf.set(x, y, new_state_id)
            x += 1
        y += 1
