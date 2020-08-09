import datetime

MAX_INACTIVE_TIME_MIN = 30


class Session:
    """A session is made by a particular IP address. It is one request,
    plus any further requests made by that IP address such that no
    more than 30 minutes pass between two requests."""
    def __init__(
            self,
            ip_addr: str,
            start_time: datetime = None,
            session_id: int = None,
    ):
        self.ip_addr = ip_addr
        self.start_time = start_time if start_time else datetime.datetime.now()
        self.session_id = session_id if session_id else 0
        self.most_recent_request = self.start_time

    def is_active(
            self,
            curr_time: datetime = None,
    ) -> bool:
        curr_time = curr_time if curr_time else datetime.datetime.now()
        return (curr_time - self.most_recent_request).total_seconds() < MAX_INACTIVE_TIME_MIN * 60

    def __str__(self):
        return 'Session({}, start_time={}, session_id={})'.format(
            self.ip_addr, self.start_time, self.session_id)