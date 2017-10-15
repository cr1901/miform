from migen import *
from migen.fhdl import verilog
from miform.structure import Assert, Assume, Formal

class Hello(Module):
    def __init__(self):
        self.en = Signal(1)
        self.cnt = Signal(4)

        last_clk = Signal(1)

        self.sync += [
            # XXX: If commented out, last_clk is never placed into Verilog
            # namespace. Formal() special somehow needs to add it to
            # namespace.
            last_clk.eq(ClockSignal("sys")),
            If(self.en,
                self.cnt.eq(self.cnt + 1)
            ).Else(
                self.cnt.eq(0)
            )
        ]

        f = Formal()
        f.add(Assert(self.cnt < 10))
        f.add(Assume(self.cnt != 9))
        f.add(Assume(self.en == 0, True))

        f.add(If(self.en,
            Assert(self.cnt == C(0, 4))
        ))

        f.add_sync("sys",
            [
                last_clk.eq(0)
            ]
        )

        f.add_global(
            [
                Assume(last_clk == 0),
                # XXX: Expression of unrecognized type ClockSignal
                # Assume(last_clk != ClockSignal("sys"))
            ]
        )
        self.specials += f

m = Hello()
print(verilog.convert(m, ios={m.en, m.cnt}))
