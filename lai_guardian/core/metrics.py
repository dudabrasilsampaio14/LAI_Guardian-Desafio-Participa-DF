from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class EvaluationMetrics:
    vp: int; fp: int; fn: int; vn: int
    precision: float; recall: float; f1: float; accuracy: float
    total: int; positivos_reais: int; negativos_reais: int

def calculate(y_true: List[int], y_pred: List[int]) -> EvaluationMetrics:
    assert len(y_true) == len(y_pred)
    vp = sum(1 for t,p in zip(y_true,y_pred) if t==1 and p==1)
    fp = sum(1 for t,p in zip(y_true,y_pred) if t==0 and p==1)
    fn = sum(1 for t,p in zip(y_true,y_pred) if t==1 and p==0)
    vn = sum(1 for t,p in zip(y_true,y_pred) if t==0 and p==0)
    precision = vp/(vp+fp) if (vp+fp)>0 else 0.0
    recall = vp/(vp+fn) if (vp+fn)>0 else 0.0
    f1 = (2*precision*recall/(precision+recall)) if (precision+recall)>0 else 0.0
    accuracy = (vp+vn)/len(y_true) if len(y_true)>0 else 0.0
    pos = sum(y_true); neg = len(y_true)-pos
    return EvaluationMetrics(vp,fp,fn,vn,precision,recall,f1,accuracy,len(y_true),pos,neg)

def to_dict(m: EvaluationMetrics) -> Dict:
    return {
        "metricas": {"precision": m.precision, "recall": m.recall, "f1": m.f1, "accuracy": m.accuracy},
        "contagens": {"vp": m.vp, "fp": m.fp, "fn": m.fn, "vn": m.vn},
        "totais": {"total": m.total, "positivos_reais": m.positivos_reais, "negativos_reais": m.negativos_reais},
    }
