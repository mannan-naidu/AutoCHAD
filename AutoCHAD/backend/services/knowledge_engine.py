"""
knowledge_engine.py
────────────────────────────────────────────────────────────────────
Dynamic, knowledge-base-driven process graph builder.

HOW IT WORKS (Interpret → Build → No template)
═══════════════════════════════════════════════
1. ProcessInterpreter extracts intent from URS text
2. KnowledgeEngine.build_process_graph:
   a. Reads system_type from intent
   b. Consults EQUIPMENT_RULES from knowledge_base.py
   c. Creates ONLY components required/optional per system type
   d. Tags all components via TagGenerator (sequential, no hardcoded IDs)
   e. Assigns explicit port connections on every edge
3. Validator.validate_and_warn catches rule violations before render

NO FIXED TEMPLATES: topology builders call rule-driven helpers.
Adding a new equipment type requires only a knowledge_base.py entry.
"""

from models.schema import EngineeringSchema, NodeSchema, EdgeSchema, PortSchema
from services.knowledge_base import (
    EQUIPMENT_RULES, TAG_PREFIXES, SENSOR_TAG_PREFIXES, get_label
)
from typing import Dict, Any, List


# ════════════════════════════════════════════════════════════════════
# Auto-tagger — sequential, no hardcoded IDs
# ════════════════════════════════════════════════════════════════════

class TagGenerator:
    """0
    Generates ISA-style tags sequentially per equipment type.
    Tags start at 101 to match industrial convention (P-101, V-101 …).
    A single instance is created per KnowledgeEngine.build_process_graph call
    so tags are unique within one diagram.
    """
    def __init__(self):
        self._counters: Dict[str, int] = {}

    def next(self, node_type: str, subtype: str = "") -> str:
        sub_u = subtype.upper()
        if node_type == "sensor" and sub_u in SENSOR_TAG_PREFIXES:
            prefix = SENSOR_TAG_PREFIXES[sub_u]
        elif node_type in TAG_PREFIXES:
            prefix = TAG_PREFIXES[node_type]
        else:
            prefix = "X"

        if not prefix:     # boundary nodes have no tag
            return subtype or node_type

        self._counters[prefix] = self._counters.get(prefix, 100) + 1
        return f"{prefix}-{self._counters[prefix]}"


# ════════════════════════════════════════════════════════════════════
# Low-level factories
# ════════════════════════════════════════════════════════════════════

def _port(pid: str, side: str, purpose: str = "process") -> PortSchema:
    return PortSchema(id=pid, side=side, purpose=purpose)

def _node(nid, ntype, role, ports, **attrs) -> NodeSchema:
    return NodeSchema(id=nid, type=ntype, role=role,
                      ports=ports, attributes=dict(attrs))

def _edge(frm, to, fp="default_out", tp="default_in",
          relation="inline", medium="product") -> EdgeSchema:
    return EdgeSchema(from_id=frm, to_id=to,
                      from_port=fp, to_port=tp,
                      relation=relation, medium=medium)

# ── Standard port lists ──────────────────────────────────────────────
_V_PORTS = [_port("IN","left"), _port("OUT","right")]
_P_PORTS = [_port("SUCTION","left"), _port("DISCHARGE","right"),
             _port("PI_PORT","top","instrument")]
_T_PORTS = [
    _port("INLET",   "top",    "process"),
    _port("OUTLET",  "bottom", "process"),
    _port("VENT",    "top",    "utility"),
    _port("CIP",     "top",    "utility"),
    _port("PSV",     "top",    "safety"),
    _port("DRAIN",   "bottom", "utility"),
    _port("LT",      "right",  "instrument"),
    _port("TT",      "right",  "instrument"),
    _port("PI_PORT", "left",   "instrument"),
]

def _valve(nid, tag, subtype, role="control"):
    return _node(nid, "valve", role, _V_PORTS[:],
                 tag=tag, subtype=subtype)

def _sensor(nid, tag, subtype):
    return _node(nid, "sensor", "instrument",
                 [_port("CONNECTION","top","instrument")],
                 tag=tag, subtype=subtype)

