from services.nlp_service import NLPService
from services.schema_builder import SchemaBuilder
from services.rule_engine import RuleEngine
from services.dxf_service import DXFService

def test():
    try:
        service = NLPService()
        schema_str = service.generate_schema("I need a pharmaceutical intermediate CIP tank roughly 2000mm in diameter, with a conical bottom, three top inlet nozzles, and one bottom outlet.")
        raw_schema = SchemaBuilder.build_from_json(schema_str)
        validated_schema = RuleEngine.enforce_rules(raw_schema)
        output_filepath = DXFService.generate_dxf(validated_schema)
        print("Generated DXF at:", output_filepath)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
