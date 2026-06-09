"""
knowledge_base.py
────────────────────────────────────────────────────────────────────
Formal engineering knowledge base for P&ID generation.

This is the SINGLE SOURCE OF TRUTH for:
  • Equipment rules (required, optional, forbidden components)
  • Port definitions per equipment type
  • Component label/description strings
  • Tag-prefix conventions
  • Zone assignments
  • Theme color palettes

The KnowledgeEngine and Validator consume this — they do NOT contain
inline rule definitions. Any new equipment type is added HERE only.

Extensibility
─────────────
To add a new equipment type (e.g. heat_exchanger, compressor):
  1. Add an entry to EQUIPMENT_RULES
  2. Add its tag prefix to TAG_PREFIXES
  3. Add its description to COMPONENT_LABELS
  4. Add its port offsets to cad_service PORT_OFFSETS
  Everything else (layout, rendering, tagging) is automatic.
"""

from typing import Dict, Any, List


# ════════════════════════════════════════════════════════════════════
# Equipment rules
# ════════════════════════════════════════════════════════════════════

EQUIPMENT_RULES: Dict[str, Dict[str, Any]] = {

    "pump": {
        "label":       "Rotary Lobe Pump",
        "zone":        "main",
        "requires":    ["suction_valve", "discharge_valve"],
        "optional":    ["nrv", "bypass_valve", "strainer", "filter",
                        "pi_indicator", "fi_indicator"],
        "forbidden":   ["tank", "spray_ball", "psv",
                        "drain_valve", "vent"],
        "ports":       ["SUCTION", "DISCHARGE", "PI_PORT"],
        "min_count":   1,
        "max_count":   4,
    },

    "tank": {
        "label":       "Process Vessel",
        "zone":        "vessel",
        "requires":    ["inlet_valve", "outlet_valve", "drain_valve", "vent"],
        "optional":    ["psv", "spray_ball", "cip_supply_valve", "lt", "tt"],
        "forbidden":   ["pump", "nrv"],
        "ports":       ["INLET", "OUTLET", "VENT", "CIP",
                        "PSV", "DRAIN", "LT", "TT", "PI_PORT"],
        "min_count":   1,
        "max_count":   8,
    },

    "transfer": {
        "label":       "Transfer System",
        "zone":        "combined",
        "requires":    ["tank", "pump", "inlet_valve", "outlet_valve",
                        "suction_valve", "discharge_valve", "nrv"],
        "optional":    ["bypass_valve", "recirculation_valve",
                        "spray_ball", "cip_supply_valve", "lt", "tt",
                        "pi_indicator"],
        "forbidden":   [],
        "ports":       [],
        "min_count":   0,
        "max_count":   0,
    },

    "filter": {
        "label":       "In-line Filter / Strainer",
        "zone":        "main",
        "requires":    [],
        "optional":    [],
        "forbidden":   [],
        "ports":       ["IN", "OUT"],
        "min_count":   0,
        "max_count":   2,
    },

    "heat_exchanger": {
        "label":       "Heat Exchanger",
        "zone":        "main",
        "requires":    ["inlet_valve", "outlet_valve"],
        "optional":    ["ti_indicator", "pi_indicator"],
        "forbidden":   [],
        "ports":       ["IN", "OUT", "TI_PORT", "PI_PORT"],
        "min_count":   0,
        "max_count":   2,
    },

    "compressor": {
        "label":       "Compressor",
        "zone":        "main",
        "requires":    ["suction_valve", "discharge_valve", "nrv"],
        "optional":    ["pi_indicator", "fi_indicator", "bypass_valve"],
        "forbidden":   ["tank"],
        "ports":       ["SUCTION", "DISCHARGE", "PI_PORT"],
        "min_count":   0,
        "max_count":   2,
    },

    # ── Sub-components (used in 'requires'/'optional' lists, not as primary eq) ──

    "valve": {
        "label":    "Isolation Valve",
        "zone":     "main",
        "requires": [], "optional": [], "forbidden": [],
        "ports":    ["IN", "OUT"],
        "min_count": 0, "max_count": 20,
    },
    "relief_valve": {
        "label":    "Pressure Safety Valve",
        "zone":     "safety",
        "requires": [], "optional": [], "forbidden": [],
        "ports":    ["IN", "OUT"],
        "min_count": 0, "max_count": 4,
    },
    "sensor": {
        "label":    "Process Instrument",
        "zone":     "instrument",
        "requires": [], "optional": [], "forbidden": [],
        "ports":    ["CONNECTION"],
        "min_count": 0, "max_count": 30,
    },
    "spray_ball": {
        "label":    "CIP Spray Ball",
        "zone":     "utility",
        "requires": [], "optional": [], "forbidden": [],
        "ports":    ["IN"],
        "min_count": 0, "max_count": 4,
    },
    "vent": {
        "label":    "Atmospheric Vent",
        "zone":     "utility",
        "requires": [], "optional": [], "forbidden": [],
        "ports":    ["IN"],
        "min_count": 0, "max_count": 4,
    },
    "boundary": {
        "label":    "Process Boundary",
        "zone":     "main",
        "requires": [], "optional": [], "forbidden": [],
        "ports":    ["OUT"],
        "min_count": 0, "max_count": 4,
    },
}


