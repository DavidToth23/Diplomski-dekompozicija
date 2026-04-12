from typing import List, Tuple, Set
from algorithm.closure import attribute_closure
from algorithm.bcnf import project_fds


def check_p3(
    lhs: frozenset,
    rhs_attr: str,
    attrs: Set[str],
    fds: List[Tuple[frozenset, frozenset]]
) -> bool:
    """
    S3 — strategija obezbeđenja progresa.
    Y→A zadovoljava P3 ako:
    1. A nije u Y (netrivijalna)
    2. Y∪{A} ≠ R (ne obuhvata ceo skup atributa)
    3. Y nije superključ
    4. A zaista sledi iz Y (FZ važi)
    """
    attrs_frozen = frozenset(attrs)
    a = frozenset({rhs_attr})

    is_nontrivial  = rhs_attr not in lhs
    not_full_set   = (lhs | a) != attrs_frozen
    not_superkey   = frozenset(attribute_closure(lhs, fds)) < attrs_frozen
    # FZ mora zaista da važi — rhs_attr mora biti u zatvaranju lhs
    fd_holds       = rhs_attr in attribute_closure(lhs, fds)

    return is_nontrivial and not_full_set and not_superkey and fd_holds


def check_p2(
    lhs: frozenset,
    rhs_attr: str,
    attrs: Set[str],
    fds: List[Tuple[frozenset, frozenset]]
) -> bool:
    """
    S2 — strategija očuvanja polaznog skupa FZ.
    Y→A zadovoljava P2 ako zadovoljava P3 i dekompozicija čuva sve FZ:
    F⁺ = (F|Y(R\\{A}) ∪ F|Y{A})⁺
    """
    if not check_p3(lhs, rhs_attr, attrs, fds):
        return False

    a = frozenset({rhs_attr})
    r1_attrs = frozenset(attrs) - a
    r2_attrs = lhs | a

    f1 = project_fds(r1_attrs, fds)
    f2 = project_fds(r2_attrs, fds)
    combined = f1 + f2

    for orig_lhs, orig_rhs in fds:
        closure_in_combined = attribute_closure(orig_lhs, combined)
        if not orig_rhs.issubset(closure_in_combined):
            return False

    return True


def check_p1(
    lhs: frozenset,
    rhs_attr: str,
    attrs: Set[str],
    fds: List[Tuple[frozenset, frozenset]]
) -> bool:
    """
    S1 — idealna strategija.
    Y→A zadovoljava P1 ako zadovoljava P2 i Y je na kraju lanca izvođenja:
    (∀X∈lhs(F))((X)F⁺ ≠ (Y)F⁺ → Y ⊄ (X)F⁺)
    """
    if not check_p2(lhs, rhs_attr, attrs, fds):
        return False

    lhs_closure = frozenset(attribute_closure(lhs, fds))

    for other_lhs, _ in fds:
        other_closure = frozenset(attribute_closure(other_lhs, fds))
        if other_closure != lhs_closure:
            if lhs.issubset(other_closure):
                return False

    return True


def select_fd(
    attrs: Set[str],
    fds: List[Tuple[frozenset, frozenset]]
) -> Tuple[frozenset, str] | None:
    """
    Bira narušavajuću FZ po prioritetu P1 > P2 > P3.
    Vraća (lhs, rhs_attr) ili None ako je šema u BCNF.
    """
    projected = project_fds(attrs, fds)

    single_rhs_fds = []
    for lhs, rhs in projected:
        for attr in rhs:
            single_rhs_fds.append((lhs, attr))

    for lhs, attr in single_rhs_fds:
        if check_p1(lhs, attr, attrs, fds):
            return (lhs, attr)

    for lhs, attr in single_rhs_fds:
        if check_p2(lhs, attr, attrs, fds):
            return (lhs, attr)

    for lhs, attr in single_rhs_fds:
        if check_p3(lhs, attr, attrs, fds):
            return (lhs, attr)

    return None