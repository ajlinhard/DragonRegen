
from typing import Dict, Any, List, Optional, Union
import json

class SchemaPydantic:
    """
    Class to generate Pydantic models from column definitions.
    """

    @staticmethod
    def map_type_to_pydantic(col_type: str, nullable: bool) -> str:
        """Map column types to Pydantic/Python types"""
        type_mapping = {
            "Integer": "int",
            "String": "str", 
            "Timestamp": "datetime",
            "JSON": "Dict[str, Any]",
            "Array": "List[Any]"
        }
        
        base_type = type_mapping.get(col_type, "Any")
        
        # Handle nullable fields
        if nullable:
            return f"Optional[{base_type}]"
        return base_type

    @staticmethod
    def generate_pydantic_class(columns: List[Dict[str, Any]], class_name: str = "Artifact", b_include_imports: bool=True) -> str:
        """Generate Pydantic class code from column definitions"""
        
        # Required imports
        imports = []
        # Include imports if specified
        if b_include_imports:
            imports = [
                "from pydantic import BaseModel, Field",
                "from typing import Optional, List, Dict, Any",
                "from datetime import datetime"
            ]
        
        # Start building the class
        class_lines = [
            f"class {class_name}(BaseModel):"
        ]
        
        # Process each column
        for col in columns:
            name = col["name"]
            col_type = col["type"]
            nullable = col.get("nullable", True)
            description = col.get("metadata", {}).get("description", "")
            
            # Map to Pydantic type
            pydantic_type = SchemaPydantic.map_type_to_pydantic(col_type, nullable)
            
            # Build field definition
            if description:
                field_def = f'    {name}: {pydantic_type} = Field(..., description="{description}")'
            else:
                field_def = f'    {name}: {pydantic_type}'
            
            # Handle nullable fields with None default
            if nullable and not field_def.endswith('Field(...)'):
                field_def = f'    {name}: {pydantic_type} = None'
            elif nullable and 'Field(' in field_def:
                field_def = field_def.replace('Field(...,', 'Field(None,')
            
            class_lines.append(field_def)
        
        # Combine everything
        code_lines = imports + ["", ""] + class_lines + [""]
        
        return "\n".join(code_lines)

