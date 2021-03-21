import datetime
import dataclasses as dc


@dc.dataclass
class UserBotDateResult:
    date: datetime.datetime
    user: int = None
    bot: int = None


@dc.dataclass
class CountryResult:
    country: str
    value: int


@dc.dataclass
class CityResult:
    city: str
    value: int


@dc.dataclass
class PostResult:
    url: str
    value: int


@dc.dataclass
class HostnameResult:
    url: str
    value: int