from pydantic import BaseModel
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import logging
from utils.data_utils import load_data, stratified_split, parse_observation
from utils.model_utils import ClfSwitcher, format_params, save_model, load_model
from utils.config import get_default

from labeler.models import Prediction, NotFound

logger = logging.getLogger(__name__)

C = get_default('models', 'regression_C')
MAX_DEPTH = get_default('models', 'tree_max_depth')
MIN_SAMPLES_LEAF = get_default('models', 'tree_min_samples_leaf')
SCORING = get_default('design', 'scoring')
NUM_FOLDS = get_default('design', 'cv')
N_SAMPLES = get_default('design', 'n_samples')


class AlreadyExists(Exception):
    pass


class CreatePredictionCommand(BaseModel):
    species: str
    params: str
    creation: str
    confidence: float

    def execute(self) -> Prediction:
        try:
            Prediction.get_by_combined(self.species, self.params, self.creation, self.confidence)
            raise AlreadyExists
        except NotFound:
            pass

        prediction = Prediction(
            species=self.species,
            params=self.params,
            creation=self.creation,
            confidence=self.confidence
        ).save()

        return prediction


class TrainModelCommand:

    def execute(self) -> dict:
        try:
            data_df = load_data()
            train_df, test_df = stratified_split(
                data=data_df, target='species', n_samples=N_SAMPLES)

            # compile the modelling pipeline for CV using sklearn
            steps = [('scaler', StandardScaler()), ('clf', ClfSwitcher())]
            pipeline = Pipeline(steps)
            parameters = [format_params(LogisticRegression(),
                                        C=C),
                          format_params(DecisionTreeClassifier(),
                                        max_depth=MAX_DEPTH,
                                        min_samples_leaf=MIN_SAMPLES_LEAF),
                          format_params(LinearDiscriminantAnalysis())]

            gscv = GridSearchCV(pipeline, parameters, cv=NUM_FOLDS,
                                scoring=SCORING)

            logger.info(f'Training model')
            gscv.fit(train_df.iloc[:, :4], train_df['species'])

            # print results
            logger.info(f'best model: {gscv.best_estimator_}')
            accuracy = gscv.score(
                test_df.iloc[:, :4], test_df['species'])
            logger.info(f'Test set accuracy: {accuracy}')

            save_model(gscv)
            results = {'Accuracy': accuracy}
            return results

        except Exception as ex:
            logger.error(f'Exception: {ex.__repr__()}')


class PredictCommand:

    def execute(self, value) -> dict:
        try:
            gscv = load_model()
            observation = value['Values']
            new_obs = parse_observation(observation)
            prediction = gscv.predict(new_obs)
            logger.info(f'Predicted class: {prediction[0]}')
            result = {'Predicted class': prediction[0]}
            return result
        except Exception as ex:
            logger.error(f'Exception: {ex.__repr__()}')




