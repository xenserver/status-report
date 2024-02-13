"""
Test fixtures to test using Linux namespaces,
see README-pytest-chroot.md for an overview:
"""

from __future__ import print_function

import os

import pytest

from .namespace_container import (
    activate_private_test_namespace,
    mount,
    umount,
)
from .utils import BUGTOOL_DOM0_TEMPL, BUGTOOL_OUTPUT_DIR, run


@pytest.fixture(autouse=True, scope="session")
def create_and_enter_test_environment():
    """Activate a namespace with bind mounts for testing xen-bugtool"""
    activate_private_test_namespace(
        BUGTOOL_DOM0_TEMPL, ["/etc", "/opt", "/usr/sbin", "/usr/lib/systemd"]
    )
    os.environ["PYTHONPATH"] = "tests/mocks"


# zip, tar, tar.bz2 are the three output formats supported by xen_bugtool:
@pytest.fixture(scope="function", params=("zip", "tar", "tar.bz2"))
def output_archive_type(request):
    """Parameterized: Issues calls for each of the three output_archive_types"""

    return request.param


@pytest.fixture(autouse=True, scope="function")
def run_test_functions_with_private_tmpfs_output_directory():
    """Yielding fixture: Run test with a bugtool output directory using tmpfs"""

    #
    # Prepare
    #

    # Mount tmpfs into the private namespace:
    mount(target="/var", fs="tmpfs", options="size=128M")
    src_dir = os.getcwd()

    #
    # Execute
    #
    yield  # The test case runs here, control returns when it exits

    #
    # Assert
    #

    #
    # Assert that the test case did not leave any unchecked output
    # file as in the output directory:
    #
    os.chdir(BUGTOOL_OUTPUT_DIR)
    remaining_files = []
    for current_path, _, files in os.walk("."):  # pragma: no cover
        for file in files:
            remaining_files.append(os.path.join(current_path, file))  # pragma: no cover
    if remaining_files:  # pragma: no cover
        print("Remaining (possibly unchecked) files found:")
        print(remaining_files)
        os.chdir(BUGTOOL_OUTPUT_DIR)
        run(["find", "-type", "f"])
        os.chdir(src_dir)
        print("Ensure that these files are checked, remove them when checked.")
        umount("/var")
        raise RuntimeError(
            "Remaining (possibly unchecked) files found. Run 'pytest -rF' for logs"
        )

    #
    # Clean-up
    #

    # Restore the original source directory before returning back to pytest
    os.chdir(src_dir)

    # Unmount the tmpfs we mounted to /var, the next test will create it fresh:
    umount("/var")
