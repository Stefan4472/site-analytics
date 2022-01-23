import datetime as dt


def datetime_from_day(year: float, day_of_year: float) -> dt.datetime:
    """Construct a datetime instance given the day-of-the-year and the year."""
    as_string = f'{int(year)}-{int(day_of_year)}'
    # %Y: 4-digit year
    # %j: Day of the year
    return dt.datetime.strptime(as_string, '%Y-%j')


def datetime_from_week(year: float, week_of_year: float) -> dt.datetime:
    """
    Construct a datetime instance given the year and the week of the year.
    Sets the date to the Monday of that week.
    The only way I've found to do this is with strptime.
    """
    as_string = f'{int(year)}-{int(week_of_year)}-1'
    # %Y: 4-digit year
    # %W: Week number of the year
    # %w: Weekday starting with 0=Sunday (set to 1 for Monday, above)
    return dt.datetime.strptime(as_string, '%Y-%W-%w')


def datetime_from_month(year: float, month_of_year: float) -> dt.datetime:
    """
    Construct a datetime instance given the year and the month of the year.
    Sets the date to the 1st of that month.
    """
    as_string = f'{int(year)}-{int(month_of_year)}-1'
    # %Y: 4-digit year
    # %m: month of the year
    # %d: day of the month
    return dt.datetime.strptime(as_string, '%Y-%m-%d')


def datetime_from_year(year: float) -> dt.datetime:
    """
    Construct a datetime instance given the year.
    Set the date to January 1st of that year.
    """
    as_string = f'{int(year)}-1-1'
    # %Y: 4-digit year
    # %m: month of the year
    # %d: day of the month
    return dt.datetime.strptime(as_string, '%Y-%m-%d')