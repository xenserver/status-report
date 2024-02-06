# The Xen-Bugtool Test Environment

The test environment contains two classes of test frameworks

- [tests/unit](tests/unit): Classic unit test framework using pytest fixtures.
  - It provides a number of pytest fixtures for testing functions including the
    the `main()` function of Xen-Bugtool, which allows to run any kind of test.

- [tests/integration](tests/integration) runs `xen-bugtool` in a container with
  simulated `root` capabilities, allowing any regular user to test xen-bugtool
  without patching it and without requiring special system configuration.

  In this framework, two kinds of tests exist:
  - Legacy shell scripts: They run in GitHub CI Containers and not locally
  - Python-based container test suite: Uses Linux namespace to enter into
    a simulated, rootless chroot container that runs locally on any modern
    Linux development VM without any setup.

  Caveats:
  Because thest tests run xen-bugtool in a container, collecting code coverage
  from them would require merging the collected code coverage from each test.
  Because this is not yet implemented, these currently do not contribute to
  the reported code coverage.

  See [README-pytest-chroot.md](README-pytest-chroot.md)
  for further introduction on the `pytest-chroot` test suite.


## Testing this project

To run the tests using, simply run `pytest`.

The pytest.ini configures `pytest` to show you logs of failed tests.

For development, do show also logs from passing tests, run `pytest -rA`

In case a test fails on an asserting, use `pytest -vv` to get the full assert.

### Introduction to pytest, pytest.mark and pytest fixtures:

[![Automated Testing in Python with pytest, tox, and GitHub Actions](https://img.youtube.com/vi/DhUpxWjOhME/0.jpg)](https://www.youtube.com/watch?v=DhUpxWjOhME)

Note: For simplicity, this project uses `pre-commit` instead of `tox`:
`pre-commit` is much easier to handle and pre-commit also provides
the possibility install it as a pre-commit hook:

Whenever in this Video, `tox` is mentioned, think of `pre-commit` instead!

See [README-pre-commmit.md](README-pre-commmit.md)
on using `pre-commit` to run the test and analysis suites locally.


## Suggested `pytest` plugins for development of test cases

### pytest-pickled
When updating existing tests or developing new code with new test coverage, we might want to
ignore all other tests. This can be achieved with an exciting plugin called `pytest-picked`:
`pytest --picked` will collect all test modules that were newly created or changed but not
yet committed in a Git repository and run only them.

### pytest-sugar
`pytest-sugar` is a plugin that, once installed, automatically changes the format of the
`pytest` standard output to include a graphical %-progress bar when running the test suite.

### Installation of these pytest plugins
For nicer diffs of dictionaries, arrays and the like, use `pytest-clarity` or `pytest-icdiff`:

```py
pip install "pytest<7" pytest-picked pytest-sugar pytest-clarity # pytest-icdiff
```

For more information to debug `pytest` test suites see: https://stribny.name/blog/pytest/

## Running the Xen-Bugtool Test Environment

```py
# Run the Python-based container test suite
python3 -m pytest tests/integration
```

```py
# Run the Unit tests:
python3 -m pytest tests/unit
```

```py
# Run a specific Unit test module
python3 -m pytest tests/unit/test_filter_xapi_clusterd_db.py
```

See the https://docs.pytest.org for more documentation on `pytest.

## Unit Tests in [tests/unit](tests/unit)

### Classical unit test cases

The strength of classic unit testing is that these test cases can
all a tested function with many different input values and thereby
check all conditions and branches in the test function to work.

- [tests/unit/test_filter_xapi_clusterd_db.py](tests/unit/test_filter_xapi_clusterd_db.py) -
  Recommended example to use for testing a function in multiple ways in order
  to assert that it works with different input data and generates expected output.
  It has extensive documentation and should be used as the basis for new tests.
- [tests/unit/test_xapidb_filter.py](tests/unit/test_xapidb_filter.py) -
  Simple test case passing XML to a function filtering it.
- [tests/unit/test_snmp.py](tests/unit/test_snmp.py) -
  Ditto, but for testing the filtering of SNMP config data
- [tests/unit/test_fs_funcs.py](tests/unit/test_fs_funcs.py) -
  Examples for testing functions that need to access some files of Dom0
- [tests/unit/test_dir_list.py](tests/unit/test_dir_list.py) -
  Example of testing function that writes xen-bugtool's global data
- [tests/unit/test_load_plugins.py](tests/unit/test_load_plugins.py) -
  Larger example of the same test where a number of global variables are checked
- [tests/unit/test_process_output.py](tests/unit/test_process_output.py) -
  Tests that check functions which run external programs from the dom0_template

### Advanced test cases

These cover a lot of code, for code coverage testing, and are needed to test the
big function of xen-bugtool to work as expected. They cover a lot of ground, but
need the classical unit tests for asserting that the smaller individual
functions handle all cases that could arise with different input formats.

These functions only use static input from
[tests/integration/dom0-template](tests/integration/dom0-template)
so they cannot cover code conditions that require many different variants
of inputs. But, they test overall functioning of the major functions of the status-report tool:

- [tests/unit/test_output.py](tests/unit/test_output.py)
  - Call individual functions in `xen-bugtool` that allow the test to
    generate bug-reports using all output formats and then, it verifies these.
- [tests/unit/test_main.py](tests/unit/test_main.py)
  - Call the main() function of `xen-bugtool`, to
    generate bug-reports using all output formats and then, it verifies these.
