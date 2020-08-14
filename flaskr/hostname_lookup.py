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
    if hostname == 'UNKNOWN' or not hostname:
        return 'UNKNOWN'

    segments = hostname.split('.')
    return segments[-2] + '.' + segments[-1]