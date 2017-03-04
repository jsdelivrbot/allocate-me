import re
from datetime import datetime, timedelta


CLAYTON_LOCATION_REGEX = re.compile(r'(?P<campus>\w+)_(?P<street_number>\d+)(?P<street_code>\w+)/(?P<room>\w+)')
CAULFIELD_LOCATION_REGEX = re.compile(r'(?P<campus>\w+)_(?P<building>\w+)/(?P<room>[\w\^]+)')
CLAYTON_STREET_NAMES = {
    'All': 'Alliance Lane',
    'Anc': 'Ancora Imparo Way',
    'Chn': 'Chancellors Walk',
    'Col': 'College Walk',
    'Exh': 'Exhibition Walk',
    'FGR': 'Ferntree Gully Road',
    'Inn': 'Innovation Walk',
    'Rnf': 'Rainforest Walk',
    'Res': 'Research Way',
    'Sce': 'Scenic Boulevard',
}


def get_pretty_location(location):
    if location.startswith('CL'):
        loc = CLAYTON_LOCATION_REGEX.match(location).groupdict()
        street_name = CLAYTON_STREET_NAMES.get(loc.get('street_code', ''))

        return 'Room {room}, {street_number} {street_name}, Monash University Clayton Campus'.format(
            room=loc.get('room'),
            street_number=loc.get('street_number'),
            street_name=street_name,
        )
    if location.startswith('CA'):
        loc = CAULFIELD_LOCATION_REGEX.match(location).groupdict()
        room = loc.get('room').replace('^', ', ')
        return 'Room {room}, Building {building}, Monash University Caulfield Campus'.format(
            room=room,
            building=loc.get('building'),
        )

    return location


def parse_date(value):
    value += '/{year}'.format(year=datetime.now().year)
    return datetime.strptime(value, '%d/%m/%Y')


def parse_dates(dates, event_time, duration):
    date_ranges = []
    start_hour, start_minute = map(int, event_time.split(':'))

    raw_date_ranges = [date_range.strip() for date_range in dates.split(',')]
    for raw_date_range in raw_date_ranges:
        try:
            start_date, finish_date = raw_date_range.split('-')
        except ValueError:
            start_date = finish_date = raw_date_range.split('-')[0]

        date_ranges.append([
            parse_date(start_date).replace(hour=start_hour, minute=start_minute),
            parse_date(finish_date).replace(hour=start_hour, minute=start_minute),
        ])

    return date_ranges


def dates_between_dates(start_date, end_date, step=7, inclusive=False):
    dates = []
    delta = end_date - start_date

    # Adjust the offsets depending on whether or not
    # the result should be inclusive of the provided dates.
    start = 0 if inclusive else step
    offset = 1 if inclusive else 0

    for i in range(start, delta.days + offset, step):
        dates.append(start_date + timedelta(days=i))
    return dates


def filter_row(row_index, row):
    """
    Ignore empty rows when parsing xlsx files.
    """
    result = [element for element in row if element != '']
    return len(result) == 0
