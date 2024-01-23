"""tests/integration/test_system_load.py: Test xen-bugtool --entries=system-load"""
import os

from .utils import assert_file, run_bugtool_entry, assert_content_from_dom0_template


# In this test case we need to sleep for 1 sec, and it is sufficient
# to test to only with zip archives to keep the test duration short:
def test_system_load(output_archive_type="zip"):
    """Test xen-bugtool --entries=system-load in test jail created by auto-fixtures in conftest.py"""
    entry = "system-load"

    # Create test input files:
    os.mkdir("/var/log")
    os.mkdir("/var/log/sa")
    with open("/var/log/sa/sa01", "w") as sa01:
        sa01.write("sa01 test data")
    with open("/var/log/sa/sar31", "w") as sar31:
        sar31.write("sar31 test data")

    # Create a dummy sar script to assert that xen-bugtool captures its output:
    os.environ["PATH"] = "/var:" + os.environ["PATH"]
    with open("/var/sar", "w") as sar:
        sar.write("#!/bin/sh\nsleep 1;cat /etc/xensource-inventory\n")
    os.chmod("/var/sar", 0o777)

    run_bugtool_entry(output_archive_type, entry)

    assert_content_from_dom0_template("sar-A.out", "etc/xensource-inventory")
    assert_file("var/log/sa/sa01", "sa01 test data")
    assert_file("var/log/sa/sar31", "sar31 test data")
