import datetime

dt_now = datetime.datetime.now()


def year(request) -> dict:
    """Returns a variable with the current year."""
    return {
        'year': datetime.datetime.timetuple(dt_now)[0]
    }
