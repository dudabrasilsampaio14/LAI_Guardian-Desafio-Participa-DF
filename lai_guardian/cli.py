from __future__ import annotations
"""CLI do LAI Guardian. Útil quando você quer controlar entradas/saídas sem mexer no run.py."""
import argparse, os, time, json

from .ui.render import console, header, kpis, confusion, spinner_progress
from .io.loader import load_table, parse_labels
from .core.engine import GuardianEngine
from .core.metrics import calculate, to_dict
from .reports.excel import export_excel
from .ml.model import TextClassifier
from .pipeline import FullPipelineConfig, run_full_pipeline

def cmd_default(args):
    ml = TextClassifier.load(args.model) if args.model else None
    engine = GuardianEngine(use_ner=not args.no_ner, ml_model=ml)

    data = load_table(args.input, args.column, label_col=args.label_col or None)
    df = data.df.copy()
    texts = df[data.text_col].astype(str).tolist()

    header()
    console.print(f"✔ Fonte carregada: [bold]{len(df)}[/bold] registros.", style="muted")

    with spinner_progress("Auditando pedidos LAI...") as prog:
        task = prog.add_task("Auditando pedidos LAI...", total=max(1, len(texts)))
        flags, reasons, redacted = [], [], []
        types_detected, max_risk, findings_count = [], [], []
        for t in texts:
            dec = engine.analyze(t, redact=True)
            flags.append(dec.contains_pii)
            reasons.append(dec.reason)
            redacted.append(dec.redacted_text)
            types_detected.append(getattr(dec, 'types_detected', ''))
            max_risk.append(getattr(dec, 'max_risk', ''))
            findings_count.append(int(getattr(dec, 'findings_count', 0)))
            prog.update(task, advance=1)

    df["Contem_Dados_Pessoais"] = flags
    df["Motivo"] = reasons
    df["Versao_Publicavel"] = redacted
    df["Tipos_Detectados"] = types_detected
    df["Risco_Max"] = max_risk
    df["Qtd_Achados"] = findings_count

    if args.out:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        export_excel(df, args.out)
        console.print(f"✅ Excel gerado em: [underline yellow]{args.out}[/underline yellow]", style="success")

def cmd_anonymize(args):
    ml = TextClassifier.load(args.model) if args.model else None
    engine = GuardianEngine(use_ner=not args.no_ner, ml_model=ml)

    data = load_table(args.input, args.column, label_col=None)
    df = data.df.copy()
    texts = df[data.text_col].astype(str).tolist()

    header()
    console.print(f"✔ Fonte carregada: [bold]{len(df)}[/bold] registros.", style="muted")

    rel = []
    with spinner_progress("Anonimizando e gerando trilha...") as prog:
        task = prog.add_task("Anonimizando e gerando trilha...", total=max(1, len(texts)))
        for idx, t in enumerate(texts):
            dec = engine.analyze(t, redact=True)
            if dec.contains_pii:
                rel.append({"row": int(idx), "reason": dec.reason, "findings": dec.findings, "public_text": dec.redacted_text})
            prog.update(task, advance=1)

    os.makedirs(os.path.dirname(args.json) or ".", exist_ok=True)
    with open(args.json, "w", encoding="utf-8") as f:
        json.dump(rel, f, ensure_ascii=False, indent=2)
    console.print(f"✅ Relatório JSON em: [underline yellow]{args.json}[/underline yellow]", style="success")


def cmd_full(args):
    cfg = FullPipelineConfig(
        input_path=args.input_full or None,
        input_column=args.column_full,
        excel_out=args.excel_full,
        json_out=args.json_full,
        train_csv=args.train_csv or None,
        train_text_col=args.train_text_col,
        train_label_col=args.train_label_col,
        eval_csv=args.eval_csv or None,
        eval_text_col=args.eval_text_col,
        eval_label_col=args.eval_label_col,
        model_path=args.model_path,
        metrics_out=args.metrics_out,
        no_ner=args.no_ner_full,
        strict=args.strict,
        bundle_dir=args.bundle_dir or None,
    )
    run_full_pipeline(cfg)

def cmd_train(args):
    header()
    data = load_table(args.csv, args.text_col, label_col=args.label_col)
    df = data.df
    y = parse_labels(df[data.label_col])
    X = df[data.text_col].astype(str).tolist()

    clf = TextClassifier()
    with spinner_progress("Treinando modelo ML (TF-IDF + LogReg)...") as prog:
        task = prog.add_task("Treinando modelo ML (TF-IDF + LogReg)...", total=100)
        for _ in range(20):
            time.sleep(0.02)
            prog.update(task, advance=5)
        clf.train(X, y)
        prog.update(task, completed=100)

    os.makedirs(os.path.dirname(args.model) or ".", exist_ok=True)
    clf.save(args.model)
    console.print(f"✅ Modelo salvo em: [underline yellow]{args.model}[/underline yellow]", style="success")

