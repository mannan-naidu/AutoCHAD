from services.nlp_service import NLPService
from services.schema_builder import SchemaBuilder

def test():
    try:
        service = NLPService()
        print("Calling Gemini...")
        schema_str = service.generate_schema("I need a pharmaceutical intermediate CIP tank roughly 2000mm in diameter, with a conical bottom, three top inlet nozzles, and one bottom outlet.")
        print("Raw JSON:", schema_str)
        schema = SchemaBuilder.build_from_json(schema_str)
        print("Schema Built:", schema)
    except Exception as e:
        import traceback
        print("FAILED:")
        traceback.print_exc()

if __name__ == "__main__":
    test()
