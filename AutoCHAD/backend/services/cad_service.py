"""
cad_service.py
────────────────────────────────────────────────────────────────────
Theme-aware, layer-assigned P&ID renderer.

Every drawing entity is:
  • Color-coded by theme  (dark / light)
  • Assigned to a named DXF layer  (PROCESS, INSTRUMENT, UTILITY …)

This makes the output professional-grade DXF:
  • Layers can be toggled in AutoCAD / FreeCAD
  • Colors change when switching themes
  • No hardcoded ACI color numbers in drawing code

SIZES (tuned for X_STEP=2200)
══════════════════════════════
  SYM  = 260   base half-dimension
"""

import math
from typing import Tuple, Dict, List, Optional, Any

from ezdxf.enums import TextEntityAlignment
from models.schema import EngineeringSchema
from services.knowledge_base import (
    THEMES, DEFAULT_THEME, RELATION_LAYER, NODE_LAYER,
    DEFAULT_NODE_LAYER, get_label
)

# ── Sizes ─────────────────────────────────────────────────────────
SYM       = 260
FONT_TAG  = 180
FONT_DESC = 100
FONT_ISA  = 100
ARROW_SZ  = 130

# ── Tank geometry constants ────────────────────────────────────────
_HW = SYM * 0.90    # tank half-width
_HH = SYM * 1.60    # tank half-height
_DR = SYM * 0.90    # dome radius

# ── Port offsets (tuned to symbols) ───────────────────────────────
PORT_OFFSETS: Dict[str, Dict[str, Tuple[float, float]]] = {
    "tank": {
        "INLET":       (0,           _HH + _DR * 0.85),
        "OUTLET":      (0,         -(_HH + _DR)),
        "VENT":        (-_HW*0.55,   _HH + _DR * 0.85),
        "CIP":         ( _HW*0.55,   _HH + _DR * 0.85),
        "PSV":         ( _HW*0.85,   _HH + _DR * 0.50),
        "DRAIN":       (0,          -(_HH + _DR * 0.60)),
        "LT":          ( _HW*1.05,   _HH * 0.50),
        "TT":          ( _HW*1.05,  -_HH * 0.15),
        "PI_PORT":     (-_HW*1.05,   0),
        "default_in":  (0,           _HH + _DR * 0.85),
        "default_out": (0,         -(_HH + _DR)),
    },
    "pump": {
        "SUCTION":     (-SYM*1.25,  0),
        "DISCHARGE":   ( SYM*1.25,  0),
        "PI_PORT":     (0,           SYM*0.85),
        "default_in":  (-SYM*1.25,  0),
        "default_out": ( SYM*1.25,  0),
    },
    "valve": {
        "IN":          (-SYM*0.60,  0),
        "OUT":         ( SYM*0.60,  0),
        "default_in":  (-SYM*0.60,  0),
        "default_out": ( SYM*0.60,  0),
    },
    "sensor": {
        "CONNECTION":  (0,  SYM*0.55),
        "default_in":  (0,  SYM*0.55),
        "default_out": (0,  0),
    },
    "relief_valve": {
        "IN":          (0, -SYM*0.65),
        "OUT":         (0,  SYM*1.50),
        "default_in":  (0, -SYM*0.65),
        "default_out": (0,  SYM*1.50),
    },
    "vent": {
        "IN":          (0,  0),
        "default_in":  (0,  0),
        "default_out": (0,  SYM*1.10),
    },
    "spray_ball": {
        "IN":          (0,  SYM*0.35),
        "default_in":  (0,  SYM*0.35),
        "default_out": (0, -SYM*0.35),
    },
    "filter": {
        "IN":          (-SYM*0.65,  0),
        "OUT":         ( SYM*0.65,  0),
        "default_in":  (-SYM*0.65,  0),
        "default_out": ( SYM*0.65,  0),
    },
    "boundary": {
        "default_in":  (-SYM*0.80,  0),
        "default_out": ( SYM*0.80,  0),
        "OUT":         ( SYM*0.80,  0),
    },
}

