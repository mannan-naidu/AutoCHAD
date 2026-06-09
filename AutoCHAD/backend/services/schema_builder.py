import json
import re
from models.schema import EngineeringSchema

def extract_json(text):
    match = re.search(r'{.*}', text, re.DOTALL)
    return match.group() if match else text

class SchemaBuilder:
    @staticmethod
    def build_from_json(json_string: str) -> EngineeringSchema:
        """
        Parses the JSON string from NLP and builds the strictly typed EngineeringSchema.
        """
        try:
            clean_json = extract_json(json_string)
            data = json.loads(clean_json)
            schema = EngineeringSchema(**data)
            return schema
        except json.JSONDecodeError as jde:
            raise ValueError(f"Failed to decode JSON from NLP: {str(jde)}")
        except Exception as e:
            raise ValueError(f"Failed to validate matching schema: {str(e)}")
