from __future__ import annotations
"""Pipeline completo do projeto (auditoria, anonimização, treino e avaliação). Usado por run.py e pelo CLI."""

import os
import json
import time
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

from .ui.render import console, header, kpis, confusion, spinner_progress
from .io.loader import load_table, parse_labels
from .core.engine import GuardianEngine
from .core.metrics import calculate, to_dict
from .reports.excel import export_excel
from .ml.model import TextClassifier


@dataclass
class FullPipelineConfig:
    # Entradas (auditoria/anonimização)
    input_path: Optional[str] = None
    input_column: str = "Texto Mascarado"

    # Saídas (auditoria/anonimização)
    excel_out: str = "data/processed/auditoria.xlsx"
    json_out: str = "data/processed/relatorio.json"

    # ML (treino/avaliação)
    train_csv: Optional[str] = None
    train_text_col: str = "text"
    train_label_col: str = "label"

    eval_csv: Optional[str] = None
    eval_text_col: str = "text"
    eval_label_col: str = "label"

    model_path: str = "data/processed/model.joblib"
    metrics_out: str = "data/processed/metrics.json"

    # Execução
    no_ner: bool = False
    strict: bool = False

    # Organização
    bundle_dir: Optional[str] = None  # se definido, salva tudo dentro deste diretório


def _ensure_dir(path: str):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)


def _apply_bundle(cfg: FullPipelineConfig) -> FullPipelineConfig:
    """Se bundle_dir estiver definido, reescreve paths para dentro do bundle."""
    if not cfg.bundle_dir:
        return cfg
    b = cfg.bundle_dir.rstrip("/\\")
    os.makedirs(b, exist_ok=True)

    def join(p: str) -> str:
        return os.path.join(b, os.path.basename(p))

    cfg.excel_out = join(cfg.excel_out)
    cfg.json_out = join(cfg.json_out)
    cfg.model_path = join(cfg.model_path)
    cfg.metrics_out = join(cfg.metrics_out)
    return cfg


