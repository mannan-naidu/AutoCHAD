class InputProcessor:
    @staticmethod
    def process(input_type: str, content: str) -> str:
        """
        Accepts raw text OR structured spec.
        If PDF -> assumes text already extracted.
        Normalizes input for the NLP layer by cleaning up common whitespace or encoding issues.
        """
        if not content or not content.strip():
            raise ValueError("Input content cannot be empty.")
        
        normalized_content = " ".join(content.split())
        
        if input_type.lower() == "pdf":
            # For this MVP, we treat PDF content as pre-extracted text
            normalized_content = f"[Extracted from PDF]: {normalized_content}"
            
        return normalized_content
