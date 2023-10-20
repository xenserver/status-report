# This uses the deprecated imp module because it has to run with Python2.7 for now:
import imp  # pylint: disable=deprecated-module
import os
import xml.dom.minidom


testdir = os.path.dirname(__file__)
bugtool = imp.load_source("bugtool", testdir + "/../../xen-bugtool")
original = r"""<?xml version="1.0" ?>
<root>
    <table name="secret">
        <row id="1">
            <value>mysecretpassword</value>
        </row>
        <row id="2">
            <value>anotherpassword</value>
        </row>
    </table>
    <table name="Cluster">
        <row id="1">
            <cluster_token>cluster_password</cluster_token>
        </row>
    </table>
    <table name="VM">
        <row id="1"
        NVRAM="(('EFI-variables'%.'myprivatedata'))"
        snapshot_metadata="('NVRAM'%.'(('_%.'_')%.(\'EFI-variables\'%.\'mydata\')()">
        </row>
    </table>
</root>
"""

# Same as original, but with passwords and private data replaced by: "REMOVED"
expected = r"""<?xml version="1.0" ?>
<root>
    <table name="secret">
        <row id="1" value="REMOVED">
            <value/>
        </row>
        <row id="2" value="REMOVED">
            <value/>
        </row>
    </table>
    <table name="Cluster">
        <row cluster_token="REMOVED" id="1">
            <cluster_token/>
        </row>
    </table>
    <table name="VM">
        <row NVRAM="(('EFI-variables'%.'REMOVED'))" id="1" snapshot_metadata="('NVRAM'%.'(('_%.'_')%.(\'EFI-variables\'%.\'REMOVED\')()"/>
    </table>
</root>
"""


def test_xapi_database_filter():
    """Assert that bugtool.DBFilter().output() filters the xAPI database as expected"""
    filtered = bugtool.DBFilter(original).output()
    assert xml.dom.minidom.parseString(filtered).toprettyxml(indent="    ") == expected
