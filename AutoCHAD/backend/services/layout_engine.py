"""
layout_engine.py
────────────────────────────────────────────────────────────────────
Zone-aware compact P&ID layout engine.

ZONE POSITIONS (Y axis)
═══════════════════════
  +5000   TOP UTILITY    (PSV, vent, spray ball, CIP supply valve   — top of vessel)
  +2800   VESSEL ZONE    (tanks / reactors — above main line)
      0   MAIN LINE      (pumps, inline valves — horizontal flow)
  −2200   BOT UTILITY    (drain valves — below main line)
  −4500   RECIRCULATION  (recirculation return rail)

ZONE SELECTION RULES (in priority order)
═════════════════════════════════════════
  "zone_hint"="top" attribute  → TOP UTILITY  (+5000)
  "zone_hint"="bot" attribute  → BOT UTILITY  (−2200)
  node.type == "tank"          → VESSEL ZONE  (+2800)
  node.role == "source"        → VESSEL ZONE  (+2800)
  node.role == "instrument"    → TOP UTILITY  (+5000) [instruments above vessel]
  node.role in (utility,safety)→ BOT UTILITY  (−2200) [unless zone_hint="top"]
  ALL OTHERS                   → MAIN LINE    (0)

SPACING
═══════
  X_STEP    = 2200   (compact, was 2800)
  X_STAGGER =  600   (branch lateral separation)

BOUNDING BOX
════════════
  Computed after all placements.
  Stored as layout["__bbox__"] = (min_x, min_y, max_x, max_y).
"""

import math
from typing import Dict, List, Tuple
from models.schema import EngineeringSchema

X_STEP    = 2200
X_STAGGER =  600
Y_TOP     =  5000    # top-of-vessel accessories
Y_VESSEL  =  2800    # tank zone
Y_MAIN    =     0    # pump / inline valve zone
Y_BOT     = -2200    # drain and bottom utilities
Y_RECIRC  = -4500    # recirculation return rail


def _node_zone(node) -> str:
    """Return the placement zone for a single node."""
    hint = node.attributes.get("zone_hint", "")
    if hint == "top":
        return "top"
    if hint == "bot":
        return "bot"
    if node.type in ("tank",) or node.role == "source":
        return "vessel"
    if node.role == "instrument":
        return "top"
    if node.role in ("utility", "safety"):
        return "bot"
    return "main"


class LayoutEngine:

    @staticmethod
    def compute_view_bounds(schema: EngineeringSchema) -> Dict[str, Tuple]:
        return {"top_view": (0.0, 0.0), "front_view": (15000.0, 0.0)}

    # ═══════════════════════════════════════════════════════════════
    @staticmethod
    def compute_graph_layout(graph) -> Dict[str, Tuple[float, float]]:
        nodes = graph["nodes"]
        edges = graph["edges"]
        layout: Dict[str, Tuple[float, float]] = {}

        if not nodes:
            return layout

        # ── Step 1: classify every node ─────────────────────────────
        zone: Dict[str, str] = {nid: _node_zone(node)
                                 for nid, node in nodes.items()}

        # ── Step 2: topo-sort main-line nodes only ──────────────────
        main_ids = [nid for nid, z in zone.items() if z == "main"]
        main_ids = LayoutEngine._topo_sort(main_ids, edges)

        total_w = max((len(main_ids) - 1) * X_STEP, 0)
        start_x = -total_w / 2.0
        main_x: Dict[str, float] = {}

        for i, nid in enumerate(main_ids):
            x = start_x + i * X_STEP
            main_x[nid] = x
            layout[nid] = (x, Y_MAIN)

        # ── Step 3: place vessel nodes centred between neighbours ────
        for nid, z in zone.items():
            if z != "vessel":
                continue
            nbr_xs: List[float] = []
            for e in edges:
                if e.relation == "inline":
                    if e.from_id == nid and e.to_id in main_x:
                        nbr_xs.append(main_x[e.to_id])
                    elif e.to_id == nid and e.from_id in main_x:
                        nbr_xs.append(main_x[e.from_id])
            vx = sum(nbr_xs) / len(nbr_xs) if nbr_xs else 0.0
            layout[nid] = (vx, Y_VESSEL)
            main_x[nid] = vx     # register for branch lookups

        # ── Step 4: place TOP nodes (instruments + top-of-vessel) ───
        slot_top: Dict[str, int] = {}
        for nid, z in zone.items():
            if z != "top":
                continue
            px  = LayoutEngine._parent_x(nid, edges, main_x)
            key = f"{px:.0f}_top"
            sl  = slot_top.get(key, 0)
            slot_top[key] = sl + 1
            layout[nid] = (px + sl * X_STAGGER, Y_TOP)

        # ── Step 5: place BOT nodes (drain, bottom utilities) ────────
        slot_bot: Dict[str, int] = {}
        for nid, z in zone.items():
            if z != "bot":
                continue
            px  = LayoutEngine._parent_x(nid, edges, main_x)
            key = f"{px:.0f}_bot"
            sl  = slot_bot.get(key, 0)
            slot_bot[key] = sl + 1
            layout[nid] = (px + sl * X_STAGGER, Y_BOT)

        # ── Step 6: recirculation return rail ────────────────────────
        for nid, node in nodes.items():
            if node.attributes.get("subtype") == "recirculation":
                xs  = list(main_x.values())
                mid = (max(xs) + min(xs)) / 2.0 if xs else 0.0
                layout[nid] = (mid, Y_RECIRC)

        # ── Step 7: bounding box ──────────────────────────────────────
        if layout:
            xs = [p[0] for p in layout.values()]
            ys = [p[1] for p in layout.values()]
            layout["__bbox__"] = (min(xs), min(ys), max(xs), max(ys))

        return layout

    # ── Helpers ──────────────────────────────────────────────────────
    @staticmethod
    def _parent_x(target: str, edges: list,
                   main_x: Dict[str, float]) -> float:
        for e in edges:
            if e.to_id   == target and e.from_id in main_x:
                return main_x[e.from_id]
            if e.from_id == target and e.to_id   in main_x:
                return main_x[e.to_id]
        return 0.0

    @staticmethod
    def _topo_sort(node_ids: List[str], edges: list) -> List[str]:
        id_set = set(node_ids)
        adj:    Dict[str, List[str]] = {n: [] for n in node_ids}
        in_deg: Dict[str, int]       = {n: 0  for n in node_ids}
        for e in edges:
            if (getattr(e, "relation", "inline") == "inline"
                    and e.from_id in id_set and e.to_id in id_set):
                adj[e.from_id].append(e.to_id)
                in_deg[e.to_id] += 1
        queue  = [n for n in node_ids if in_deg[n] == 0]
        result: List[str] = []
        while queue:
            n = queue.pop(0)
            result.append(n)
            for m in adj[n]:
                in_deg[m] -= 1
                if in_deg[m] == 0:
                    queue.append(m)
        for n in node_ids:
            if n not in result:
                result.append(n)
        return result


class NozzleEngine:
    @staticmethod
    def compute_nozzle_positions(schema: EngineeringSchema,
                                  cx: float, cy: float) -> list:
        r = schema.equipment.dimensions.diameter / 2
        return [{"nozzle": n,
                 "x": cx + r * math.cos(math.radians(n.angle)),
                 "y": cy + r * math.sin(math.radians(n.angle))}
                for n in schema.nozzles]
