import migen.fhdl.verilog

import miform.structure

# XXX: Hack to extend Migen's Verilog generation.
_oldprintnode = migen.fhdl.verilog._printnode

def _formalprintnode(ns, at, level, node):
    def pe(e):
        return migen.fhdl.verilog._printexpr(ns, e)[0]

    if isinstance(node, miform.structure._FormalStatement):
        # return "test"
        r = "\t"*level
        if isinstance(node, miform.structure.Assert):
            r += "assert (" + pe(node.cond) + ");\n"
        elif isinstance(node, miform.structure.Assume):
            r += "assert (" + pe(node.cond) + ");\n"
        else:
            TypeError("Unsupported _FormalStatement within block.")
        return r
    else:
        return _oldprintnode(ns, at, level, node)

migen.fhdl.verilog._printnode = _formalprintnode
