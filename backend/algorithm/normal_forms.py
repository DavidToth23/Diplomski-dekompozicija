from typing import List, Tuple, Set
from algorithm.closure import attribute_closure, find_candidate_keys


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

def find_3nf_violation(
    attrs: Set[str],
    fds: List[Tuple[frozenset, frozenset]]
) -> Tuple[frozenset, frozenset] | None:
    """
    Vraća prvu FZ koja krši 3NF, ili None ako je šema u 3NF.

    FZ X→Y krši 3NF ako:
      1. nije trivijalna (Y ⊄ X)
      2. X nije superključ
      3. postoji atribut u Y koji nije prime atribut
    """
    attrs_frozen = frozenset(attrs)
    projected = project_fds(attrs, fds)

    candidate_keys = find_candidate_keys(attrs, fds)

    prime_attrs = set()
    for key in candidate_keys:
        prime_attrs.update(key)

    for lhs, rhs in projected:
        is_trivial = rhs.issubset(lhs)

        closure = attribute_closure(lhs, projected)
        is_superkey = frozenset(closure) >= attrs_frozen

        rhs_all_prime = all(attr in prime_attrs for attr in rhs)

        if not is_trivial and not is_superkey and not rhs_all_prime:
            return (lhs, rhs)

    return None

def is_3nf(
    attrs: Set[str],
    fds: List[Tuple[frozenset, frozenset]]
) -> bool:
    """
    Proverava da li je šema (attrs, fds) u 3NF.
    """
    return find_3nf_violation(attrs, fds) is None