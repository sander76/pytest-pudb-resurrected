# pytest-pudb-resurrected

[![CI Status](https://github.com/sander76/pytest-pudb-resurrected/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/sander76/pytest-pudb-resurrected/actions/workflows/ci.yml)

Pytest PuDB debugger integration based on pytest [PDB integration](https://docs.pytest.org/en/stable/how-to/failures.html#using-pdb-with-pytest).

This is a maintained fork of the original [pytest-pudb](https://github.com/wronglink/pytest-pudb) project.

## Installation

```bash
pip install pytest-pudb-resurrected
```

Or with uv:

```bash
uv add pytest-pudb-resurrected
```

## Usage

Start the debugger on test failures with `--pudb`:

```bash
pytest --pudb
```

Start the debugger at the beginning of each test with `--pudb-trace`:

```bash
pytest --pudb-trace
```

Or set breakpoints directly in your code with `pudb.set_trace()`:

```python
def test_set_trace_integration():
    # No --capture=no needed
    import pudb
    pudb.set_trace()
    assert 1 == 2

def test_pudb_b_integration():
    # No --capture=no needed
    import pudb.b
    # breakpoint is set here
    assert 1 == 2
```

## See Also

- [pytest](https://pypi.org/project/pytest/)
- [pudb](https://pypi.org/project/pudb/)
