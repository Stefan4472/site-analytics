from flask import current_app
from flaskr import db
from flaskr.processing.hostname import lookup_hostname, domain_from_hostname, is_bot
from flaskr.processing.location import lookup_location


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    # uuid = db.Column(db.String, server_default=lambda: str(uuid.uuid4()), unique=True, primary_key=True)
    ip_address = db.Column(db.String, nullable=False, unique=True, index=True)
    hostname = db.Column(db.String)
    domain = db.Column(db.String)
    city = db.Column(db.String)
    region = db.Column(db.String)
    country = db.Column(db.String)
    is_bot = db.Column(db.Boolean)
    was_processed = db.Column(db.Boolean, server_default='0')
    # Associated Views.
    # Named "my_views" to distinguish from the "views" DB table
    my_views = db.relationship('View', back_populates='my_user')

    def process(self):
        """
        Process and update the User's data.

        Throws ValueError if unable to process.
        """
        try:
            hostname = lookup_hostname(self.ip_address)
            print('Got hostname {}'.format(hostname))
            self.hostname = hostname
            self.domain = domain_from_hostname(hostname)
        except ValueError:
            # Hostname exceptions aren't critical.
            # Some IP addresses don't have a valid DNS record.
            pass

        try:
            location = lookup_location(self.ip_address)
            print('Got location {}'.format(location))
            self.city = location.city
            self.region = location.region_name
            self.country = location.country_name
        except ValueError as e:
            raise e

        self.is_bot = self._check_is_bot()
        print('is_bot = {}'.format(self.is_bot))
        self.was_processed = True

    def _check_is_bot(self) -> bool:
        """Decides whether this User is a bot. Call after determining hostname."""
        if any(v.is_bot() for v in self.my_views):
            print('A view is a bot')
            return True
        elif is_bot(self.hostname):
            print('hostname is a bot')
            return True
        elif self._calc_requests_per_second() >= 1:
            print('RPS over 1')
            return True
        else:
            return False

    def _calc_requests_per_second(self) -> float:
        if self.my_views:
            time_diff = self.my_views[-1].timestamp - self.my_views[0].timestamp
            return time_diff.total_seconds() / len(self.my_views)
        else:
            return 0

    def __repr__(self):
        return 'User(id="{}", ip_address="{}", hostname="{}", country="{}")'.format(
            self.id,
            self.ip_address,
            self.hostname,
            self.country,
        )
