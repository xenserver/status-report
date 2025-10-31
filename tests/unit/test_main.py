"""pytest module for unit-testing xen-bugtool's main() function"""

import logging
import os
import sys
import tarfile
import zipfile

import pytest

# sourcery skip: dont-import-test-modules
from . import test_xapidb_filter
from .test_output import MOCK_EXCEPTION_STRINGS, assert_valid_inventory_schema, mock_data_collector, parse


yes_to_all_warning = """\
Warning: '--yestoall' argument provided, will not prompt for individual files.
"""
bugtool_banner = """
This application will collate the Xen dmesg output, details of the
hardware configuration of your machine, information about the build of
Xen that you are using, plus, if you allow it, various logs.

The collated information will be saved as a .zip for archiving or
sending to a Technical Support Representative.

The logs may contain private information, and if you are at all
worried about that, you should exit now, or you should explicitly
exclude those logs from the archive.


"""


def test_unknown_option(bugtool, caplog):
    """Test a bugtool module to execute main() and fail for an unknown option.

    This minimal test serves as a teaching and code coverage to show
    capturing and checking of log messages using the caplog fixture.

    :param bugtool: The imported bugtool module object to be patched.
    :param caplog: The caplog pytest fixture for capturing log messages.
    """

    with caplog.at_level(logging.FATAL):
        sys.argv[1] = "--unknown-option"
        assert bugtool.main() == 2
    assert len(caplog.record_tuples) == 2
    logger, level, message = caplog.record_tuples[0]
    assert logger == "root"
    assert level == logging.FATAL
    assert message == "xen-bugtool: option --unknown-option not recognized"
    logger, level, message = caplog.record_tuples[1]
    assert logger == "root"
    assert level == logging.FATAL
    assert message == bugtool.usage()


def test_no_root_privileges(bugtool, caplog, mocker):
    """Test a bugtool module to execute main() and fail for missing root perms

    This minimal test serves as a teaching tool to how these are done:
    - patching an imported bugtool module provided by the bugtool pytest fixture
    - capturing and checking of log messages using the caplog fixture

    :param bugtool: The imported bugtool module object to be patched.
    :param caplog: The caplog pytest fixture for capturing log messages.
    :param mocker: The mocker pytest fixture for mocking functions and attributes.
    """

    mocker.patch("os.getuid", return_value=1000)
    with caplog.at_level(logging.FATAL):
        assert bugtool.main() == 1
    assert len(caplog.record_tuples) == 1
    logger, level, message = caplog.record_tuples[0]
    assert logger == "root"
    assert level == logging.FATAL
    assert message == "Error: xen-bugtool must be run as root"


def patch_bugtool(bugtool, mocker, dom0_template, report_name, tmp_path):
    """Patch a bugtool module with mocks and configurations to execute main()

    :param bugtool: The imported bugtool module object to be patched.
    :param mocker: The mocker object for mocking functions and attributes.
    :param dom0_template: The path to the dom0 template directory.
    :param report_name: The base name of the bug report file and its subdirectory
    :param tmp_path: The temporary path for storing files.
    """

    # Mock os.getuid to simulate the root user:
    mocker.patch("os.getuid", return_value=0)

    # Turn the timestamp in the logs into a fixed string:
    mocker.patch("time.strftime", return_value="time.strftime")

    # Set the name of the bug-report file and the subdirectory in it:
    os.environ["XENRT_BUGTOOL_BASENAME"] = report_name

    # Mock the location of the several path to be in our dom0 template dir:
    bugtool.VAR_LOG_DIR = dom0_template + "/var"
    bugtool.XENSOURCE_INVENTORY = dom0_template + "/etc/xensource-inventory"
    bugtool.SYSTEMD_CONF_DIR = dom0_template + "/etc/systemd"
    bugtool.BIN_STATIC_VDIS = dom0_template + "/opt/xensource/bin/static-vdis"

    # These do not have to be exact mocks, they just have to return success:
    bugtool.HA_QUERY_LIVESET = dom0_template + "/usr/sbin/mdadm"
    bugtool.XENSTORE_LS = dom0_template + "/usr/sbin/xenstore-ls"
    bugtool.PLUGIN_DIR = dom0_template + "/etc/xensource/bugtool"
    bugtool.RPM = dom0_template + "/usr/sbin/multipathd"
    tmp = tmp_path.as_posix()

    # Write a simple xAPI DB for bugtool to filter and check its output later
    xensource_db_conf = tmp + "/db.conf"
    xen_api_state_db = tmp + "/xen_api_state.db"
    with open(xen_api_state_db, "w") as db_state:
        db_state.write(test_xapidb_filter.original)
    with open(xensource_db_conf, "w") as db_conf:
        db_conf.write("[" + xen_api_state_db + "]")
    bugtool.DB_CONF = xensource_db_conf

    # To cover the the code resulting from inputting "n", we need to mock input:
    def return_no_for_proc_files(prompt):
        """Mock the input() function to return "n" when prompted for /proc files"""

        return "n" if "/proc" in prompt else "y"

    if sys.version_info.major == 2:  # pragma: no cover
        bugtool.raw_input = return_no_for_proc_files
    else:
        bugtool.input = return_no_for_proc_files

    entries = [
        "xenserver-config",
        "xenserver-databases",
        "mock",
        "xen-bugtool",
        "unknown",
    ]
    sys.argv.append("--entries=" + ",".join(entries))
    bugtool.BUG_DIR = tmp


