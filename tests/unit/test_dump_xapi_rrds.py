"""Test: test_dump_xapi_rrds"""

import sys
from email.message import Message

import pytest
from mock import MagicMock

if sys.version_info.major == 2:  # pragma: no cover
    from urllib2 import HTTPError  # type:ignore[import-not-found,attr-defined]
else:
    from urllib.request import HTTPError


@pytest.fixture
def mock_session1():
    """Return a mock XenAPI session.

    xapi_local_session is mocked to return this session.

    The pool has 3 VMs, one of which is not resident and one template.
    The test runs on the pool master.

    Because the session runs on the pool master, dump_xapi_rrds() will
    fetch the RRDs of resident VMs on any host and of the pool master.
    """
    session = MagicMock()
    session._session = "id"
    session.xenapi.login_with_password.return_value = "session_id"

    # Simulates that the pool has 3 VMs, one of them is a template:
    session.xenapi.VM.get_all_records.return_value = {
        "invalid VM: mock_urlopen will return 404 on opening the 1st URL": {
            "uuid": "0",
            "is_a_template": False,
            "power_state": "Suspended",
            "resident_on": "host0",
        },
        "vm1": {
            "uuid": "1",
            "is_a_template": False,
            "resident_on": "host1",
            "power_state": "Running",
        },
        "vm2": {
            "uuid": "2",
            "is_a_template": False,
            "resident_on": "host2",
            "power_state": "Suspended",
        },
        "vm4": {
            "uuid": "4",
            "is_a_template": False,
            "resident_on": "OpaqueRef:NULL",
        },
        "template": {"is_a_template": True},
    }
    # Simulate that the test runs on the pool master:
    session.xenapi.pool.get_all_records.return_value = {
        "pool1": {"master": "host1"},
    }
    session.xenapi.session.get_this_host.return_value = "host1"
    return session


@pytest.fixture
def mock_urlopen():
    """Return a mock urlopen() that returns different mock RRD data on each call"""

    mock_response = MagicMock()
    mock_response.read.side_effect = [b"mock_rrd1", b"mock_rrd2", b"mock_rrd3"]

    mock_urlopen = MagicMock(return_value=mock_response)

    # Mock the urlopen() to return the mock_response with different data on each call
    side_effect = [HTTPError("url", 404, "Not Found", Message(), None)]

    side_effect += [mock_response] * 3
    mock_urlopen.side_effect = side_effect

    # Mock the fileno() method to return 0 for use by select(), except for Python3,
    # urlopen returns http.client.HTTPResponse, which doesn't have a fileno() method:
    if sys.version_info.major == 2:  # pragma: no cover
        mock_urlopen.return_value.fileno.return_value = 0

    return mock_urlopen


def assert_mock_session1(bugtool, mock_urlopen):
    """Assert the results expected from the mock_session1() fixture.

    The pool has 3 VMs, one of which is not resident and one template.

    Because the session was run on the pool master, dump_xapi_rrds() is expected
    fetch the RRDs of resident VMs on any host and of the pool master.
    """
    # Expect to see 3 calls to urlopen, one for each VM and one for the host
    assert mock_urlopen.return_value.read.call_count == 3

    # Assert that the RRDs of both VM are fetched
    mock_urlopen.assert_any_call(
        "http://localhost/vm_rrd?session_id=id&uuid=1",
        timeout=5,
    )
    mock_urlopen.assert_any_call(
        "http://localhost/vm_rrd?session_id=id&uuid=2",
        timeout=5,
    )

    # Check the keys of the data dictionary
    files = sorted(bugtool.data.keys())
    assert files == ["xapi_rrd-1.out", "xapi_rrd-2.out", "xapi_rrd-host"]

    # Check the cap values of the data dictionary
    expected_caps = ["persistent-stats"] * 3
    assert [key["cap"] for key in bugtool.data.values()] == expected_caps

    # Call the func_output() functions and check the return values
    values = [key["func"]("") for key in bugtool.data.values() if "func" in key]
    assert sorted(values) == [b"mock_rrd1", b"mock_rrd2", b"mock_rrd3"]

    with open(bugtool.XEN_BUGTOOL_LOG, "r") as f:
        log = f.read()
        assert log == "Failed to fetch RRD for VM 0: HTTP Error 404: Not Found\n"

    # Clear the log file, this indicates to the isolated_bugtool fixture
    # that we checked the log file contents to be what we expected.
    with open(bugtool.XEN_BUGTOOL_LOG, "w") as f:
        f.write("")


def run_dump_xapi_rrds(mocker, bugtool, mock_session, mock_urlopen):
    """Run the bugtool function dump_xapi_rrds(entries) with the given mocks."""
    # Patch the urlopen, xapi_local_session and entries
    mocker.patch("bugtool.urlopen", side_effect=mock_urlopen)
    mocker.patch("bugtool.xapi_local_session", return_value=mock_session)
    mocker.patch("bugtool.entries", [bugtool.CAP_PERSISTENT_STATS])

    # Run the function
    bugtool.dump_xapi_rrds(bugtool.entries)

    # Check if host RRD is fetched
    mock_urlopen.assert_any_call("http://localhost/host_rrd?session_id=id")

    # Check the calls to xapi_local_session
    assert mock_session.xenapi.VM.get_all_records.call_count == 1
    assert mock_session.xenapi.pool.get_all_records.call_count == 1
    assert mock_session.xenapi.session.get_this_host.call_count == 1
    assert mock_session.xenapi.session.logout.call_count == 1


def test_dump_xapi_rrds_master(mocker, isolated_bugtool, mock_session1, mock_urlopen):
    """Test dump_xapi_rrds() on a pool master with 2 VMs in the pool.

    Test the bugtool function dump_xapi_rrds(entries) to perform as expected
    with mock_session1 which simulates a pool with 2 VMs and a pool master.
    """

    run_dump_xapi_rrds(mocker, isolated_bugtool, mock_session1, mock_urlopen)
    assert_mock_session1(isolated_bugtool, mock_urlopen)


def test_log_exceptions(isolated_bugtool, capsys):
    """Test log_exceptions() to log the exception message and return the exception type."""

    try:
        with isolated_bugtool.log_exceptions():
            raise IOError("message")
    except BaseException:  # pragma: no cover # NOSONAR
        assert False, "log_exceptions() is expected to catch all Exceptions"
    finally:
        with capsys.disabled():
            # Assert that the exception message is logged to stdout
            assert_log_contents(capsys.readouterr().out.splitlines())

            # Assert that the exception message is logged to the log file
            with open(isolated_bugtool.XEN_BUGTOOL_LOG, "r") as f:
                log = f.read().splitlines()
                assert_log_contents(log)

            # Clear the log file to indicate that we checked the log file contents
            with open(isolated_bugtool.XEN_BUGTOOL_LOG, "w") as f:
                f.write("")


def assert_log_contents(log):
    """Assert the contents of the log"""

    # Check the log file contents
    assert log[0] == "message, Traceback (most recent call last):"
    assert ", in log_exceptions" in log[1]
    assert log[2] == "    yield"
    assert ", in test_log_exceptions" in log[3]
    assert log[4] == '    raise IOError("message")'
