"""Regression tests for the bugtool helper function mdadm_arrays()"""

import pytest


def test_mdadm_arrays(bugtool, dom0_template):
    """Assert mdadm_arrays() returning arrays dom0_template/usr/sbin/mdadm"""
    bugtool.MDADM = dom0_template + "/usr/sbin/mdadm"
    assert list(bugtool.mdadm_arrays()) == ["/dev/md0", "/dev/md1"]


@pytest.mark.xfail("True", reason="Python2 decode() fails with UTF-8: remove it next")
def test_module_info(bugtool, dom0_template):
    """Assert module_info() returning module names from test_module_info.modules"""

    bugtool.PROC_MODULES = __file__.replace(".py", ".modules")
    bugtool.MODINFO = dom0_template + "/usr/sbin/modinfo"
    # Expect bytes containing the UTF-8 sequence \xc3\xa1 in the names of the authors
    expected = b"""\
filename:       /lib/modules/6.6.22+0/kernel/drivers/platform/x86/dell/dell-smbios.ko
license:        GPL
description:    Common functions for kernel modules using Dell SMBIOS
author:         Mario Limonciello <mario.limonciello@outlook.com>
author:         Pali Roh\xc3\xa1r <pali@kernel.org>
author:         Gabriele Mazzotta <gabriele.mzt@gmail.com>
author:         Matthew Garrett <mjg@redhat.com>
srcversion:     CBEF13F3C192A771A462239
alias:          wmi:A80593CE-A997-11DA-B012-B622A1EF5492
depends:        dell-wmi-descriptor,dcdbas,wmi
retpoline:      Y
intree:         Y
name:           dell_smbios
vermagic:       6.6.22+0 SMP mod_unload modversions
"""
    assert bugtool.module_info(bugtool.CAP_KERNEL_INFO) == expected


def test_multipathd_topology(bugtool, dom0_template):
    """Assert multipathd_topology() returning the output of the faked multipathd tool"""

    bugtool.MULTIPATHD = dom0_template + "/usr/sbin/multipathd"
    assert bugtool.multipathd_topology(bugtool.CAP_MULTIPATH) == "multipathd-k"
