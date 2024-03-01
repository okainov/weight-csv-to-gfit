# -------------------------------------------------------------------------------
# Purpose: Load weights.csv and import to a Google Fit account
# Some codes refer to:
# 1. https://github.com/tantalor/fitsync
# 2. http://www.ewhitling.com/2015/04/28/scrapping-data-from-google-fitness/
# 3. https://github.com/googleapis/google-api-python-client/blob/main/docs/oauth.md
import google_auth_oauthlib.flow
import yaml
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from read_weight_csv import read_weights_csv_with_gfit_format

# Setup for Google API:
# Steps:
# 1. Go to https://console.developers.google.com/apis/credentials
# 2. Create credentials => OAuth Client ID, use Web Application
# 3. Set Redirect URI to http://localhost:8080/
# 4. Download client_secret.json and put it next to the script
CLIENT_SECRET_FILE_PATH = 'client_secret.json'
secrets = yaml.safe_load(open('secrets.yml'))

# Set some random project ID. Later on can be replaced to some actual numbered string
# TODO: figure out whether it's actually needed, can it be "whatever"?
PROJECT_ID = secrets['project_id']

# See scope here: https://developers.google.com/fit/rest/v1/authorization
SCOPE_WRITE = 'https://www.googleapis.com/auth/fitness.body.write'
SCOPE_READ = 'https://www.googleapis.com/auth/fitness.body.read'

# API Key
# Steps:
# 1. Go https://console.developers.google.com/apis/credentials
# 2. Create credentials => API Key => Server Key
# TODO: Not sure it's actually needed, can we remove it?
API_KEY = secrets['fitness_api_key']


def get_data_source_id(data_source):
    return ':'.join((
        data_source['type'],
        data_source['dataType']['name'],
        PROJECT_ID,
        data_source['device']['manufacturer'],
        data_source['device']['model'],
        data_source['device']['uid']
    ))


def import_weight_to_gfit():
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE_PATH,
        scopes=[SCOPE_WRITE, SCOPE_READ])

    flow.run_local_server()
    cred = flow.credentials

    fitness_service = build('fitness', 'v1', credentials=cred, developerKey=API_KEY)

    # init the fitness objects
    fitusr = fitness_service.users()
    fitdatasrc = fitusr.dataSources()

    data_source = dict(
        type='raw',
        application=dict(name='weight_import'),
        dataType=dict(
            name='com.google.weight',
            field=[dict(format='floatPoint', name='weight')]
        ),
        device=dict(
            type='scale',
            manufacturer='withings',
            model='smart-body-analyzer',
            uid='ws-50',
            version='1.0',
        )
    )

    data_source_id = get_data_source_id(data_source)

    print('datasourceID')
    print(data_source_id)
    # Ensure datasource exists for the device.
    try:
        fitness_service.users().dataSources().get(
            userId='me',
            dataSourceId=data_source_id).execute()
    except HttpError as error:
        if 'DataSourceId not found' not in str(error):
            raise error
        # Doesn't exist, so create it.
        fitness_service.users().dataSources().create(
            userId='me',
            body=data_source).execute()

    weights = read_weights_csv_with_gfit_format()
    print('got weights...')
    min_log_ns = min([x["startTimeNanos"] for x in weights])
    max_log_ns = max([x["startTimeNanos"] for x in weights])
    dataset_id = f'{min_log_ns}-{max_log_ns}'

    # Actually push data to Google Fit
    fitness_service.users().dataSources().datasets().patch(
        userId='me',
        dataSourceId=data_source_id,
        datasetId=dataset_id,
        body=dict(
            dataSourceId=data_source_id,
            maxEndTimeNs=max_log_ns,
            minStartTimeNs=min_log_ns,
            point=weights,
        )).execute()

    # read data to verify
    print(fitness_service.users().dataSources().datasets().get(
        userId='me',
        dataSourceId=data_source_id,
        datasetId=dataset_id).execute())


if __name__ == "__main__":
    import_weight_to_gfit()
