"""This module contains the unit tests for the dump_xapi_procs function"""

import sys


def test_dump_xapi_subprocess_info(bugtool, fs):
    """Test the dump_xapi_subprocess_info() function to perform as expected"""

    # Prepare the virtual pyfakefs filesystem for the test

    fs.create_file("/proc/2/status", contents="PPid: 1")
    fs.create_file("/proc/3/status", contents="PPid: 2")
    fs.create_file("/proc/4/status", contents="")
    fs.create_file("/proc/2/cmdline", contents="/opt/xensource/bin/xapi")
    fs.create_file("/proc/3/cmdline", contents="/bin/sh")
    fs.create_file("/proc/4/cmdline", contents="")
    fs.create_symlink("/proc/2/fd/1", "/dev/null")
    fs.create_symlink("/proc/3/fd/0", "/dev/zero")

    # Prepare the expected result

    expected_result = """{   '2': {   'children': {   '3': {   'children': {},
                                      'cmdline': '/bin/sh',
                                      'fds': {'0': '/dev/zero'}}},
             'cmdline': '/opt/xensource/bin/xapi',
             'fds': {'1': '/dev/null'}}}"""

    if sys.version_info.major == 2:  # pragma: no cover
        expected_result = expected_result.replace("{}", "{   }")
        expected_result = expected_result.replace(": {'", ": {   '")

    # Assert the expected result

    assert bugtool.dump_xapi_subprocess_info("cap") == expected_result