def cmd_evaluate(args):
    header()
    data = load_table(args.csv, args.text_col, label_col=args.label_col)
    df = data.df
    y_true = parse_labels(df[data.label_col])
    X = df[data.text_col].astype(str).tolist()

    clf = TextClassifier.load(args.model)

    with spinner_progress("Avaliando modelo ML...") as prog:
        task = prog.add_task("Avaliando modelo ML...", total=max(1, len(X)))
        y_pred = []
        for i in range(0, len(X), 256):
            batch = X[i:i+256]
            y_pred.extend(clf.predict(batch))
            prog.update(task, advance=len(batch))

    m = calculate(y_true, y_pred)
    kpis(m.precision, m.recall, m.f1, m.fn)
    confusion(m.vn, m.fp, m.fn, m.vp)

    os.makedirs(os.path.dirname(args.report) or ".", exist_ok=True)
    with open(args.report, "w", encoding="utf-8") as f:
        json.dump(to_dict(m), f, ensure_ascii=False, indent=2)
    console.print(f"✅ Relatório salvo em: [underline yellow]{args.report}[/underline yellow]", style="success")

def build_parser():
    p = argparse.ArgumentParser(prog="lai_guardian", add_help=True)
    sub = p.add_subparsers(dest="cmd")

    p.add_argument("--input", type=str, default="data/raw/AMOSTRA_e-SIC.xlsx")
    p.add_argument("--column", type=str, default="Texto Mascarado")
    p.add_argument("--label-col", type=str, default="")
    p.add_argument("--out", type=str, default="data/processed/auditoria.xlsx")
    p.add_argument("--model", type=str, default="")
    p.add_argument("--no-ner", action="store_true")

    a = sub.add_parser("anonymize", help="Anonimiza textos e gera trilha JSON.")
    a.add_argument("--input", type=str, default="data/raw/AMOSTRA_e-SIC.xlsx")
    a.add_argument("--column", type=str, default="Texto Mascarado")
    a.add_argument("--json", type=str, default="data/processed/relatorio.json")
    a.add_argument("--model", type=str, default="")
    a.add_argument("--no-ner", action="store_true")

    
    f = sub.add_parser("full", help="Executa auditoria + anonimização + (opcional) treino + (opcional) avaliação em um comando.")
    f.add_argument("--input-full", type=str, default="data/raw/AMOSTRA_e-SIC.xlsx")
    f.add_argument("--column-full", type=str, default="Texto Mascarado")
    f.add_argument("--excel-full", type=str, default="data/processed/auditoria.xlsx")
    f.add_argument("--json-full", type=str, default="data/processed/relatorio.json")

    f.add_argument("--train-csv", type=str, default="")
    f.add_argument("--train-text-col", type=str, default="text")
    f.add_argument("--train-label-col", type=str, default="label")

    f.add_argument("--eval-csv", type=str, default="")
    f.add_argument("--eval-text-col", type=str, default="text")
    f.add_argument("--eval-label-col", type=str, default="label")

    f.add_argument("--model-path", type=str, default="data/processed/model.joblib")
    f.add_argument("--metrics-out", type=str, default="data/processed/metrics.json")

    f.add_argument("--bundle-dir", type=str, default="", help="Se definido, salva todas as saídas dentro deste diretório.")
    f.add_argument("--no-ner-full", action="store_true", help="Desativa NER (spaCy) durante a execução FULL.")
    f.add_argument("--strict", action="store_true", help="Falha se alguma etapa solicitada não puder rodar.")

t = sub.add_parser("train", help="Treina modelo ML supervisionado (CSV rotulado).")
    t.add_argument("--csv", type=str, required=True)
    t.add_argument("--text-col", type=str, default="text")
    t.add_argument("--label-col", type=str, default="label")
    t.add_argument("--model", type=str, default="data/processed/model.joblib")

    e = sub.add_parser("evaluate", help="Avalia modelo ML em CSV rotulado.")
    e.add_argument("--csv", type=str, required=True)
    e.add_argument("--text-col", type=str, default="text")
    e.add_argument("--label-col", type=str, default="label")
    e.add_argument("--model", type=str, required=True)
    e.add_argument("--report", type=str, default="data/processed/metrics.json")

    return p

def main():
    args = build_parser().parse_args()
    if args.cmd == "full": return cmd_full(args)
    if args.cmd == "train": return cmd_train(args)
    if args.cmd == "evaluate": return cmd_evaluate(args)
    if args.cmd == "anonymize": return cmd_anonymize(args)
    return cmd_default(args)
