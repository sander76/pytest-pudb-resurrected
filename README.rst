===========
pytest-pudb
===========

.. image:: https://github.com/sander76/pytest-pudb-resurrected/actions/workflows/ci.yml/badge.svg?branch=main
   :target: https://github.com/sander76/pytest-pudb-resurrected/actions/workflows/ci.yml
   :alt: CI Status

Pytest PuDB debugger integration based on pytest `PDB integration`_


Installation
------------

.. code-block:: console

    pip install pytest-pudb


Usage
-----

Start the debugger on test failures with ``--pudb``:

.. code-block:: console

    pytest --pudb

Start the debugger at the beginning of each test with ``--pudb-trace``:

.. code-block:: console

    pytest --pudb-trace

Or set breakpoints directly in your code with ``pudb.set_trace()``:

.. code-block:: python

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


See also `pytest`_ and `pudb`_ projects.


.. _PDB integration: https://docs.pytest.org/en/stable/how-to/failures.html#using-pdb-with-pytest
.. _pudb: https://pypi.org/project/pudb/
.. _pytest: https://pypi.org/project/pytest/