def run_full_pipeline(cfg: FullPipelineConfig) -> Dict[str, Any]:
    """
    Executa:
      1) Auditoria + Excel
      2) Anonimização + JSON (trilha)
      3) Treinamento ML (opcional)
      4) Avaliação ML (opcional)

    Sem strict: roda o que der e registra etapas puladas.
    Com strict: se a etapa solicitada não puder rodar, aborta.
    """
    cfg = _apply_bundle(cfg)

    header()
    console.print("[muted]Modo: FULL PIPELINE (Auditoria → Anonimização → Treino → Avaliação)[/muted]\n")

    summary: Dict[str, Any] = {
        "inputs": asdict(cfg),
        "steps": {"audit_excel": False, "anonymize_json": False, "train_ml": False, "evaluate_ml": False},
        "outputs": {},
        "warnings": [],
    }

    # Carrega modelo existente se houver (para backstop na auditoria)
    ml_model = None
    if cfg.model_path and os.path.exists(cfg.model_path):
        try:
            ml_model = TextClassifier.load(cfg.model_path)
            summary["warnings"].append(f"Modelo existente carregado: {cfg.model_path}")
        except Exception as e:
            msg = f"Falha ao carregar modelo existente ({cfg.model_path}): {e}"
            if cfg.strict:
                raise RuntimeError(msg)
            summary["warnings"].append(msg)

    engine = GuardianEngine(use_ner=not cfg.no_ner, ml_model=ml_model)

    # --- Etapas 1 e 2 ---
    if cfg.input_path:
        data = load_table(cfg.input_path, cfg.input_column, label_col=None)
        df = data.df.copy()
        texts = df[data.text_col].astype(str).tolist()

        console.print(f"✔ Fonte: [bold]{cfg.input_path}[/bold] | Registros: [bold]{len(df)}[/bold]", style="muted")

        json_rows = []
        with spinner_progress("Processando auditoria + versão publicável...") as prog:
            task = prog.add_task("Processando auditoria + versão publicável...", total=max(1, len(texts)))
            flags, reasons, redacted = [], [], []
            types_detected, max_risk, findings_count = [], [], []
            for idx, t in enumerate(texts):
                dec = engine.analyze(t, redact=True)
                flags.append(dec.contains_pii)
                reasons.append(dec.reason)
                redacted.append(dec.redacted_text)
                types_detected.append(getattr(dec, 'types_detected', ''))
                max_risk.append(getattr(dec, 'max_risk', ''))
                findings_count.append(int(getattr(dec, 'findings_count', 0)))
                if dec.contains_pii:
                    json_rows.append({
                        "row": int(idx),
                        "reason": dec.reason,
                        "findings_count": dec.findings_count,
                        "findings": dec.findings,
                        "public_text": dec.redacted_text,
                    })
                prog.update(task, advance=1)

        df["Contem_Dados_Pessoais"] = flags
        df["Motivo"] = reasons
        df["Versao_Publicavel"] = redacted
        df["Tipos_Detectados"] = types_detected
        df["Risco_Max"] = max_risk
        df["Qtd_Achados"] = findings_count

        _ensure_dir(cfg.excel_out)
        export_excel(df, cfg.excel_out)
        summary["steps"]["audit_excel"] = True
        summary["outputs"]["excel"] = cfg.excel_out
        console.print(f"✅ Excel gerado: [underline yellow]{cfg.excel_out}[/underline yellow]", style="success")

        _ensure_dir(cfg.json_out)
        with open(cfg.json_out, "w", encoding="utf-8") as f:
            json.dump(json_rows, f, ensure_ascii=False, indent=2)
        summary["steps"]["anonymize_json"] = True
        summary["outputs"]["json"] = cfg.json_out
        console.print(f"✅ Relatório JSON: [underline yellow]{cfg.json_out}[/underline yellow]", style="success")

    else:
        msg = "Etapas 1/2 puladas: nenhum --input informado."
        if cfg.strict:
            raise RuntimeError(msg)
        summary["warnings"].append(msg)
        console.print(f"⚠️ {msg}", style="warning")

    # --- Etapa 3: treino ---
    trained_model = None
    if cfg.train_csv:
        data = load_table(cfg.train_csv, cfg.train_text_col, label_col=cfg.train_label_col)
        df = data.df
        y = parse_labels(df[data.label_col])
        X = df[data.text_col].astype(str).tolist()

        trained_model = TextClassifier()
        with spinner_progress("Treinando modelo ML (TF-IDF + LogReg)...") as prog:
            task = prog.add_task("Treinando modelo ML (TF-IDF + LogReg)...", total=100)
            for _ in range(20):
                time.sleep(0.02)
                prog.update(task, advance=5)
            trained_model.train(X, y)
            prog.update(task, completed=100)

        _ensure_dir(cfg.model_path)
        trained_model.save(cfg.model_path)
        summary["steps"]["train_ml"] = True
        summary["outputs"]["model"] = cfg.model_path
        console.print(f"✅ Modelo salvo: [underline yellow]{cfg.model_path}[/underline yellow]", style="success")
        engine.ml_model = trained_model
    else:
        summary["warnings"].append("Etapa 3 (treino) pulada: nenhum --train-csv informado.")

    # --- Etapa 4: avaliação ---
    if cfg.eval_csv:
        model_for_eval = trained_model
        if model_for_eval is None and cfg.model_path and os.path.exists(cfg.model_path):
            try:
                model_for_eval = TextClassifier.load(cfg.model_path)
            except Exception as e:
                msg = f"Não foi possível carregar modelo para avaliação: {e}"
                if cfg.strict:
                    raise RuntimeError(msg)
                summary["warnings"].append(msg)
                model_for_eval = None

        if model_for_eval is None:
            msg = "Etapa 4 solicitada, mas não há modelo disponível (treine ou forneça um modelo existente)."
            if cfg.strict:
                raise RuntimeError(msg)
            summary["warnings"].append(msg)
            console.print(f"⚠️ {msg}", style="warning")
        else:
            data = load_table(cfg.eval_csv, cfg.eval_text_col, label_col=cfg.eval_label_col)
            df = data.df
            y_true = parse_labels(df[data.label_col])
            X = df[data.text_col].astype(str).tolist()

            with spinner_progress("Avaliando modelo ML...") as prog:
                task = prog.add_task("Avaliando modelo ML...", total=max(1, len(X)))
                y_pred = []
                for i in range(0, len(X), 256):
                    batch = X[i:i+256]
                    y_pred.extend(model_for_eval.predict(batch))
                    prog.update(task, advance=len(batch))

            m = calculate(y_true, y_pred)
            kpis(m.precision, m.recall, m.f1, m.fn)
            confusion(m.vn, m.fp, m.fn, m.vp)

            _ensure_dir(cfg.metrics_out)
            with open(cfg.metrics_out, "w", encoding="utf-8") as f:
                json.dump(to_dict(m), f, ensure_ascii=False, indent=2)

            summary["steps"]["evaluate_ml"] = True
            summary["outputs"]["metrics"] = cfg.metrics_out
            console.print(f"✅ Métricas salvas: [underline yellow]{cfg.metrics_out}[/underline yellow]", style="success")
    else:
        summary["warnings"].append("Etapa 4 (avaliação) pulada: nenhum --eval-csv informado.")

    console.print("\n[success]🏁 FULL PIPELINE CONCLUÍDO[/success]")
    if summary["warnings"]:
        console.print(f"[warning]⚠️ Avisos: {len(summary['warnings'])}[/warning]")
    return summary
