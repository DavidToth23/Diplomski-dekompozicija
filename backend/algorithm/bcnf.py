from typing import List, Tuple, Set
from algorithm.closure import attribute_closure


def project_fds(
    attrs: Set[str],
    fds: List[Tuple[frozenset, frozenset]]
) -> List[Tuple[frozenset, frozenset]]:
    """
    Projektuje skup FZ na podskup atributa attrs.
    Za svaki LHS koji je podskup attrs, računa zatvaranje
    i zadržava samo atribute koji su u attrs.
    """
    result = []
    attrs_frozen = frozenset(attrs)
    seen = set()

    for lhs, _ in fds:
        lhs_in_attrs = lhs & attrs_frozen
        if lhs_in_attrs in seen:
            continue
        seen.add(lhs_in_attrs)

        closure = attribute_closure(lhs_in_attrs, fds)
        rhs = frozenset(closure) & attrs_frozen - lhs_in_attrs

        if rhs:
            result.append((lhs_in_attrs, rhs))

    return result


def find_bcnf_violation(
    attrs: Set[str],
    fds: List[Tuple[frozenset, frozenset]]
) -> Tuple[frozenset, frozenset] | None:
    """
    Vraća prvu FZ koja krši BCNF, ili None ako je šema u BCNF.
    FZ X→Y krši BCNF ako:
      1. nije trivijalna (Y ⊄ X)
      2. X nije superključ
    """
    attrs_frozen = frozenset(attrs)
    projected = project_fds(attrs, fds)

    for lhs, rhs in projected:
        is_trivial = rhs.issubset(lhs)
        closure = attribute_closure(lhs, projected)
        is_superkey = frozenset(closure) >= attrs_frozen

        if not is_trivial and not is_superkey:
            return (lhs, rhs)

    return None


def is_bcnf(
    attrs: Set[str],
    fds: List[Tuple[frozenset, frozenset]]
) -> bool:
    """
    Proverava da li je šema (attrs, fds) u BCNF.
    """
    return find_bcnf_violation(attrs, fds) is None