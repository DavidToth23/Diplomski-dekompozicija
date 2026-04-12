from typing import List, Set, Tuple
from itertools import combinations


def attribute_closure(
    attrs_subset: Set[str],
    fds: List[Tuple[frozenset, frozenset]],
    steps: list = None
) -> Set[str]:
    """
    Računa zatvaranje skupa atributa X+ u odnosu na skup FZ F.

    attrs_subset — početni skup atributa X
    fds          — lista FZ kao (lhs, rhs) parovi frozenset-ova
    steps        — ako se prosledi lista, upisuje korake za prikaz na frontendu
    """
    closure = set(attrs_subset)

    if steps is not None:
        steps.append({
            "action": "init",
            "closure": sorted(closure),
            "message": f"Početno zatvaranje: {{{', '.join(sorted(closure))}}}"
        })

    changed = True
    while changed:
        changed = False
        for lhs, rhs in fds:
            new_attrs = rhs - closure
            if lhs.issubset(closure) and new_attrs:
                closure |= rhs
                changed = True
                if steps is not None:
                    steps.append({
                        "action": "apply_fd",
                        "fd": f"{{{', '.join(sorted(lhs))}}} → {{{', '.join(sorted(rhs))}}}",
                        "added": sorted(new_attrs),
                        "closure": sorted(closure),
                        "message": (
                            f"Primenjujem {{{', '.join(sorted(lhs))}}} → {{{', '.join(sorted(rhs))}}}: "
                            f"dodajem {{{', '.join(sorted(new_attrs))}}} → "
                            f"zatvaranje = {{{', '.join(sorted(closure))}}}"
                        )
                    })

    if steps is not None:
        steps.append({
            "action": "result",
            "closure": sorted(closure),
            "message": f"Rezultat: {{{', '.join(sorted(attrs_subset))}}}⁺ = {{{', '.join(sorted(closure))}}}"
        })

    return closure


def is_superkey(
    subset: Set[str],
    all_attrs: Set[str],
    fds: List[Tuple[frozenset, frozenset]]
) -> bool:
    """
    Proverava da li je subset superključ relacije sa atributima all_attrs.
    X je superključ ako je X+ = R.
    """
    return attribute_closure(subset, fds) == all_attrs

def find_candidate_keys(
    all_attrs: Set[str],
    fds: List[Tuple[frozenset, frozenset]]
) -> List[frozenset]:
    """
    Pronalazi sve kandidat ključeve relacije.
    Kandidat ključ je minimalni superključ —
    nijedan pravi podskup nije superključ.
    """
    candidate_keys = []
    all_frozen = frozenset(all_attrs)

    # probamo skupove rastuće veličine
    for size in range(1, len(all_attrs) + 1):
        for subset in combinations(sorted(all_attrs), size):
            subset_frozen = frozenset(subset)

            # preskačemo ako već sadrži poznati kandidat ključ
            if any(ck.issubset(subset_frozen) for ck in candidate_keys):
                continue

            if attribute_closure(subset_frozen, fds) == all_frozen:
                candidate_keys.append(subset_frozen)

    return candidate_keys