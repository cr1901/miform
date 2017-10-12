from migen import *
from migen.fhdl import verilog
from miform.structure import Assert, Assume, Formal

class Hello(Module):
    def __init__(self):
        self.cnt = Signal(4)
        self.sync += [self.cnt.eq(self.cnt + 1)]

        f = Formal()
        f.add(Assert(self.cnt < 10))
        f.add(Assume(self.cnt != 9))
        self.specials += f

print(verilog.convert(Hello()))
