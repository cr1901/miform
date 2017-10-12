from migen import *
from migen.fhdl import verilog
from miform.structure import Assert, Assume, Formal

class Hello(Module):
    def __init__(self):
        self.en = Signal(1)
        self.cnt = Signal(4)
        self.sync += [
            If(self.en,
                self.cnt.eq(self.cnt + 1)
            ).Else(
                self.cnt.eq(0)
            )
        ]

        f = Formal()
        f.add(Assert(self.cnt < 10))
        f.add(Assume(self.cnt != 9))

        f.add(If(self.en,
            Assert(self.cnt == C(0, 4))
        ))
        self.specials += f

m = Hello()
print(verilog.convert(m, ios={m.en, m.cnt}))
