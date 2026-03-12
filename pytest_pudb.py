"""interactive debugging with PuDB, the Python Debugger."""

import functools
import sys

import pudb
from _pytest.config import hookimpl


def pytest_addoption(parser):
    group = parser.getgroup("general")
    group.addoption(
        "--pudb",
        "--db",
        action="store_true",
        dest="usepudb",
        default=False,
        help="start the PuDB debugger on errors.",
    )
    group.addoption(
        "--pudb-trace",
        "--dbt",
        action="store_true",
        dest="usepudb_trace",
        default=False,
        help="immediately break when running each test.",
    )


def pytest_configure(config):
    pudb_wrapper = PuDBWrapper(config)

    if config.getvalue("usepudb"):
        config.pluginmanager.register(pudb_wrapper, "pudb_wrapper")

    if config.getvalue("usepudb_trace"):
        trace_wrapper = PuDBTraceWrapper(config)
        config.pluginmanager.register(trace_wrapper, "pudb_trace")

    pudb_wrapper.mount()
    config.add_cleanup(pudb_wrapper.unmount)


class PuDBWrapper:
    """Pseudo PDB that defers to the real pudb."""

    pluginmanager = None
    config = None

    def __init__(self, config):
        self.config = config
        self.pluginmanager = config.pluginmanager
        self._pudb_get_debugger = None

    def mount(self):
        self._pudb_get_debugger = pudb._get_debugger
        pudb._get_debugger = self._get_debugger

    def unmount(self):
        if self._pudb_get_debugger:
            pudb._get_debugger = self._pudb_get_debugger
            self._pudb_get_debugger = None

    def disable_io_capture(self):
        if self.pluginmanager is not None:
            capman = self.pluginmanager.getplugin("capturemanager")
            if capman:
                outerr = self._suspend_capture(capman, in_=True)
                if outerr:
                    out, err = outerr
                    sys.stdout.write(out)
                    sys.stdout.write(err)
            terminalreporter = self.pluginmanager.getplugin("terminalreporter")
            if terminalreporter is not None:
                tw = terminalreporter._tw
                tw.line()
                tw.sep(">", "entering PuDB (IO-capturing turned off)")
            # Use the original _get_debugger to avoid infinite recursion
            dbg = self._pudb_get_debugger()
            self.pluginmanager.hook.pytest_enter_pdb(config=self.config, pdb=dbg)

    def _get_debugger(self, **kwargs):
        self.disable_io_capture()
        return self._pudb_get_debugger.__call__(**kwargs)

    def pytest_exception_interact(self, node, call, report):
        """
        Pytest plugin interface for exception handling
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_exception_interact
        """
        self.disable_io_capture()
        _enter_pudb(node, call.excinfo, report)

    def pytest_internalerror(self, excrepr, excinfo):
        """
        Pytest plugin interface for internal errors handling
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_internalerror
        """
        for line in str(excrepr).split("\n"):
            sys.stderr.write(f"INTERNALERROR> {line}\n")
            sys.stderr.flush()
        tb = _postmortem_traceback(excinfo)
        post_mortem(tb, excinfo)

    def _suspend_capture(self, capman, *args, **kwargs):
        capman.suspend_global_capture(*args, **kwargs)
        return capman.read_global_capture()


class PuDBTraceWrapper:
    """Wrapper that starts PuDB at the beginning of each test."""

    def __init__(self, config):
        self.config = config
        self.pluginmanager = config.pluginmanager

    def disable_io_capture(self):
        if self.pluginmanager is not None:
            capman = self.pluginmanager.getplugin("capturemanager")
            if capman:
                capman.suspend_global_capture(in_=True)
                outerr = capman.read_global_capture()
                if outerr:
                    out, err = outerr
                    sys.stdout.write(out)
                    sys.stdout.write(err)
            terminalreporter = self.pluginmanager.getplugin("terminalreporter")
            if terminalreporter is not None:
                tw = terminalreporter._tw
                tw.line()
                tw.sep(">", "entering PuDB (IO-capturing turned off)")
            dbg = pudb._get_debugger()
            self.pluginmanager.hook.pytest_enter_pdb(config=self.config, pdb=dbg)

    @hookimpl(wrapper=True)
    def pytest_pyfunc_call(self, pyfuncitem):
        """Wrap test function to start PuDB at the beginning of each test."""
        self._wrap_function_for_tracing(pyfuncitem)
        return (yield)

    def _wrap_function_for_tracing(self, pyfuncitem):
        """Wrap the test function to enter pudb before calling it."""
        self.disable_io_capture()
        testfunction = pyfuncitem.obj
        dbg = pudb._get_debugger()

        @functools.wraps(testfunction)
        def wrapper(*args, **kwargs):
            func = functools.partial(testfunction, *args, **kwargs)
            dbg.runcall(func)

        pyfuncitem.obj = wrapper


def _enter_pudb(node, excinfo, rep):
    tb = _postmortem_traceback(excinfo)
    post_mortem(tb, excinfo)
    rep._pdbshown = True
    return rep


def _postmortem_traceback(excinfo):
    # A doctest.UnexpectedException is not useful for post_mortem.
    # Use the underlying exception instead:
    from doctest import UnexpectedException

    if isinstance(excinfo.value, UnexpectedException):
        return excinfo.value.exc_info[2]
    else:
        return excinfo._excinfo[2]


def post_mortem(tb, excinfo):
    dbg = pudb._get_debugger()
    stack, i = dbg.get_stack(None, tb)
    dbg.reset()
    i = _find_last_non_hidden_frame(stack)
    dbg.interaction(stack[i][0], excinfo._excinfo)


def _find_last_non_hidden_frame(stack):
    i = max(0, len(stack) - 1)
    while i and stack[i][0].f_locals.get("__tracebackhide__", False):
        i -= 1
    return i
