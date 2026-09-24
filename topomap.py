#!/usr/bin/env python3
"""Build a network topology map from RouterOS neighbor discovery data.

Usage:
    python topomap.py inventory.json --json
"""
import argparse
import json
import re
import socket
import sys

import paramiko

NEIGHBOR_RE = re.compile(
    r'interface=(\S+).*?address=(\S+).*?identity="([^"]*)"'
)
DEFAULT_TIMEOUT = 10


def load_inventory(path: str) -> list:
    with open(path) as f:
        return json.load(f)["routers"]


def fetch_neighbors(router: dict, timeout: int = DEFAULT_TIMEOUT) -> list:
    """SSH to a router and return its neighbor list as [{interface, address, identity}]."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            router["host"],
            port=router.get("port", 22),
            username=router["username"],
            password=router["password"],
            timeout=timeout,
        )
        stdin, stdout, stderr = client.exec_command("/ip neighbor print terse without-paging",
                                                      timeout=timeout)
        output = stdout.read().decode(errors="replace")
    except (paramiko.ssh_exception.SSHException, socket.timeout, socket.error, OSError) as e:
        raise RuntimeError(f"Could not fetch neighbors from {router['host']}: {e}")
    finally:
        client.close()

    return parse_neighbor_output(output)


def parse_neighbor_output(output: str) -> list:
    neighbors = []
    for line in output.splitlines():
        match = NEIGHBOR_RE.search(line)
        if match:
            interface, address, identity = match.groups()
            if identity:
                neighbors.append({"interface": interface, "address": address, "identity": identity})
    return neighbors


def build_edges(routers: list) -> list:
    """Return a list of {from, to, interface, address} edges, one per (router, neighbor) pair."""
    edges = []
    for router in routers:
        name = router.get("name", router["host"])
        try:
            neighbors = fetch_neighbors(router)
        except RuntimeError as e:
            print(f"Warning: {e}", file=sys.stderr)
            continue
        for n in neighbors:
            edges.append({"from": name, "to": n["identity"],
                          "interface": n["interface"], "address": n["address"]})
    return edges


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory_file", help="Path to an inventory.json file")
    parser.add_argument("--json", action="store_true", help="Print edges as JSON")
    args = parser.parse_args()

    routers = load_inventory(args.inventory_file)
    edges = build_edges(routers)

    if args.json:
        print(json.dumps(edges, indent=2))
    else:
        for edge in edges:
            print(f"{edge['from']} --[{edge['interface']}]--> {edge['to']} ({edge['address']})")


if __name__ == "__main__":
    main()