def check_output(bugtool, captured, tmp_path, filename, filetype):
    # sourcery skip: path-read
    """Check the stdout, db and inventory output of a bugtool's main() function

    This function checks the output of the bugtool application to ensure that
    it matches the expected output. It compares the captured output with the
    expected output and performs various assertions to validate the output.

    It extracts the output files from the archive and checks that the xAPI db
    and the inventory.xml.

    Tested output:
    - The start and end of the collected bugtool messages from captured.out
    - The inventory.xml file is checked to be validated using its XML schema.
    - The xapi-db.xml is checked to have secrets filtered using a dummy xapi db

    :param bugtool: The patched bugtool module object to be executed
    :param captured: The captured stdout output from running the bugtool main()
    :param tmp_path: The temporary path where the output files are stored.
    :param filename: The name of the bug-report output archive.
    :param filetype: The type of the output file (zip, tar, or tar.bz2)

    :raises AssertionError: When the output does not match the expected output.
    """

    out_begin = bugtool_banner.replace("zip", filetype)
    p = "[time.strftime]  "

    if bugtool.ProcOutput.debug:
        out_begin += p + "Starting 'mdadm --detail --scan'\n"

    fd = "--outfd=" in " ".join(sys.argv)
    if not fd:
        out_begin += p + "Creating output file\n"

    out_begin += p + "Running commands to collect data\n"
    # Provides a nicely formatted diff (unlike str.startswith()) on assertions:
    assert captured.out[: len(out_begin)] == out_begin

    # Assert that the backtrace from the mock data collector is printed:
    for backtrace_string in MOCK_EXCEPTION_STRINGS:
        assert backtrace_string in captured.out

    if bugtool.ProcOutput.debug:
        assert p + "Starting '%s list'\n" % bugtool.BIN_STATIC_VDIS in captured.out
        for ls in ("/opt/xensource", "/etc/xensource/static-vdis"):
            assert p + "Starting 'ls -lR %s'\n" % ls in captured.out

    if not fd:
        archive = "tarball" if filetype.startswith("tar") else "archive"
        success = "Writing %s %s successful.\n" % (archive, filename)
        assert success in captured.out

    # Extract the created output file into the tmp_path
    if filetype == "zip":
        zipfile.ZipFile(filename).extractall(tmp_path)  # nosec # noqa: B202 # NOSONAR
    elif filetype == "tar":
        tar = tarfile.TarFile.open(filename)
        tar.extractall(tmp_path)  # nosec
        tar.close()
    elif filetype == "tar.bz2":
        tar = tarfile.TarFile.open(filename, "r:bz2")
        tar.extractall(tmp_path)  # nosec
        tar.close()

    output_directory = filename.replace(".%s" % filetype, "/")

    # Assert that the captured dummy Xen-API database to filtered as expected:
    with open(output_directory + "/xapi-db.xml") as xen_api_db:
        data = xen_api_db.read()
    test_xapidb_filter.assert_xml_str_equiv(data, test_xapidb_filter.expected)

    # Assert that the captured output from the fake xenstore-ls is as expected:
    with open(output_directory + "/xenstore-ls-f.out") as xenstore_ls_f:
        d = xenstore_ls_f.read()
    assert d == "/local/domain/1/data/set_clipboard = <filtered for security>\n"

    #
    # Given that --entries= includes `xen-bugtool`, the output should contain a log
    # file with the backtrace from the Exception raised by the mock data collector:
    #
    with open(output_directory + "/xen-bugtool.log") as logfile:
        assert_bugtool_logfile_data(logfile)

    # Assertion check of the output files is missing an inventory entry:
    # Do this check in a future test which runs
    assert_valid_inventory_schema(parse(output_directory + "inventory.xml"))


