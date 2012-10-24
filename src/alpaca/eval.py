from alpaca.ast import AST


def eval_state_ref(playfield, x, y, ast):
    if ast.type == 'StateRefEq':
        return ast.value
    elif ast.type == 'StateRefRel':
        return playfield.get(x + ast.value[0], y + ast.value[1])
    else:
        raise ValueError

def eval_expr(playfield, x, y, ast):
    """Given a playfield and a position within it, and a boolean expression,
    return what the expression evaluates to at that position.
    
    """
    if ast.type == 'BoolOp':
        lhs = eval_expr(playfield, x, y, ast.children[0])
        rhs = eval_expr(playfield, x, y, ast.children[1])
        if op == 'and':
            return lhs and rhs
        elif op == 'or':
            return lhs or rhs
        elif op == 'xor':
            return not (lhs == rhs)
    else:
        return False
