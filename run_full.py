#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entrada única para rodar o LAI Guardian em modo FULL PIPELINE.

Exemplos:
  python run_full.py --input data/raw/AMOSTRA_e-SIC.xlsx --column "Texto Mascarado"
  python run_full.py --input ... --train-csv ... --eval-csv ... --bundle
"""
from __future__ import annotations

import argparse
import datetime
import json
import os

from lai_guardian.pipeline import FullPipelineConfig, run_full_pipeline


def build_parser():
    p = argparse.ArgumentParser(prog="run_full.py", add_help=True)

    # Auditoria/Anonimização
    p.add_argument("--input", type=str, default="")
    p.add_argument("--column", type=str, default="Texto Mascarado")
    p.add_argument("--excel", type=str, default="data/processed/auditoria.xlsx")
    p.add_argument("--json", type=str, default="data/processed/relatorio.json")

    # Treino ML
    p.add_argument("--train-csv", type=str, default="")
    p.add_argument("--train-text-col", type=str, default="text")
    p.add_argument("--train-label-col", type=str, default="label")

    # Avaliação ML
    p.add_argument("--eval-csv", type=str, default="")
    p.add_argument("--eval-text-col", type=str, default="text")
    p.add_argument("--eval-label-col", type=str, default="label")

    # Artefatos ML
    p.add_argument("--model", type=str, default="data/processed/model.joblib")
    p.add_argument("--metrics", type=str, default="data/processed/metrics.json")

    # Execução
    p.add_argument("--no-ner", action="store_true")
    p.add_argument("--strict", action="store_true")

    # Bundle
    p.add_argument("--bundle", action="store_true", help="Salva todas as saídas em um diretório único por execução.")
    p.add_argument("--bundle-dir", type=str, default="", help="Diretório do bundle (se vazio e --bundle, auto).")

    # Summary opcional
    p.add_argument("--summary", type=str, default="", help="Salva um resumo do pipeline em JSON (opcional).")
    return p


def main():
    args = build_parser().parse_args()

    bundle_dir = None
    if args.bundle:
        if args.bundle_dir:
            bundle_dir = args.bundle_dir
        else:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            bundle_dir = os.path.join("data", "processed", f"run_{ts}")

    cfg = FullPipelineConfig(
        input_path=args.input or None,
        input_column=args.column,
        excel_out=args.excel,
        json_out=args.json,
        train_csv=args.train_csv or None,
        train_text_col=args.train_text_col,
        train_label_col=args.train_label_col,
        eval_csv=args.eval_csv or None,
        eval_text_col=args.eval_text_col,
        eval_label_col=args.eval_label_col,
        model_path=args.model,
        metrics_out=args.metrics,
        no_ner=args.no_ner,
        strict=args.strict,
        bundle_dir=bundle_dir,
    )

    summary = run_full_pipeline(cfg)

    if args.summary:
        os.makedirs(os.path.dirname(args.summary) or ".", exist_ok=True)
        with open(args.summary, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
