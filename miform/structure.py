from migen.fhdl.structure import _Statement, wrap, _check_statement
from migen.fhdl.specials import Special
from migen.fhdl.verilog import _printexpr as verilog_printexpr

class _FormalStatement:
    pass

class Formal(Special):
    """
    The Migen Special for formal verification. This is mainly required to
    place all formal statements in their own block.
    """
    def __init__(self):
        Special.__init__(self)
        self.imm = list()
        self.conc = list()

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

        # Top-level formal asserts/assumes not bound by other events- i.e.
        # checked for all time- are by definition concurrent.
        if isinstance(statement, _FormalStatement):
            self.conc.append(statement)

    @staticmethod
    def emit_verilog(formal, ns, add_data_file):
        def pe(e):
            return verilog_printexpr(ns, e)[0]

        r = "`ifdef FORMAL\n"
        for c in formal.conc:
            if isinstance(c, Assert):
                r += "assert property (" + pe(c.cond) + ");\n"
            elif isinstance(c, Assume):
                r += "assume property (" + pe(c.cond) + ");\n"
        r += "`endif\n"
        return r


class Assert(_Statement, _FormalStatement):
    """Assert a condition

    Parameters
    ----------
    cond : _Value(1), in
        Condition

    Examples
    --------
    >>> a = Signal()
    >>> b = Signal()
    >>> c = Signal()
    >>> If(c,
    ...     Assert(a == b)
    ... )
    """
    def __init__(self, cond):
        self.cond = wrap(cond)


class Assume(_Statement, _FormalStatement):
    """Assume a condition holds

    Parameters
    ----------
    cond : _Value(1), in
        Condition

    Examples
    --------
    >>> a = Signal()
    >>> Assume(a == 0)
    """
    def __init__(self, cond):
        self.cond = wrap(cond)