# ════════════════════════════════════════════════════════════════════
# Component labels (tag subtype → human readable name)
# ════════════════════════════════════════════════════════════════════

COMPONENT_LABELS: Dict[str, str] = {
    # Valve subtypes
    "suction":       "Suction Valve",
    "discharge":     "Discharge Valve",
    "inlet":         "Inlet Valve",
    "outlet":        "Outlet Valve",
    "drain":         "Drain Valve",
    "nrv":           "Non-Return Valve",
    "bypass":        "Bypass Valve",
    "recirculation": "Recirculation Valve",
    "CIP":           "CIP Supply Valve",
    "cip":           "CIP Supply Valve",
    # Instruments
    "PI":  "Pressure Indicator",
    "PT":  "Pressure Transmitter",
    "FI":  "Flow Indicator",
    "FT":  "Flow Transmitter",
    "LI":  "Level Indicator",
    "LT":  "Level Transmitter",
    "TI":  "Temperature Indicator",
    "TT":  "Temperature Transmitter",
    # Equipment
    "pump":         "Rotary Lobe Pump",
    "centrifugal":  "Centrifugal Pump",
    "tank":         "Process Vessel",
    "filter":       "In-line Filter",
    "heat_exchanger":"Heat Exchanger",
    "compressor":   "Compressor",
    "spray_ball":   "CIP Spray Ball",
    "vent":         "Atmospheric Vent",
    "relief_valve": "Pressure Safety Valve",
    "boundary":     "Boundary",
}


# ════════════════════════════════════════════════════════════════════
# Tag prefix table (equipment type → ISA/IEC tag prefix)
# ════════════════════════════════════════════════════════════════════

TAG_PREFIXES: Dict[str, str] = {
    "pump":           "P",
    "tank":           "T",
    "valve":          "V",
    "relief_valve":   "PSV",
    "filter":         "FLT",
    "heat_exchanger": "HX",
    "compressor":     "C",
    "spray_ball":     "SB",
    "vent":           "VT",
    "boundary":       "",
    # Instrument sub-types (sensor overridden by subtype)
    "sensor":         "XI",
}

SENSOR_TAG_PREFIXES: Dict[str, str] = {
    "PI": "PI", "PT": "PT",
    "FI": "FI", "FT": "FT",
    "LI": "LI", "LT": "LT",
    "TI": "TI", "TT": "TT",
    "XI": "XI",
}


# ════════════════════════════════════════════════════════════════════
# Zone → Y position mapping (read by LayoutEngine)
# ════════════════════════════════════════════════════════════════════

ZONE_Y: Dict[str, float] = {
    "top":        5000.0,    # PSV, vent, SB, CIP supply — top of vessel
    "vessel":     2800.0,    # tanks
    "main":          0.0,    # pumps, inline valves
    "bot":       -2200.0,    # drain valves
    "instrument":  5000.0,   # LT, TT, PI — grouped with top
    "utility":   -2200.0,    # generic utility below main line
    "safety":    -2200.0,    # PSV at fixed position (also top for vessel)
    "recirc":    -4500.0,    # recirculation return rail
}


