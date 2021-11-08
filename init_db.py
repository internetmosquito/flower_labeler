import os


if __name__ == '__main__':
    from labeler.models import Prediction

    os.environ['DATABASE_NAME'] = 'predictions.db'
    path = os.path.dirname(os.path.realpath(__file__)) + '/predictions.db'
    Prediction.create_table(database_name=path)