def _port_pos(node, port_name: str, cx: float, cy: float) -> Tuple[float,float]:
    offsets = PORT_OFFSETS.get(node.type, {})
    dx, dy  = offsets.get(port_name, offsets.get("default_out", (0.0, 0.0)))
    return (cx+dx, cy+dy)


# ════════════════════════════════════════════════════════════════════
# Theme-aware drawing helpers
# ════════════════════════════════════════════════════════════════════

def _attribs(color: int, lw: int, layer: str) -> dict:
    return {"color": color, "lineweight": lw, "layer": layer}

def _L(msp, p1, p2, color, lw, layer):
    try: msp.add_line(p1, p2, dxfattribs=_attribs(color, lw, layer))
    except Exception: pass

def _C(msp, ctr, r, color, lw, layer):
    try: msp.add_circle(ctr, r, dxfattribs=_attribs(color, lw, layer))
    except Exception: pass

def _A(msp, ctr, r, a1, a2, color, lw, layer):
    try: msp.add_arc(ctr, r, a1, a2, dxfattribs=_attribs(color, lw, layer))
    except Exception: pass

def _P(msp, pts, color, lw, layer, close=False):
    try:
        msp.add_lwpolyline(pts,
                           dxfattribs=_attribs(color, lw, layer), close=close)
    except Exception: pass

def _T(msp, x, y, text, height, color, layer,
       align=TextEntityAlignment.CENTER):
    try:
        msp.add_text(str(text),
                     dxfattribs={"height": height, "color": color,
                                 "layer": layer}
                     ).set_placement((x, y), align=align)
    except Exception: pass

def _arrow(msp, x, y, direction, color, layer):
    a = ARROW_SZ
    if   direction == "right": pts = [(x-a, y+a*.5),(x,y),(x-a, y-a*.5)]
    elif direction == "left":  pts = [(x+a, y+a*.5),(x,y),(x+a, y-a*.5)]
    elif direction == "up":    pts = [(x-a*.5,y-a),(x,y),(x+a*.5,y-a)]
    else:                      pts = [(x-a*.5,y+a),(x,y),(x+a*.5,y+a)]
    _P(msp, pts, color, 28, layer)

def _label(msp, x, y, tag, desc, c_tag, c_dim, layer):
    _T(msp, x, y,              tag,         FONT_TAG,          c_tag, layer)
    _T(msp, x, y-FONT_TAG*1.05, f"({desc})", FONT_DESC, c_dim, layer)


# ════════════════════════════════════════════════════════════════════
# Symbol draw functions — all theme-parameterised
# ════════════════════════════════════════════════════════════════════

def _draw_tank(msp, x, y, tag, desc, T, EL="EQUIPMENT"):
    hw, hh, r = _HW, _HH, _DR
    c = T["equipment"]
    _L(msp,(x-hw,y-hh),(x-hw,y+hh),c,55,EL)
    _L(msp,(x+hw,y-hh),(x+hw,y+hh),c,55,EL)
    _L(msp,(x-hw,y-hh),(x+hw,y-hh),c,55,EL)
    _L(msp,(x-hw,y+hh),(x+hw,y+hh),c,55,EL)
    _A(msp,(x,y+hh),r,  0,180,c,55,EL)
    _A(msp,(x,y-hh),r,180,360,c,55,EL)
    # Centre-line (phantom)
    for i in range(4):
        lx = x - hw*0.45 + i*hw*0.30
        _L(msp,(lx,y),(lx+hw*0.15,y),T["guide"],10,"GUIDE")
    _label(msp, x, y-hh-r-FONT_TAG*1.1, tag, desc,
           T["text_primary"], T["text_dim"], "ANNOTATION")

def _draw_pump(msp, x, y, tag, desc, T, EL="EQUIPMENT"):
    r=SYM*0.70; ox=r*0.45
    c = T["pump"]
    _C(msp,(x-ox,y),r,c,50,EL)
    _C(msp,(x+ox,y),r,c,50,EL)
    _C(msp,(x,y),r*0.13,c,20,EL)
    _label(msp, x, y-r-FONT_TAG*1.2, tag, desc,
           c, T["text_dim"], "ANNOTATION")

