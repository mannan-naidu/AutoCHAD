"""
process_interpreter.py
──────────────────────
Extracts semantic process intent from the raw URS text.
Returns a structured intent dict that the Knowledge Engine
uses to build the correct P&ID topology dynamically.

Intent keys
-----------
process_type     : str  — "transfer" | "recirculation" | "cip" | "bioreactor" | "generic"
has_recirculation: bool — return loop back to source
has_cip          : bool — CIP branch + spray ball
has_drain        : bool — drain valve + line
has_nrv          : bool — non-return valve on discharge
has_bypass       : bool — pump bypass line
has_filter       : bool — in-line filter / strainer
instruments      : list — ["PI", "FI", "LI", "TI", "TT", "LT"]
main_equipment   : list — ["pump", "tank", "reactor", "heat_exchanger"]
"""

import re
from typing import Dict, Any


# ──────────────────────────────────────────────────────────────────
# Keyword → intent mappings
# ──────────────────────────────────────────────────────────────────

_KEYWORD_FLAGS: Dict[str, str] = {
    # Recirculation
    r"\brecirculat": "has_recirculation",
    r"\brecycle":    "has_recirculation",
    r"\breturn line": "has_recirculation",
    # CIP
    r"\bcip\b":        "has_cip",
    r"\bclean.in.place": "has_cip",
    r"\bspray\s*ball":  "has_cip",
    # Drain
    r"\bdrain\b":      "has_drain",
    r"\bdraining\b":   "has_drain",
    # Non-return valve
    r"\bnrv\b":          "has_nrv",
    r"\bcheck valve":    "has_nrv",
    r"\bnon.return":     "has_nrv",
    # Bypass
    r"\bbypass":         "has_bypass",
    # Filter / Strainer
    r"\bfilter\b":       "has_filter",
    r"\bstrainer\b":     "has_filter",
    r"\bcartridge filter": "has_filter",
}

_INSTRUMENT_KEYWORDS: Dict[str, str] = {
    r"\bpressure\s*(indicator|gauge|transmitter|sensor)": "PI",
    r"\bPI\b":             "PI",
    r"\bflow\s*(indicator|meter|transmitter|sensor)":    "FI",
    r"\bFI\b|\bFT\b":     "FI",
    r"\blevel\s*(indicator|transmitter|sensor)":         "LI",
    r"\bLI\b|\bLT\b":     "LI",
    r"\btemperature\s*(indicator|transmitter|sensor)":   "TI",
    r"\bTI\b|\bTT\b":     "TI",
}

_EQUIPMENT_KEYWORDS: Dict[str, str] = {
    r"\blobe\s*pump|\bcentrifugal\s*pump|\bpump\b":  "pump",
    r"\btank\b|\bvessel\b|\bstorage\b":              "tank",
    r"\breactor\b|\bbioreactor\b":                   "reactor",
    r"\bheat\s*exchanger|\bHX\b":                    "heat_exchanger",
}

_PROCESS_TYPE_PATTERNS: Dict[str, str] = {
    r"\btransfer\b|\btransferring\b":      "transfer",
    r"\brecirculat|\brecycle":             "recirculation",
    r"\bcip\b|\bclean.in.place":           "cip",
    r"\bbioreactor\b|\bferment":           "bioreactor",
}


class ProcessInterpreter:

    @staticmethod
    def interpret(urs_text: str) -> Dict[str, Any]:
        """
        Parse the URS text and return a structured intent dictionary.
        """
        text = urs_text.lower()

        intent: Dict[str, Any] = {
            "process_type":      "generic",
            "system_type":       "generic",   # storage | transfer | cip | recirculation
            "has_recirculation": False,
            "has_cip":           False,
            "has_drain":         False,
            "has_nrv":           False,
            "has_bypass":        False,
            "has_filter":        False,
            "instruments":       [],
            "main_equipment":    [],
        }

        # ── Detect boolean flags ────────────────────────────────────
        for pattern, flag in _KEYWORD_FLAGS.items():
            if re.search(pattern, text, re.IGNORECASE):
                intent[flag] = True

        # ── Detect instruments ──────────────────────────────────────
        seen_instruments = set()
        for pattern, tag in _INSTRUMENT_KEYWORDS.items():
            if re.search(pattern, text, re.IGNORECASE):
                seen_instruments.add(tag)

        # Always include PI for pumps / tanks (minimum instrumentation)
        intent["instruments"] = list(seen_instruments) if seen_instruments else ["PI"]

        # ── Detect equipment ────────────────────────────────────────
        seen_equip = set()
        for pattern, equip in _EQUIPMENT_KEYWORDS.items():
            if re.search(pattern, text, re.IGNORECASE):
                seen_equip.add(equip)
        intent["main_equipment"] = list(seen_equip)

        # ── Detect process type ─────────────────────────────────────
        for pattern, ptype in _PROCESS_TYPE_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                intent["process_type"] = ptype
                break

        # ── Classify system_type ────────────────────────────────────
        # Priority: equipment combination FIRST, then process modifiers
        eq_set   = set(intent["main_equipment"])
        has_pump = "pump" in eq_set
        has_tank = "tank" in eq_set or "reactor" in eq_set

        if has_tank and has_pump:
            # Both tank and pump detected → always a transfer system
            # CIP/NRV/recirculation are *features* of this transfer system
            intent["system_type"] = "transfer"
        elif intent["has_recirculation"] and has_pump:
            intent["system_type"] = "recirculation"
        elif has_tank and intent["has_cip"] and not has_pump:
            intent["system_type"] = "cip"
        elif has_tank:
            intent["system_type"] = "storage"
        elif has_pump:
            intent["system_type"] = "pump_only"
        else:
            # Fallback: derive from process_type keyword
            intent["system_type"] = intent["process_type"]

        print(f"[ProcessInterpreter] intent={intent}")
        return intent
