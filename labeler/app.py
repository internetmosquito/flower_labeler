from flask import Flask, jsonify, request, make_response
from pydantic import ValidationError

from labeler.commands import CreatePredictionCommand, TrainModelCommand, PredictCommand
from labeler.queries import GetPredictionByIDQuery, ListPredictionsQuery


app = Flask(__name__)


@app.errorhandler(ValidationError)
def handle_validation_exception(error):
    response = jsonify(error.errors())
    response.status_code = 400
    return response


@app.route('/train', methods=['GET'])
def train_model():
    TrainModelCommand().execute()
    message = jsonify(message='"Model trained successsfully')
    return make_response(message, 200)


@app.route('/predict', methods=['POST'])
def predict():
    value = request.json
    prediction = PredictCommand().execute(**value)
    message = jsonify(prediction)
    return make_response(message, 200)


@app.route('/create-prediction/', methods=['POST'])
def create_prediction():
    # TODO: Use params from request to get actual prediction
    cmd = CreatePredictionCommand(
        **request.json
    )
    return jsonify(cmd.execute().dict())


@app.route('/prediction/<prediction_id>/', methods=['GET'])
def get_prediction(prediction_id):
    query = GetPredictionByIDQuery(
        id=prediction_id
    )
    return jsonify(query.execute().dict())


@app.route('/prediction-list/', methods=['GET'])
def list_predictions():
    query = ListPredictionsQuery()
    records = [record.dict() for record in query.execute()]
    return jsonify(records)


if __name__ == '__main__':
    app.run()
