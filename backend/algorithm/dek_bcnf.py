from typing import List, Tuple, Set
from algorithm.normal_forms import project_fds, is_bcnf
from algorithm.fd_selection import select_fd


def dek_bcnf(
    attrs: Set[str],
    fds: List[Tuple[frozenset, frozenset]]
) -> Tuple[List[dict], List[dict]]:
    """
    Segment 'dek_BCNF' algoritma dekompozicije.
    
    Dekomponuje šemu (attrs, fds) na skup šema u BCNF
    koristeći strategije izbora FZ P1 > P2 > P3.
    
    Vraća:
        relations — lista šema u BCNF, svaka kao dict sa 'attrs' i 'fds'
        steps     — lista koraka za prikaz
    """
    # T — radni skup šema koje još treba proveriti
    # S — finalni skup šema u BCNF
    T = [{"attrs": frozenset(attrs), "fds": fds}]
    S = []
    steps = []

    steps.append({
        "phase": "init",
        "message": (
            f"Početak dek_BCNF: "
            f"T = {{R({', '.join(sorted(attrs))})}}, S = ∅"
        )
    })

    while T:
        # uzimamo jednu šemu iz T
        current = T.pop(0)
        Ri = current["attrs"]
        Fi = current["fds"]

        ri_str = f"R({', '.join(sorted(Ri))})"

        # proveravamo BCNF uslov iz pseudokoda:
        if is_bcnf(Ri, Fi):
            S.append(current)
            steps.append({
                "phase": "bcnf_ok",
                "relation": sorted(Ri),
                "message": f"✓ {ri_str} je u BCNF → premještamo u S"
            })
        else:
            # biramo FZ za dekompoziciju po prioritetu P1 > P2 > P3
            selected = select_fd(Ri, Fi)

            if selected is None:
                # ne bi trebalo da se desi ako is_bcnf vraca False
                S.append(current)
                continue

            lhs, rhs_attr = selected
            a = frozenset({rhs_attr})

            lhs_str = f"{{{', '.join(sorted(lhs))}}}"
            steps.append({
                "phase": "decompose",
                "relation": sorted(Ri),
                "fd_lhs": sorted(lhs),
                "fd_rhs": rhs_attr,
                "message": (
                    f"✗ {ri_str} nije u BCNF — "
                    f"dekompozicija po {lhs_str} → {rhs_attr}"
                )
            })

            # R1 = Ri \ {A}, R2 = Y ∪ {A}
            r1_attrs = Ri - a
            r2_attrs = lhs | a

            f1 = project_fds(r1_attrs, Fi)
            f2 = project_fds(r2_attrs, Fi)

            r1_str = f"R({', '.join(sorted(r1_attrs))})"
            r2_str = f"R({', '.join(sorted(r2_attrs))})"

            steps.append({
                "phase": "split",
                "r1": sorted(r1_attrs),
                "r2": sorted(r2_attrs),
                "message": f"  Delimo na: {r1_str} i {r2_str}"
            })

            T.append({"attrs": r1_attrs, "fds": f1})
            T.append({"attrs": r2_attrs, "fds": f2})

    steps.append({
        "phase": "done",
        "relations": [sorted(s["attrs"]) for s in S],
        "message": (
            f"dek_BCNF završen — "
            f"dobijeno {len(S)} šema relacija"
        )
    })

    return S, steps