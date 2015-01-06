"""
Backend for compiling ALPACA AST to Javascript.  Perhaps not complete.

"""

from alpaca.analysis import (
    get_class_map, find_nbhd_defn, BoundingBox, fit_bounding_box,
    get_defined_playfield, construct_representation_map
)


# We'll just stick (almost) the entire yoob/playfield.js file inline here
# see https://github.com/catseye/yoob.js for where this came from (v0.2)
YOOB_PLAYFIELD_JS = r"""
var yoob = {};
if (typeof window !== 'undefined') {
    if (!window.yoob) window.yoob = {};
    yoob = window.yoob;
}

/*
 * A two-dimensional Cartesian grid of values.
 */
yoob.Playfield = function() {
    this._store = {};
    this.minX = undefined;
    this.minY = undefined;
    this.maxX = undefined;
    this.maxY = undefined;
    this._default = undefined;

    /*
     * Set the default value for this Playfield.  This
     * value is returned by get() for any cell that was
     * never written to, or had `undefined` put() into it.
     */
    this.setDefault = function(v) {
        this._default = v;
    };

    /*
     * Obtain the value at (x, y).  The default value will
     * be returned if the cell was never written to.
     */
    this.get = function(x, y) {
        var v = this._store[x+','+y];
        if (v === undefined) return this._default;
        return v;
    };

    /*
     * Write a new value into (x, y).  Note that writing
     * `undefined` into a cell has the semantics of deleting
     * the value at that cell; a subsequent get() for that
     * location will return this Playfield's default value.
     */
    this.put = function(x, y, value) {
        var key = x+','+y;
        if (value === undefined || value === this._default) {
            delete this._store[key];
            return;
        }
        if (this.minX === undefined || x < this.minX) this.minX = x;
        if (this.maxX === undefined || x > this.maxX) this.maxX = x;
        if (this.minY === undefined || y < this.minY) this.minY = y;
        if (this.maxY === undefined || y > this.maxY) this.maxY = y;
        this._store[key] = value;
    };

    /*
     * Like put(), but does not update the playfield bounds.  Do
     * this if you must do a batch of put()s in a more efficient
     * manner; after doing so, call recalculateBounds().
     */
    this.putDirty = function(x, y, value) {
        var key = x+','+y;
        if (value === undefined || value === this._default) {
            delete this._store[key];
            return;
        }
        this._store[key] = value;
    };

    /*
     * Recalculate the bounds (min/max X/Y) which are tracked
     * internally to support methods like foreach().  This is
     * not needed *unless* you've used putDirty() at some point.
     * (In which case, call this immediately after your batch
     * of putDirty()s.)
     */
    this.recalculateBounds = function() {
        this.minX = undefined;
        this.minY = undefined;
        this.maxX = undefined;
        this.maxY = undefined;

        for (var cell in this._store) {
            var pos = cell.split(',');
            var x = parseInt(pos[0], 10);
            var y = parseInt(pos[1], 10);
            if (this.minX === undefined || x < this.minX) this.minX = x;
            if (this.maxX === undefined || x > this.maxX) this.maxX = x;
            if (this.minY === undefined || y < this.minY) this.minY = y;
            if (this.maxY === undefined || y > this.maxY) this.maxY = y;
        }
    };

    /*
     * Clear the contents of this Playfield.
     */
    this.clear = function() {
        this._store = {};
        this.minX = undefined;
        this.minY = undefined;
        this.maxX = undefined;
        this.maxY = undefined;
    };

    /*
     * Load a string into this Playfield.
     * The string may be multiline, with newline (ASCII 10)
     * characters delimiting lines.  ASCII 13 is ignored.
     *
     * If transformer is given, it should be a one-argument
     * function which accepts a character and returns the
     * object you wish to write into the playfield upon reading
     * that character.
     */
    this.load = function(x, y, string, transformer) {
        var lx = x;
        var ly = y;
        if (transformer === undefined) {
            transformer = function(c) {
                if (c === ' ') {
                    return undefined;
                } else {
                    return c;
                }
            }
        }
        for (var i = 0; i < string.length; i++) {
            var c = string.charAt(i);
            if (c === '\n') {
                lx = x;
                ly++;
            } else if (c === '\r') {
            } else {
                this.putDirty(lx, ly, transformer(c));
                lx++;
            }
        }
        this.recalculateBounds();
    };

    /*
     * Convert this Playfield to a multi-line string.  Each row
     * is a line, delimited with a newline (ASCII 10).
     *
     * If transformer is given, it should be a one-argument
     * function which accepts a playfield element and returns a
     * character (or string) you wish to place in the resulting
     * string for that element.
     */
    this.dump = function(transformer) {
        var text = "";
        if (transformer === undefined) {
            transformer = function(c) { return c; }
        }
        for (var y = this.minY; y <= this.maxY; y++) {
            var row = "";
            for (var x = this.minX; x <= this.maxX; x++) {
                row += transformer(this.get(x, y));
            }
            text += row + "\n";
        }
        return text;
    };

    /*
     * Iterate over every defined cell in the Playfield.
     * fun is a callback which takes three parameters:
     * x, y, and value.  If this callback returns a value,
     * it is written into the Playfield at that position.
     * This function ensures a particular order.
     */
    this.foreach = function(fun) {
        for (var y = this.minY; y <= this.maxY; y++) {
            for (var x = this.minX; x <= this.maxX; x++) {
                var key = x+','+y;
                var value = this._store[key];
                if (value === undefined)
                    continue;
                var result = fun(x, y, value);
                if (result !== undefined) {
                    if (result === ' ') {
                        result = undefined;
                    }
                    this.put(x, y, result);
                }
            }
        }
    };

    /*
     * Analogous to (monoid) map in functional languages,
     * iterate over this Playfield, transform each value using
     * a supplied function, and write the transformed value into
     * a destination Playfield.
     *
     * Supplied function should take a Playfield (this Playfield),
     * x, and y, and return a value.
     *
     * The map source may extend beyond the internal bounds of
     * the Playfield, by giving the min/max Dx/Dy arguments
     * (which work like margin offsets.)
     *
     * Useful for evolving a cellular automaton playfield.  In this
     * case, min/max Dx/Dy should be computed from the neighbourhood.
     */
    this.map = function(destPf, fun, minDx, minDy, maxDx, maxDy) {
        if (minDx === undefined) minDx = 0;
        if (minDy === undefined) minDy = 0;
        if (maxDx === undefined) maxDx = 0;
        if (maxDy === undefined) maxDy = 0;
        for (var y = this.minY + minDy; y <= this.maxY + maxDy; y++) {
            for (var x = this.minX + minDx; x <= this.maxX + maxDx; x++) {
                destPf.putDirty(x, y, fun(pf, x, y));
            }
        }
        destPf.recalculateBounds();
    };

    this.getExtentX = function() {
        if (this.maxX === undefined || this.minX === undefined) {
            return 0;
        } else {
            return this.maxX - this.minX + 1;
        }
    };

    this.getExtentY = function() {
        if (this.maxY === undefined || this.minY === undefined) {
            return 0;
        } else {
            return this.maxY - this.minY + 1;
        }
    };
};
"""

