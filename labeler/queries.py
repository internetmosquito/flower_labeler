from typing import List

from pydantic import BaseModel

from labeler.models import Prediction


class ListPredictionsQuery(BaseModel):

    def execute(self) -> List[Prediction]:
        predictions = Prediction.list()

        return predictions


class GetPredictionByIDQuery(BaseModel):
    id: str

    def execute(self) -> Prediction:
        prediction = Prediction.get_by_id(self.id)

        return prediction
