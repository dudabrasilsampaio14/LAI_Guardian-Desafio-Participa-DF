#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Execução ultra simples do LAI Guardian.

Uso:
  python run.py

O script tenta rodar o pipeline completo (FULL):
  - Auditoria + Excel (se existir data/raw/AMOSTRA_e-SIC.xlsx)
  - Anonimização + JSON (idem)
  - Treino ML (se existir data/raw/dataset_labeled.csv)
  - Avaliação ML (idem)

Saídas ficam em data/processed/run_YYYYMMDD_HHMMSS/
"""
from __future__ import annotations

import os
import datetime

from lai_guardian.pipeline import FullPipelineConfig, run_full_pipeline

DEFAULT_XLSX = os.path.join("data", "raw", "AMOSTRA_e-SIC.xlsx")
DEFAULT_CSV = os.path.join("data", "raw", "dataset_labeled.csv")
DEFAULT_COL = "Texto Mascarado"


def main():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bundle = os.path.join("data", "processed", f"run_{ts}")

    cfg = FullPipelineConfig(
        input_path=DEFAULT_XLSX if os.path.exists(DEFAULT_XLSX) else None,
        input_column=DEFAULT_COL,
        excel_out=os.path.join("data", "processed", "auditoria.xlsx"),
        json_out=os.path.join("data", "processed", "relatorio.json"),
        train_csv=DEFAULT_CSV if os.path.exists(DEFAULT_CSV) else None,
        train_text_col="text",
        train_label_col="label_any_pii",
        eval_csv=DEFAULT_CSV if os.path.exists(DEFAULT_CSV) else None,
        eval_text_col="text",
        eval_label_col="label_any_pii",
        model_path=os.path.join("data", "processed", "model.joblib"),
        metrics_out=os.path.join("data", "processed", "metrics.json"),
        bundle_dir=bundle,
        strict=False,
    )

    run_full_pipeline(cfg)


if __name__ == "__main__":
    main()