def assert_bugtool_logfile_data(logfile):
    """
    Given that --entries= includes `xen-bugtool`, the output should contain a log
    file with the backtrace from the Exception raised by the mock data collector:
    """
    log = logfile.read()
    lines = log.splitlines()
    assert len(lines) >= 2
    assert lines[0].startswith(
        "xen-bugtool --unlimited --entries=xenserver-config,"
        "xenserver-databases,mock,xen-bugtool,unknown --out",
    )
    assert lines[1].startswith("PATH=")

    #
    # Given that the exception raised by the mock data collector function is
    # caught and logged, the log file should contain the backtrace from the
    # raised exception:
    #
    logfile_lines = 11
    if sys.version_info >= (3, 11):  # pragma: no cover
        logfile_lines += 1  # Python 3.11+ includes a new line in the backtrace
    assert len(lines) == logfile_lines

    #
    # Some log messages are only logged to the logfile, not to stdout:
    # These are not part of MOCK_EXCEPTION_STRINGS as they are
    # only logged to the logfile, not to stdout.
    # They depend on the requested --entries= and the test environment.
    # The order of these log messages in the log is not guaranteed.
    #
    missing = "Missing command for cap "
    only_logged_to_the_logfile = [
        missing + "xenserver-databases: xe pool-dump-database file-name=",
        missing + "mock: /usr/sbin/This command doesn't exist",
    ]
    # Check that all expected lines (also the backtrace) are in the log file:
    for backtrace_string in MOCK_EXCEPTION_STRINGS + only_logged_to_the_logfile:
        assert backtrace_string in log


def assert_valid_inventory(bugtool, args, cap, tmp_path, base_path, filetype):
    """Run the bugtool module object's main() function and check its output

    This function runs the patched bugtool module object and asserts that its
    output matches the expected output.

    :param bugtool: The patched bugtool module object to be executed
    :param args: Additional arguments to set for running the bugtool's main()
    :param cap: cap pytest fixture to validate the bugtool stdout
    :param tmp_path: The temporary path where the output files are stored.
    :param base_path: The base directory and base name of the output file.
    :param filetype: The type of the output file (zip, tar, or tar.bz2)

    :raises AssertionError: When the output does not match the expected output.
    """
    sys.argv.extend(args)

    # Given that we'd like to test handling of exceptions from func_output callbacks,
    # we add a mock data collector function to a mock entry that raises an exception:
    #
    bugtool.entries = ["mock"]
    bugtool.func_output("mock", "function_output.out", mock_data_collector)

    assert bugtool.main() == 0
    filename = base_path + "." + filetype
    with cap.disabled():
        check_output(bugtool, cap.readouterr(), tmp_path, filename, filetype)


@pytest.fixture(scope="function")
def patched_bugtool(bugtool, mocker, dom0_template, tmp_path):
    """PyTest fixture providing a patched bugtool module with mocks and
    configurations to execute its main() from a unprivileged unit test process
    on a regular Linux host, with test data from the framework's dom0 template.

    :param bugtool: The imported bugtool module object to be patched.
    :param mocker: The mocker object for mocking functions and attributes.
    :param dom0_template: The path to the dom0 template directory.
    :param tmp_path: The temporary path for storing files.
    """
    patch_bugtool(bugtool, mocker, dom0_template, "main_mocked", tmp_path)

    base_path = tmp_path / os.environ["XENRT_BUGTOOL_BASENAME"]
    return bugtool, base_path.as_posix(), tmp_path.as_posix()


def test_main_func_output_to_zipfile(patched_bugtool, capfd):
    """Assert creating a zipfile creates a zipfile with a valid XML inventory

    :param patched_bugtool: The patched bugtool module object to be tested
    :param capfd: The capfd pytest fixture capturing stdout and stderr fds
    """

    bugtool, base_path, tmp_path = patched_bugtool
    filetype = "zip"
    args = ["--output=" + filetype]
    assert_valid_inventory(bugtool, args, capfd, tmp_path, base_path, filetype)


def test_main_func_output_to_tarfd(patched_bugtool, capfd):
    """Assert writing a tar fd creates a tarball with a valid XML inventory

    :param patched_bugtool: The patched bugtool module object to be tested
    :param capfd: The capfd pytest fixture capturing stdout and stderr fds
    """

    bugtool, base_path, tmp_path = patched_bugtool
    filetype = "tar"
    filename = base_path + "." + filetype
    # Test writing the tarball to an opened file descriptor:
    fd = os.open(filename, os.O_CREAT | os.O_WRONLY)
    args = ["--outfd=%s" % fd, "--output=tar"]
    bugtool.ProcOutput.debug = False
    assert_valid_inventory(bugtool, args, capfd, tmp_path, base_path, filetype)


def test_main_func_output_to_tarbz2(patched_bugtool, capfd):
    """Assert creating a tar.bz2 creates a tarball with a valid XML inventory

    :param patched_bugtool: The patched bugtool module object to be tested
    :param capfd: The capfd pytest fixture capturing stdout and stderr fds
    """

    bugtool, base_path, tmp_path = patched_bugtool
    filetype = "tar.bz2"
    args = ["--output=" + filetype]
    bugtool.ProcOutput.debug = False
    assert_valid_inventory(bugtool, args, capfd, tmp_path, base_path, filetype)
