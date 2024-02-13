# Documentation on the pytest-chroot framework

This test environment runs `xen-bugtool` in a container with simulated `root`
capabilities, for regular users without requiring special system configuration.

Because it uses a container, developers using it must be familiar with tests
that executes code which switches into a container.
In the container, code lives inside its own private mount namespace,
where it can mount special file system trees to simulate a XenServer
Dom0 without patching the program under test.

The unique feature of this container is that `xen-bugtool` can run like
in Dom0 and even execute arbitrary other programs like it does in Dom0.
Even those other programs that it calls run in the same container.
And these programs can be specially prepared programs which simulate
errors that would be very hard to create outside the container.

However, this requires the developer to be familiar with the concept of
`containers` or `chroot` which may puzzle beginners. While it can be used
to run `xen-bugtool` virtually untouched in it, believing it has root
capabilities and test error handling without any mocking of `xen-bugtool`,
the unit tests are the preferred environment for beginners.

## Implementation of the pytest-chroot Test Environment in Pytest

This environment uses autouse `pytest` fixtures creating a container.

Using the container, a fresh instance of a clean output directory
`/var/opt/xen/bug-report`) is provided for each test, and its contents
are checked after each test.

## Implementation of the container by pytest-chroot framework

- Assumption to be run as root:
  `xen-bugtool` assumes to be run as root, checks it and writes
  its output to `/var/opt/xen/bug-report`.
- The container simulates these root privileges using a root-less container
  with a new mount namespace to bind-mount the test files.
- The container allows to bind-mount the directory trees with test files
  at the places where `xen-bugtool` collects them.
- The mount namespace also allows to create a `tmpfs` mount at
  `/var/opt/xen/bug-report` for the output data.
- It avoids the need to create a temporary directory and to bind-mount
  it into the container.
- Additionally, it ensures that no temporary data can accumulate on the host.

It implements `/usr/bin/unshare --map-root-user --mount --net`
using and mounts test directories:

- `--map-root-user`: Creates a Linux user namespace where the effective user
  and group IDs of the current user are mapped to the superuser UID and GID.
- `--mount`: Creates a Linux mount namespace for mounting temporary file
  systems and bind-mounting test data.
- `--net`: Creates a Linux network namespace to ensure that `bugtool` works
  without outside connectivity.

The container then bind-mounts the directory trees from
[tests/integration/dom0-template](tests/integration/dom0-template)
into the container. This means the object under test (`xen-bugtool`)
runs in an isolated test environment.

This is mostly implemented in
[tests/integration/namespace_container.py](tests/integration/namespace_container.py).

## Work flow of Test Case Execution using the pytest-chroot framework

The test fixture and the test case code perform the following steps
- for each test case and
- for each output format:

The test fixture:
1. mounts a `tmpfs` for `bugtool` to use for its output at the hard-coded path.
2. yields to the test case implementation for running the individual test.

The test case code itself then starts to act. It:
- runs a function to run `xen-bugtool` with the arguments required by the test.

This wrapper function:
1. Runs `xen-bugtool` with the given arguments
2. Asserts the `inventory.xml` to validate against the created XML schema.

The test case code itself then starts the custom verification. It:
1. Checks all output files and removes all files that it successfully verified.
2. Returns control to the test fixture by simply returning.

Finally, the test fixture:
- asserts that now remaining untested/unexpected files are in the output tree.
- unmounts the temporary output directory,
  preparing for the next test case to start afresh.
