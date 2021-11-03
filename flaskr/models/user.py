from flaskr import db
from flaskr.hostname import hostname_from_ip, domain_from_hostname, is_bot
from flaskr.location import location_from_ip


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
        hostname = hostname_from_ip(self.ip_address)
        self.hostname = hostname
        self.domain = domain_from_hostname(hostname)

        location = location_from_ip(self.ip_address)
        self.city = location.city
        self.region = location.region_name
        self.country = location.country_name

        self.is_bot = self._check_is_bot()
        self.was_processed = True

    def _check_is_bot(self) -> bool:
        """Decides whether this User is a bot. Call after determining hostname."""
        if any(v.is_bot() for v in self.views):
            return True
        elif is_bot(self.hostname):
            return True
        elif self._calc_requests_per_second() >= 1:
            return True
        else:
            return False

    def _calc_requests_per_second(self) -> float:
        if self.views:
            time_diff = self.views[-1].timestamp - self.views[0].timestamp
            return time_diff.total_seconds() / len(self.views)
        else:
            return 0

    def __repr__(self):
        return 'User(id="{}", ip_address="{}", hostname="{}", country="{}")'.format(
            self.id,
            self.ip_address,
            self.hostname,
            self.country,
        )
