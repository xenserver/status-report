"""Regression tests for the bugtool helper function mdadm_arrays()"""
import os
import sys

import pytest


@pytest.mark.skipif(sys.version_info >= (3, 0), reason="limited to python2 until fixed")
def test_mdadm_arrays(bugtool, testdir):
    """Assert mdadm_arrays() returning arrays of the mdadm mockup in the dom0-template"""

    os.environ["PATH"] = testdir + "/../integration/dom0-template/usr/sbin"
    assert list(bugtool.mdadm_arrays()) == ["/dev/md0", "/dev/md1"]
