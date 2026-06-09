from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os

from services.input_processor import InputProcessor
from services.nlp_service import NLPService
from services.schema_builder import SchemaBuilder
from services.rule_engine import RuleEngine
from services.dxf_service import DXFService

router = APIRouter()

class GenerateRequest(BaseModel):
    input_type: str  # "text" | "pdf"
    content: str     # "user description OR parsed spec"

@router.post("/generate-dxf")
async def generate_dxf(payload: GenerateRequest):
    try:
        print("Received request")
        # Step 1: Input Processor
        cleaned_input = InputProcessor.process(payload.input_type, payload.content)
        
        # Step 2: NLP Service extracting Schema
        nlp_service = NLPService()
        json_schema_str = nlp_service.generate_schema(cleaned_input)
        print("RAW LLM OUTPUT:", json_schema_str)
        
        # Step 3: Parse and coerce to Pydantic Model
        raw_schema = SchemaBuilder.build_from_json(json_schema_str)
        print("Parsed Schema:", raw_schema.dict())
        
        # Step 4: Process Interpreter — extract engineering intent from raw URS
        from services.process_interpreter import ProcessInterpreter
        from services.knowledge_engine import KnowledgeEngine
        intent = ProcessInterpreter.interpret(cleaned_input)

        # Step 5: Dynamic graph builder — convert intent to full P&ID topology
        enriched_schema = KnowledgeEngine.build_process_graph(raw_schema, intent)
        
        # Step 6: Rule Engine enforces ASME/GMP standard logic
        validated_schema = RuleEngine.enforce_rules(enriched_schema)
        
        print("Generating DXF...")
        output_filepath = DXFService.generate_dxf(validated_schema)
        print("DXF Path:", output_filepath)
        
        return {
            "status": "success",
            "message": "DXF File generated successfully complying with BPE/GMP principles.",
            "file_path": output_filepath,
            "intent": intent,
            "parsed_schema": validated_schema.dict()
        }

    except ValueError as ve:
        error_msg = f"Validation Error: {str(ve)}"
        print("ERROR:", error_msg)
        return JSONResponse(
            status_code=500,
            content={"error": error_msg}
        )
    except Exception as e:
        error_msg = f"Internal Server Error: {str(e)}"
        print("ERROR:", str(e))
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
