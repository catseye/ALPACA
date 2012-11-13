"""
Backend for compiling ALPACA AST to Javascript.  Not yet complete.

"""

from alpaca.analysis import (
    get_class_map, find_nbhd_defn, BoundingBox, fit_bounding_box,
    get_defined_playfield
)


class Compiler(object):
    def __init__(self, alpaca, file):
        """alpaca is an ALPACA description in AST form.  file is a file-like
        object to which the compiled code will be written.

        """
        self.alpaca = alpaca
        self.file = file

    def compile(self):
        bb = BoundingBox(0, 0, 0, 0)
        fit_bounding_box(self.alpaca, bb)
        self.file.write("""\
/*
 * This file was AUTOMATICALLY generated from an ALPACA description.
 * EDIT AT YOUR OWN RISK!
 */

Playfield = function() {
    this._store = {};
    this.min_x = undefined;
    this.min_y = undefined;
    this.max_x = undefined;
    this.max_y = undefined;

    this.get = function(x, y) {
        return this._store[x+','+y];
    };

    this.put = function(x, y, value) {
        if (this.min_x === undefined || x < this.min_x) this.min_x = x;
        if (this.max_x === undefined || x > this.max_x) this.max_x = x;
        if (this.min_y === undefined || y < this.min_y) this.min_y = y;
        if (this.max_y === undefined || y > this.max_y) this.max_y = y;
        if (value === undefined) {
            delete this._store[x+','+y];
        }
        this._store[x+','+y] = value;
    };
};

function in_nbhd_pred(pf, x, y, pred, nbhd) {
  var count = 0;
  for (var i = 0; i < len(nbhd); i++) {
    if (pred(pf.get(x+nbhd[i][0], y+nbhd[i][1]))) {
      count++;
    }
  }
  return count;
}

function in_nbhd_eq(pf, x, y, stateId, nbhd) {
  return in_nbhd_pred(pf, x, y, function(x) { return x === stateId; }, nbhd);
}

function evolve_playfield(pf, new_pf) {
  for (var y = pf.min_y - %d; y <= pf.max_y - %d; y++) {
    for (var x = pf.min_x - %d; x <= pf.max_x - %d; x++) {
      new_pf.set(x, y, evalState(pf, x, y))
    }
  }
}
""" % (bb.max_dy, bb.min_dy, bb.max_dx, bb.min_dx))
        class_map = get_class_map(self.alpaca)
        for (class_id, state_set) in class_map.iteritems():
            self.file.write("function is_%s(st) {\n" % class_id)
            self.file.write("  return ");
            for state_id in state_set:
                self.file.write("(st === '%s') || " % state_id)
            self.file.write("0;\n}\n\n")
        defns = self.alpaca.children[0]
        for defn in defns.children:
            if defn.type == 'ClassDefn':
                self.compile_class_defn(defn)
        for defn in defns.children:
            if defn.type == 'StateDefn':
                self.compile_state_defn(defn)
        self.write_evalstate_function()
        pf = get_defined_playfield(self.alpaca)
        if pf is not None:
            self.file.write("pf = new Playfield();\n")
            for (x, y, c) in pf.iteritems():
                self.file.write("pf.put(%d, %d, '%s');\n" % (x, y, c))
            self.file.write('/* %r */' % pf.state_to_repr)

    def write_evalstate_function(self):
        self.file.write("""\
function evalState(pf, x, y) {
  var stateId = pf.get(x, y);
""")
        defns = self.alpaca.children[0]
        for defn in defns.children:
            if defn.type == 'StateDefn':
                self.file.write("""\
  if (stateId === '%s') return eval_%s(pf, x, y);
""" % (defn.value, defn.value));
        self.file.write('}\n')

    def compile_class_defn(self, defn):
        membership = defn.children[1]
        rules = defn.children[0]
        self.file.write("function evalClass_%s(pf, x, y) {\nvar id;\n" % defn.value);
        for rule in rules.children:
            dest = rule.children[0]
            expr = rule.children[1]
            self.file.write("if (")
            self.compile_expr(expr)
            self.file.write(") {\n  return ")
            self.compile_state_ref(dest)
            self.file.write(";\n}\n" % (dest))
        for superclass in membership.children:
            self.file.write("id = evalClass_%s(pf, x, y);\n" % superclass.value)
            self.file.write("if (id !== undefined) return id;\n")
        self.file.write("return undefined;\n}\n\n")

    def compile_state_defn(self, defn):
        #char_repr = defn.children[0]
        #repr_decls = defn.children[1]
        membership = defn.children[2]
        rules = defn.children[3]
        self.file.write("function eval_%s(pf, x, y) {\nvar id;\n" % defn.value);
        for rule in rules.children:
            dest = rule.children[0]
            expr = rule.children[1]
            self.file.write("if (")
            self.compile_expr(expr)
            self.file.write(") {\n  return ")
            self.compile_state_ref(dest)
            self.file.write(";\n}\n" % (dest))
        for superclass in membership.children:
            self.file.write("id = evalClass_%s(pf, x, y);\n" % superclass.value)
            self.file.write("if (id !== undefined) return id;\n")
        self.file.write("return '%s';\n}\n\n" % defn.value)

    def compile_state_ref(self, ref):
        # compare to eval_state_ref
        if ref.type == 'StateRefEq':
            self.file.write("'%s'" % ref.value)
        elif ref.type == 'StateRefRel':
            self.file.write("pf.get(x+%d,y+%d)" % (ref.value[0], ref.value[1]))
        else:
            raise NotImplementedError(repr(ref))

    def compile_relation(self, ref, ast):
        if ast.type == 'ClassDecl':
            self.file.write('is_%s(' % ast.value)
            self.compile_state_ref(ref)
            self.file.write(")")
        else:
            self.file.write('(')
            self.compile_state_ref(ref)
            self.file.write('===')
            self.compile_state_ref(ast)
            self.file.write(')')

    def compile_expr(self, expr):
        if expr.type == 'BoolOp':
            self.file.write('(')
            self.compile_expr(expr.children[0])
            self.file.write({
                'or': '||',
                'and': '&&',
                'xor': '!==',
            }[expr.value])
            self.compile_expr(expr.children[1])
            self.file.write(')')
        elif expr.type == 'Not':
            self.file.write('!(')
            self.compile_expr(expr.children[0])
            self.file.write(')')
        elif expr.type == 'BoolLit':
            self.file.write(expr.value)
        elif expr.type == 'Relational':
            self.compile_relation(expr.children[0], expr.children[1])
        elif expr.type == 'Adjacency':
            count = expr.value
            rel = expr.children[0]
            nb = expr.children[1]
            if nb.type == 'NbhdRef':
                nb = find_nbhd_defn(self.alpaca, nb.value).children[0]
            if rel.type == 'ClassDecl':
                self.file.write("(in_nbhd_pred(pf, x, y, is_%s" % rel.value)
            else:
                self.file.write('(in_nbhd_eq(pf, x, y, ')
                self.compile_state_ref(rel)
            self.file.write(', [')
            self.file.write(','.join(
                ['[%d,%d]' % child.value for child in nb.children]
            ))
            self.file.write(']) >= %d)' % int(count))
        else:
            raise NotImplementedError(repr(expr))
