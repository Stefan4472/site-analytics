import datetime
import dataclasses as dc
import typing
from analyticsdb.database import Classification


class ParseException(Exception):
    def __init__(
            self,
            message: str,
    ):
        """
        Super simple custom exception class raised on error
        in parsing request args.
        """
        super().__init__(message)


@dc.dataclass
class RequestArgs:
    """
    Wrapper for the possible arguments that can be passed
    in a request.
    """
    start_date: datetime.datetime = None
    end_date: datetime.datetime = None
    classification: Classification = None


def parse_date(date_str: str) -> datetime:
    """Parses a string date in format YYYY-MM-DD."""
    return datetime.datetime.strptime(date_str, '%Y-%m-%d')


def parse_args(
        args: typing.Dict[str, typing.Any],
        req_start_date: bool = False,
        req_end_date: bool = False,
        req_classification: bool = False,
) -> RequestArgs:
    """
    Parses the provided JSON `args` object and returns a
    `RequestArgs` instance.

    The `req-` arguments specify which arguments are required.
    If `args` is missing a required argument, this function will
    throw a `ParseException`.
    A non-required arg will still be parsed and added to the
    returned `RequestArgs` if it exists and is in the correct format.
    """
    # Check for missing requirements
    if req_start_date and 'start_date' not in args:
        raise ParseException('Missing start_date')
    if req_end_date and 'end_date' not in args:
        raise ParseException('Missing end_date')
    if req_classification and 'classification' not in args:
        raise ParseException('Missing classification')

    # Create fields with default None
    parsed_start_date: typing.Optional[datetime.datetime] = None
    parsed_end_date: typing.Optional[datetime.datetime] = None
    parsed_classification: typing.Optional[Classification] = None

    # Parse
    if 'start_date' in args:
        try:
            parsed_start_date = parse_date(args['start_date'])
        except ValueError:
            raise ParseException('start_date in improper format')
    if 'end_date' in args:
        try:
            parsed_end_date = parse_date(args['end_date'])
        except ValueError:
            raise ParseException('end_date in improper format')
    if 'classification' in args:
        if args['classification'].upper() == 'USER':
            parsed_classification = Classification.USER
        elif args['classification'].upper() == 'BOT':
            parsed_classification = Classification.BOT
        else:
            raise ParseException('classification is invalid')

    if 'start_date' in args and 'end_date' in args and parsed_end_date <= parsed_start_date:
        raise ParseException('end_date must be later than start_date')

    return RequestArgs(
        start_date=parsed_start_date,
        end_date=parsed_end_date,
        classification=parsed_classification,
    )
