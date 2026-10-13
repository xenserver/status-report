"""Regression tests for bugtool helper functions like get_recent_logs()"""


def test_get_recent_logs(bugtool):
    """Assert get_recent_logs() returning the most recent file(s)"""

    files = ["/proc/1/stat", "/proc/self/stat"]  # self/stat is more recent.
    # return the files, ordered by their modification time, most recent first:
    assert bugtool.get_recent_logs(files, 9) == files
    assert bugtool.get_recent_logs([files[1], files[0]], 9) == files
    # When verbosity is 1, only return the most recent file:
    assert bugtool.get_recent_logs(files, 1) == [files[1]]


def test_get_rotated_logs(bugtool, tmpdir):
    """Assert get_rotated_logs() returning all the rotations of the logs"""

    kern = str(tmpdir.join("kern.log"))
    wtmp = str(tmpdir.join("wtmp"))
    for name in ["kern.log", "kern.log.1", "kern.log.1.bak", "wtmp.1"]:
        tmpdir.join(name).write("")
    for number in range(2, 26):
        tmpdir.join("kern.log.%d.gz" % number).write("")

    # All the rotations, beyond the 19th, ordered by number, then by log.
    # kern.log.1.bak is not a rotation: neither `<log>.<n>` nor `<log>.<n>.gz`.
    expected = [kern + ".1", wtmp + ".1"] + [kern + ".%d.gz" % n for n in range(2, 26)]
    assert bugtool.get_rotated_logs([kern, wtmp], 9) == expected
    # 8 is the highest verbosity which limits the rotations: only return
    # the rotations 1 to 7:
    expected = [kern + ".1", wtmp + ".1"] + [kern + ".%d.gz" % n for n in range(2, 8)]
    assert bugtool.get_rotated_logs([kern, wtmp], 8) == expected


def test_read_inventory(bugtool, dom0_template):
    """Assert readKeyValueFile() reading the a xensource inventory file"""

    inventory = bugtool.readKeyValueFile(dom0_template + bugtool.XENSOURCE_INVENTORY)
    assert inventory["PRODUCT_VERSION"] == "8.3.0"


def test_disk_list(bugtool, tmpdir):
    """Test bugtool.disk_list() to filter disks an only return native disks"""

    # Arrange:

    # Save the original value of bugtool.PROC_PARTITIONS and set it to the new file:
    proc_partitions = bugtool.PROC_PARTITIONS

    # Replace the original file with a new one:
    bugtool.PROC_PARTITIONS = str(tmpdir.join("partitions"))
    tmpdir.join("partitions").write(
        """major minor  #blocks  name

    8    0  125034840 sda
    8    1  125033856 sda1
    8   16  125034840 sdb
    8   17  125033856 sdb1
    220  0  125034840 xvda
    220  1  125033856 xvda1
    259  0  125034840 nvme0n1
    259  1  125033856 nvme0n1p1
    """
    )

    # Assert:

    # nvme0n1 is removed by disk_list as its major number is 259 (not < 254):
    assert bugtool.disk_list() == ["sda", "sdb"]

    # Restore:

    # Restore the original value of bugtool.PROC_PARTITIONS:
    bugtool.PROC_PARTITIONS = proc_partitions
