"""
debug_inference.py
──────────────────
5-scenario test:
  1. Pump-only       (DARK theme)
  2. Tank-only / CIP (DARK theme)
  3. Transfer system (DARK theme)
  4. Pump recirc     (DARK theme)
  5. Transfer system (LIGHT theme) — same URS, different theme
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from services.schema_builder import SchemaBuilder
from services.process_interpreter import ProcessInterpreter
from services.knowledge_engine import KnowledgeEngine
from services.dxf_service import DXFService
from services.validator import Validator


def _schema_json(equip_type, nodes):
    return (
        '{"equipment": {"type": "%s", "capacity": 2000,'
        '"geometry": {"shape":"cylindrical","bottom":"dished","top":"dished"},'
        '"dimensions": {"height": 2000, "diameter": 1000}},'
        '"nodes": %s, "edges": [], "nozzles": [], "material": "SS316L"}'
        % (equip_type, nodes)
    )


CASES = [
    {
        "name":  "PUMP-ONLY       (DARK, no tank)",
        "theme": "dark",
        "urs":   ("Centrifugal pump for product transfer. "
                  "Include isolation valves on suction and discharge. "
                  "Add non-return valve after pump. Include pressure indicator. "
                  "Bypass valve required."),
        "schema": _schema_json(
            "centrifugal_pump",
            '[{"id":"P_001","type":"centrifugal_pump"}]'),
    },
    {
        "name":  "TANK-ONLY / CIP (DARK)",
        "theme": "dark",
        "urs":   ("2000L stainless steel CIP vessel for buffer storage. "
                  "Level transmitter, temperature transmitter required. "
                  "CIP spray ball system. PSV and atmospheric vent on top. "
                  "Drain valve on vessel bottom."),
        "schema": _schema_json(
            "cip_tank",
            '[{"id":"T_001","type":"cip_tank"}]'),
    },
    {
        "name":  "TRANSFER SYSTEM (DARK, tank + pump)",
        "theme": "dark",
        "urs":   ("Intermediate bulk transfer system. Product is fed from "
                  "mixing vessel T-101 via lobe pump P-101 to filling line. "
                  "Include inlet and outlet isolation valves, non-return valve, "
                  "CIP spray ball, level transmitter, temperature transmitter, "
                  "pressure indicator and PSV. Drain provision required."),
        "schema": _schema_json(
            "lobe_pump",
            '[{"id":"P_001","type":"lobe_pump"},{"id":"T_001","type":"tank"}]'),
    },
    {
        "name":  "PUMP RECIRC     (DARK, recirculation loop)",
        "theme": "dark",
        "urs":   ("Recirculation loop for in-process hold. Centrifugal pump "
                  "with bypass valve and return line. NRV on discharge. "
                  "Flow indicator and pressure indicator required."),
        "schema": _schema_json(
            "centrifugal_pump",
            '[{"id":"P_001","type":"centrifugal_pump"}]'),
    },
    {
        "name":  "TRANSFER SYSTEM (LIGHT theme)",
        "theme": "light",
        "urs":   ("Pharmaceutical grade lobe pump transfer system. "
                  "Source vessel T-101 feeds filling station via P-101. "
                  "CIP provision, NRV, LT, TT, PI. PSV and vent on vessel. "
                  "Drain on vessel bottom. All wetted parts SS316L."),
        "schema": _schema_json(
            "lobe_pump",
            '[{"id":"P_001","type":"lobe_pump"},{"id":"T_001","type":"tank"}]'),
    },
]


def run(case: dict):
    print(f"\n{'=' * 70}")
    print(f"  TEST : {case['name']}")
    print(f"  THEME: {case['theme'].upper()}")
    print(f"  URS  : {case['urs'][:80]}...")
    print('=' * 70)
    try:
        raw    = SchemaBuilder.build_from_json(case["schema"])
        raw.attributes["theme"] = case["theme"]
        intent = ProcessInterpreter.interpret(case["urs"])
        schema = KnowledgeEngine.build_process_graph(raw, intent)

        # Pre-render validation report
        system_type = intent.get("system_type","generic")
        errs = Validator.validate(schema, system_type)
        if errs:
            for e in errs: print(f"  [Validator] {e}")
        else:
            print("  [Validator] OK - no violations")

        path = DXFService.generate_dxf(schema, theme=case["theme"])

        ntypes = [f"{n.type}:{n.attributes.get('tag','?')}" for n in schema.nodes]
        print(f"  system_type : {intent.get('system_type')}")
        print(f"  Nodes ({len(schema.nodes)}) : {', '.join(ntypes)}")
        etypes = [(e.from_id[:8], e.to_id[:8], e.relation) for e in schema.edges]
        print(f"  Edges ({len(schema.edges)}) : {etypes}")
        print(f"  OUTPUT      : {path}")
    except Exception:
        import traceback
        print("  FAILED:")
        traceback.print_exc()


if __name__ == "__main__":
    for case in CASES:
        run(case)
    print("\nAll tests complete.")
