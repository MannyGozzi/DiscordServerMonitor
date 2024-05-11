import socket
from itertools import chain
from collections import defaultdict
from typing import Dict

def get_open_ports(server_address: str) -> Dict[int, str]:
    open_ports = {}
    port_range = range(1, 65536)

    for port in port_range:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((server_address, port))

        if result == 0:
            open_ports[port] = 'open'
        else:
            open_ports[port] = 'closed'
        sock.close()
    return open_ports

def find_port_changes(prev_ports: Dict[int, str], curr_ports: Dict[int, str]) -> Dict[int, str]:
    changes = defaultdict(str)

    for port, status in chain(prev_ports.items(), curr_ports.items()):
        if prev_ports.get(port) != curr_ports.get(port):
            changes[port] = f'{prev_ports.get(port, "closed")} -> {curr_ports.get(port, "closed")}'

    return dict(changes)
