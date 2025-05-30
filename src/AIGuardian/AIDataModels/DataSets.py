
from pydantic import BaseModel, Field


class DataSet(BaseModel):
    """
    Represents a dataset with its name, description, and columns.
    """
    name: str = Field(..., description="The name of the dataset.")
    purpose: str = Field(..., description="A brief description of the dataset.")
    fields: list[str] = Field(..., description="A list of column names in the dataset.")

    def __str__(self):
        return f"DataSet(name={self.name}, description={self.purpose}, columns={self.colfieldsumns})"
    
class FieldInfo(BaseModel):
    """
    Represents information about a field in a dataset.
    """
    name: str = Field(..., description="The name of the field.")
    type: str = Field(..., description="The data type of the field (e.g., 'string', 'integer').")
    metadata: str = Field(..., description="A brief description of the field.")
    nullable: bool = Field(True, description="Indicates if the field can contain null values.")
    
    def __str__(self):
        return f"FieldInfo(name={self.name}, data_type={self.type}, description={self.metadata}, nullable={self.nullable})"