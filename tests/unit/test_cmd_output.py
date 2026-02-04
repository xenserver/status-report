"""tests/unit/test_cmd_output.py: Unit-Test bugtool.cmd_output()"""


def test_cmd_output_mismatching_cap(bugtool_fixture):
    """Assert that mismatching cap causes no extension of bugtool.data:"""

    # Prepare that mismatching cap causes no output in bugtool.data:
    bugtool_fixture.entries = [bugtool_fixture.CAP_PAM]

    # Act
    bugtool_fixture.cmd_output(bugtool_fixture.CAP_XENSERVER_LOGS, ["/bin/sh"])

    # Assert that the command is not added to data
    assert bugtool_fixture.data == {}


def check_cmd_output_data(bugtool, command, label=None, filter_func=None):
    """
    Assert that cmd_output() stores the expected command in bugtool.data
    It works by setting bugtool.data and bugtool.entries to fixed values
    and asserting the expected bugtool.data after the check.

    Use this function only with bugtool_fixture which saves and restores
    the original values of these variables to avoid affecting other test cases.
    """

    # Prepare
    bugtool.entries = [bugtool.CAP_PAM]
    bugtool.data = {}

    # Act
    bugtool.cmd_output(bugtool.entries[0], command, label, filter=filter_func)

    # Assert
    assert bugtool.data == {
        label
        or command: {
            "filter": filter_func,
            "cap": bugtool.entries[0],
            "cmd_args": command,
        }
    }


def test_cmd_output_command(bugtool_fixture):
    """Test how cmd_output() handles a command which can be found"""

    check_cmd_output_data(bugtool_fixture, "pwd --version")


def test_cmd_output_command_label(bugtool_fixture):
    """Test how cmd_output() handles a command which can be found with a label"""

    check_cmd_output_data(bugtool_fixture, "pwd --version", "label")


def test_cmd_output_missing_command(bugtool_fixture):
    """Test how cmd_output() handles a missing command"""

    check_cmd_output_data(bugtool_fixture, "/missing-cmd arg")


def test_cmd_output_missing_command_with_label(bugtool_fixture):
    """Test how cmd_output() handles a missing command with a label"""

    check_cmd_output_data(bugtool_fixture, "/missing-cmd arg", "label")


def test_cmd_output_multiple_calls(bugtool_fixture):
    """Assert the cumulative effect of multiple cmd_output() calls."""

    # Prepare
    #
    cap1 = bugtool_fixture.CAP_OEM
    cap2 = bugtool_fixture.CAP_PAM
    bugtool_fixture.entries = [cap1, cap2]

    def mock_filter():
        """No-op mock filter used in tests for asserting it in bugtool_fixture.data"""

    # Act
    #
    cmd1 = ["/usr/bin/pwd", "--version"]
    cmd2 = ["/missing-cmd", "arg1", "arg2"]
    bugtool_fixture.cmd_output("not_an_activated_capability", cmd1)
    bugtool_fixture.cmd_output(cap1, [cmd1[0]], filter=mock_filter)
    bugtool_fixture.cmd_output(cap1, cmd1)
    bugtool_fixture.cmd_output(cap2, cmd2)

    # Assert
    #
    assert bugtool_fixture.data == {
        "pwd": {
            "cap": cap1,
            "cmd_args": ["/usr/bin/pwd"],
            "filter": mock_filter,
        },
        # At the moment, we also add commands which are missing on the system to data
        "missing-cmd arg1 arg2": {
            "cap": cap2,
            "cmd_args": cmd2,
            "filter": None,
        },
        # Uses command as string without path as key when no label is set
        "pwd --version": {
            "cap": cap1,
            "cmd_args": cmd1,
            "filter": None,
        },
    }
