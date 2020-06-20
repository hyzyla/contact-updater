# Instructions

# Common setup
0. Create google cloud application. https://cloud.google.com/appengine/docs/standard/python/quickstart
1. Create client_secret.json from developer console and put into root folder. https://developers.google.com/adwords/api/docs/guides/authentication#webapp
3. Create app_secret.json from developer console and put into root folder.  https://cloud.google.com/docs/authentication/getting-started#creating_a_service_account
2. Install python3, Google Cloud SDK
3. Create virtual environment:<br> `python3 -m venv .env`
4. Activate virtual environment:<br> `source .env/bin/activate`
6. Install libraries:<br> `pip install -r requirements.txt`


# Run locally
```shell script
REDIRECT_URL=http://127.0.0.1:5000/auth GOOGLE_APPLICATION_CREDENTIALS=./app_secret.json  FLASK_DEBUG=1 flask run
```


# Deploy to google cloud
```shell script
gcloud app deploy app.prod.yaml cron.yaml index.yaml
```