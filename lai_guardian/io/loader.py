from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List
import pandas as pd
import os

@dataclass
class LoadedData:
    df: pd.DataFrame
    text_col: str
    label_col: Optional[str] = None

def load_table(path: str, text_col: str, label_col: Optional[str] = None) -> LoadedData:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    if path.lower().endswith((".xlsx",".xls")):
        df = pd.read_excel(path, engine="openpyxl")
    else:
        df = pd.read_csv(path)
    if text_col not in df.columns:
        raise ValueError(f"Coluna de texto '{text_col}' não encontrada. Colunas: {list(df.columns)}")
    if label_col and label_col not in df.columns:
        raise ValueError(f"Coluna de label '{label_col}' não encontrada. Colunas: {list(df.columns)}")
    return LoadedData(df=df, text_col=text_col, label_col=label_col)

def parse_labels(series: pd.Series) -> List[int]:
    def to_int(x):
        if isinstance(x, bool): return 1 if x else 0
        if x is None: return 0
        if isinstance(x, int): return 1 if x != 0 else 0
        if isinstance(x, float): return 1 if x != 0.0 else 0
        s = str(x).strip().lower()
        if s in {"1","true","t","sim","yes","y"}: return 1
        if s in {"0","false","f","não","nao","no","n"}: return 0
        return 0
    return [to_int(v) for v in series.tolist()]
