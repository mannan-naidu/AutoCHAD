"""
rule_engine.py
──────────────
Validates and normalises the EngineeringSchema after KnowledgeEngine injection.

Responsibilities
────────────────
1. Normalise node types (lobe_pump → pump, agitator_tank → tank, etc.)
2. Assign roles from type if not set
3. Assign / preserve industrial tags
4. Strip dangling edges (edges whose endpoints don't exist in node set)
5. Enforce ASME BPE / GMP material & fitting constraints
"""

from models.schema import EngineeringSchema, NodeSchema, EdgeSchema

# ── Type normalisation map ─────────────────────────────────────────
TYPE_NORM = {
    "lobe_pump": "pump", "centrifugal_pump": "pump", "gear_pump": "pump",
    "agitator_tank": "tank", "storage_tank": "tank", "vessel": "tank",
    "reactor": "tank", "bioreactor": "tank",
    "gate_valve": "valve", "ball_valve": "valve", "butterfly_valve": "valve",
    "check_valve": "valve", "nrv": "valve",
    "pressure_indicator": "sensor", "level_transmitter": "sensor",
    "temperature_sensor": "sensor", "flow_meter": "sensor",
    "psv": "relief_valve", "prv": "relief_valve",
    "strainer": "filter",
}

# ── Role assignment from final type ───────────────────────────────
TYPE_ROLE = {
    "pump":         "process",
    "tank":         "source",
    "valve":        "control",
    "sensor":       "instrument",
    "spray_ball":   "utility",
    "filter":       "utility",
    "vent":         "utility",
    "relief_valve": "safety",
}

# ── Tag prefix from type ───────────────────────────────────────────
TAG_PFX = {
    "pump":         "P",
    "tank":         "T",
    "valve":        "V",
    "relief_valve": "PSV",
    "spray_ball":   "SB",
    "filter":       "FLT",
    "vent":         "VT",
}

SENSOR_PFX = {"LT": "LT", "TT": "TT", "PI": "PI", "FI": "FI",
              "LI": "LI", "TI": "TI", "PT": "PT"}


class RuleEngine:

    @staticmethod
    def apply_rules(schema: EngineeringSchema) -> EngineeringSchema:
        nodes = {n.id: n for n in schema.nodes}
        edges = schema.edges

        # Tag counters (start at 100 so first tag is T-101 etc.)
        counters = {k: 100 for k in TAG_PFX}
        s_counters = {k: 100 for k in SENSOR_PFX}

        for node in nodes.values():
            # ── Normalise type ────────────────────────────────────────
            raw = node.type.lower()
            for pattern, norm in TYPE_NORM.items():
                if pattern in raw:
                    node.type = norm
                    break

            # ── Assign role ───────────────────────────────────────────
            node.role = TYPE_ROLE.get(node.type, node.role)

            # ── Assign tag if not already set by KnowledgeEngine ──────
            if node.attributes.get("tag"):
                continue

            if not node.attributes:
                node.attributes = {}

            if node.type == "sensor":
                sub = node.attributes.get("subtype", "PI").upper()
                pfx = SENSOR_PFX.get(sub, "XI")
                s_counters[sub] = s_counters.get(sub, 100) + 1
                node.attributes["tag"] = f"{pfx}-{s_counters[sub]}"
            elif node.type in TAG_PFX:
                pfx = TAG_PFX[node.type]
                counters[node.type] = counters.get(node.type, 100) + 1
                node.attributes["tag"] = f"{pfx}-{counters[node.type]}"

        # ── Strip dangling / self-loop edges ──────────────────────────
        valid_edges = [
            e for e in edges
            if e.from_id != e.to_id
            and e.from_id in nodes
            and e.to_id   in nodes
        ]

        # ── Remove nodes not connected to anything (multi-node graph) ─
        if len(nodes) > 1:
            connected = set()
            for e in valid_edges:
                connected.add(e.from_id)
                connected.add(e.to_id)
            nodes = {nid: n for nid, n in nodes.items() if nid in connected}

        schema.nodes = list(nodes.values())
        schema.edges = valid_edges
        return schema

    @staticmethod
    def enforce_rules(schema: EngineeringSchema) -> EngineeringSchema:
        """ASME BPE / cGMP compliance."""
        if "316" not in schema.material.upper():
            schema.material = "SS316L"

        for nozzle in schema.nozzles:
            conn = nozzle.connection.upper()
            if "TC" not in conn and "TRI-CLAMP" not in conn:
                nozzle.connection = "TC"

        if schema.equipment.dimensions.height <= 0:
            schema.equipment.dimensions.height = 1000.0
        if schema.equipment.dimensions.diameter <= 0:
            schema.equipment.dimensions.diameter = schema.equipment.dimensions.height * 0.5
        if schema.equipment.geometry.bottom.lower() == "flat":
            schema.equipment.geometry.bottom = "dished"

        return schema
