import uuid
from flaskr import db
from flaskr import hostname_lookup
from flaskr import location_lookup


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


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    # TODO: USE UUID ONCE SWITCHED OVER TO POSTGRES
    # uuid = db.Column(db.String, server_default=lambda: str(uuid.uuid4()), unique=True, primary_key=True)
    ip_address = db.Column(db.String, nullable=False, unique=True, index=True)
    hostname = db.Column(db.String)
    domain = db.Column(db.String)
    city = db.Column(db.String)
    region = db.Column(db.String)
    country = db.Column(db.String)
    is_bot = db.Column(db.Boolean)
    was_processed = db.Column(db.Boolean, server_default='0')
    # Associated Views
    views = db.relationship('View', back_populates='user')

    def process(self):
        hostname = hostname_lookup.hostname_from_ip(self.ip_address)
        self.hostname = hostname
        self.domain = hostname_lookup.domain_from_hostname(hostname)

        location = location_lookup.location_from_ip(self.ip_address)
        self.city = location.city
        self.region = location.region_name
        self.country = location.country_name

        self.is_bot = self._check_is_bot()
        self.was_processed = True

    # TODO: CLASSIFY BASED ON USER_AGENT / Views
    def _check_is_bot(self) -> bool:
        """Decides whether this User is a bot. Call after determining hostname."""
        # if session.calc_requests_per_second() > 1.5:
        #     return True
        if any(keyword in self.hostname.lower() for keyword in BOT_KEYWORDS):
            return True
        else:
            return False

    def __repr__(self):
        return 'User(id="{}", ip_address="{}")'.format(
            self.id,
            self.ip_address,
        )
