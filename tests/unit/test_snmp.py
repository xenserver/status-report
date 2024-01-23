"""Unit tests for the bugtool SNMP filter functions: filter_snmp.*_conf()"""


def test_filter_snmp_xs_conf(bugtool, builtins, mocker):
    """Assert that filter_snmp_xs_conf() replaces sensitive strings"""

    snmp_xs_conf_input = """
        "community": "SECRET",
        "authentication_key": "SECRET",
        "privacy_key": "SECRET",
    """
    snmp_xs_conf_output = """
        "community": "REMOVED",
        "authentication_key": "REMOVED",
        "privacy_key": "REMOVED",
    """
    mocker.patch(builtins + ".open", mocker.mock_open(read_data=snmp_xs_conf_input))
    assert bugtool.filter_snmp_xs_conf("_") == snmp_xs_conf_output


def test_filter_snmpd_xs_conf(bugtool, builtins, mocker):
    """Assert that filter_snmpd_xs_conf() replaces sensitive strings"""

    snmpd_xs_conf_input = "com2sec notConfigUser default SECRET"
    snmpd_xs_conf_output = "com2sec notConfigUser default REMOVED"
    mocker.patch(builtins + ".open", mocker.mock_open(read_data=snmpd_xs_conf_input))
    assert bugtool.filter_snmpd_xs_conf("_") == snmpd_xs_conf_output


def test_filter_snmpd_conf(bugtool, builtins, mocker):
    """Assert that filter_snmpd_conf() replaces sensitive strings"""

    snmpd_conf_input = (
        "usmUser 1 3 0x80001f8880f369b576d8b2a46500000000 0x7872746d69612d30372d3035 "
        + "0x7872746d69612d30372d3035 NULL .1.3.6.1.6.3.10.1.1.3 "
        + "SECRET "
        + ".1.3.6.1.6.3.10.1.2.2 "
        + "SECRET "
        + "0x"
    )
    snmpd_conf_output = (
        "usmUser 1 3 0x80001f8880f369b576d8b2a46500000000 0x7872746d69612d30372d3035 "
        + "0x7872746d69612d30372d3035 NULL .1.3.6.1.6.3.10.1.1.3 "
        + "REMOVED "
        + ".1.3.6.1.6.3.10.1.2.2 "
        + "REMOVED "
        + "0x"
    )
    mocker.patch(builtins + ".open", mocker.mock_open(read_data=snmpd_conf_input))
    assert bugtool.filter_snmpd_conf("_") == snmpd_conf_output
