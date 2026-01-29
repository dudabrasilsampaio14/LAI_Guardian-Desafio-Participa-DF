from __future__ import annotations
"""Detector híbrido: regras + (opcionalmente) NER. A intenção é identificar PII sem confundir com IDs administrativos."""
import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple

from .patterns import (
    CPF, EMAIL, CEP, CARD, RG_CTX, PHONE, ADDRESS,
    PROCESSO_SEI, PROCESSO_CNJ, PROTOCOLO_NUM, KW_PROCESSO
)
from .validators import validate_cpf_mod11, only_digits

# Remove SEI/CNJ shapes from a text view used for phone scanning to avoid confusion
SEI_OR_CNJ = re.compile(r"(\b\d{4,6}-\d{4,10}/\d{4}-\d{2}\b|\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b)")
YEARS = set(str(y) for y in range(1900, 2101))

IDISH_PUNCT = re.compile(r"[/.]")

RISK_ORDER = {"CRÍTICO": 4, "ALTO": 3, "MÉDIO": 2, "BAIXO": 1}
DEFAULT_RISK = {
    "CPF": "ALTO",
    "RG": "MÉDIO",
    "E-MAIL": "MÉDIO",
    "TELEFONE": "MÉDIO",
    "CEP": "MÉDIO",
    "ENDEREÇO": "BAIXO",
    "CARTÃO": "CRÍTICO",
    "NOME_PESSOA": "BAIXO",
    "PROCESSO_SEI": "BAIXO",
    "PROCESSO_CNJ": "BAIXO",
    "PROTOCOLO": "BAIXO",
}

@dataclass
class Finding:
    tipo: str
    valor: str
    risco: str
    start: int
    end: int
    detalhes: Optional[Dict[str, Any]] = None


class HybridDetector:
    def __init__(self, use_ner: bool = True):
        self.use_ner = use_ner
        self._nlp = None
        self._ner_ready = False
        if use_ner:
            self._try_init_spacy()

    def _try_init_spacy(self):
        try:
            import spacy
            try:
                self._nlp = spacy.load("pt_core_news_sm")
            except Exception:
                self._nlp = None
            self._ner_ready = self._nlp is not None
        except Exception:
            self._nlp = None
            self._ner_ready = False

    def detect(self, text: str) -> List[Finding]:
        if not isinstance(text, str):
            return []

        findings: List[Finding] = []
        t = text

        # Primeiro tratamos identificadores administrativos (SEI/CNJ/protocolo).
        # Eles aparecem muito em pedido LAI e não devem virar 'telefone' por engano.
        # --- Administrative identifiers ---
        for m in PROCESSO_SEI.finditer(t):
            findings.append(Finding("PROCESSO_SEI", m.group(0), DEFAULT_RISK["PROCESSO_SEI"], m.start(0), m.end(0)))
        for m in PROCESSO_CNJ.finditer(t):
            findings.append(Finding("PROCESSO_CNJ", m.group(0), DEFAULT_RISK["PROCESSO_CNJ"], m.start(0), m.end(0)))
        for m in PROTOCOLO_NUM.finditer(t):
            window_start = max(0, m.start(0) - 20)
            window_end = min(len(t), m.end(0) + 20)
            if KW_PROCESSO.search(t[window_start:window_end]):
                findings.append(Finding("PROTOCOLO", m.group(0), DEFAULT_RISK["PROTOCOLO"], m.start(0), m.end(0)))

        # --- CPF ---
        for m in CPF.finditer(t):
            raw = m.group(1)
            if validate_cpf_mod11(raw):
                findings.append(Finding("CPF", raw, DEFAULT_RISK["CPF"], m.start(1), m.end(1)))

        # --- RG contextual ---
        for m in RG_CTX.finditer(t):
            raw = m.group(1)
            findings.append(Finding("RG", raw, DEFAULT_RISK["RG"], m.start(1), m.end(1)))

        # --- Endereço ---
        for m in ADDRESS.finditer(t):
            raw = m.group(1)
            left = raw.split(",")[0].strip()
            if len(left) >= 6:
                findings.append(Finding("ENDEREÇO", raw, DEFAULT_RISK["ENDEREÇO"], m.start(1), m.end(1)))

        # CEP
        for m in CEP.finditer(t):
            findings.append(Finding("CEP", m.group(0), DEFAULT_RISK["CEP"], m.start(0), m.end(0)))

        # Email
        for m in EMAIL.finditer(t):
            findings.append(Finding("E-MAIL", m.group(0), DEFAULT_RISK["E-MAIL"], m.start(0), m.end(0)))

        # Telefone é uma fonte clássica de falso positivo (datas, processos, números secos).
        # Aqui a gente varre com filtro extra para evitar confusão.
        # --- Telefone com proteção anti-processo ---
        t_for_phone = SEI_OR_CNJ.sub(" ", t)
        for m in PHONE.finditer(t_for_phone):
            raw = m.group(0)
            digits = only_digits(raw)
            if len(digits) < 8:
                continue

            if len(digits) == 8 and digits[:4] in YEARS:
                continue

            if len(digits) == 8 and ("-" not in raw and "(" not in raw and ")" not in raw and " " not in raw):
                continue

            if IDISH_PUNCT.search(raw):
                continue

            findings.append(Finding("TELEFONE", raw, DEFAULT_RISK["TELEFONE"], m.start(0), m.end(0)))

        # Cartão
        for m in CARD.finditer(t):
            findings.append(Finding("CARTÃO", m.group(0), DEFAULT_RISK["CARTÃO"], m.start(0), m.end(0)))

        # NER é opcional: ajuda em nomes de pessoas, mas não pode atrapalhar o básico.
        # Se o modelo não estiver instalado, seguimos só com regras.
        # --- NER (opcional) ---
        if self._ner_ready:
            doc = self._nlp(t)
            blacklist = {
                "relatório","governo","distrito","secretaria","diário","ministério",
                "pedido","nota","fiscal","auditoria","processo","protocolo","licitação"
            }
            for ent in doc.ents:
                if ent.label_ == "PER" and " " in ent.text and len(ent.text.strip()) > 3:
                    low = ent.text.lower()
                    if any(b in low for b in blacklist):
                        continue
                    findings.append(Finding("NOME_PESSOA", ent.text, DEFAULT_RISK["NOME_PESSOA"], ent.start_char, ent.end_char))

        findings.sort(key=lambda f: (f.start, f.end, f.tipo))
        dedup, seen = [], set()
        for f in findings:
            key = (f.tipo, f.start, f.end, f.valor)
            if key not in seen:
                seen.add(key)
                dedup.append(f)
        return dedup

    @staticmethod
    def summarize(findings: List[Finding]) -> Tuple[str, str, int]:
        if not findings:
            return ("", "", 0)
        types = sorted({f.tipo for f in findings})
        max_risk = max((f.risco for f in findings), key=lambda r: RISK_ORDER.get(r, 0))
        return ("; ".join(types), max_risk, len(findings))
