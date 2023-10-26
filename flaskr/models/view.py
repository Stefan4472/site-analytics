# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from datetime import datetime

import user_agents

from flaskr import db


class View(db.Model):
    __tablename__ = "views"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    user_agent = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    operating_system = db.Column(db.String)
    browser = db.Column(db.String)
    device = db.Column(db.String)
    device_type = db.Column(db.String)
    # Associated User
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    my_user = db.relationship("User", back_populates="my_views")

    def __init__(
        self,
        url: str,
        user_agent: str,
        timestamp: datetime,
    ):
        self.url = url
        self.user_agent = user_agent
        self.timestamp = timestamp

        agent = user_agents.parse(self.user_agent)
        self.operating_system = agent.os.family + " " + agent.os.version_string
        self.browser = agent.browser.family + " " + agent.browser.version_string
        self.device = (
            agent.device.family + " " + agent.device.brand if agent.device.brand else ""
        )
        self.device_type = (
            "Mobile"
            if agent.is_mobile
            else "Tablet"
            if agent.is_tablet
            else "PC"
            if agent.is_pc
            else ""
        )

    def is_bot(self) -> bool:
        agent = user_agents.parse(self.user_agent)
        if agent.is_bot:
            return True
        elif "bot" in self.user_agent.lower():
            return True
        elif "scan" in self.user_agent.lower():
            return True
        elif "request" in self.user_agent.lower():
            return True
        else:
            return False

    def __repr__(self):
        return 'View(user_id="{}", url="{}", timestamp={}, agent="{}")'.format(
            self.user_id,
            self.url,
            self.timestamp,
            self.user_agent,
        )
