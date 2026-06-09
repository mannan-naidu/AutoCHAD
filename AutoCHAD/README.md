AutoCHAD

AutoCHAD (Automated CAD Generation from Engineering Specifications) is an AI-powered engineering design automation platform that converts natural language requirements, URS (User Requirement Specifications), engineering documents, and sketches into standards-compliant CAD drawings.

The system aims to reduce manual drafting effort, minimize engineering errors, accelerate project delivery, and standardize design generation across industrial domains.

Engines & Models
-----------------

This section describes the core engines, processing pipeline, and the typed runtime models (`backend/models/schema.py`) that power AutoCHAD. The architecture is modular: small, focused engines transform data from raw text → structured engineering schema → validated process graph → layout → rendered CAD/DXF.

1) NLP / Extraction
	- `NLPService` (services/nlp_service.py): calls an LLM/GROQ endpoint to extract a complete `EngineeringSchema`-shaped JSON from free-text URS. The service returns strictly-formatted JSON (the prompt enforces schema conformance), and is the single point where external LLMs are invoked.
	- Key behaviour: enforces type normalisation, ID conventions (uppercase, prefixed IDs), default materials (SS316L), and returns only JSON for deterministic downstream parsing.

2) Intent & Interpretation
	- `ProcessInterpreter` (services/process_interpreter.py): lightweight rule-based parser that inspects the URS text to set boolean flags and classify `system_type` (e.g. `transfer`, `recirculation`, `cip`, `storage`, `pump_only`).
	- Outputs a compact `intent` dict used by the Knowledge Engine to decide topology and optional accessories.

3) Schema Builder & Validation
	- `SchemaBuilder` (services/schema_builder.py): converts the JSON from the NLP step into the strongly-typed `EngineeringSchema` Pydantic model. It handles extraction of JSON fragments and raises clear errors on invalid JSON.
	- `RuleEngine` (services/rule_engine.py): normalises types (e.g. `lobe_pump` → `pump`), assigns industrial tag prefixes (P-, T-, V- etc.), and enforces material/nozzle defaults.
	- `Validator` (services/validator.py): pre-render checks per `system_type` (required/forbidden components, connectivity, tag uniqueness) and emits warnings or errors.

4) Knowledge-driven Topology Builder
	- `KnowledgeEngine` (services/knowledge_engine.py): the dynamic topology builder. It reads `intent` and consults `knowledge_base.py` to instantiate only the equipment required by the selected `system_type`.
	- Tagging: uses an internal `TagGenerator` to create sequential ISA-style tags starting from 101 (e.g. `P-101`, `T-101`).
	- Builders: implements small, testable builders for common systems: `_build_pump_only`, `_build_storage_tank`, `_build_transfer_system` and accessory builders (tank accessories, PSV, vents, CIP spray balls, etc.).

5) Graph & Layout Engines
	- `GraphEngine` (services/graph_engine.py): converts the `EngineeringSchema` into a graph structure (`nodes` dict and `edges` list) consumed by the layout and CAD renderers.
	- `LayoutEngine` (services/layout_engine.py): zone-aware placement for compact P&ID layouts. Zones include `VESSEL`, `MAIN LINE`, `TOP UTILITY`, `BOT UTILITY`, and `RECIRCULATION`. It computes X/Y positions, topo-sorts inline flows, and emits a bounding box for rendering.
	- `NozzleEngine` (services/nozzle_engine.py): computes nozzle Cartesian positions for top-view coordinates based on equipment dimensions and nozzle angles.

6) CAD Rendering & DXF Export
	- `CADService` (services/cad_service.py): theme-aware drawing primitives and symbol renderers for tanks, pumps, valves, sensors, spray balls, relief valves, filters, etc. All entities are assigned to named DXF layers and theme colors (dark/light). Symbol sizes are tuned to layout spacing constants.
	- `DXFService` (services/dxf_service.py): orchestrates the full pipeline: `RuleEngine` → `KnowledgeEngine` → `Validator` → `GraphEngine` → `LayoutEngine` → `CADService`. Produces a DXF saved under `backend/outputs/` with a safe filename.

7) Supporting services
	- `InputProcessor`: normalises raw text or pre-extracted PDF text before sending to `NLPService`.
	- `SchemaBuilder`: tight Pydantic validation and helpful error messages on schema mismatch.

Models (typed schema)
---------------------
All runtime data is represented by the Pydantic models in `backend/models/schema.py`. Key models:

- `EngineeringSchema`: root model holding `equipment`, `nozzles`, `material`, `nodes`, `edges`, and `attributes`.
- `EquipmentSchema`: equipment-level metadata (type, capacity, geometry, dimensions).
- `NozzleSchema`: nozzle id, type, connection (default `TC`), angle and height.
- `NodeSchema`: graph node with `id`, `type` (pump, tank, valve, sensor etc.), `role`, named `ports`, and arbitrary `attributes` (e.g. `tag`, `subtype`, `zone_hint`).
- `EdgeSchema`: connection between nodes with named ports, relation (`inline`, `branch`, `drain`, `instrument`, `loop`), and `medium`.

How to run (quick)
-------------------
Backend (FastAPI / Uvicorn): from `backend/` with the virtualenv active:

```powershell
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Verify health:

```text
http://127.0.0.1:8000/health
```

Frontend (Vite + React): from project root:

```powershell
npm install
npm run dev
```

Extensibility notes
-------------------
- To add a new equipment type: update `knowledge_base.py` with rules and labels, and add any symbol drawing in `cad_service.py` if new graphics are required.
- To change NLP behaviour: modify the prompt in `NLPService` or swap the client implementation. The pipeline relies on the NLP output matching `EngineeringSchema`.
- For CI-friendly runs prefer Python 3.11/3.12 to avoid native build issues for packages like `pydantic-core` on Windows.

Contributing
------------
- Follow the existing modular pattern: keep new features as small engines or helpers.
- Add unit tests for builders in `services/` that exercise `KnowledgeEngine` with representative `intent` dicts.
