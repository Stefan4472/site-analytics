from flaskr import db
from flaskr import user_agent


class View(db.Model):
    __tablename__ = 'view'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    user_agent = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    operating_system = db.Column(db.String)
    browser = db.Column(db.String)

    # Associated User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='views')

    def process(self):
        self.operating_system = user_agent.determine_os(self.user_agent)
        self.browser = user_agent.determine_browser(self.user_agent)

    def is_bot(self) -> bool:
        return user_agent.is_bot(self.user_agent)

    def __repr__(self):
        return 'View(user_id="{}", url="{}", timestamp={}, agent="{}")'.format(
            self.user_id,
            self.url,
            self.timestamp,
            self.user_agent,
        )
