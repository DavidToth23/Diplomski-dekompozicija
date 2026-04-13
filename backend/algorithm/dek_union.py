from typing import List, Tuple
from algorithm.closure import attribute_closure, find_candidate_keys
from algorithm.normal_forms import project_fds


def dek_union(
    relations: List[dict],
    fds: List[Tuple[frozenset, frozenset]]
) -> Tuple[List[dict], List[dict]]:
    """
    Segment 'unija' algoritma dekompozicije.

    Spaja šeme relacija koje imaju ekvivalentne ključeve —
    tj. šeme koje modeliraju istu klasu entiteta.

    Uslov ekvivalentnosti: (∃X∈Ki)(∃Y∈Kj)(XF+ = YF+)

    Vraća:
        relations — lista šema nakon spajanja
        steps     — lista koraka za prikaz
    """
    T = list(relations)
    S = []
    steps = []

    steps.append({
        "phase": "init",
        "message": (
            f"Početak unija: "
            f"T = {[sorted(r['attrs']) for r in T]}"
        )
    })

    while T:
        current = T.pop(0)
        Ri = current["attrs"]
        Ki = find_candidate_keys(Ri, current["fds"])

        ri_str = f"R({', '.join(sorted(Ri))})"

        # tražimo šeme u T sa ekvivalentnim ključevima
        merged = False
        i = 0
        while i < len(T):
            other = T[i]
            Rj = other["attrs"]
            Kj = find_candidate_keys(Rj, other["fds"])

            rj_str = f"R({', '.join(sorted(Rj))})"

            # proveravamo uslov ekvivalentnosti ključeva
            # (∃X∈Ki)(∃Y∈Kj)(XF+ = YF+)
            equivalent = False
            for x in Ki:
                for y in Kj:
                    x_closure = frozenset(attribute_closure(x, fds))
                    y_closure = frozenset(attribute_closure(y, fds))
                    if x_closure == y_closure:
                        equivalent = True
                        break
                if equivalent:
                    break

            if equivalent:
                # spajamo Ri i Rj u jednu šemu
                merged_attrs = Ri | Rj
                merged_fds = project_fds(merged_attrs, fds)

                steps.append({
                    "phase": "merge",
                    "r1": sorted(Ri),
                    "r2": sorted(Rj),
                    "merged": sorted(merged_attrs),
                    "message": (
                        f"Spajam {ri_str} i {rj_str} → "
                        f"R({', '.join(sorted(merged_attrs))})"
                    )
                })

                # ažuriramo current i uklanjamo other iz T
                Ri = merged_attrs
                current = {"attrs": merged_attrs, "fds": merged_fds}
                Ki = find_candidate_keys(Ri, merged_fds)
                ri_str = f"R({', '.join(sorted(Ri))})"
                T.pop(i)
                merged = True
            else:
                i += 1

        if not merged:
            steps.append({
                "phase": "no_merge",
                "relation": sorted(Ri),
                "message": f"Nema ekvivalentnih ključeva za {ri_str}"
            })

        S.append(current)

    steps.append({
        "phase": "done",
        "relations": [sorted(r["attrs"]) for r in S],
        "message": (
            f"unija završena — "
            f"dobijeno {len(S)} šema relacija"
        )
    })

    return S, steps