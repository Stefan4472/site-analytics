import user_agents
from flaskr import db
from flaskr.processing import user_agent


class View(db.Model):
    __tablename__ = 'views'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    user_agent = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    operating_system = db.Column(db.String)
    browser = db.Column(db.String)
    # Associated User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    my_user = db.relationship('User', back_populates='my_views')

    def process(self):
        agent = user_agents.parse(self.user_agent)
        self.operating_system = agent.os.family + ' ' + agent.os.version_string  #user_agent.determine_os(self.user_agent)
        self.browser = agent.browser.family + ' ' + agent.browser.version_string  #user_agent.determine_browser(self.user_agent)

    def is_bot(self) -> bool:
        return user_agent.is_bot(self.user_agent)

    def __repr__(self):
        return 'View(user_id="{}", url="{}", timestamp={}, agent="{}")'.format(
            self.user_id,
            self.url,
            self.timestamp,
            self.user_agent,
        )
