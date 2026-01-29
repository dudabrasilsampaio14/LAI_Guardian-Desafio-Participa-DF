"""Padrões (regex) usados na detecção. Aqui ficam apenas os formatos; a lógica de decisão fica no detector."""
import re

# --- PII patterns ---
CPF = re.compile(r"(?:\D|^)(\d{3}\.?\d{3}\.?\d{3}-?\d{2})(?:\D|$)")
EMAIL = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")
CEP = re.compile(r"\b\d{5}-?\d{3}\b")
CARD = re.compile(r"\b(?:\d{4}[-\s]){3}\d{4}\b")
RG_CTX = re.compile(r"(?:RG|Identidade|Reg\.?\s*Geral)\s*[:\-]?\s*(\d{1,2}\.?\d{3}\.?\d{3}-?[\dX])", re.IGNORECASE)

# Phone: permissive; anti-false-positive happens in detector.
PHONE = re.compile(r"(?:\(?\d{2}\)?\s?)?(?:9\d{4}|\d{4})[-.\s]?\d{4}")

# Address heuristic
ADDRESS = re.compile(r"([A-ZÀ-Úa-zà-ú0-9\s\.]{6,},\s*\d+(?:[/-]\d+)?(?:\s*[A-Za-z]+)?)")

# --- Administrative identifiers (NOT PII by default) ---
# SEI-like: flexible, e.g. 00015-01009853/2026-01
PROCESSO_SEI = re.compile(r"\b\d{4,6}-\d{4,10}/\d{4}-\d{2}\b")

# CNJ: 0000000-00.0000.0.00.0000
PROCESSO_CNJ = re.compile(r"\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b")

# Broad protocol/identifier (context-limited in detector)
PROTOCOLO_NUM = re.compile(r"\b(?:\d{4,}[-/]\d{2,4}|\d{4,}/\d{4}(?:-\d{2})?)\b")

# Keywords for contextual disambiguation
KW_PROCESSO = re.compile(r"\b(sei|processo|protocolo|autos|procedimento|n[ºo]\.?|número)\b", re.IGNORECASE)
