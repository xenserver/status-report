"""This module contains the unit tests for the file_output() function"""

import os


def test_file_output_coverage(isolated_bugtool, fs, capsys):
    """Cover the function file_output(): Skip files that don't apply"""

    # Common definitions: Define a fake capability and test file paths

    fake_capability = "fake_capability"
    path1 = "/sys/kernel/debug/dlm/comms/1"
    path2 = "/sys/kernel/debug/dlm/comms/2"
    path3 = "/sys/kernel/debug/dlm/comms/3"
    path4 = "/sys/kernel/debug/dlm/comms/4"

    #
    # Prepare
    #

    # Prepare the virtual pyfakefs filesystem for the test

    # 8 bytes, to be included
    fs.create_file(path1, contents="content1")

    # 8 bytes, but will be made unreadable
    fs.create_file(path2, contents="content2")
    os.chmod(path2, 0o000)  # Make path2 unreadable

    # 8 bytes, to be included
    fs.create_file(path3, contents="content3")

    # 8 bytes, but will not fit in the max_size limit of 16 bytes
    fs.create_file(path4, contents="content4")

    # Create the fake capability with max_size=16 in our isolated_bugtool instance
    isolated_bugtool.cap(fake_capability, max_size=16)

    #
    # Request two capabilities to be processed
    # - the fake capability for the test files
    # - the "xen-bugtool" capability to log messages to XEN_BUGTOOL_LOG
    #
    isolated_bugtool.entries = [fake_capability, "xen-bugtool"]

    #
    # Act
    #

    # Call the function under test
    isolated_bugtool.file_output(fake_capability, [path1, path2, path3, path4])

    #
    # Assert
    #

    #
    # Define the expected log messages
    #
    # We do not expect a log about path2, as unreadable files are silently skipped
    #
    expected = [
        f"Omitting {path4}, size constraint of {fake_capability} exceeded",
    ]

    assert isolated_bugtool.data == {
        path1: {
            "cap": fake_capability,
            "filename": path1,
        },
        # path2 is unreadable, so it should be skipped
        path3: {
            "cap": fake_capability,
            "filename": path3,
        },
        # path4 would exceed the size limit, so it should be skipped
    }

    # Collect and assert the captured stdout with the expected log messages
    assert capsys.readouterr().out.splitlines() == expected

    # Also check that the log file contains the expected entries
    with open(isolated_bugtool.XEN_BUGTOOL_LOG, "r") as f:
        assert f.read().splitlines() == expected
