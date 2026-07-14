from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClassificationResult:
    is_consumable: bool
    category: str | None
    matched_term: str | None


TERMS = {
    "O_RING": ["O-RING", "O RING", "PACKING, PREFORMED"],
    "PACKING": ["PACKING"],
    "GASKET": ["GASKET"],
    "SEAL": ["SEAL"],
    "FILTER": ["FILTER", "ELEMENT, FILTER"],
    "WASHER": ["WASHER"],
    "COTTER_PIN": ["COTTER PIN"],
    "LOCKWIRE": ["LOCKWIRE", "SAFETY WIRE"],
    "ADHESIVE": ["ADHESIVE"],
    "LUBRICANT": ["LUBRICANT", "GREASE", "OIL"],
    "COMPOUND": ["COMPOUND", "SEALANT"],
}


def classify(description: str) -> ClassificationResult:
    normalized = description.upper()

    for category, terms in TERMS.items():
        for term in terms:
            if term in normalized:
                return ClassificationResult(True, category, term)

    return ClassificationResult(False, None, None)
