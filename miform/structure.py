from migen.fhdl.structure import _Statement, wrap, _check_statement
from migen.fhdl.specials import Special
from migen.fhdl.verilog import _AT_BLOCKING, _printexpr as verilog_printexpr
from migen.fhdl.module import _flat_list, _cd_append


import miform.verilog

class _FormalStatement:
    pass


class _FormalTask:
    def __init__(self):
        pass

    def to_system_verilog(self):
        raise NotImplementedError


class Formal(Special):
    """
    The Migen Special for formal verification. This is mainly required to
    place all formal statements in their own block.
    """
    def __init__(self):
        Special.__init__(self)
        self.init = list()
        self.imm = list()
        self.conc = list()
        self.glob = list()
        self.sync = dict()

    """
    Add an assertion or assumption for formal verification purposes.

    Parameters
    ----------
    statement : _Statement(), in
    A Migen Statement that contains a _FormalStatement such as Assume or Assert;
    such statements are tested only when the conditions for the Assume/Assert
    are met.

    The statement itself can also be a _FormalStatement; these statements
    are continously assumed to be true or tested to be true, at all clock ticks.
    """
    def add(self, statement):
        if not _check_statement(statement):
            raise TypeError("Input to Formal specials must be Migen statements")

        if isinstance(statement, _FormalStatement):
            if statement.initial:
                # Initial asserts/assumes look similar to concurrent, though
                # the initial "block" is considered an event (I think?).
                self.init.append(statement)
            else:
                # Top-level formal asserts/assumes not bound by other events- i.e.
                # checked for all time- are by definition concurrent.
                self.conc.append(statement)
        else:
            # TODO: ensure at least one statement in list is a _FormalStatement.
            self.imm += _flat_list(statement)


    """Add an assertion using the SystemVerilog $globalclock task. This is the implied clock
    during formal verification; in `yosys`, if the `clk2dfflogic` pass
    is executed, all other Migen clock domains, including the default "sys"
    clock domain, become synchronous inputs relative to the $global_clock.

    Parameters
    ----------
    statement : _Statement(), in
    A Migen Statement that is asserted/assumed each tick of the $global_clock.
    """
    def add_global(self, statement):
        self.glob += _flat_list(statement)

    """Add an assertion that is checked on the positive-edge of the input
    clock domain.

    Parameters
    ----------
    cd : str, in
    Name of the clock-domain for which the assertion/assumption is checked.

    statement : _Statement(), in
    A Migen Statement that is asserted/assumed each positive-edge of the named `cd`.
    """
    def add_sync(self, cd, statement):
        _cd_append(self.sync, cd, statement)

    @staticmethod
    def emit_verilog(formal, ns, add_data_file):
        def pe(e):
            return verilog_printexpr(ns, e)[0]

        r = "`ifdef FORMAL\n"
        for i in formal.init:
            if isinstance(i, Assert):
                r += "initial assert (" + pe(i.cond) + ");\n"
            elif isinstance(i, Assume):
                r += "initial assume (" + pe(i.cond) + ");\n"

        r += "\n"
        for c in formal.conc:
            if isinstance(c, Assert):
                r += "assert property (" + pe(c.cond) + ");\n"
            elif isinstance(c, Assume):
                r += "assume property (" + pe(c.cond) + ");\n"
            else:
                TypeError("Only Assume and Assert supported for concurrent assertions.")

        r += "\n"
        for i in formal.imm:
            r += "always @(*) begin\n"
            r += miform.verilog._formalprintnode(ns, _AT_BLOCKING, 1, i)
            r += "end\n"

        r += "\n"
        r += miform.verilog._formalprintsync(formal, ns)

        r += "\n"
        for g in formal.glob:
            r += "always @($global_clock) begin\n"
            r += miform.verilog._formalprintnode(ns, _AT_BLOCKING, 1, g)
            r += "end\n"

        r += "`endif\n"
        return r


class Assert(_Statement, _FormalStatement):
    """Assert a condition

    Parameters
    ----------
    cond : _Value(1), in
        Condition
    initial : bool, in
        Only test the assertion on the first cycle. Defaults to false.
        Ignored if the assert is not continuous.

    Examples
    --------
    >>> a = Signal()
    >>> b = Signal()
    >>> c = Signal()
    >>> If(c,
    ...     Assert(a == b)
    ... )
    """
    def __init__(self, cond, initial=False):
        self.cond = wrap(cond)
        self.initial = initial


class Assume(_Statement, _FormalStatement):
    """Assume a condition holds

    Parameters
    ----------
    cond : _Value(1), in
        Condition
    initial : bool, in
        Only assume `cond` on the first cycle. Defaults to false.
        Ignored if the assume is not continuous.

    Examples
    --------
    >>> a = Signal()
    >>> Assume(a == 0)
    """
    def __init__(self, cond, initial=False):
        self.cond = wrap(cond)
        self.initial=initial


# class GlobalClock(_Statement, _FormalStatement, _FormalTask):
#     """The SystemVerilog $globalclock task. This is the implied clock
#     during formal verification; in `yosys`, if the `clk2dfflogic` pass
#     is executed, all clock domains become synchronous relative to the
#     global clock."""
#     def __init__(self):
#         pass
#
#     def to_system_verilog(self):
#         return "$"
