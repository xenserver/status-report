"""tests/conftest.py: top-level pytest fixtures for testing xen-bugtool

Introduction to fixtures:
https://docs.pytest.org/en/8.0.x/fixture.html

How to use fixtures:
https://docs.pytest.org/en/8.0.x/how-to/fixtures.html

The full documentation on fixtures:
https://docs.pytest.org/en/8.0.x/reference/fixtures.html
"""

import os

import pytest


@pytest.fixture(scope="session")
def tests_dir():
    """pytest fixture to provide the path to status-report/tests"""
    return os.path.dirname(__file__)


@pytest.fixture(scope="session")
def bugtool_script(tests_dir):
    """pytest fixture to provide the path to status-report/tests"""
    return os.path.abspath(os.path.join(tests_dir, os.pardir, "xen-bugtool"))


@pytest.fixture(scope="session")
def mocks_dir(tests_dir):
    """pytest fixture to provide the path to status-report/tests/mocks"""
    return os.path.join(tests_dir, "mocks")


@pytest.fixture(scope="session")
def dom0_template(tests_dir):
    """Fixture to provide the path to status-report/tests/integration/dom0-template"""
    return os.path.join(tests_dir, "integration", "dom0-template")
