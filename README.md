# allocate-me

Simple web app to convert an exported timetable from Monash University's Allocate Plus to iCal.

## Getting Started

Inside a virtual env:

```bash
npm install
pip install -r requirements.txt

npm run dev
FLASK_DEBUG=1 FLASK_APP=server/app.py flask run
```

In your browser, go to `http://localhost:5000`.
