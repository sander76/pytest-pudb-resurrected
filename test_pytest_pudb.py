pytest_plugins = "pytester"

HELP_MESSAGE = "\\?\\:help"
VARIABLES_TABLE = "V\x1b\\[0;30;47mariables:"


def test_pudb_interaction(pytester):
    p1 = pytester.makepyfile("""
        def test_1():
            assert 0 == 1
    """)
    child = pytester.spawn_pytest(f"--pudb {p1}")
    child.expect("PuDB")
    child.expect(HELP_MESSAGE)
    child.expect(VARIABLES_TABLE)
    child.sendeof()


def test_pudb_trace(pytester):
    """Test that --pudb-trace starts debugger at beginning of test."""
    p1 = pytester.makepyfile("""
        def test_1():
            x = 1
            assert x == 1
    """)
    child = pytester.spawn_pytest(f"--pudb-trace {p1}")
    child.expect("PuDB")
    child.expect(HELP_MESSAGE)
    child.expect(VARIABLES_TABLE)
    child.sendeof()


def test_pudb_set_trace_integration(pytester):
    p1 = pytester.makepyfile("""
        def test_1():
            import pudb
            pudb.set_trace()
            assert 1
    """)
    child = pytester.spawn_pytest(str(p1))
    child.expect("PuDB")
    child.expect(HELP_MESSAGE)
    child.expect(VARIABLES_TABLE)
    child.sendeof()


def test_pu_db_integration(pytester):
    p1 = pytester.makepyfile("""
        def test_1():
            import pudb
            pu.db
            assert 1
    """)
    child = pytester.spawn_pytest(str(p1))
    child.expect("PuDB")
    child.expect(HELP_MESSAGE)
    child.expect(VARIABLES_TABLE)
    child.sendeof()


def test_pudb_b_integration(pytester):
    p1 = pytester.makepyfile("""
        def test_1():
            import pudb.b
            assert 1
    """)
    child = pytester.spawn_pytest(str(p1))
    child.expect("PuDB")
    child.expect(HELP_MESSAGE)
    child.expect(VARIABLES_TABLE)
    child.sendeof()


def test_pudb_options_registered(pytester):
    """Test that --pudb and --pudb-trace options are registered."""
    result = pytester.runpytest("--help")
    result.stdout.fnmatch_lines(["*--pudb*", "*--pudb-trace*"])
