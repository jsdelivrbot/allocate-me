# Allocate Me

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

## Deploying to Heroku

To get your own Allocate Me instance running on Heroku, click the button below:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/skozer/allocate-me)

## Updating

After deploying your own Allocate Me instance, you can update it by running the following commands:

```
heroku git:clone --app YOURAPPNAME && cd YOURAPPNAME
git remote add origin https://github.com/skozer/allocate-me
git pull origin master # may trigger a few merge conflicts, depending on how long since last update
git push heroku master
```

This will pull down the code that was deployed to Heroku so you have it locally, attach this repository as a new remote, attempt to pull down the latest version and merge it in, and then push that change back to your Heroku app instance.

## Problems?

If you have problems using Allocate Me, you should open an issue on [the GitHub issue tracker](https://github.com/skozer/allocate-me/issues).

## Disclaimer

Released under the [MIT license](./LICENSE.md).

This application and its source code are not affiliated with Monash University or Allocate Plus.
