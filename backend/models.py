from pydantic import BaseModel
from typing import List


class FunctionalDependency(BaseModel):
    lhs: List[str]
    rhs: List[str]


class SchemaInput(BaseModel):
    relation_name: str
    attributes: List[str]
    functional_dependencies: List[FunctionalDependency]


class SchemaOutput(BaseModel):
    relation_name: str
    attributes: List[str]
    functional_dependencies: List[dict]
    summary: str