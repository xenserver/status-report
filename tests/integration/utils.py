"""tests/integration/utils.py: utility functions to test xen-bugtool by invoking it"""
from __future__ import print_function

import filecmp
import os
import shutil
import sys
import tarfile
import zipfile
from subprocess import PIPE, Popen

from lxml import etree

if sys.version_info.major == 2:
    from commands import getoutput  # pyright: ignore[reportMissingImports]
else:
    from subprocess import getoutput

BUGTOOL_OUTPUT_DIR = "/var/opt/xen/bug-report/"
BUGTOOL_DOM0_TEMPL = "tests/integration/dom0-template"


def run(command):
    """Run the given shell command, print it's stdout and stderr and return them"""
    process = Popen(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    stdout, stderr = process.communicate()
    returncode = process.wait()
    print("# " + " ".join(command) + ":")
    if returncode:
        raise Exception(returncode, stderr)
    print(stdout, stderr)
    return stdout, stderr


def assert_cmd(cmd, remove_file):
    """Run the given command, print its stdout and stderr and return them. Remove the given remove_file"""
    stdout, stderr = run(cmd)
    # After successfuly verficiation of the files, remove the checked output file(missed files remain):
    os.unlink(remove_file)
    return stdout, stderr


def check_file(path):
    """Return the contents of the passed bugtool output file for verification"""
    with open(path) as handle:
        contents = handle.read()
    # After successfuly verficiation of the files, remove the checked output file (missed files remain):
    os.unlink(path)
    return contents


def verify_content_from_dom0_template(path):
    """Compare the contents of output directories or files with the test's Dom0 template directories"""
    assert path[0] != "/"
    assert filecmp.dircmp(path, BUGTOOL_DOM0_TEMPL + path)
    # After successfuly verficiation of the files, remove the checked output files (missed files remain):
    try:
        os.unlink(path)
    except OSError:
        shutil.rmtree(path)


def run_bugtool_entry(archive_type, test_entries):
    """Run bugtool for the given entry or entries, extract the output, and chdir to it"""
    os.environ["XENRT_BUGTOOL_BASENAME"] = test_entries
    # For case the default python interpreter of the user is python3, we must use python2(for now):
    command = "python2 ./xen-bugtool -y --output=%s --entries=%s" % (archive_type, test_entries)
    print("# " + command)
    print(getoutput(command))
    srcdir = os.getcwd()
    os.chdir(BUGTOOL_OUTPUT_DIR)
    output_file = test_entries + "." + archive_type
    print("# Unpacking " + BUGTOOL_OUTPUT_DIR + output_file + " and verifying inventory.xml")
    # Python2.7 does not have shutil.unpack_archive():
    # shutil.unpack_archive(output_file):
    if archive_type == "zip":
        archive = zipfile.ZipFile(output_file)
    elif archive_type == "tar":
        archive = tarfile.open(output_file)
    elif archive_type == "tar.bz2":
        archive = tarfile.open(output_file, "r:bz2")
    else:
        raise RuntimeError("Unsupported output archive type: %s" % archive_type)
    archive.extractall()
    os.chdir(test_entries)
    # Validate the extracted inventory.xml using the XML schema from the test framework:
    with open(srcdir + "/tests/integration/inventory.xsd") as xmlschema:
        etree.XMLSchema(etree.parse(xmlschema)).assertValid(etree.parse("inventory.xml"))
        # After successfuly validation of the inventory.xml, remove it (not removed files make the test fail):
        os.unlink("inventory.xml")
