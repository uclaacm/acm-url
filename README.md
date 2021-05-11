# ACM URL

Creates vanity URLS for ACM at UCLA with the root URL "https://links.uclaacm.com/"

It is a server-side site, using Flask + SQLite3.

## Run Locally
### Setup
Activate your virtual environment if you'd like to use it.

Install all the libraries:
```shell
$ pip install -r requirements.txt
```

Add the environment variables in `.env` (make this yourself if it's not in your directory):
- FLASK_APP=acm_url
- OFFICER_PWD
- SECRET_KEY
- FLASK_ENV=development

Also add `DATABASE_URL` if you want to connect to the database that is live. If you just want to test and don't want to affect the live database, don't add it.

To set up a local database, run the following:
```shell
$ flask db init
$ flask db migrate
$ flask db upgrade
```

### Run
```shell
$ flask run
```

Head on over to `http://localhost:5000/` to see the app!