from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import SchemaInput, SchemaOutput, FunctionalDependency, DecompositionOutput
from validation import validate_fd_attributes

app = FastAPI(title="Dekompozicija Seme Relacije")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _parse_fds(fd_list):
    """Konvertuje FunctionalDependency modele u (frozenset, frozenset) parove."""
    return [
        (frozenset(fd.lhs), frozenset(fd.rhs))
        for fd in fd_list
    ]


def _parse_mvds(mvd_list):
    """Konvertuje MultivaluedDependency modele u (frozenset, frozenset) parove."""
    return [
        (frozenset(mvd.lhs), frozenset(mvd.rhs))
        for mvd in (mvd_list or [])
    ]


def _parse_join_deps(jd_list):
    """Konvertuje JoinDependency modele u liste frozenset-ova."""
    return [
        [frozenset(component) for component in jd.components]
        for jd in (jd_list or [])
    ]


@app.post("/api/schema", response_model=SchemaOutput)
def process_schema(data: SchemaInput):
    """Endpoint za prikaz i validaciju seme — bez dekompozicije."""
    sorted_attrs = sorted(set(data.attributes))
    attrs_set = set(sorted_attrs)

    validate_fd_attributes(attrs_set, data.functional_dependencies)

    formatted_fds = []
    for fd in data.functional_dependencies:
        lhs_sorted = sorted(set(fd.lhs))
        rhs_sorted = sorted(set(fd.rhs))
        formatted_fds.append({
            "lhs": lhs_sorted,
            "rhs": rhs_sorted,
            "display": f"{', '.join(lhs_sorted)} -> {', '.join(rhs_sorted)}"
        })

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


@app.post("/api/decompose", response_model=DecompositionOutput)
def decompose_schema(data: SchemaInput):
    """
    Endpoint za dekompoziciju seme relacije do zeljene normalne forme.

    Podrzane normalne forme: BCNF, 4NF, 5NF

    Za 4NF: potrebno je navesti multivalued_dependencies (MVD).
    Za 5NF: potrebno je navesti join_dependencies (JD) pored MVD.
    """
    from algorithm.decomposition import decompose

    attrs_set = set(data.attributes)
    validate_fd_attributes(attrs_set, data.functional_dependencies)

    target_nf = (data.target_nf or "BCNF").upper()
    if target_nf not in ("BCNF", "4NF", "5NF"):
        raise HTTPException(
            status_code=400,
            detail=f"Nepodrzana normalna forma: {target_nf}. Koristite BCNF, 4NF ili 5NF."
        )

    fds = _parse_fds(data.functional_dependencies)
    mvds = _parse_mvds(data.multivalued_dependencies)
    join_deps = _parse_join_deps(data.join_dependencies)

    result = decompose(
        attrs=attrs_set,
        fds=fds,
        target_nf=target_nf,
        mvds=mvds,
        join_deps=join_deps
    )

    return DecompositionOutput(
        relation_name=data.relation_name,
        target_nf=result["target_nf"],
        relations=result["relations"],
        steps=result["steps"],
        relation_count=result["relation_count"]
    )


@app.get("/api/health")
def health():
    return {"status": "ok"}