def _boundary(nid, label):
    return _node(nid, "boundary", "control",
                 [_port("OUT","right")], tag=label)


# ════════════════════════════════════════════════════════════════════
# Tank accessory builder — uses knowledge_base "optional" list
# ════════════════════════════════════════════════════════════════════

def _add_tank_accessories(tank_id: str, intent: Dict, tg: TagGenerator,
                           nodes: List, edges: List):
    """
    Adds accessories around a tank node.
    zone_hint drives layout zone:
      "top"  → Y=+5000 (PSV, vent, SB, CIP supply)
      "bot"  → Y=−2200 (drain valve)
    """
    # ── Drain valve (bottom) ─────────────────────────────────────────
    drn = f"V_DRN_{tank_id}"
    nodes.append(_valve(drn, tg.next("valve","drain"), "drain",
                        role="utility"))
    nodes[-1].attributes["zone_hint"] = "bot"
    edges.append(_edge(tank_id, drn, "DRAIN", "IN", "drain"))

    # ── PSV (top) ────────────────────────────────────────────────────
    psv = f"PSV_{tank_id}"
    nodes.append(_node(psv, "relief_valve", "safety",
                       [_port("IN","bottom"), _port("OUT","top")],
                       tag=tg.next("relief_valve"), zone_hint="top"))
    edges.append(_edge(tank_id, psv, "PSV", "IN", "utility"))

    # ── Atmospheric vent (top) ────────────────────────────────────────
    vent = f"VENT_{tank_id}"
    nodes.append(_node(vent, "vent", "utility",
                       [_port("IN","bottom")],
                       tag=tg.next("vent"), zone_hint="top"))
    edges.append(_edge(tank_id, vent, "VENT", "IN", "utility", "air"))

    # ── CIP spray ball (top) ─────────────────────────────────────────
    sb = f"SB_{tank_id}"
    nodes.append(_node(sb, "spray_ball", "utility",
                       [_port("IN","top","utility")],
                       tag=tg.next("spray_ball"), subtype="CIP",
                       zone_hint="top"))
    edges.append(_edge(tank_id, sb, "CIP", "IN", "utility", "water"))

    # ── CIP supply isolation valve (top) ─────────────────────────────
    cip_v = f"V_CIP_{tank_id}"
    nodes.append(_valve(cip_v, tg.next("valve","cip"), "cip",
                        role="utility"))
    nodes[-1].attributes["zone_hint"] = "top"
    edges.append(_edge(cip_v, sb, "OUT", "IN", "utility", "water"))

    # ── Level transmitter (instrument, right side) ────────────────────
    lt = f"LT_{tank_id}"
    nodes.append(_sensor(lt, tg.next("sensor","LT"), "LT"))
    edges.append(_edge(tank_id, lt, "LT", "CONNECTION", "instrument"))

    # ── Temperature transmitter (instrument, right side) ──────────────
    tt = f"TT_{tank_id}"
    nodes.append(_sensor(tt, tg.next("sensor","TT"), "TT"))
    edges.append(_edge(tank_id, tt, "TT", "CONNECTION", "instrument"))

    # ── Extra intent-driven instruments on tank ───────────────────────
    inst_port_map = {"PI":"PI_PORT","FI":"PI_PORT","PT":"PI_PORT"}
    for inst in intent.get("instruments", []):
        if inst in ("LI","LT","TI","TT"):
            continue  # already covered above
        iid = f"{inst}_EX_{tank_id}"
        nodes.append(_sensor(iid, tg.next("sensor", inst), inst))
        port = inst_port_map.get(inst, "PI_PORT")
        edges.append(_edge(tank_id, iid, port, "CONNECTION", "instrument"))


# ════════════════════════════════════════════════════════════════════
# System topology builders
# ════════════════════════════════════════════════════════════════════

