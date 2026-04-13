from typing import List, Tuple, Set, Optional
from algorithm.dek_bcnf import dek_bcnf
from algorithm.dek_union import dek_union


def decompose(
    attrs: Set[str],
    fds: List[Tuple[frozenset, frozenset]],
    target_nf: str = "BCNF"
) -> dict:
    """
    Glavni orkestrator algoritma dekompozicije.

    Izvršava segmente algoritma redom do željene normalne forme:
        BCNF → dek_bcnf + unija
        4NF  → BCNF + dek_4nf  (još nije implementirano)
        5NF  → 4NF  + dek_5nf  (još nije implementirano)

    Parametri:
        attrs     — skup atributa univerzalne relacije U
        fds       — skup funkcionalnih zavisnosti F
        target_nf — ciljna normalna forma: "BCNF", "4NF" ili "5NF"

    Vraća dict sa:
        relations — finalni skup šema relacija
        steps     — svi koraci svih faza za prikaz na frontendu
        target_nf — ciljna normalna forma
    """
    all_steps = []

    # ── Faza 1: dek_BCNF ─────────────────────────────────────────────────────
    bcnf_relations, bcnf_steps = dek_bcnf(attrs, fds)
    all_steps.extend(bcnf_steps)

    # ── Faza 2: unija ─────────────────────────────────────────────────────────
    union_relations, union_steps = dek_union(bcnf_relations, fds)
    all_steps.extend(union_steps)

    current_relations = union_relations

    # ── Faza 3: dek_4NF (placeholder) ────────────────────────────────────────
    if target_nf in ("4NF", "5NF"):
        all_steps.append({
            "phase": "not_implemented",
            "message": "dek_4NF još nije implementiran"
        })

    # ── Faza 4: dek_5NF (placeholder) ────────────────────────────────────────
    if target_nf == "5NF":
        all_steps.append({
            "phase": "not_implemented",
            "message": "dek_5NF još nije implementiran"
        })

    # ── Formatiranje rezultata ────────────────────────────────────────────────
    formatted_relations = []
    for rel in current_relations:
        formatted_relations.append({
            "attrs": sorted(rel["attrs"]),
            "fds": [
                {
                    "lhs": sorted(lhs),
                    "rhs": sorted(rhs),
                    "display": (
                        f"{{{', '.join(sorted(lhs))}}} → "
                        f"{{{', '.join(sorted(rhs))}}}"
                    )
                }
                for lhs, rhs in rel["fds"]
            ]
        })

    return {
        "relations": formatted_relations,
        "steps": all_steps,
        "target_nf": target_nf,
        "relation_count": len(formatted_relations)
    }