# allocate-me

Simple web app to convert an exported timetable from Monash University's Allocate Plus to iCal.

## Getting Started

Inside a virtual env:

```bash
pip install -r requirements.txt
bower install

export FLASK_DEBUG=1 FLASK_APP=app.py
flask run
```

In your browser, go to `http://localhost:5000`.
