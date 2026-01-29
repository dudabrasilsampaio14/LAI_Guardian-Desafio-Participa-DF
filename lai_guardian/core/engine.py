from __future__ import annotations
"""Motor de decisão: consolida achados do detector e, se configurado, usa um modelo estatístico como apoio."""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from .detector import HybridDetector
from .anonymizer import audit_record
from ..ml.model import TextClassifier

@dataclass
class Decision:
    contains_pii: bool
    reason: str
    findings_count: int
    findings: List[Dict[str, Any]]
    redacted_text: str
    types_detected: str = ""
    max_risk: str = ""

class GuardianEngine:
    def __init__(self, use_ner: bool = True, ml_model: Optional[TextClassifier] = None):
        self.detector = HybridDetector(use_ner=use_ner)
        self.ml_model = ml_model

    def analyze(self, text: str, redact: bool = True) -> Decision:
        audit, redacted = audit_record(text, self.detector)

        if audit:
            types = sorted({a.get("tipo","") for a in audit if a.get("tipo")})
            risk_order = {"CRÍTICO":4,"ALTO":3,"MÉDIO":2,"BAIXO":1}
            max_risk = max((a.get("risco","") for a in audit), key=lambda r: risk_order.get(r,0))
            return Decision(
                True,
                "REGRAS/NER: achados detectados",
                len(audit),
                audit,
                redacted if redact else text,
                "; ".join(types),
                max_risk
            )

        if self.ml_model is not None:
            pred = self.ml_model.predict([text])[0]
            if pred == 1:
                return Decision(True, "ML: backstop classificou como positivo", 0, [], redacted if redact else text)

        return Decision(False, "NEGATIVO: nenhum sinal estruturado + ML negativo/ausente", 0, [], text)
