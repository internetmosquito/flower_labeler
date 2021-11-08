import os
import sqlite3
import uuid
from typing import List


from pydantic import BaseModel, Field


class NotFound(Exception):
    pass


class Prediction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    species: str
    params: str
    creation: str
    confidence: float

    @classmethod
    def get_by_id(cls, prediction_id: str):
        con = sqlite3.connect(os.getenv('DATABASE_NAME', 'predictions.db'))
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("SELECT * FROM predictions WHERE id=?", (prediction_id,))

        record = cur.fetchone()

        if record is None:
            raise NotFound

        prediction = cls(**record)
        con.close()

        return prediction

    @classmethod
    def get_by_combined(cls, species: str, params: str, creation: str, confidence: float):
        con = sqlite3.connect(os.getenv('DATABASE_NAME', 'predictions.db'))
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("SELECT * FROM predictions WHERE species = ? AND params = ? AND creation = ? AND confidence = ?",
                    (species, params, creation, confidence))

        record = cur.fetchone()

        if record is None:
            raise NotFound

        prediction = cls(**record)  # Row can be unpacked as dict
        con.close()

        return prediction

    @classmethod
    def list(cls) -> List['Prediction']:
        con = sqlite3.connect(os.getenv('DATABASE_NAME', 'predictions.db'))
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("SELECT * FROM predictions")

        records = cur.fetchall()
        predictions = [cls(**record) for record in records]
        con.close()

        return predictions

    def save(self) -> 'Prediction':
        with sqlite3.connect(os.getenv('DATABASE_NAME', 'predictions.db')) as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO predictions (id,species,params,creation, confidence) VALUES(?, ?, ?, ?, ?)",
                (self.id, self.species, self.params, self.creation, self.confidence)
            )
            con.commit()

        return self

    @classmethod
    def create_table(cls, database_name='predictions.db'):
        conn = sqlite3.connect(database_name)

        conn.execute(
            'CREATE TABLE IF NOT EXISTS predictions (id TEXT, species TEXT, params TEXT, creation TEXT, confidence REAL)'
        )
        conn.close()