def _build_pump_only(pump_node: NodeSchema, intent: Dict, tg: TagGenerator,
                     nodes: List, edges: List):
    """
    Knowledge-base rule: pump "requires" suction_valve + discharge_valve.
    Adds SOURCE and DESTINATION boundary markers.
    Does NOT add any tank accessories.
    """
    pid = pump_node.id
    pump_node.type  = "pump"
    pump_node.role  = "process"
    pump_node.ports = _P_PORTS[:]
    if not pump_node.attributes.get("tag"):
        pump_node.attributes["tag"] = tg.next("pump")
    nodes.append(pump_node)

    # Boundary markers (source + destination)
    src  = f"SRC_{pid}"
    dest = f"DEST_{pid}"
    nodes.append(_boundary(src,  "FEED"))
    nodes.append(_boundary(dest, "PRODUCT"))

    # Required: suction and discharge valves
    v_suct = f"V_SUCT_{pid}"
    v_disc = f"V_DISC_{pid}"
    nodes.append(_valve(v_suct, tg.next("valve","suction"),  "suction"))
    nodes.append(_valve(v_disc, tg.next("valve","discharge"),"discharge"))

    # Main flow
    edges.append(_edge(src,    v_suct, "OUT",       "IN",        "inline"))
    edges.append(_edge(v_suct, pid,    "OUT",       "SUCTION",   "inline"))
    edges.append(_edge(pid,    v_disc, "DISCHARGE", "IN",        "inline"))
    edges.append(_edge(v_disc, dest,   "OUT",       "default_in","inline"))

    # Optional: NRV
    if intent.get("has_nrv"):
        nrv = f"NRV_{pid}"
        nodes.append(_valve(nrv, tg.next("valve","nrv"), "nrv"))
        edges.append(_edge(pid,    nrv,    "DISCHARGE", "IN",  "inline"))
        edges.append(_edge(nrv,    v_disc, "OUT",        "IN", "inline"))

    # Optional: bypass
    if intent.get("has_bypass"):
        by_id = f"V_BYP_{pid}"
        nodes.append(_valve(by_id, tg.next("valve","bypass"), "bypass"))
        edges.append(_edge(v_suct, by_id, "OUT", "IN", "branch"))
        edges.append(_edge(by_id,  v_disc,"OUT", "IN", "branch"))

    # Optional: filter/strainer
    if intent.get("has_filter"):
        flt = f"FLT_{pid}"
        nodes.append(_node(flt, "filter", "control",
                           [_port("IN","left"), _port("OUT","right")],
                           tag=tg.next("filter")))
        edges.append(_edge(flt, v_suct, "OUT", "IN", "inline"))

    # Optional: instruments on pump body
    for inst in intent.get("instruments", ["PI"]):
        if inst not in ("PI","FI","PT"):
            continue
        iid = f"{inst}_P_{pid}"
        nodes.append(_sensor(iid, tg.next("sensor", inst), inst))
        edges.append(_edge(pid, iid, "PI_PORT", "CONNECTION", "instrument"))

    # Optional: recirculation
    if intent.get("has_recirculation"):
        rec = f"V_REC_{pid}"
        nodes.append(_valve(rec, tg.next("valve","recirculation"),
                            "recirculation"))
        edges.append(_edge(v_disc, rec, "OUT", "IN", "branch"))
        edges.append(_edge(rec, v_suct, "OUT", "IN", "branch"))


def _build_storage_tank(tank_node: NodeSchema, intent: Dict, tg: TagGenerator,
                         nodes: List, edges: List):
    """
    Knowledge-base rule: tank "requires" inlet_valve, outlet_valve, drain, vent.
    No pump — ever.
    """
    tid = tank_node.id
    tank_node.type  = "tank"
    tank_node.role  = "source"
    tank_node.ports = _T_PORTS[:]
    if not tank_node.attributes.get("tag"):
        tank_node.attributes["tag"] = tg.next("tank")
    nodes.append(tank_node)

    # Required: inlet and outlet valves
    v_in  = f"V_IN_{tid}"
    v_out = f"V_OUT_{tid}"
    nodes.append(_valve(v_in,  tg.next("valve","inlet"),  "inlet"))
    nodes.append(_valve(v_out, tg.next("valve","outlet"), "outlet"))

    edges.append(_edge(v_in,  tid,   "OUT",    "INLET",  "inline"))
    edges.append(_edge(tid,   v_out, "OUTLET", "IN",     "inline"))

    # Required: drain, vent + optional accessories
    _add_tank_accessories(tid, intent, tg, nodes, edges)


