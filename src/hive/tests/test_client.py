from ipaddress import IPv4Address, IPv6Address

import pytest

from hive.client import ClientEnode


@pytest.mark.parametrize(
    "enode",
    [
        ClientEnode(id="ab" * 64, ip=IPv4Address("192.0.2.1"), port=30303),
        ClientEnode(id="cd" * 64, ip=IPv6Address("2001:db8::1"), port=30303),
    ],
)
def test_client_enode_round_trip(enode: ClientEnode):
    assert ClientEnode.from_string(str(enode)) == enode


def test_client_enode_formats_ipv6_with_brackets():
    enode = ClientEnode(id="ab" * 64, ip=IPv6Address("2001:db8::1"), port=30303)

    assert str(enode) == f"enode://{'ab' * 64}@[2001:db8::1]:30303"
