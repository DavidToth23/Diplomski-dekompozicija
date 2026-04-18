from pydantic import BaseModel
from typing import List, Optional


class FunctionalDependency(BaseModel):
    lhs: List[str]
    rhs: List[str]


class MultivaluedDependency(BaseModel):
    lhs: List[str]
    rhs: List[str]


class JoinDependency(BaseModel):
    components: List[List[str]]


class SchemaInput(BaseModel):
    relation_name: str
    attributes: List[str]
    functional_dependencies: List[FunctionalDependency]
    multivalued_dependencies: Optional[List[MultivaluedDependency]] = []
    join_dependencies: Optional[List[JoinDependency]] = []
    target_nf: Optional[str] = "BCNF"


class SchemaOutput(BaseModel):
    relation_name: str
    attributes: List[str]
    functional_dependencies: List[dict]
    summary: str


class DecompositionOutput(BaseModel):
    relation_name: str
    target_nf: str
    relations: List[dict]
    steps: List[dict]
    relation_count: int