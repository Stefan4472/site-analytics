import datetime
import dataclasses as dc


@dc.dataclass
class UserBotDateResult:
    date: datetime.datetime
    user: int = None
    bot: int = None
