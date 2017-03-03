#!/usr/bin/env python3
import os
import re
import uuid
from datetime import timedelta

import pyexcel
import pytz
import vobject
from dateutil.parser import parse
from dateutil.rrule import rrule, rruleset, WEEKLY
from flask import Flask, render_template, request, send_from_directory
from xlrd.biffh import XLRDError

from utils import dates_between_dates, filter_row, get_pretty_location, parse_dates


app = Flask(__name__)

DURATION_REGEX = re.compile(r'([\d.]+) hrs?')
DEFAULT_TIMEZONE = pytz.timezone('Australia/Melbourne')


def build_event(record):
    date_ranges = parse_dates(record['Dates'], record['Time'], record['Duration'])
    excluded_dates = []

    duration = timedelta(hours=float(DURATION_REGEX.match(record['Duration']).group(1)))
    event_start = date_ranges[0][0]
    event_end = event_start + duration
    subject = record['Subject Code'].split('_')[0]

    for i, date_range in enumerate(date_ranges):
        if (i + 1) < len(date_ranges):
            previous_date = date_range[1]
            next_date = date_ranges[i + 1][0]
            excluded_dates.extend(dates_between_dates(previous_date, next_date))

    return {
        'event_start': DEFAULT_TIMEZONE.localize(event_start),
        'event_end': DEFAULT_TIMEZONE.localize(event_end),
        'day_index': parse(record['Day']).weekday(),
        'until': DEFAULT_TIMEZONE.localize(date_ranges[-1][-1]),
        'excludes': map(DEFAULT_TIMEZONE.localize, excluded_dates),
        'location': get_pretty_location(record['Location']),
        'title': '{subject} {group}'.format(subject=subject, group=record['Group']),
        'description': '{description}\n\nStaff: {staff}'.format(
            description=record['Description'],
            staff=record['Staff']
        )
    }


@app.route('/upload', methods=['POST', ])
def upload():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return 'No file received.'
        input_file = request.files['file']

        # If the user doesn't select a file, the browser also
        # submit an empty part without a filename.
        if input_file.filename == '':
            return 'No file selected.'

        if not input_file.filename.lower().endswith('.xls'):
            return 'File must be XLS format.'

        try:
            sheet = pyexcel.get_sheet(file_content=input_file.read(), file_type='xls', name_columns_by_row=1)
            del sheet.row[filter_row]  # Delete empty rows
            records = sheet.to_records()
        except XLRDError as e:
            return 'File is corrupt.'

        cal = vobject.iCalendar()
        for record in records:
            event = build_event(record)
            vevent = cal.add('vevent')
            vevent.add('uid').value = str(uuid.uuid4()).upper()
            vevent.add('summary').value = event['title']
            vevent.add('description').value = event['description']
            vevent.add('location').value = event['location']
            vevent.add('dtstart').value = event['event_start']
            vevent.add('dtend').value = event['event_end']

            ruleset = rruleset()
            ruleset.rrule(
                rrule(WEEKLY, byweekday=event['day_index'], until=event['until'])
            )

            for exdate in event['excludes']:
                ruleset.exdate(exdate)

            vevent.rruleset = ruleset

        return cal.serialize()

    return ''


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/bower_components/<path:path>')
def send_bower(path):
    return send_from_directory(os.path.join(app.root_path, 'bower_components'), path)


@app.route('/static/<path:path>')
def send_dist(path):
    return send_from_directory(os.path.join(app.root_path, 'static'), path)


if __name__ == '__main__':
    app.run()
