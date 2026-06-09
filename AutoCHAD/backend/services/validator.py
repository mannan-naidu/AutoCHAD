"""
validator.py
────────────────────────────────────────────────────────────────────
Pre-render validation engine.

Validates the process graph against knowledge-base rules:
  • System type consistency  (no tank in pump-only, etc.)
  • Required components present
  • Forbidden components absent
  • Edge connectivity (no orphan nodes)
  • Tag uniqueness (no duplicate tags)

Usage
─────
    errors = Validator.validate(schema, system_type)
    if errors:
        raise ValueError("\\n".join(errors))
"""

from typing import List, Dict
from models.schema import EngineeringSchema
from services.knowledge_base import EQUIPMENT_RULES, get_rule


class Validator:

    # ── Public API ────────────────────────────────────────────────
    @staticmethod
    def validate(schema: EngineeringSchema, system_type: str) -> List[str]:
        """
        Run all validations; return list of error strings.
        Empty list = diagram is valid.
        """
        errors: List[str] = []
        errors += Validator._check_system_type_consistency(schema, system_type)
        errors += Validator._check_required_components(schema, system_type)
        errors += Validator._check_forbidden_components(schema, system_type)
        errors += Validator._check_connectivity(schema)
        errors += Validator._check_tag_uniqueness(schema)
        return errors

    @staticmethod
    def validate_and_warn(schema: EngineeringSchema, system_type: str) -> None:
        """Run validation; print warnings but do NOT raise."""
        errors = Validator.validate(schema, system_type)
        if errors:
            for e in errors:
                print(f"[Validator] WARNING: {e}")

    # ── Internal checks ───────────────────────────────────────────
    @staticmethod
    def _check_system_type_consistency(schema, system_type: str) -> List[str]:
        errors = []
        node_types = {n.type for n in schema.nodes}
        has_tank = "tank" in node_types
        has_pump = "pump" in node_types

        if system_type == "pump_only":
            if has_tank:
                errors.append(
                    f"[system_type=pump_only] Unexpected 'tank' nodes found. "
                    f"A pump-only system must NOT contain tanks."
                )
        elif system_type in ("storage", "cip", "tank_only"):
            if has_pump:
                errors.append(
                    f"[system_type={system_type}] Unexpected 'pump' nodes found. "
                    f"A tank-only system must NOT contain pumps."
                )
        elif system_type == "transfer":
            if not has_tank:
                errors.append(
                    "[system_type=transfer] Missing 'tank' node. "
                    "A transfer system requires at least one vessel."
                )
            if not has_pump:
                errors.append(
                    "[system_type=transfer] Missing 'pump' node. "
                    "A transfer system requires at least one pump."
                )

        return errors

    @staticmethod
    def _check_required_components(schema, system_type: str) -> List[str]:
        """Check that required accessories are present based on system type rule."""
        errors = []
        rule = get_rule(system_type)
        node_ids = {n.id for n in schema.nodes}
        subtypes  = {n.attributes.get("subtype","").lower() for n in schema.nodes}
        node_types = {n.type for n in schema.nodes}

        for req in rule.get("requires", []):
            # Map requirement name to check
            if req == "tank"  and "tank"  not in node_types:
                errors.append(f"[{system_type}] Missing required component: tank")
            elif req == "pump" and "pump" not in node_types:
                errors.append(f"[{system_type}] Missing required component: pump")
            elif req in ("suction_valve","inlet_valve"):
                if not any(s in ("suction","inlet") for s in subtypes):
                    errors.append(f"[{system_type}] Missing suction/inlet valve")
            elif req in ("discharge_valve","outlet_valve"):
                if not any(s in ("discharge","outlet") for s in subtypes):
                    errors.append(f"[{system_type}] Missing discharge/outlet valve")
            elif req == "drain_valve":
                if "drain" not in subtypes:
                    errors.append(f"[{system_type}] Missing drain valve")
            elif req == "vent":
                if "vent" not in node_types:
                    errors.append(f"[{system_type}] Missing atmospheric vent")
        return errors

    @staticmethod
    def _check_forbidden_components(schema, system_type: str) -> List[str]:
        """Check that forbidden components are absent."""
        errors = []
        rule = get_rule(system_type)
        node_types = {n.type for n in schema.nodes}
        for forbidden in rule.get("forbidden", []):
            if forbidden in node_types:
                errors.append(
                    f"[{system_type}] Forbidden component '{forbidden}' detected. "
                    f"This should not appear in a {system_type} diagram."
                )
        return errors

    @staticmethod
    def _check_connectivity(schema) -> List[str]:
        """Ensure no completely orphaned nodes (no edges at all for multi-node graphs)."""
        errors = []
        if len(schema.nodes) <= 1:
            return errors

        connected = set()
        for e in schema.edges:
            connected.add(e.from_id)
            connected.add(e.to_id)

        # Boundary nodes and isolated instruments occasionally have no edges — OK
        # Report only non-instrument orphans
        skipped_types = {"boundary", "sensor"}
        for node in schema.nodes:
            if node.type in skipped_types:
                continue
            if node.id not in connected:
                errors.append(
                    f"Orphan node '{node.id}' ({node.type}) has no edges. "
                    f"Check topology builder."
                )
        return errors

    @staticmethod
    def _check_tag_uniqueness(schema) -> List[str]:
        """Detect duplicate ISA tags."""
        errors = []
        tags: Dict[str, List[str]] = {}
        for node in schema.nodes:
            tag = node.attributes.get("tag")
            if tag:
                tags.setdefault(tag, []).append(node.id)
        for tag, node_ids in tags.items():
            if len(node_ids) > 1:
                errors.append(
                    f"Duplicate tag '{tag}' on nodes: {node_ids}. "
                    f"All tags must be unique."
                )
        return errors