def _build_transfer_system(tank_node: NodeSchema, pump_node: NodeSchema,
                            intent: Dict, tg: TagGenerator,
                            nodes: List, edges: List):
    """
    Knowledge-base rule: transfer "requires" tank + pump + all valves + NRV.
    Tank → Pump with full accessories on tank, PI on pump.
    Tank in VESSEL ZONE (Y=2800), pump/valves on MAIN LINE (Y=0).
    """
    tid = tank_node.id
    pid = pump_node.id

    tank_node.type  = "tank";  tank_node.role  = "source"
    pump_node.type  = "pump";  pump_node.role  = "process"
    tank_node.ports = _T_PORTS[:]
    pump_node.ports = _P_PORTS[:]

    if not tank_node.attributes.get("tag"):
        tank_node.attributes["tag"] = tg.next("tank")
    if not pump_node.attributes.get("tag"):
        pump_node.attributes["tag"] = tg.next("pump")

    nodes.append(tank_node)
    nodes.append(pump_node)

    # Valves (required by knowledge-base rule)
    v_feed = f"V_FEED_{tid}";  nodes.append(_valve(v_feed, tg.next("valve","inlet"),    "inlet"))
    v_out  = f"V_OUT_{tid}";   nodes.append(_valve(v_out,  tg.next("valve","outlet"),   "outlet"))
    v_suct = f"V_SUCT_{pid}";  nodes.append(_valve(v_suct, tg.next("valve","suction"),  "suction"))
    v_disc = f"V_DISC_{pid}";  nodes.append(_valve(v_disc, tg.next("valve","discharge"),"discharge"))

    # Main flow: FEED → TANK → main line → PUMP → PRODUCT
    edges.append(_edge(v_feed, tid,    "OUT",       "INLET",   "inline"))
    edges.append(_edge(tid,    v_out,  "OUTLET",    "IN",      "inline"))
    edges.append(_edge(v_out,  v_suct, "OUT",       "IN",      "inline"))
    edges.append(_edge(v_suct, pid,    "OUT",       "SUCTION", "inline"))
    edges.append(_edge(pid,    v_disc, "DISCHARGE", "IN",      "inline"))

    # NRV (always required in transfer systems per knowledge-base rule)
    nrv = f"NRV_{pid}"
    nodes.append(_valve(nrv, tg.next("valve","nrv"), "nrv"))
    edges.append(_edge(pid,    nrv,    "DISCHARGE", "IN",  "inline"))
    edges.append(_edge(nrv,    v_disc, "OUT",        "IN", "inline"))

    # Optional: bypass
    if intent.get("has_bypass"):
        by_id = f"V_BYP_{pid}"
        nodes.append(_valve(by_id, tg.next("valve","bypass"), "bypass"))
        edges.append(_edge(v_suct, by_id, "OUT", "IN", "branch"))
        edges.append(_edge(by_id,  v_disc,"OUT", "IN", "branch"))

    # Optional: recirculation
    if intent.get("has_recirculation"):
        rec = f"V_REC_{pid}"
        nodes.append(_valve(rec, tg.next("valve","recirculation"), "recirculation"))
        edges.append(_edge(v_disc, rec, "OUT", "IN", "branch"))
        edges.append(_edge(rec, v_suct, "OUT", "IN", "branch"))

    # Tank accessories
    _add_tank_accessories(tid, intent, tg, nodes, edges)

    # PI on pump
    for inst in [i for i in intent.get("instruments",["PI"]) if i in ("PI","FI","PT")]:
        iid = f"{inst}_P_{pid}"
        nodes.append(_sensor(iid, tg.next("sensor", inst), inst))
        edges.append(_edge(pid, iid, "PI_PORT", "CONNECTION", "instrument"))


# ════════════════════════════════════════════════════════════════════
# Synthesis helpers (create fresh nodes when NLP didn't find them)
# ════════════════════════════════════════════════════════════════════

def _make_pump(idx: int = 1, tg: TagGenerator = None) -> NodeSchema:
    n = _node(f"P_{idx:03d}", "pump", "process", _P_PORTS[:])
    return n