def _draw_valve(msp, x, y, tag, desc, T, subtype="", EL="PROCESS"):
    hw=SYM*0.60; hh=SYM*0.40; sh=hh*1.75
    c = T["valve"]
    _P(msp,[(x-hw,y+hh),(x-hw,y-hh),(x+hw,y+hh),(x+hw,y-hh),(x-hw,y+hh)],
       c,38,EL)
    _L(msp,(x,y),(x,y+sh),c,20,EL)
    _L(msp,(x-hw*.45,y+sh),(x+hw*.45,y+sh),c,20,EL)
    if subtype in ("drain","outlet"):
        _L(msp,(x,y),(x,y-hh*1.25),c,14,EL)
    if subtype in ("nrv","check"):
        _L(msp,(x-hw*.55,y),(x+hw*.55,y),c,14,EL)
    _label(msp, x, y-hh-FONT_TAG*1.2, tag, desc,
           c, T["text_dim"], "ANNOTATION",
           )

def _draw_sensor(msp, x, y, tag, desc, T, subtype="PI", EL="INSTRUMENT"):
    r=SYM*0.50
    c = T["instrument"]
    _C(msp,(x,y),r,c,20,EL)
    _L(msp,(x-r,y),(x+r,y),c,14,EL)
    lbl=(subtype or "XI")[:3]
    _T(msp,x,y+FONT_ISA*.10,lbl,FONT_ISA,c,EL)
    _label(msp, x, y-r-FONT_TAG*0.95, tag, desc,
           c, T["text_dim"], "ANNOTATION")

def _draw_spray_ball(msp, x, y, tag, desc, T, EL="UTILITY"):
    r=SYM*0.28
    c = T["utility_pipe"]
    _C(msp,(x,y),r,c,18,EL)
    for ang in (45,135,225,315):
        rad=math.radians(ang)
        _L(msp,(x+r*math.cos(rad),y+r*math.sin(rad)),
               (x+r*2.4*math.cos(rad),y+r*2.4*math.sin(rad)),c,16,EL)
    _label(msp, x, y-r*2.8, tag, desc,
           c, T["text_dim"], "ANNOTATION")

def _draw_relief_valve(msp, x, y, tag, desc, T, EL="SAFETY"):
    hw=SYM*0.52; hh=SYM*0.58
    c = T["safety"]
    _P(msp,[(x,y+hh),(x-hw,y-hh),(x+hw,y-hh),(x,y+hh)],c,42,EL)
    cur_y,end_y=y+hh,y+hh+SYM*0.75
    seg,tog,prev=SYM*0.11,1,(x,y+hh)
    while cur_y<end_y:
        ny=min(cur_y+seg,end_y); nx=x+tog*SYM*0.16
        _L(msp,prev,(nx,ny),c,18,EL); prev=(nx,ny); cur_y=ny; tog=-tog
    _label(msp, x, y-hh-FONT_TAG*1.0, tag, desc,
           c, T["text_dim"], "ANNOTATION")

def _draw_vent(msp, x, y, tag, desc, T, EL="UTILITY"):
    sh=SYM*1.0
    c = T["utility_pipe"]
    _L(msp,(x,y),(x,y+sh),c,20,EL)
    _arrow(msp,x,y+sh,"up",c,"UTILITY")
    _T(msp,x+ARROW_SZ*.7,y+sh*.5,tag,FONT_TAG*.72,c,"ANNOTATION",
       align=TextEntityAlignment.LEFT)

def _draw_filter(msp, x, y, tag, desc, T, EL="PROCESS"):
    hw=SYM*0.58; hh=SYM*0.58
    c = T["pipe"]
    _P(msp,[(x,y+hh),(x+hw,y),(x,y-hh),(x-hw,y),(x,y+hh)],c,26,EL)
    _L(msp,(x-hw*.60,y+hh*.60),(x+hw*.60,y-hh*.60),c,14,EL)
    _label(msp, x, y-hh-FONT_TAG*1.1, tag, desc,
           T["text_primary"], T["text_dim"], "ANNOTATION")

