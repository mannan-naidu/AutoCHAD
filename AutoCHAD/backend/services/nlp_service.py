import os
import json
from dotenv import load_dotenv
from groq import Groq
from models.schema import EngineeringSchema

# Ensure environments are loaded
load_dotenv()

class NLPService:
    def __init__(self):
        # Initializing the Groq client which automatically searches for GROQ_API_KEY if not explicitly passed
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment.")
        self.client = Groq(api_key=self.api_key)

    def generate_schema(self, user_input: str) -> str:
        """
        Calls Groq to extract the engineering schema strictly as JSON.
        """
        # We fetch the exact schema definition dynamically to assist the LLM
        schema_definition = json.dumps(EngineeringSchema.model_json_schema(), indent=2)
        
        prompt = f"""
You are a process design engineer specialising in pharmaceutical and chemical plant design.

Your job is to extract a PROCESS GRAPH from the user's specification.

You MUST:
- Identify every piece of equipment
- Identify flow direction and connections
- Identify control valves, sensors, and safety devices
- Create a fully connected graph of nodes and edges
- Output a complete engineering system — NOT a minimal list

If the specification contains only one equipment type:
→ Infer a minimal valid process loop (valves, instruments, safety)
→ DO NOT assume tanks unless explicitly mentioned

Return ONLY valid JSON matching this schema:
{schema_definition}

RULES:
* Output ONLY JSON — no explanation, no markdown
* Node IDs must be UPPERCASE and prefixed: PUMP_1, VALVE_IN, etc.
* Normalise types: "lobe pump" → "pump", "agitator tank" → "tank"
* material defaults to SS316L
* nozzle connections default to TC (Tri-Clamp)
* Always include at least one sensor node
"""

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": user_input,
                    }
                ],
                model="llama-3.1-8b-instant", # Updated to currently supported model
                temperature=0.1,
                response_format={"type": "json_object"},
                timeout=15.0
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"NLP extraction failed via Groq: {str(e)}")
