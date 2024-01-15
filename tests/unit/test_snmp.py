"""Regression tests for bugtool functions like filter_snmp*_conf()"""

import sys


if sys.version_info.major == 3:
    builtin_module_name = "builtins"
else:
    builtin_module_name = "__builtin__"


def test_filter_snmp_xs_conf(bugtool, mocker):
    """Assert filter_snmp_xs_conf() replaces sensitive strings"""
    snmp_xs_conf_init_str = """
        "community": "INITIAL_STR",
        "authentication_key": "INITIAL_STR",
        "privacy_key": "INITIAL_STR",
    """
    mocker.patch(
        "{}.open".format(builtin_module_name),
        new=mocker.mock_open(read_data=snmp_xs_conf_init_str),
        create=True,
    )

    snmp_xs_conf_out_str = """
        "community": "REMOVED",
        "authentication_key": "REMOVED",
        "privacy_key": "REMOVED",
    """
    assert bugtool.filter_snmp_xs_conf("_") == snmp_xs_conf_out_str


def test_filter_snmpd_xs_conf(bugtool, mocker):
    """Assert filter_snmpd_xs_conf() replaces sensitive strings"""
    snmpd_xs_conf_init_str = "com2sec notConfigUser default INITIAL_STR"
    mocker.patch(
        "{}.open".format(builtin_module_name),
        new=mocker.mock_open(read_data=snmpd_xs_conf_init_str),
        create=True,
    )

    snmpd_xs_conf_out_str = "com2sec notConfigUser default REMOVED"
    assert bugtool.filter_snmpd_xs_conf("_") == snmpd_xs_conf_out_str


def test_filter_snmpd_conf(bugtool, mocker):
    """Assert filter_snmpd_conf() replaces sensitive strings"""
    snmpd_conf_init_str = (
        "usmUser 1 3 0x80001f8880f369b576d8b2a46500000000 0x7872746d69612d30372d3035 "
        + "0x7872746d69612d30372d3035 NULL .1.3.6.1.6.3.10.1.1.3 "
        + "INITIAL_STR "
        + ".1.3.6.1.6.3.10.1.2.2 "
        + "INITIAL_STR "
        + "0x"
    )
    mocker.patch(
        "{}.open".format(builtin_module_name),
        new=mocker.mock_open(read_data=snmpd_conf_init_str),
        create=True,
    )

    snmpd_conf_out_str = (
        "usmUser 1 3 0x80001f8880f369b576d8b2a46500000000 0x7872746d69612d30372d3035 "
        + "0x7872746d69612d30372d3035 NULL .1.3.6.1.6.3.10.1.1.3 "
        + "REMOVED "
        + ".1.3.6.1.6.3.10.1.2.2 "
        + "REMOVED "
        + "0x"
    )
    assert bugtool.filter_snmpd_conf("_") == snmpd_conf_out_str