def _draw_boundary(msp, x, y, tag, T, EL="BOUNDARY"):
    hw=SYM*0.80; hh=SYM*0.40
    c = T["boundary"]
    pts=[(x-hw,y),(x-hw*.5,y+hh),(x+hw*.5,y+hh),
         (x+hw,y),(x+hw*.5,y-hh),(x-hw*.5,y-hh)]
    _P(msp,pts,c,20,EL,close=True)
    _T(msp,x,y-FONT_TAG*.35,tag,FONT_TAG*.85,c,"ANNOTATION")
    _arrow(msp,x-hw-ARROW_SZ*.5,y,"right",c,"BOUNDARY")


# ════════════════════════════════════════════════════════════════════
# Node dispatcher
# ════════════════════════════════════════════════════════════════════

def draw_node(msp, node, pos, T: Dict):
    x, y  = pos
    tag   = node.attributes.get("tag", node.id)
    sub   = node.attributes.get("subtype","").lower()
    sub_u = sub.upper()
    desc  = get_label(node.type, sub or sub_u)
    EL    = NODE_LAYER.get(node.type, DEFAULT_NODE_LAYER)

    dispatch = {
        "tank":         lambda: _draw_tank(msp,x,y,tag,desc,T,EL),
        "pump":         lambda: _draw_pump(msp,x,y,tag,desc,T,EL),
        "valve":        lambda: _draw_valve(msp,x,y,tag,desc,T,sub,EL),
        "sensor":       lambda: _draw_sensor(msp,x,y,tag,desc,T,sub_u or "PI",EL),
        "spray_ball":   lambda: _draw_spray_ball(msp,x,y,tag,desc,T,EL),
        "relief_valve": lambda: _draw_relief_valve(msp,x,y,tag,desc,T,EL),
        "vent":         lambda: _draw_vent(msp,x,y,tag,desc,T,EL),
        "filter":       lambda: _draw_filter(msp,x,y,tag,desc,T,EL),
        "boundary":     lambda: _draw_boundary(msp,x,y,tag,T,EL),
    }
    fn = dispatch.get(node.type)
    if fn:
        fn()
    else:
        _P(msp,[(x-SYM,y-SYM),(x+SYM,y-SYM),(x+SYM,y+SYM),(x-SYM,y+SYM)],
           T["equipment"],28,"EQUIPMENT",close=True)
        _label(msp,x,y-SYM-FONT_TAG,tag,desc,
               T["text_primary"],T["text_dim"],"ANNOTATION")


# ════════════════════════════════════════════════════════════════════
# Pipe routing (theme-aware + layer-aware)
# ════════════════════════════════════════════════════════════════════

def _pipe_color(relation: str, T: Dict) -> int:
    return {
        "inline":     T["pipe"],
        "branch":     T["pipe"],
        "loop":       T["pipe"],
        "utility":    T["utility_pipe"],
        "drain":      T["utility_pipe"],
        "instrument": T["instrument"],
    }.get(relation, T["pipe"])

PIPE_LW = {"inline":60,"branch":35,"loop":30,
           "utility":28,"drain":28,"instrument":18}

def _draw_pipe(msp, p_start, p_end, relation, T):
    sx, sy = p_start; ex, ey = p_end
    if abs(sx-ex) < 2 and abs(sy-ey) < 2: return
    color = _pipe_color(relation, T)
    lw    = PIPE_LW.get(relation, 40)
    layer = RELATION_LAYER.get(relation, "PROCESS")

    if relation == "instrument":
        _L(msp,(sx,sy),(ex,ey),color,lw,layer); return

    if relation in ("utility","drain"):
        _L(msp,(sx,sy),(sx,ey),color,lw,layer)
        _L(msp,(sx,ey),(ex,ey),color,lw,layer)
        _arrow(msp,sx,(sy+ey)/2,"up" if ey>sy else "down",color,layer)
        return

    if relation in ("branch","loop"):
        mid_y = min(sy,ey) - 1000
        _L(msp,(sx,sy),(sx,mid_y),color,lw,layer)
        _L(msp,(sx,mid_y),(ex,mid_y),color,lw,layer)
        _L(msp,(ex,mid_y),(ex,ey),color,lw,layer)
        _arrow(msp,(sx+ex)/2,mid_y,"right" if ex>sx else "left",color,layer)
        return

    # Inline → elbow
    dy=abs(ey-sy); dx=abs(ex-sx)
    if dy < 15:
        _L(msp,(sx,sy),(ex,ey),color,lw,layer)
        _arrow(msp,(sx+ex)/2,sy,"right" if ex>sx else "left",color,layer)
    elif dy > dx:
        _L(msp,(sx,sy),(ex,sy),color,lw,layer)
        _L(msp,(ex,sy),(ex,ey),color,lw,layer)
        _arrow(msp,ex,(sy+ey)/2,"up" if ey>sy else "down",color,layer)
    else:
        _L(msp,(sx,sy),(sx,ey),color,lw,layer)
        _L(msp,(sx,ey),(ex,ey),color,lw,layer)
        _arrow(msp,(sx+ex)/2,ey,"right" if ex>sx else "left",color,layer)


