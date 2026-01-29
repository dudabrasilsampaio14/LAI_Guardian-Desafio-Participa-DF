from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

@dataclass
class MLConfig:
    min_df: int = 2
    ngram_max: int = 2
    C: float = 4.0

class TextClassifier:
    def __init__(self, config: Optional[MLConfig] = None):
        self.config = config or MLConfig()
        self.pipe = Pipeline([
            ("tfidf", TfidfVectorizer(min_df=self.config.min_df, ngram_range=(1, self.config.ngram_max))),
            ("clf", LogisticRegression(C=self.config.C, max_iter=2000, class_weight="balanced")),
        ])

    def train(self, texts: List[str], labels: List[int]):
        self.pipe.fit(texts, labels)

    def predict(self, texts: List[str]) -> List[int]:
        return self.pipe.predict(texts).tolist()

    def save(self, path: str):
        joblib.dump({"config": self.config, "pipe": self.pipe}, path)

    @classmethod
    def load(cls, path: str) -> "TextClassifier":
        obj = joblib.load(path)
        inst = cls(obj.get("config"))
        inst.pipe = obj["pipe"]
        return inst
