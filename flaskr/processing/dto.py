import datetime
import dataclasses as dc


@dc.dataclass
class QueryResult:
    quantity: int
    date: datetime.datetime = None


@dc.dataclass
class QuantityResult:
    quantity: int
    date: datetime.datetime


@dc.dataclass
class CountryResult:
    country: str
    value: int


@dc.dataclass
class CityResult:
    city: str
    value: int


@dc.dataclass
class UrlResult:
    url: str
    value: int


@dc.dataclass
class HostnameResult:
    hostname: str
    value: int
