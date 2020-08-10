import datetime
import typing

MAX_INACTIVE_TIME_SEC = 10


class Session:
    """A session is made by a particular IP address. It is one request,
    plus any further requests made by that IP address such that no
    more than 30 minutes pass between two requests."""
    def __init__(
            self,
            session_id: int,
            user_id: int,
            first_request_time: datetime.datetime,
            last_request_time: datetime.datetime = None,
            num_requests: int = 1,
    ):
        self.session_id = session_id
        self.user_id = user_id  # TODO: PROVIDE 'USER' INSTANCE DIRECTLY?
        self.first_request_time = first_request_time
        self.last_request_time = \
            last_request_time if last_request_time else first_request_time
        self.num_requests = num_requests

    def record_request(
            self,
            view_time: datetime.datetime,
    ):
        self.num_requests += 1
        self.last_request_time = view_time
        self.is_active()

    def is_active(
            self,
            curr_time: datetime = None,
    ) -> bool:
        curr_time = curr_time if curr_time else datetime.datetime.now()
        sec_inactive = (curr_time - self.last_request_time).total_seconds()
        return sec_inactive < MAX_INACTIVE_TIME_SEC

    def __str__(self):
        return 'Session(id={}, user_id={}, start_time={}, requests={})'.format(
            self.session_id, 
            self.user_id, 
            self.first_request_time, 
            self.num_requests,
        )