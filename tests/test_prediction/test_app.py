import json
import pathlib
from datetime import datetime
import pytest
from jsonschema import validate, RefResolver
import requests

from labeler.app import app
from labeler.models import Prediction


@pytest.fixture
def client():
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


def validate_payload(payload, schema_name):
    """
    Validate payload with selected schema
    """
    schemas_dir = str(
        f'{pathlib.Path(__file__).parent.absolute()}/schemas'
    )
    schema = json.loads(pathlib.Path(f'{schemas_dir}/{schema_name}').read_text())
    validate(
        payload,
        schema,
        resolver=RefResolver(
            'file://' + str(pathlib.Path(f'{schemas_dir}/{schema_name}').absolute()),
            schema  # it's used to resolve file: inside schemas correctly
        )
    )


def test_create_prediction(client):
    """
    GIVEN request data for new prediction
    WHEN endpoint /create-prediction/ is called
    THEN it should return Prediction in json format matching schema
    """
    data = {
        'species': 'setosa',
        'params': 'Some extra awesome content',
        'creation': datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
        'confidence': 0.88
    }
    response = client.post(
        '/create-prediction/',
        data=json.dumps(
            data
        ),
        content_type='application/json',
    )

    validate_payload(response.json, 'Prediction.json')


def test_get_prediction(client):
    """
    GIVEN ID of prediction stored in the database
    WHEN endpoint /prediction/<id-of-prediction>/ is called
    THEN it should return Prediction in json format matching schema
    """
    prediction = Prediction(
        species='versicolor',
        params='3.3, 4.2, 1.1, 0.6',
        creation=datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
        confidence=0.88
    ).save()
    response = client.get(
        f'/prediction/{prediction.id}/',
        content_type='application/json',
    )

    validate_payload(response.json, 'Prediction.json')


def test_list_predictions(client):
    """
    GIVEN predictions stored in the database
    WHEN endpoint /prediction-list/ is called
    THEN it should return list of Prediction in json format matching schema
    """
    Prediction(
        species='setosa',
        params='5.1, 3.8, 1.5, 0.3',
        creation=datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
        confidence=0.86
    ).save()
    response = client.get(
        '/prediction-list/',
        content_type='application/json',
    )

    validate_payload(response.json, 'PredictionList.json')


@pytest.mark.parametrize(
    'data',
    [
        {
            'species': None,
            'params': '3.6, 2.6, 0.9, 1.1',
            'creation': datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
            'confidence': 0.65
        },
        {
            'species': None,
            'params': None,
            'creation': datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
            'confidence': 0.65
        },
        {
            'species': 'virginica',
            'params': '3.6, 2.6, 0.9, 1.1',
            'creation': None,
            'confidence': None
        }
    ]
)
def test_create_prediction_bad_request(client, data):
    """
    GIVEN request data with invalid values or missing attributes
    WHEN endpoint /create-prediction/ is called
    THEN it should return status 400 and JSON body
    """
    response = client.post(
        '/create-prediction/',
        data=json.dumps(
            data
        ),
        content_type='application/json',
    )

    assert response.status_code == 400
    assert response.json is not None


@pytest.mark.e2e
def test_create_list_get(client):
    requests.post(
        'http://localhost:5000/create-prediction/',
        json={
            'species': 'setosa',
            'params': 'Some extra awesome content',
            'creation': datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
            'confidence': 0.88
        }
    )
    response = requests.get(
        'http://localhost:5000/prediction-list/',
    )

    predictions = response.json()

    response = requests.get(
        f'http://localhost:5000/prediction/{predictions[0]["id"]}/',
    )

    assert response.status_code == 200
