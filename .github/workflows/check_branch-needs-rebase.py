#!/usr/bin/env python3
"""Check if the current branch is up-to-date with the remote branch."""

# pylint: disable=using-f-string-in-unsupported-version
import subprocess
import sys
from logging import basicConfig, INFO, info as log


def run(command: list[str], check=False) -> tuple[int, str]:
    """Run a command and return the output."""
    log(" ".join(command))
    cmd: subprocess.CompletedProcess[str] = subprocess.run(
        command,
        check=check,
        text=True,
        capture_output=True,
    )
    return cmd.returncode, cmd.stdout.strip()


def check_if_local_branch_is_behind_target(
    current_branch: str,
    target="origin/master",
) -> int:
    """
    Check if the current branch is behind the target branch.

    Return: int - the number of commits behind the target branch or 0 if up-to-date
    """

    # Fetch the remote branch in order to get the number of commits behind
    if run(["git", "fetch", *target.split("/", maxsplit=1)])[0]:
        log("Failed to fetch the remote branch, but you may be offline, go online.")

    # Get the number of commits behind the remote branch
    error, commits_behind = run(
        ["git", "rev-list", "--left-right", "--count", f"{target}...{current_branch}"],
    )
    if error:
        log(f"Failed to get the number of commits behind {target}")
        return 1

    # If the current branch is behind the remote branch, print the commits
    # and return the number of commits behind
    if commits_behind.split()[0] != "0":
        print(
            f"The current branch {current_branch} is behind {target} "
            f"by {commits_behind.split()[0]} commits:"
        )

        left_right = run(
            ["git", "rev-list", "--left-right", "--oneline", f"{target}...HEAD"],
        )[1]
        for line in left_right.split("\n"):
            if line.startswith("<"):
                print(line.replace("<", ""))

        return int(commits_behind.split()[0])  # Return the number of commits behind

    print(f"The current branch {current_branch} is up-to-date with {target}")
    return 0  # Return 0 if the current branch is up-to-date


def get_remote_default_branch(remote_url):
    """Get the default branch name of the remote repository."""

    default_branch_info = subprocess.check_output(
        ["git", "ls-remote", "--symref", remote_url, "HEAD"], text=True
    )
    return default_branch_info.strip().split("\t")[0].split("refs/heads/")[1]


def main():
    """Check if the current branch is up-to-date with the remote branch.

    Check if the current branch is up-to-date with the remote branch.
    On errors and if not up-to-date, return an error exit code.
    """

    # Check if the current directory is a git repository
    # Get the current branch name
    current_branch = subprocess.check_output(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True
    ).strip()

    # Get the default branch name of the remote repository
    err, remote_ref = run(
        ["git", "rev-parse", "--abbrev-ref", f"{current_branch}@{{upstream}}"],
    )
    if err:  # Default to origin/master if no upstream is set yet
        target = "origin/master"
    else:
        remote = remote_ref.split("/")[0]
        remote_default = get_remote_default_branch(remote)
        target = f"{remote}/{remote_default}"

    return check_if_local_branch_is_behind_target(current_branch, target)


if __name__ == "__main__":
    basicConfig(format="%(message)s", level=INFO)
    sys.exit(main())
