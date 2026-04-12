from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import SchemaInput, SchemaOutput, FunctionalDependency
from validation import validate_fd_attributes

app = FastAPI(title="Dekompozicija Seme Relacije")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/schema", response_model=SchemaOutput)
def process_schema(data: SchemaInput):
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
            "display": f"{', '.join(lhs_sorted)} → {', '.join(rhs_sorted)}"
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


@app.get("/api/health")
def health():
    return {"status": "ok"}