# ════════════════════════════════════════════════════════════════════
# Zone guide lines
# ════════════════════════════════════════════════════════════════════

def _draw_zone_guides(msp, min_x, max_x, nodes, T):
    pad = 800
    x1, x2 = min_x-pad, max_x+pad
    has_vessel  = any(n.type=="tank"  for n in nodes.values())
    has_top     = any(n.attributes.get("zone_hint")=="top" for n in nodes.values())
    has_bot     = any(n.attributes.get("zone_hint")=="bot" for n in nodes.values())
    c = T["guide"]
    guides = []
    if has_vessel:  guides.append((1400,  "VESSEL ZONE"))
    if has_top:     guides.append((3700,  "INSTRUMENT / UTILITY (TOP)"))
    if has_bot:     guides.append((-1100, "DRAIN / UTILITY (BOTTOM)"))
    for y_sep, lbl in guides:
        _L(msp,(x1,y_sep),(x2,y_sep),c,6,"GUIDE")
        _T(msp,x2+60,y_sep,lbl,FONT_DESC*0.80,c,"GUIDE",
           align=TextEntityAlignment.LEFT)


# ════════════════════════════════════════════════════════════════════
# Flow direction header
# ════════════════════════════════════════════════════════════════════

def _draw_flow_header(msp, xs, T):
    if len(xs) < 2: return
    x1,x2 = min(xs)-300, max(xs)+300
    y = -SYM*2.3
    c = T["guide"]
    _L(msp,(x1,y),(x2,y),c,6,"GUIDE")
    _arrow(msp,(x1+x2)/2,y,"right",c,"GUIDE")
    _T(msp,(x1+x2)/2,y-FONT_DESC*1.4,
       "<<< FLOW DIRECTION >>>",FONT_DESC*0.85,c,"GUIDE")


# ════════════════════════════════════════════════════════════════════
# Legend
# ════════════════════════════════════════════════════════════════════

LEGEND_ROWS = [
    ("process",     "pipe",         "Main process line"),
    ("utility",     "utility_pipe", "Utility / CIP line"),
    ("instrument",  "instrument",   "Instrument signal"),
    ("T-xxx",       "equipment",    "Process Vessel"),
    ("P-xxx",       "pump",         "Rotary Lobe Pump"),
    ("V-xxx",       "valve",        "Isolation Valve"),
    ("NRV-xxx",     "valve",        "Non-Return Valve"),
    ("PSV-xxx",     "safety",       "Pressure Safety Valve"),
    ("LT-xxx",      "instrument",   "Level Transmitter"),
    ("TT-xxx",      "instrument",   "Temperature Transmitter"),
    ("PI-xxx",      "instrument",   "Pressure Indicator"),
    ("SB-xxx",      "utility_pipe", "CIP Spray Ball"),
    ("VT-xxx",      "utility_pipe", "Atmospheric Vent"),
    ("V-DRN",       "valve",        "Drain Valve"),
    ("FEED",        "boundary",     "Feed / Source point"),
    ("PRODUCT",     "boundary",     "Product / Destination"),
]
ROW_H=FONT_DESC*1.65; COL_SYM=280; COL_DSC=1250; BOX_W=4200

