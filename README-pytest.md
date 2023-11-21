# Guide to Setting Up and Running the Xen-Bugtool Test Environment

This document provides detailed information about the test environment for `xen-bugtool`,
a tool designed to assist with debugging XenServer issues.
The test environment runs `xen-bugtool` in a container with simulated `root` capabilities,
allowing it to be run by any regular user without requiring special system configuration.

This document guides you through the setup of the container and the execution of each test case.

## Lessons Learned from the Initial Prototype

The initial shell-based tests were quick to create, but were only meant as an early prototype.
These tests required an external environment with root privileges (preferably a container) to run.
Additionally, failed checks because of mismatched file paths could go unnoticed,
leading to tests passing even when the `bugtool` output was not properly verified.

## Installing Packages to Run the Xen-Bugtool Test Environment

Ensure that `pip` is installed in your `python2.7` environment. Same for Python3, but it's optional.

Install the libraries required by `xen-bugtool` with the following command:

```sh
# Install the libraries required to run `xen-bugtool` itself into your environment:
python2 -m pip install --user -r requirements.txt
```

The test framework itself can use Python2 or Python3.
Depending on the installed builds, you can install one or both:

```sh
# Install pytest and its depdendencies into your environment:
python2 -m pip install --user -r requirements-dev.txt # and/or:
python3 -m pip install --user -r requirements-dev.txt
```

## Running the Xen-Bugtool Test Environment

```py
# Run the Xen-Bugtool Test Environment
python3 -m pytest tests/integration
```
Hint: `python2 -m pytest` could be used too, but it may run into problems on CentOS 8.0.

## Implementation of the Xen-Bugtool Test Environment in Pytest

This section provides detailed information about the test environment for `xen-bugtool`.
It explains how the container is set up and how each test case is executed.

The test environment is implemented by automatic `pytest` fixtures creating a container for the `pytest` process session and its sub-processes.
A fresh instance of a clean `bugtool` output directory (located at `/var/opt/xen/bug-report`)
is provided for invocation of the test functions.

## Container Setup

The container is implemented in [tests/integration/namespace_container.py](tests/integration/namespace_container.py).

`xen-bugtool` requires to be run as root and checks it and writes its output to `/var/opt/xen/bug-report`.
The container setup provides these root privileges and a new mount namespace to bind-mount the test files.
It allows to bind-mount the directory trees with test files at the places where `xen-bugtool` collects them.
The mount namespace also allows to create a `tmpfs` mount at `/var/opt/xen/bug-report` for the output data.
It avoids the need to create a temporary directory and to bind-mount it into the container.
Additionally, it ensures that no temporary data can accumulate on the host.

It implements the equivalent of `/usr/bin/unshare --map-root-user --mount --net` and mounts test directories:

- `--map-root-user`: Creates a Linux user namespace where the effective user and group IDs of the current user are mapped to the superuser UID and GID.
- `--mount`: Creates a Linux mount namespace for mounting temporary file systems and bind-mounting test data.
- `--net`: Creates a Linux network namespace to ensure that `bugtool` works without outside connectivity.

The container then bind-mounts the directory trees from [tests/integration/dom0-template](tests/integration/dom0-template) into the container.
This means the object under test (`xen-bugtool`) runs in an isolated test environment.

## Test Case Execution

For each test case and each output format, the test fixture and the test case code perform the following steps:

1. The fixture mounts a `tmpfs` directory for `bugtool` to use for its output at the static path it uses.
2. The fixture yields to the test case implementation for running the individual test.
3. The test case code implementation runs `xen-bugtool` with the arguments required by the test.
4. The function to run it checks that the `inventory.xml` in the output archive conforms to the XML schema.
5. The test case checks all output files and removes all files that it successfully verified.
6. The fixture then asserts that the test case has not left any remaining unexpected files in the output tree.
7. The fixture then unmounts the temporary output directory, preparing for the next test case to start afresh.