# ════════════════════════════════════════════════════════════════════
# Theme palettes
# ════════════════════════════════════════════════════════════════════

THEMES: Dict[str, Dict[str, int]] = {
    "dark": {
        "pipe":         7,    # white
        "utility_pipe": 3,    # green
        "instrument":   5,    # blue
        "safety":       1,    # red
        "equipment":    7,    # white
        "pump":         4,    # cyan
        "valve":        2,    # yellow
        "text_primary": 2,    # yellow
        "text_dim":     8,    # grey
        "title":        6,    # magenta
        "boundary":     8,    # grey
        "guide":        8,    # grey
    },
    "light": {
        "pipe":         0,    # black
        "utility_pipe": 2,    # green (darker aci)
        "instrument":   5,    # blue
        "safety":       1,    # red
        "equipment":    0,    # black
        "pump":         4,    # cyan
        "valve":        0,    # black
        "text_primary": 0,    # black
        "text_dim":     8,    # grey
        "title":        6,    # magenta
        "boundary":     8,    # grey
        "guide":        9,    # light grey
    },
}

DEFAULT_THEME = "dark"


# ════════════════════════════════════════════════════════════════════
# DXF layer definitions
# ════════════════════════════════════════════════════════════════════

DXF_LAYERS: Dict[str, Dict[str, Any]] = {
    "PROCESS":     {"color": 7,  "lineweight": 60,  "linetype": "CONTINUOUS"},
    "INSTRUMENT":  {"color": 5,  "lineweight": 18,  "linetype": "CONTINUOUS"},
    "UTILITY":     {"color": 3,  "lineweight": 28,  "linetype": "DASHED"},
    "SAFETY":      {"color": 1,  "lineweight": 35,  "linetype": "CONTINUOUS"},
    "ANNOTATION":  {"color": 8,  "lineweight": 13,  "linetype": "CONTINUOUS"},
    "EQUIPMENT":   {"color": 7,  "lineweight": 50,  "linetype": "CONTINUOUS"},
    "BOUNDARY":    {"color": 8,  "lineweight": 20,  "linetype": "CONTINUOUS"},
    "GUIDE":       {"color": 9,  "lineweight":  9,  "linetype": "CONTINUOUS"},
}

# Relation → DXF layer mapping
RELATION_LAYER: Dict[str, str] = {
    "inline":     "PROCESS",
    "branch":     "PROCESS",
    "loop":       "PROCESS",
    "utility":    "UTILITY",
    "drain":      "UTILITY",
    "instrument": "INSTRUMENT",
}

# Node type → DXF layer mapping
NODE_LAYER: Dict[str, str] = {
    "pump":         "EQUIPMENT",
    "tank":         "EQUIPMENT",
    "valve":        "PROCESS",
    "relief_valve": "SAFETY",
    "sensor":       "INSTRUMENT",
    "spray_ball":   "UTILITY",
    "vent":         "UTILITY",
    "filter":       "PROCESS",
    "boundary":     "BOUNDARY",
}
DEFAULT_NODE_LAYER = "EQUIPMENT"


# ════════════════════════════════════════════════════════════════════
# Helper: look up rule for an equipment type
# ════════════════════════════════════════════════════════════════════

def get_rule(equipment_type: str) -> Dict[str, Any]:
    """Return the rule entry for equipment_type, defaulting to empty rule."""
    return EQUIPMENT_RULES.get(equipment_type.lower(), {
        "label": equipment_type, "zone": "main",
        "requires": [], "optional": [], "forbidden": [],
        "ports": [], "min_count": 0, "max_count": 99,
    })


def get_label(node_type: str, subtype: str = "") -> str:
    """Return human-readable label for a component."""
    if subtype and subtype in COMPONENT_LABELS:
        return COMPONENT_LABELS[subtype]
    if subtype.upper() in COMPONENT_LABELS:
        return COMPONENT_LABELS[subtype.upper()]
    return COMPONENT_LABELS.get(node_type, node_type.replace("_"," ").title())


def get_theme(name: str = DEFAULT_THEME) -> Dict[str, int]:
    """Return a color palette by theme name."""
    return THEMES.get(name, THEMES[DEFAULT_THEME])
