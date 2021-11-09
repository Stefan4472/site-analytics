import socket
import typing


# TODO: NARROW THE LIST? SEE HOW WELL THE "REQUESTS-PER-SECOND" METRIC WORKS
BOT_KEYWORDS = [
    'bot',
    'scan',
    'surf',
    'spider',
    'crawl',
    'pool',
    'ip189',
    'amazon',
    'google',
    'bezeqint',
    'greenhousedata',
    'comcastbusiness',
    'dataprovider',
]


def hostname_from_ip(ip_address: str) -> str:
    try:
        hostname = socket.gethostbyaddr(ip_address)[0]
    except (socket.herror, socket.gaierror):
        raise ValueError('Socket error')

    # For the rare case that 'hostname' = Nan
    if isinstance(hostname, float):
        raise ValueError('hostname = Nan')

    return hostname


def domain_from_hostname(hostname) -> typing.Optional[str]:
    if not hostname or '.' not in hostname:
        return hostname
    segments = hostname.split('.')
    return segments[-2] + '.' + segments[-1]


def is_bot(hostname: str) -> bool:
    # If the hostname couldn't be resolved, we can't assume it's a bot
    if not hostname:
        return False
    return any(k in hostname.lower() for k in BOT_KEYWORDS)