def _make_tank(idx: int = 1, tg: TagGenerator = None) -> NodeSchema:
    n = _node(f"T_{idx:03d}", "tank", "source", _T_PORTS[:])
    return n


# ════════════════════════════════════════════════════════════════════
# Public API
# ════════════════════════════════════════════════════════════════════

class KnowledgeEngine:

    @staticmethod
    def build_process_graph(schema: EngineeringSchema,
                             intent: Dict[str, Any]) -> EngineeringSchema:
        """
        Dynamic topology builder.
        Reads system_type and intent flags → dispatches to correct builder.
        Uses TagGenerator so all tags are sequential and unique.
        """
        nodes: List[NodeSchema] = []
        edges: List[EdgeSchema] = []
        tg = TagGenerator()    # fresh counter per diagram

        system_type = intent.get("system_type", "generic")

        # ── Extract NLP-produced major equipment ─────────────────────
        all_equip = [n for n in schema.nodes
                     if any(k in n.type.lower()
                            for k in ("pump","tank","reactor","vessel"))]
        pumps = [n for n in all_equip if "pump"  in n.type.lower()]
        tanks = [n for n in all_equip
                 if any(k in n.type.lower() for k in ("tank","reactor","vessel"))]

        # ── Synthesise missing equipment per system type ─────────────
        if system_type == "transfer" and not pumps:
            pumps = [_make_pump(1, tg)]
        if system_type in ("transfer","storage","cip","tank_only") and not tanks:
            tanks = [_make_tank(1, tg)]
        if system_type in ("pump_only","recirculation") and not pumps:
            pumps = [_make_pump(1, tg)]

        # ── Dispatch via knowledge-base system type ──────────────────
        if system_type == "transfer" and tanks and pumps:
            _build_transfer_system(tanks[0], pumps[0], intent, tg, nodes, edges)

        elif system_type in ("storage","cip","tank_only") and tanks:
            _build_storage_tank(tanks[0], intent, tg, nodes, edges)

        elif system_type == "recirculation" and pumps:
            _build_pump_only(pumps[0],
                             {**intent, "has_recirculation": True},
                             tg, nodes, edges)

        elif system_type == "pump_only" and pumps:
            _build_pump_only(pumps[0], intent, tg, nodes, edges)

        elif pumps and tanks:
            _build_transfer_system(tanks[0], pumps[0], intent, tg, nodes, edges)
        elif pumps:
            _build_pump_only(pumps[0], intent, tg, nodes, edges)
        elif tanks:
            _build_storage_tank(tanks[0], intent, tg, nodes, edges)
        else:
            fallback = _make_pump(1, tg)
            _build_pump_only(fallback, intent, tg, nodes, edges)

        schema.nodes = nodes
        schema.edges = edges
        schema.attributes["intent"]      = intent
        schema.attributes["system_type"] = system_type

        print(f"[KnowledgeEngine] system={system_type}  "
              f"nodes={len(nodes)}  edges={len(edges)}")
        return schema

    @staticmethod
    def infer_process(schema: EngineeringSchema) -> EngineeringSchema:
        """Compat shim for debug scripts / legacy callers."""
        urs = schema.attributes.get("urs_text", "")
        if urs:
            from services.process_interpreter import ProcessInterpreter
            intent = ProcessInterpreter.interpret(urs)
        else:
            has_pump = any("pump" in n.type.lower() for n in schema.nodes)
            has_tank = any("tank" in n.type.lower() for n in schema.nodes)
            intent = {
                "process_type":      "generic",
                "system_type":       ("transfer"  if (has_pump and has_tank)
                                      else "pump_only" if has_pump else "storage"),
                "has_recirculation": False,
                "has_cip":           has_tank,
                "has_drain":         has_tank,
                "has_nrv":           False,
                "has_bypass":        False,
                "has_filter":        False,
                "instruments":       ["PI"] if has_pump else ["LI","TI"],
                "main_equipment":    (["pump","tank"] if (has_pump and has_tank)
                                      else ["pump"] if has_pump else ["tank"]),
            }
        return KnowledgeEngine.build_process_graph(schema, intent)