def draw_legend(msp, ax, ay, T):
    total_h = len(LEGEND_ROWS)*ROW_H+400
    c_dim   = T["text_dim"]
    _P(msp,[(ax,ay),(ax+BOX_W,ay),(ax+BOX_W,ay-total_h),
            (ax,ay-total_h),(ax,ay)], c_dim,14,"ANNOTATION")
    _T(msp,ax+BOX_W/2,ay-240,"P&ID SYMBOL LEGEND",
       FONT_TAG*0.78,c_dim,"ANNOTATION")
    _L(msp,(ax+60,ay-320),(ax+BOX_W-60,ay-320),c_dim,10,"ANNOTATION")
    for i,(sym,ckey,desc) in enumerate(LEGEND_ROWS):
        ry=ay-400-i*ROW_H
        _T(msp,ax+COL_SYM,ry,sym,FONT_DESC,T.get(ckey,c_dim),"ANNOTATION",
           align=TextEntityAlignment.LEFT)
        _T(msp,ax+COL_DSC,ry,desc,FONT_DESC,c_dim,"ANNOTATION",
           align=TextEntityAlignment.LEFT)


# ════════════════════════════════════════════════════════════════════
# Public CADService
# ════════════════════════════════════════════════════════════════════

class CADService:
    @staticmethod
    def draw_top_view(*a,**k): pass
    @staticmethod
    def draw_front_elevation(*a,**k): pass

    @staticmethod
    def draw_graph(msp, graph, layout, schema=None,
                   theme: str = DEFAULT_THEME,
                   doc=None):
        """
        Render the process graph to modelspace.
        Every entity is:
          • colored per theme palette
          • assigned to a named DXF layer
        """
        T     = THEMES.get(theme, THEMES[DEFAULT_THEME])
        nodes = graph["nodes"]
        edges = graph["edges"]
        bbox  = layout.pop("__bbox__", None)

        # ── 1. Draw nodes ─────────────────────────────────────────
        for nid, node in nodes.items():
            pos = layout.get(nid)
            if pos is None: continue
            draw_node(msp, node, pos, T)

        # ── 2. Draw pipes ─────────────────────────────────────────
        for edge in edges:
            fn = nodes.get(edge.from_id)
            tn = nodes.get(edge.to_id)
            if not fn or not tn: continue
            fc = layout.get(edge.from_id)
            tc = layout.get(edge.to_id)
            if fc is None or tc is None: continue
            start = _port_pos(fn, edge.from_port, *fc)
            end   = _port_pos(tn, edge.to_port,   *tc)
            _draw_pipe(msp, start, end,
                       getattr(edge,"relation","inline"), T)

        # ── 3. Flow direction header ─────────────────────────────
        main_xs = [
            layout[nid][0]
            for nid,node in nodes.items()
            if nid in layout
            and node.role not in ("instrument","utility","safety","source")
        ]
        if main_xs: _draw_flow_header(msp, main_xs, T)

        # ── 4. Zone guides ────────────────────────────────────────
        if bbox:
            _draw_zone_guides(msp, bbox[0], bbox[2], nodes, T)

        # ── 5. Title + legend ─────────────────────────────────────
        if schema and bbox:
            min_x, min_y, max_x, max_y = bbox
            intent = schema.attributes.get("intent", {})
            stype  = schema.attributes.get("system_type",
                      intent.get("system_type","generic")).upper().replace("_"," ")
            eqtype = (schema.equipment.type or "DIAGRAM").upper().replace("_"," ")
            mat    = schema.material
            theme_label = theme.upper()
            title_y = min_y - 1400
            _T(msp,(min_x+max_x)/2, title_y,
               f"P&ID  |  {eqtype}  |  SYSTEM: {stype}  |  "
               f"Mat: {mat}  |  Theme: {theme_label}  |  AUTOCHAD",
               185, T["title"], "ANNOTATION")

            draw_legend(msp, min_x, title_y - 550, T)


class AnnotationEngine:
    @staticmethod
    def draw_title_block(*a,**k): pass
    @staticmethod
    def draw_dimensions(*a,**k): pass
