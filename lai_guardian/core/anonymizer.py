from __future__ import annotations
"""Anonimização e trilha de auditoria. Aplica tarjas com base na posição real do achado, preservando o texto restante."""
from dataclasses import asdict
from typing import List, Dict, Any, Tuple
import datetime

from .detector import HybridDetector, Finding

RISK_TO_TAG = {"CRÍTICO":"CRITICO","ALTO":"ALTO","MÉDIO":"MEDIO","BAIXO":"BAIXO"}

def redact_by_spans(text: str, findings: List[Finding]) -> str:
    # Atenção: aplicamos as tarjas de trás para frente para não bagunçar os índices.
    # Isso evita trocar a posição dos próximos achados.
    if not findings:
        return text
    out = text
    for f in sorted(findings, key=lambda x: x.start, reverse=True):
        tag = RISK_TO_TAG.get(f.risco, "INFO")
        out = out[:f.start] + f"[{f.tipo}_{tag}_OMITIDO]" + out[f.end:]
    return out

def audit_record(text: str, detector: HybridDetector) -> Tuple[List[Dict[str, Any]], str]:
    findings = detector.detect(text)
    now = datetime.datetime.now().isoformat()
    audit = []
    for f in findings:
        d = asdict(f)
        d["timestamp"] = now
        audit.append(d)
    return audit, redact_by_spans(text, findings)
