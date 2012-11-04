"""
Compile ALPACA AST to Javascript.

CURRENTLY JUST A STUB.

"""

from alpaca.ast import AST


def compile(alpaca, file):
    """alpaca is an ALPACA description in AST form.  file is a file-like
    object to which the compiled code will be written.

    """
    file.write("""
/*
 * This file was AUTOMATICALLY generated from an ALPACA description.
 * EDIT AT YOUR OWN RISK!
 */
""")
    defns = alpaca.children[0]
    for defn in defns.children:
        if defn.type == 'StateDefn':
            compile_state_defn(alpaca, defn, file)
        elif defn.type == 'ClassDefn':
            pass
        elif defn.type == 'NbhdDefn':
            pass
        else:
            raise NotImplementedError(repr(defn))


def compile_state_defn(alpaca, defn, file):
    char_repr = defn.children[0]
    repr_decls = defn.children[1]
    membership = defn.children[2]
    rules = defn.children[3]
    file.write("function eval_%s() {\n" % defn.value);
    for rule in rules.children:
        dest = rule.children[0]
        expr = rule.children[1]
        file.write("if (/*%r*/) { state = /*%r*/; }\n" % (expr, dest))
    file.write("}\n\n")
