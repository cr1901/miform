from migen import *
from migen.fhdl import verilog
from miform.structure import Assert, Formal

class Hello(Module):
    def __init__(self):
        self.cnt = Signal(4)
        self.sync += [self.cnt.eq(self.cnt + 1)]

        f = Formal()
        f.add(Assert(self.cnt < 10))
        self.specials += f

print(verilog.convert(Hello()))