class Compiler(object):
    def __init__(self, alpaca, file, options=None):
        """alpaca is an ALPACA description in AST form.  file is a file-like
        object to which the compiled code will be written.

        """
        self.alpaca = alpaca
        self.file = file
        self.options = options

    def compile(self):
        bb = BoundingBox(0, 0, 0, 0)
        fit_bounding_box(self.alpaca, bb)
        self.file.write("""\
/*
 * This file was AUTOMATICALLY generated from an ALPACA description.
 * EDIT AT YOUR OWN RISK!
 */

""")
        if self.options is not None and \
           self.options.include_yoob_playfield_inline:
            self.file.write(YOOB_PLAYFIELD_JS)
        self.file.write("""
function in_nbhd_pred(pf, x, y, pred, nbhd) {
  var count = 0;
  for (var i = 0; i < nbhd.length; i++) {
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
  pf.map(new_pf, evalState, %d, %d, %d, %d);
}
""" % (-1 * bb.max_dx, -1 * bb.max_dy, -1 * bb.min_dx, -1 * bb.min_dy,))

        # write the CA's load and dump mappers
        repr_map = construct_representation_map(self.alpaca)
        self.file.write("function loadMapper(c) {\n")
        for (char, state_id) in repr_map.iteritems():
            self.file.write("  if (c === '%s') return '%s';\n" %
                            (char, state_id))
        self.file.write("};\n")

        self.file.write("function dumpMapper(s) {\n")
        for (char, state_id) in repr_map.iteritems():
            self.file.write("  if (s === '%s') return '%s';\n" %
                            (state_id, char))
        self.file.write("};\n")

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
            self.file.write("""
pf = new yoob.Playfield();
pf.setDefault('%s');
""" % pf.default)
            for (x, y, c) in pf.iteritems():
                self.file.write("pf.putDirty(%d, %d, '%s');\n" % (x, y, c))
            self.file.write("pf.recalculateBounds();\n")
            self.file.write(r"""
newPf = new yoob.Playfield();
newPf.setDefault('%s');
evolve_playfield(pf, newPf);
console.log('-----');
console.log(newPf.dump(dumpMapper).replace(/\n$/, ""));
console.log('-----');
""" % pf.default)
        return True

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
            self.file.write(";\n}\n")
        for superclass in membership.children:
            self.file.write("id = evalClass_%s(pf, x, y);\n" % superclass.value)
            self.file.write("if (id !== undefined) return id;\n")
        self.file.write("return undefined;\n}\n\n")

    def compile_state_defn(self, defn):
        #char_repr = defn.children[0]
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
            self.file.write(";\n}\n")
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
            if ast.value == 'guess':
                self.file.write('(Math.random()<.5)')
            else:
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
