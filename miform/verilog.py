from operator import itemgetter

from migen.fhdl.structure import *
import migen.fhdl.verilog

import miform.structure

# XXX: Hack to extend Migen's Verilog generation.
# XXX: I can't prevent someone from trying to use Assert() outside of
# formal blocks.
_oldprintnode = migen.fhdl.verilog._printnode

def _formalprintnode(ns, at, level, node):
    def pe(e):
        return migen.fhdl.verilog._printexpr(ns, e)[0]

    if isinstance(node, miform.structure._FormalStatement):
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


def _formalprintsync(f, ns):
    def pe(e):
        return migen.fhdl.verilog._printexpr(ns, e)[0]

    r = ""
    for k, v in sorted(f.sync.items(), key=itemgetter(0)):
        # XXX: Memory Special uses a similar mechanism to get the names of
        # clock signals in clock domains without actually being a _Fragment
        # (which keeps knowledge about existing clock domains). But it's
        # still hacky.
        clk = ClockSignal(k)

        # XXX: ns.get_name(pe(clk)) doesn't work, but it's what Memory Special uses.
        r += "always @(posedge " + ns.get_name(clk) + ") begin\n"
        r += _formalprintnode(ns, migen.fhdl.verilog._AT_SIGNAL, 1, v)
        r += "end\n\n"
    return r

migen.fhdl.verilog._printnode = _formalprintnode
