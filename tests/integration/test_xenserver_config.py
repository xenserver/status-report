"""Test xen-bugtool --entries=server-config"""

import os

from .utils import (
    assert_cmd,
    assert_file,
    run_bugtool_entry,
    assert_content_from_dom0_template,
)


def test_xenserver_config(output_archive_type):
    """
    Run xen-bugtool --entries=xenserver-config in test jail
    (created by auto-fixtures, see README-pytest-chroot.md)
    """
    entry = "xenserver-config"

    run_bugtool_entry(output_archive_type, entry)

    # Check the output of xen-bugtool --entries=xenserver-config:

    assert_file("ls-lR-%opt%xensource.out", "/opt/xensource:", only_first_line=True)
    assert_file("ls-lR-%etc%xensource%static-vdis.out", "")
    assert_file("static-vdis-list.out", "list")

    # Assert the contents of the extracted etc/systemd.tar

    # etc/systemd.tar's toplevel directory is os.environ["XENRT_BUGTOOL_BASENAME"]
    os.chdir("..")

    # Extract the etc/systemd.tar file:
    assert_cmd(["tar", "xvf", entry + "/etc/systemd.tar"], entry + "/etc/systemd.tar")

    # Change back to the bugtool output to check the etc/systemd directory:
    os.chdir(entry)

    assert_content_from_dom0_template("etc/systemd")
    assert_content_from_dom0_template("etc/xensource-inventory")
