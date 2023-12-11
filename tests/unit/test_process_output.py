"""Regression tests for the bugtool helper function mdadm_arrays()"""


def test_mdadm_arrays(bugtool, dom0_template):
    """Assert mdadm_arrays() returning arrays of the mdadm mockup in the dom0-template"""
    assert list(bugtool.mdadm_arrays()) == ["/dev/md0", "/dev/md1"]


def test_module_info(bugtool, dom0_template):
    """Assert module_info() returning module names from mockup file in the dom0-template"""

    bugtool.PROC_MODULES = __file__.replace(".py", ".modules")
    output = bugtool.module_info(bugtool.CAP_KERNEL_INFO)
    assert output == "modinfo for tcp_diag\nmodinfo for udp_diag\nmodinfo for inet_diag\n"


def test_multipathd_topology(bugtool, dom0_template):
    """Assert multipathd_topology() returning the output of the faked multipathd tool"""
    assert bugtool.multipathd_topology(bugtool.CAP_MULTIPATH) == bugtool.MULTIPATHD + "-k"
