from sqlite3 import Cursor
import datetime
from . import dto


def format_timeboxed_result(result: Cursor) -> [dto.UserBotDateResult]:
    """
    Helper function for handling the results of timeboxed queries.

    Currently only supports timeboxing by week (%Y-%W in SQLite).

    This function will be generalized as needed/as the timeboxing
    query functionality improves to support other types of boxes.
    Currently it has a very specific use case--see its usages in
    `database.py`.
    """
    # NOTE: I am assuming that the Python %W is equivalent
    # to the SQlite %W (i.e., weeks start on Monday). This is
    # not specified in official SQLite documentation, but is
    # supported here: https://www.techonthenet.com/sqlite/functions/strftime.php

    # Build objects by going in sequence.
    # They will have already been sorted by date.
    res = []
    prev_date: datetime.datetime = None
    for row in result.fetchall():
        # Parse date out of the %Y-%W sqlite format.
        # This requires setting the weekday to "1" (Monday).
        # See https://stackoverflow.com/a/17087427
        curr_date = datetime.datetime.strptime(row[0] + '-1', '%Y-%W-%w')
        if curr_date != prev_date:
            res.append(dto.UserBotDateResult(curr_date))
            prev_date = curr_date
        if row[1] == 'USER':
            res[-1].user = row[2]
        elif row[1] == 'BOT':
            res[-1].bot = row[2]
    return res