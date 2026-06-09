"""
dxf_service.py
────────────────────────────────────────────────────────────────────
P&ID generation pipeline:

  Schema → RuleEngine → KnowledgeEngine → Validator
         → GraphEngine → LayoutEngine → CADService → DXF

DXF LAYERS
══════════
  All entities are assigned to named DXF layers:
    PROCESS    — main process pipes and inline equipment
    INSTRUMENT — instruments and signal lines
    UTILITY    — CIP, drain, vent lines
    SAFETY     — PSV, relief valves
    EQUIPMENT  — major equipment (pump, tank)
    ANNOTATION — title, legend, text
    BOUNDARY   — feed/product markers
    GUIDE      — zone separator lines

THEME SUPPORT
═════════════
  Pass theme="dark" (default) or theme="light" in schema.attributes
  or as generate_dxf(schema, theme="light").
  Colors are resolved from knowledge_base.THEMES.
"""

import ezdxf
import os
import uuid

from services.layout_engine import LayoutEngine
from services.cad_service import CADService, AnnotationEngine
from services.rule_engine import RuleEngine
from services.graph_engine import GraphEngine
from services.validator import Validator
from services.knowledge_base import DXF_LAYERS, DEFAULT_THEME, THEMES
from models.schema import EngineeringSchema


# ── Helper: create DXF layers ────────────────────────────────────────

def _create_layers(doc, theme_name: str = DEFAULT_THEME) -> None:
    """
    Create all named P&ID layers in the DXF document.
    Colors are overridden by the theme palette where applicable.
    """
    theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])

    # Map layer name → theme color key
    layer_theme_key = {
        "PROCESS":    "pipe",
        "INSTRUMENT": "instrument",
        "UTILITY":    "utility_pipe",
        "SAFETY":     "safety",
        "EQUIPMENT":  "equipment",
        "ANNOTATION": "text_dim",
        "BOUNDARY":   "boundary",
        "GUIDE":      "guide",
    }

    for layer_name, props in DXF_LAYERS.items():
        color = theme.get(layer_theme_key.get(layer_name, "pipe"), props["color"])
        try:
            layer = doc.layers.new(name=layer_name)
            layer.color = color
            layer.lineweight = props["lineweight"]
            if props["linetype"] != "CONTINUOUS":
                try:
                    layer.linetype = props["linetype"]
                except Exception:
                    pass    # linetype files not always loadable
        except Exception:
            pass    # layer may already exist


class DXFService:

    @staticmethod
    def generate_dxf(schema: EngineeringSchema,
                     theme: str = DEFAULT_THEME) -> str:
        """
        Full pipeline:
          Schema → rules → build graph → validate → layout → render → DXF

        Parameters
        ----------
        schema : EngineeringSchema
        theme  : "dark" | "light"   (default: "dark")
        """
        # ── Resolve theme (schema attribute overrides arg) ────────────
        theme = schema.attributes.get("theme", theme)
        if theme not in THEMES:
            theme = DEFAULT_THEME

        # ── Create DXF document ──────────────────────────────────────
        doc = ezdxf.new()
        msp = doc.modelspace()

        # ── Load linetype for DASHED utility lines ───────────────────
        try:
            doc.linetypes.load_linetype_file(
                "acadiso.lin", list_of_line_types=["DASHED"])
        except Exception:
            pass

        # ── Create named layers ──────────────────────────────────────
        _create_layers(doc, theme)

        # ── Set model-space background color hint (DXF header) ───────
        try:
            doc.header["$PSLTSCALE"] = 0
        except Exception:
            pass

        # ── 1. Rule engine: validate/tag/prune ───────────────────────
        schema = RuleEngine.apply_rules(schema)
        print(f"[DXFService] After rules: nodes={len(schema.nodes)}, "
              f"edges={len(schema.edges)}")

        # ── 2. Pre-render validation ─────────────────────────────────
        system_type = schema.attributes.get("system_type", "generic")
        Validator.validate_and_warn(schema, system_type)

        # ── 3. Build graph ───────────────────────────────────────────
        graph = GraphEngine.build_graph(schema)

        # ── 4. Compute layout ────────────────────────────────────────
        layout = LayoutEngine.compute_graph_layout(graph)
        print(f"[DXFService] Layout positions: {list(layout.keys())}")

        # ── 5. Render ────────────────────────────────────────────────
        CADService.draw_graph(msp, graph, layout, schema,
                              theme=theme, doc=doc)

        # ── 6. Save ─────────────────────────────────────────────────
        output_dir = os.path.join(os.getcwd(), "outputs")
        os.makedirs(output_dir, exist_ok=True)

        safe_type = (schema.equipment.type or "DIAGRAM").upper() \
                        .replace(" ", "_")[:20]
        filename  = f"AUTOCHAD_{safe_type}_{uuid.uuid4().hex[:8]}.dxf"
        file_path = os.path.join(output_dir, filename)

        print("Saving DXF to:", file_path)
        doc.saveas(file_path)
        print("DXF saved successfully at:", file_path)

        return file_path
