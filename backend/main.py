from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Dekompozicija Seme Relacije")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class FunctionalDependency(BaseModel):
    """
    Jedna funkcionalna zavisnost: lhs → rhs
    Primer: {"lhs": ["A", "B"], "rhs": ["C"]}
    """
    lhs: List[str]   # leva strana fz
    rhs: List[str]   # desna strana fz

class SchemaInput(BaseModel):
    """
    Ulazni podaci koje frontend salje.
    """
    relation_name: str           # ime relacije
    attributes: List[str]        # skup obelezja
    functional_dependencies: List[FunctionalDependency] # skup fz


class SchemaOutput(BaseModel):
    """
    Izlazni podaci koje backend vraća frontendu.
    (Za sada samo echo)
    """
    relation_name: str
    attributes: List[str]
    functional_dependencies: List[dict]  # stringovani prikaz
    summary: str                         # citljivi sazetak

@app.post("/api/schema", response_model=SchemaOutput)
def process_schema(data: SchemaInput):
    """
    Faza 1: Prima semu, vraca je normalizovanu nazad.
    """
    
    # Sortiramo obelezja
    sorted_attrs = sorted(set(data.attributes))

    # Normalizujemo i formatiramo FZ-ove
    formatted_fds = []
    for fd in data.functional_dependencies:
        lhs_sorted = sorted(set(fd.lhs))
        rhs_sorted = sorted(set(fd.rhs))
        formatted_fds.append({
            "lhs": lhs_sorted,
            "rhs": rhs_sorted,
            "display": f"{', '.join(lhs_sorted)} → {', '.join(rhs_sorted)}"
        })

    # Citljivi sazetak
    summary = (
        f"Relacija {data.relation_name}("
        f"{', '.join(sorted_attrs)}) "
        f"ima {len(formatted_fds)} funkcionaln"
        f"{'u zavisnost' if len(formatted_fds) == 1 else 'e zavisnosti' if len(formatted_fds) in [2,3,4] else 'ih zavisnosti'}."
    )

    return SchemaOutput(
        relation_name=data.relation_name,
        attributes=sorted_attrs,
        functional_dependencies=formatted_fds,
        summary=summary,
    )


@app.get("/api/health")
def health():
    return {"status": "ok"}