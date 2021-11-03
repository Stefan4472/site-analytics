import dataclasses as dc
from . import session


# TODO: MAKE INTO NAMEDTUPLE
@dc.dataclass
class User:
    user_id: int
    ip_address: str
    hostname: str
    domain: str
    city: str
    region: str
    country: str
    classification: str
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
def classify_user(
        user: User,
        session: session.Session,
) -> str:
    if session.calc_requests_per_second() > 1.5:
        return 'BOT'
    elif any(keyword in user.hostname.lower() for keyword in BOT_KEYWORDS):
        return 'BOT'
    else:
        return 'USER'