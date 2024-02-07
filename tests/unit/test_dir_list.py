"""tests/unit/test_dir_list.py: Unit-Test bugtool.dir_list(cap, path_list)"""


def test_dir_list(bugtool_log):
    """Test the bugtool function dir_list(cap, path_list) to perform as expected"""

    # Arguments for the positive test:
    cap = bugtool_log.CAP_XENSERVER_CONFIG
    path_list = [__file__.replace(".", "*")]

    # Assert that mis-matching cap causes no output in bugtool.data:
    bugtool_log.entries = [bugtool_log.CAP_DISK_INFO, cap, bugtool_log.CAP_PAM]
    bugtool_log.dir_list(cap=bugtool_log.CAP_XENSERVER_LOGS, path_list=path_list)
    assert bugtool_log.data == {}

    # Assert that mis-matching path_list results in no bugtool.data:
    bugtool_log.dir_list(cap=cap, path_list=[__file__ + "*notexist*"])
    assert bugtool_log.data == {}

    # Assert matching cap and path_list produces expected_data
    bugtool_log.dir_list(cap=cap, path_list=path_list)

    expected_data = {
        "ls -l "
        + __file__: {
            "filter": None,
            "cap": "xenserver-config",
            "cmd_args": [
                "ls",
                "-l",
                __file__,
            ],
        }
    }
    assert bugtool_log.data == expected_data
