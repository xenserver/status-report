"""Unit tests for bugtool core functions creating minimal output archives"""
import os
import tarfile
import zipfile

from lxml.etree import XMLSchema, parse  # pytype: disable=import-error


def assert_valid_inventory_schema(inventory_tree):
    """Assert that the passed inventory validates against the inventory schema"""

    with open(os.getcwd() + "/tests/integration/inventory.xsd") as xml_schema:
        XMLSchema(parse(xml_schema)).assertValid(inventory_tree)


def assert_mock_bugtool_plugin_output(temporary_directory, subdir, names):
    """Assertion check of the output files from the mock bugtool plugin"""

    # Assert the list of file names in the status report archive:
    expected_names = [
        subdir + "/etc/group",
        subdir + "/etc/passwd.tar",
        subdir + "/inventory.xml",
        subdir + "/ls-l-%etc.out",
        subdir + "/proc/self/status",
        subdir + "/proc/sys/fs/epoll/max_user_watches",
        subdir + "/proc_version.out",
    ]
    assert sorted(names) == expected_names

    extracted = "%s/%s/" % (temporary_directory, subdir)

    # Will be refactored to be more easy in a separate commit soon:
    assert_valid_inventory_schema(parse(extracted + "inventory.xml"))
    with open(extracted + "proc_version.out") as proc_version:
        assert proc_version.read()[:14] == "Linux version "
    with open(extracted + "ls-l-%etc.out") as etc:
        assert etc.read()[:6] == "total "
    with open(extracted + "proc/self/status") as status:
        assert status.read()[:5] == "Name:"
    with open(extracted + "proc/sys/fs/epoll/max_user_watches") as max_user_watches:
        assert int(max_user_watches.read()) > 0
    with open(extracted + "etc/group") as group:
        assert group.readline() == "root:x:0:\n"

    # Check the contents of the sub-archive "etc/passwd.tar":
    with tarfile.TarFile(extracted + "etc/passwd.tar") as tar:
        assert tar.getnames() == [subdir + "/etc/passwd"]
        # TarFile.extractfile() does not support context managers on Python2:
        passwd = tar.extractfile(subdir + "/etc/passwd")
        assert passwd
        assert passwd.readline() == b"root:x:0:0:root:/root:/bin/bash\n"
        passwd.close()


def minimal_bugtool(bugtool, dom0_template, archive, subdir):
    """Load the plugins from the template and include the generated inventory"""

    # Load the mock plugin from dom0_template and process the plugin's caps:
    bugtool.PLUGIN_DIR = dom0_template + "/etc/xensource/bugtool"
    bugtool.entries = ["mock"]
    archive.declare_subarchive("/etc/passwd", subdir + "/etc/passwd.tar")
    bugtool.load_plugins(just_capabilities=False)
    # Mock the 2nd argument of the ls -l /etc to collect it using dom0_template:
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
    with tarfile.TarFile(tmp + "/tarball.tar") as tar:
        tar.extractall(tmp)
        assert_mock_bugtool_plugin_output(tmp, subdir, tar.getnames())


def test_zip_output(bugtool, tmp_path, dom0_template):
    """Assert that a bugtool unit test creates a valid minimal zip archive"""

    bugtool.BUG_DIR = tmp_path
    archive = bugtool.ZipOutput("zipfile")
    subdir = "zip_dir"

    # Create a minimal bugtool output archive to test core functions:
    minimal_bugtool(bugtool, dom0_template, archive, subdir)

    # Check the ZipFile contents
    tmp = tmp_path.as_posix()
    with zipfile.ZipFile(tmp + "/zipfile.zip") as zip:
        zip.extractall(tmp)
        assert_mock_bugtool_plugin_output(tmp, subdir, zip.namelist())
