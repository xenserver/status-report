"""Unit tests for bugtool core functions creating minimal output archives"""
import os
import tarfile
import zipfile

from lxml.etree import XMLSchema, parse  # pytype: disable=import-error


def assert_valid_inventory_schema(inventory_tree):
    """Assert that the passed inventory validates against the inventory schema"""

    with open(os.getcwd() + "/tests/integration/inventory.xsd") as xml_schema:
        XMLSchema(parse(xml_schema)).assertValid(inventory_tree)


def assert_mock_bugtool_plugin_output(extracted):
    """Assertion check of the output files from the mock bugtool plugin"""
    assert_valid_inventory_schema(parse(extracted + "inventory.xml"))
    with open(extracted + "proc_version.out") as proc_version:
        assert proc_version.read()[:14] == "Linux version "
    with open(extracted + "ls-l-%etc.out") as etc:
        assert etc.read()[:6] == "total "
    with open(extracted + "proc/self/status") as status:
        assert status.read()[:5] == "Name:"
    with open(extracted + "proc/sys/fs/epoll/max_user_watches") as max_user_watches:
        assert int(max_user_watches.read()) > 0


def minimal_bugtool(bugtool, dom0_template, archive, subdir):
    """Load the plugins from the template and include the generated inventory"""

    # Load the mock plugin from dom0_template and process the plugin's caps:
    bugtool.PLUGIN_DIR = dom0_template + "/etc/xensource/bugtool"
    bugtool.entries = ["mock"]
    bugtool.load_plugins(just_capabilities=False)
    bugtool.data["ls -l /etc"]["cmd_args"][2] = dom0_template + "/etc"
    bugtool.collect_data(subdir, archive)
    bugtool.include_inventory(archive, subdir)
    archive.close()


def test_tar_output(bugtool, tmp_path, dom0_template):
    """Assert that a bugtool unit test creates a valid minimal tar archive"""

    bugtool.BUG_DIR = tmp_path
    archive = bugtool.TarOutput("tarball", "tar", -1)
    subdir = "tar_dir"

    # Create a minimal bugtool output archive to test core functions:
    minimal_bugtool(bugtool, dom0_template, archive, subdir)

    # Check the TarFile contents
    tmp = tmp_path.as_posix()
    tar_archive = tarfile.TarFile(tmp + "/tarball.tar")
    tar_archive.extractall(tmp)
    tar_archive.close()
    assert_mock_bugtool_plugin_output(tmp + "/" + subdir + "/")


def test_zip_output(bugtool, tmp_path, dom0_template):
    """Assert that a bugtool unit test creates a valid minimal zip archive"""

    bugtool.BUG_DIR = tmp_path
    archive = bugtool.ZipOutput("zipfile")
    subdir = "zip_dir"

    # Create a minimal bugtool output archive to test core functions:
    minimal_bugtool(bugtool, dom0_template, archive, subdir)

    # Check the ZipFile contents
    tmp = tmp_path.as_posix()
    zipfile.ZipFile(tmp + "/zipfile.zip").extractall(tmp)
    assert_mock_bugtool_plugin_output(tmp + "/" + subdir + "/")
