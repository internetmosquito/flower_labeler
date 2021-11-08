import pytest
from datetime import datetime
from labeler.models import Prediction
from labeler.commands import CreatePredictionCommand, AlreadyExists, TrainModelCommand, PredictCommand


def test_create_prediction():
    """
    GIVEN CreatePredictionCommand with a valid properties params and confidence
    WHEN the execute method is called
    THEN a new Prediction must exist in the database with the same attributes
    """
    cmd = CreatePredictionCommand(
        species='setosa',
        params='5.1, 3.8, 1.5, 0.3',
        creation=datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
        confidence=0.86
    )

    prediction = cmd.execute()

    db_prediction = Prediction.get_by_id(prediction.id)

    assert db_prediction.id == prediction.id
    assert db_prediction.species == prediction.species
    assert db_prediction.params == prediction.params
    assert db_prediction.creation == prediction.creation
    assert db_prediction.confidence == prediction.confidence


def test_create_prediction_already_exists():
    """
    GIVEN CreatePredictionCommand with params, species and confidence
    WHEN the execute method is called
    THEN the AlreadyExists exception must be raised
    """

    Prediction(
        species='setosa',
        params='5.1, 3.8, 1.5, 0.3',
        creation=datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
        confidence=0.86
    ).save()

    cmd = CreatePredictionCommand(
        species='setosa',
        params='5.1, 3.8, 1.5, 0.3',
        creation=datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
        confidence=0.86
    )

    with pytest.raises(AlreadyExists):
        cmd.execute()


def test_train_model():
    """
    GIVEN TrainModelCommand
    WHEN the execute method is called
    THEN a model is trained
    """
    cmd = TrainModelCommand()
    results = cmd.execute()
    assert 'Accuracy' in results


def test_predict():
    """
    GIVEN PredictCommand receives a list of values to predict
    WHEN the execute method is called
    THEN a prediction for the set of values is returned
    """
    cmd = PredictCommand()
    observation = {'Values': [5.1, 3.8, 1.5, 0.3]}
    results = cmd.execute(value=observation)
    assert 'Predicted class' in results
    assert results['Predicted class'] == 'setosa'
