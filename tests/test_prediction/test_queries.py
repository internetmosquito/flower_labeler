from datetime import datetime

from labeler.models import Prediction
from labeler.queries import ListPredictionsQuery, GetPredictionByIDQuery


def test_list_articles():
    """
    GIVEN 2 predictions stored in the database
    WHEN the execute method is called
    THEN it should return 2 predictions
    """
    Prediction(
        species='setosa',
        params='5.1, 3.8, 1.5, 0.3',
        creation=datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
        confidence=0.86
    ).save()
    Prediction(
        species='versicolor',
        params='3.3, 4.2, 1.1, 0.6',
        creation=datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
        confidence=0.88
    ).save()

    query = ListPredictionsQuery()

    assert len(query.execute()) == 2


def test_get_prediction_by_id():
    """
    GIVEN ID of prediction stored in the database
    WHEN the execute method is called on GetPredictionByIDQuery with id set
    THEN it should return the prediction with the same id
    """
    prediction = Prediction(
        species='virginica',
        params='3.6, 2.6, 0.9, 1.1',
        creation=datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
        confidence=0.75
    ).save()

    query = GetPredictionByIDQuery(
        id=prediction.id
    )

    assert query.execute().id == prediction.id

