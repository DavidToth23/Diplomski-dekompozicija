from typing import List, Tuple, Set, Optional
from algorithm.dek_bcnf import dek_bcnf
from algorithm.dek_union import dek_union
from algorithm.dek_4nf import dek_4nf
from algorithm.dek_5nf import dek_5nf


def decompose(
    attrs: Set[str],
    fds: List[Tuple[frozenset, frozenset]],
    target_nf: str = "BCNF",
    mvds: list = None,
    join_deps: list = None
) -> dict:
    """
    Glavni orkestrator algoritma dekompozicije.

    Izvršava segmente algoritma redom do željene normalne forme:
        BCNF → dek_bcnf + unija
        4NF  → BCNF + dek_4nf 
        5NF  → 4NF  + dek_5nf

    Parametri:
        attrs     — skup atributa univerzalne relacije U
        fds       — skup funkcionalnih zavisnosti F
        target_nf — ciljna normalna forma: "BCNF", "4NF" ili "5NF"
        mvds      — skup višeznačnih zavisnosti M    (potrebno za 4NF/5NF)
        join_deps — skup zavisnosti spajanja J       (potrebno za 5NF)

    Vraća dict sa:
        relations — finalni skup šema relacija
        steps     — svi koraci svih faza za prikaz na frontendu
        target_nf — ciljna normalna forma
        relation_count  — broj dobijenih sema
    """
    if mvds is None:
        mvds = []
    if join_deps is None:
        join_deps = []
    
    all_steps = []

    # ── Faza 1: dek_BCNF ─────────────────────────────────────────────────────
    bcnf_relations, bcnf_steps = dek_bcnf(attrs, fds)
    all_steps.extend(bcnf_steps)

    # ── Faza 2: unija ─────────────────────────────────────────────────────────
    union_relations, union_steps = dek_union(bcnf_relations, fds)
    all_steps.extend(union_steps)

    current_relations = union_relations

    # ── Faza 3: dek_4NF ────────────────────────────────────────
    if target_nf in ("4NF", "5NF"):
        relations_4nf, steps_4nf = dek_4nf(current_relations, fds, mvds)
        all_steps.extend(steps_4nf)
        current_relations = relations_4nf

    # ── Faza 4: dek_5NF ────────────────────────────────────────
    if target_nf == "5NF":
        relations_5nf, steps_5nf = dek_5nf(current_relations, fds, join_deps)
        all_steps.extend(steps_5nf)
        current_relations = relations_5nf

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
                        f"{{{', '.join(sorted(lhs))}}} -> "
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