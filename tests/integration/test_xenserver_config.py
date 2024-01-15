"""tests/integration/test_xenserver_config.py: Test xen-bugtool --entries=xenserver-config"""
import os

from .utils import assert_cmd, check_file, run_bugtool_entry, assert_content_from_dom0_template


def test_xenserver_config(output_archive_type):
    """Test xen-bugtool --entries=xenserver-config in test jail created by auto-fixtures in conftest.py"""
    entry = "xenserver-config"

    # Add config files for SNMP
    os.makedirs("/etc/snmp", exist_ok=True)
    snmp_xs_conf_init_str = (
        '"community": "INITIAL_STR",\n'
        + '"authentication_key": "INITIAL_STR",\n'
        + '"privacy_key": "INITIAL_STR",'
    )
    with open("/etc/snmp/snmp.xs.conf", "w") as snmp_xs_conf:
        snmp_xs_conf.write(snmp_xs_conf_init_str)

    with open("/etc/snmp/snmpd.xs.conf", "w") as snmpd_xs_conf:
        snmpd_xs_conf.write("com2sec notConfigUser default INITIAL_STR")

    os.makedirs("/var/lib/net-snmp", exist_ok=True)
    snmpd_conf_init_str = (
        "usmUser 1 3 0x80001f8880f369b576d8b2a46500000000 0x7872746d69612d30372d3035 "
        + "0x7872746d69612d30372d3035 NULL .1.3.6.1.6.3.10.1.1.3 "
        + "INITIAL_STR "
        + ".1.3.6.1.6.3.10.1.2.2 "
        + "INITIAL_STR "
        + "0x"
    )
    with open("/var/lib/net-snmp/snmpd.conf", "w") as snmpd_conf:
        snmpd_conf.write(snmpd_conf_init_str)

    os.makedirs("/etc/sysconfig", exist_ok=True)
    with open("/etc/sysconfig/snmpd", "w") as snmpd:
        snmpd.write('OPTIONS="-c /etc/snmp/snmpd.xs.conf -m +XENSERVER-MIB -Dxenserver -LS0-7d"')

    run_bugtool_entry(output_archive_type, entry)

    # Assert that the bugtool output archive of --entries=xenserver-config matches our expectations for it:
    assert check_file("ls-lR-%opt%xensource.out").splitlines()[0] == "/opt/xensource:"
    assert check_file("ls-lR-%etc%xensource%static-vdis.out") == ""
    assert check_file("static-vdis-list.out") == "list"

    # Assert the contents of the extracted etc/systemd.tar
    os.chdir("..")
    # etc/systemd.tar's toplevel directory is os.environ["XENRT_BUGTOOL_BASENAME"] (= entries for the test)
    assert_cmd(["tar", "xvf", entry + "/etc/systemd.tar"], entry + "/etc/systemd.tar")

    os.chdir(entry)
    assert_content_from_dom0_template("etc/systemd")
    assert_content_from_dom0_template("etc/xensource-inventory")

    # Assert SNMP config files have been collected and the sensitive strings have been replaced.
    snmp_xs_conf_out_str = (
        '"community": "REMOVED",\n' + '"authentication_key": "REMOVED",\n' + '"privacy_key": "REMOVED",'
    )
    assert check_file("snmp_xs_conf.out") == snmp_xs_conf_out_str
    assert check_file("snmpd_xs_conf.out") == "com2sec notConfigUser default REMOVED"
    snmpd_conf_out_str = (
        "usmUser 1 3 0x80001f8880f369b576d8b2a46500000000 0x7872746d69612d30372d3035 "
        + "0x7872746d69612d30372d3035 NULL .1.3.6.1.6.3.10.1.1.3 "
        + "REMOVED "
        + ".1.3.6.1.6.3.10.1.2.2 "
        + "REMOVED "
        + "0x"
    )
    assert check_file("snmpd_conf.out") == snmpd_conf_out_str
    assert (
        check_file("etc/sysconfig/snmpd")
        == 'OPTIONS="-c /etc/snmp/snmpd.xs.conf -m +XENSERVER-MIB -Dxenserver -LS0-7d"'
    )
