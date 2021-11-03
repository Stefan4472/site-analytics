import dataclasses as dc
from . import session


@dc.dataclass
class User:
    user_id: int
    ip_address: str
    hostname: str
    domain: str
    city: str
    region: str
    country: str
    is_bot: bool
    was_processed: bool


# TODO: NARROW THE LIST? SEE HOW WELL THE "REQUESTS-PER-SECOND" METRIC WORKS
BOT_KEYWORDS = [
    'bot', 
    'scan', 
    'surf', 
    'spider', 
    'crawl', 
    'pool', 
    'ip189', 
    'amazonaws', 
    'googleusercontent',
    'bezeqint', 
    'greenhousedata', 
    'comcastbusiness',
    'dataprovider',
]


# TODO: CLASSIFY BASED ON USER_AGENT
def is_bot(
        user: User,
) -> bool:
    if session.calc_requests_per_second() > 1.5:
        return True
    elif any(keyword in user.hostname.lower() for keyword in BOT_KEYWORDS):
        return True
    else:
        return False