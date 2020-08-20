import socket
import typing


def hostname_from_ip(
        ip_address: str,
) -> str:
    try:
        hostname = socket.gethostbyaddr(ip_address)[0]
    except (socket.herror, socket.gaierror):
        return 'UNKNOWN'

    # For the rare case that 'hostname' = Nan
    if isinstance(hostname, float):
        return 'UNKNOWN'

    return hostname


def domain_from_hostname(hostname):
    if not hostname or hostname == 'UNKNOWN':
        return 'UNKNOWN'
    if not '.' in hostname:
        return hostname
    segments = hostname.split('.')
    return segments[-2] + '.' + segments[-1]