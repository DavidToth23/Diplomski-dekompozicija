from typing import List, Tuple, Set
from algorithm.closure import attribute_closure
"""
Višeznačne zavisnosti (Multivalued Dependencies — MVD) i pomoćne funkcije za 4NF.

MVD X ↠ Y važi u relaciji R ako za svaki par torki t1, t2 koje se slažu na X,
postoji torka t3 takva da se slaže sa t1 na X, sa t1 na Y, i sa t2 na R bez (X ∪ Y).

Za algoritmičke potrebe, MVD se reprezentuje kao (lhs: frozenset, rhs: frozenset).
Trivijalna MVD: Y ⊆ X  ili  X ∪ Y = R
"""


MVD = Tuple[frozenset, frozenset]


def is_trivial_mvd(lhs: frozenset, rhs: frozenset, all_attrs: frozenset) -> bool:
    """
    MVD X ↠ Y je trivijalna ako:
      1. Y ⊆ X  (rhs je podskup lhs), ili
      2. X ∪ Y = R  (zajedno pokrivaju celu relaciju)
    """
    return rhs.issubset(lhs) or (lhs | rhs) == all_attrs


def fd_to_mvd(fds: List[Tuple[frozenset, frozenset]]) -> List[MVD]:
    """
    Svaka FZ X → Y implicira MVD X ↠ Y.
    Ovo koristimo za proveru 4NF — FZ je specijalni slučaj MVD.
    """
    return [(lhs, rhs) for lhs, rhs in fds]


def project_mvds(
    attrs: frozenset,
    fds: List[Tuple[frozenset, frozenset]],
    mvds: List[MVD]
) -> List[MVD]:
    """
    Projektuje MVD-ove na podskup atributa `attrs`.

    Za MVD X ↠ Y u originalnoj relaciji R, projektovana MVD na R' ⊆ R je:
    (X ∩ R') ↠ (Y ∩ R') ako je (X ∩ R') ∪ (Y ∩ R') ≠ R' i Y ∩ R' ≠ ∅.

    Takođe uključujemo MVD-ove koji potiču od FZ (X → Y ⟹ X ↠ Y).
    """
    result = []
    seen = set()

    all_mvds = mvds + fd_to_mvd(fds)

    for lhs, rhs in all_mvds:
        proj_lhs = lhs & attrs
        proj_rhs = rhs & attrs

        if not proj_rhs:
            continue
        if proj_rhs.issubset(proj_lhs):
            continue

        key = (proj_lhs, proj_rhs)
        if key in seen:
            continue
        seen.add(key)

        result.append((proj_lhs, proj_rhs))

    return result


def find_4nf_violation(
    attrs: Set[str],
    fds: List[Tuple[frozenset, frozenset]],
    mvds: List[MVD]
) -> MVD | None:
    """
    Traži prvu MVD koja krši 4NF u šemi (attrs, fds, mvds).

    MVD X ↠ Y krši 4NF ako:
      1. nije trivijalna
      2. X nije superključ

    Napomena: svaka FZ X → Y implicira MVD X ↠ Y, pa FZ narušavanja
    BCNF su automatski i 4NF narušavanja. Međutim, dek_BCNF faza
    već garantuje BCNF, pa ovde tražimo samo "čiste" MVD narušavanja.
    """

    attrs_frozen = frozenset(attrs)
    all_mvds = project_mvds(attrs_frozen, fds, mvds)

    for lhs, rhs in all_mvds:
        if is_trivial_mvd(lhs, rhs, attrs_frozen):
            continue

        closure = frozenset(attribute_closure(lhs, fds))
        if closure >= attrs_frozen:
            # X je superključ — MVD je trivijalna u smislu 4NF
            continue

        return (lhs, rhs)

    return None


def is_4nf(
    attrs: Set[str],
    fds: List[Tuple[frozenset, frozenset]],
    mvds: List[MVD]
) -> bool:
    """Proverava da li je šema u 4NF."""
    return find_4nf_violation(attrs, fds, mvds) is None
