import dataclasses as dc
from . import session
from . import location_lookup
from . import hostname_lookup


@dc.dataclass
class User:
    user_id: int
    ip_address: str
    location: str = 'UNKNOWN'
    city: str = 'UNKNOWN'
    hostname: str = 'UNKNOWN'

    def lookup_location(self):
        """Use the set ip_address to set location."""
        # TODO
        self.location = 'UNKOWN'

    def lookup_hostname(self):
        return

    def on_session_finished(
            self, 
            user_session: session.Session,
    ):
        print(location_lookup.location_from_ip(self.ip_address))
        print(hostname_lookup.hostname_from_ip(self.ip_address))
        print(classify_user(self, user_session))


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

def classify_user(
        user: User,
        session: session.Session,
) -> str:
    if user.ip_address == '24.63.226.42' or user.city == 'Concord':
        return 'ME'
    elif session.calc_requests_per_second() > 1.5:
        return 'BOT'
    elif any(keyword in user.hostname for keyword in BOT_KEYWORDS):
        return 'BOT'
    else:
        return 'USER'