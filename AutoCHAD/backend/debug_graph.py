from services.nlp_service import NLPService
from services.schema_builder import SchemaBuilder
from services.rule_engine import RuleEngine
from services.dxf_service import DXFService

def test():
    try:
        service = NLPService()
        schema_str = service.generate_schema("500L CIP tank connected to lobe pump via valve")
        print("Raw JSON:", schema_str)
        raw_schema = SchemaBuilder.build_from_json(schema_str)
        print("\nParsed Nodes:", raw_schema.nodes)
        print("Parsed Edges:", raw_schema.edges)
        validated_schema = RuleEngine.enforce_rules(raw_schema)
        output_filepath = DXFService.generate_dxf(validated_schema)
        print("\nSUCCESS! Generated DXF at:", output_filepath)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
