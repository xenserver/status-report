"""tests/integration/test_xenserver_config.py: Test xen-bugtool --entries=xenserver-config"""
import os

from .utils import assert_cmd, check_file, run_bugtool_entry, assert_content_from_dom0_template


def test_xenserver_config(output_archive_type):
    """Test xen-bugtool --entries=xenserver-config in test jail created by auto-fixtures in conftest.py"""
    entry = "xenserver-config"

    run_bugtool_entry(output_archive_type, entry)

    # Assert that the bugtool output archive of --entries=xenserver-config matches our expectations for it:
    assert check_file("ls-lR-%opt%xensource.out").splitlines()[0] == "/opt/xensource:"
    assert check_file("ls-lR-%etc%xensource%static-vdis.out") == ""
    assert check_file("static-vdis-list.out") == "list"

    # Assert the contents of the extracted etc/systemd.tar
    os.chdir("..")
    # etc/systemd.tar's toplevel directory is os.environ["XENRT_BUGTOOL_BASENAME"] (= entries for the test)
    assert_cmd(["tar", "xvf", entry + "/etc/systemd.tar"], entry + "/etc/systemd.tar")

    os.chdir(entry)
    assert_content_from_dom0_template("etc/systemd")
    assert_content_from_dom0_template("etc/xensource-inventory")
