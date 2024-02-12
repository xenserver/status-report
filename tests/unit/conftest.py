"""tests/unit/conftest.py: pytest fixtures for unit-testing functions in the xen-bugtool script"""
from __future__ import print_function

import os
import shutil
import sys

import pytest


@pytest.fixture(scope="function")
def builtins():
    """
    Pytest fixture to return the name of the built-in module.
    The built-in module provides the built-in functions, exceptions, etc.
    It is needed to replace built-in functions like open() with a new mock.

    :returns (str): The name of the built-in module.
    """
    return "__builtin__" if sys.version_info < (3,) else "builtins"


@pytest.fixture(scope="session")
def testdir():
    """Test fixture to get the directory of the unit test for finding other files relative to it"""
    return os.path.dirname(__file__)


@pytest.fixture(scope="session")
def dom0_template(testdir):
    """Test fixture to get the directory of the dom0 template and adding it's /usr/sbin to the PATH"""
    return testdir + "/../integration/dom0-template"


@pytest.fixture(scope="session")
def imported_bugtool(testdir, dom0_template):
    """Test fixture to import the xen-bugtool script as a module for executing unit tests on functions"""

    # This uses the deprecated imp module because it needs also to run with Python2.7 for now:
    def import_from_file(module_name, file_path):
        if sys.version_info.major == 2:  # pragma: no cover
            import imp  # pylint: disable=deprecated-module  # pyright: ignore[reportMissingImports]

            return imp.load_source(module_name, file_path)
        else:
            # Py3.11+: Importing Python source code from a script without the .py extension:
            # https://gist.github.com/bernhardkaindl/1aaa04ea925fdc36c40d031491957fd3:
            from importlib import machinery, util

            loader = machinery.SourceFileLoader(module_name, file_path)
            spec = util.spec_from_loader(module_name, loader)
            assert spec
            assert spec.loader
            module = util.module_from_spec(spec)
            # Probably a good idea to add manually imported module stored in sys.modules
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            return module

    bugtool = import_from_file("xen-bugtool", testdir + "/../../xen-bugtool")
    bugtool.ProcOutput.debug = True
    # Prepend tests/mocks to force the use of our mock xen.lowlevel.xc module:
    sys.path.insert(0, testdir + "/../mocks")
    os.environ["PATH"] = dom0_template + "/usr/sbin"  # for modinfo, mdadm, etc
    return bugtool


@pytest.fixture(scope="function")
def bugtool(imported_bugtool):
    """Test fixture for unit tests, initializes the bugtool data dict for each test"""
    # Init import_bugtool.data, so each unit test function gets it pristine:
    imported_bugtool.data = {}
    sys.argv = ["xen-bugtool", "--unlimited"]
    return imported_bugtool


@pytest.fixture(scope="function")
def in_tmpdir(tmpdir):
    """
    Run each test function in it's own temporary directory

    This fixture warps pytest's built-in tmpdir fixture with a chdir()
    to the tmpdir and a check for leftover files after the test returns.

    Usage in a test function:

    @pytest.usefixtures("in_tmpdir")
    def test_foo(other_fixtures):
        # ... test code that runs with the tmpdir as its working directory ...

    # If the test function wants to use the in_tmpdir variable:
    def test_foo(in_tmpdir):
        in_tmpdir.mkdir("subdir").join("filename").write("content_for_testing")
        # code under test, that runs with the tmpdir as its working directory:
        with open("subdir/filename") as f:
            assert f.read() == "content_for_testing"

    Documentation on the wrapped tmpdir fixture:
    https://docs.pytest.org/en/6.2.x/tmpdir.html#the-tmpdir-fixture
    """

    # Get the current directory:
    curdir = os.getcwd()

    # Change to the temporary directory:
    os.chdir(str(tmpdir))

    # Run the test:
    yield tmpdir  # provide the fixture value to the pytest test function

    # Change back to the original directory:
    os.chdir(curdir)

    # upon return, the tmpdir fixture will cleanup the temporary directory


@pytest.fixture(scope="function")
def bugtool_log(in_tmpdir, bugtool):
    """Like in_tmpdir and check that no logs are left in XEN_BUGTOOL_LOG"""

    in_tmpdir.mkdir("tmp")  # Create a tmp directory for use by test cases

    in_tmpdir.join(bugtool.XEN_BUGTOOL_LOG).write("")  # create the log file

    # Run the test:
    yield bugtool  # provide the bugtool to the test function

    log = in_tmpdir.join(bugtool.XEN_BUGTOOL_LOG).read()  # read the log file
    if log:  # pragma: no cover
        print("Content of " + bugtool.XEN_BUGTOOL_LOG + ":" + log, file=sys.stderr)
        pytest.fail("Code under test left logs in " + bugtool.XEN_BUGTOOL_LOG)

    # Cleanup the temporary directory to prepare to check leftover files:
    os.remove(bugtool.XEN_BUGTOOL_LOG)
    shutil.rmtree("tmp")

    # Check for files that the code under test might have left:
    files = in_tmpdir.listdir()
    if files:  # pragma: no cover
        print("Files left in temporary working dir:", files, file=sys.stderr)
        pytest.fail("Code under test left files in the its working directory")

    # upon return, the in_tmpdir switches back to the original directory


@pytest.fixture(scope="function")
def isolated_bugtool(bugtool_log):
    """
    Like `bugtool_log` and make the temporary working directory read-only
    to prevent creating files in it
    """

    # Make the current cwd (a temporary directory) read-only:
    os.chmod(".", 0o555)

    yield bugtool_log  # runs the test function in the read-only directory

    os.chmod(".", 0o777)  # restore write permissions (for cleanup)

    # upon return, bugtool_log continues with its cleanup
