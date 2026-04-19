from algorithm.mvd import (
    is_trivial_mvd,
    fd_to_mvd,
    project_mvds,
    find_4nf_violation,
    is_4nf,
)

# ── Primer 1: Klasičan 4NF primer ────────────────────────────────────────────
# R(kurs, nastavnik, udzbenik)
# MVD: kurs ↠ nastavnik, kurs ↠ udzbenik
# Ključ: {kurs, nastavnik, udzbenik} (ceo skup)
# Narušava 4NF jer kurs nije superključ

ATTRS_KNU = frozenset({"kurs", "nastavnik", "udzbenik"})
FDS_KNU = []
MVDS_KNU = [
    (frozenset({"kurs"}), frozenset({"nastavnik"})),
    (frozenset({"kurs"}), frozenset({"udzbenik"})),
]

# ── Primer 2: R(A,B,C), MVD A ↠ B ───────────────────────────────────────────
# Krši 4NF ako A nije superključ

ATTRS_ABC = frozenset({"A", "B", "C"})
FDS_ABC = []
MVDS_ABC = [
    (frozenset({"A"}), frozenset({"B"})),
]

# ── Primer 3: R(A,B), FZ A→B (implikuje MVD A ↠ B) ──────────────────────────
# A je superključ → 4NF nije narušena

ATTRS_AB = frozenset({"A", "B"})
FDS_AB = [(frozenset({"A"}), frozenset({"B"}))]
MVDS_AB = []


# --- is_trivial_mvd ---

# Y ⊆ X → trivijalna (rhs podskup lhs)
def test_trivial_mvd_rhs_subset_lhs():
    assert is_trivial_mvd(frozenset({"A", "B"}), frozenset({"A"}), frozenset({"A", "B", "C"})) == True

# X ∪ Y = R → trivijalna
def test_trivial_mvd_covers_all():
    assert is_trivial_mvd(frozenset({"A", "B"}), frozenset({"C"}), frozenset({"A", "B", "C"})) == True

# netrivijalna MVD — ostaje C van X ∪ Y
def test_nontrivial_mvd():
    assert is_trivial_mvd(frozenset({"A"}), frozenset({"B"}), frozenset({"A", "B", "C"})) == False

# jednočlana relacija — X ∪ Y ne može biti R ako je R veće
def test_trivial_mvd_single_attr():
    assert is_trivial_mvd(frozenset({"A"}), frozenset({"A"}), frozenset({"A", "B"})) == True

# prazni skupovi — trivijalna jer je rhs ⊆ lhs (oba prazna)
def test_trivial_mvd_empty():
    assert is_trivial_mvd(frozenset(), frozenset(), frozenset({"A", "B"})) == True


# --- fd_to_mvd ---

# svaka FZ mora biti konvertovana u MVD
def test_fd_to_mvd_count():
    fds = [
        (frozenset({"A"}), frozenset({"B"})),
        (frozenset({"B"}), frozenset({"C"})),
    ]
    result = fd_to_mvd(fds)
    assert len(result) == 2

# lhs i rhs se čuvaju
def test_fd_to_mvd_preserves_sets():
    fds = [(frozenset({"A"}), frozenset({"B", "C"}))]
    result = fd_to_mvd(fds)
    assert result[0] == (frozenset({"A"}), frozenset({"B", "C"}))

# prazna lista FZ → prazna lista MVD
def test_fd_to_mvd_empty():
    assert fd_to_mvd([]) == []


# --- project_mvds ---

# projekcija na ceo skup — MVD ostaje
def test_project_mvds_full_set():
    result = project_mvds(ATTRS_KNU, FDS_KNU, MVDS_KNU)
    lhs_list = [lhs for lhs, _ in result]
    assert frozenset({"kurs"}) in lhs_list

# projekcija na podskup koji sadrži lhs i rhs MVD
def test_project_mvds_subset_with_mvd():
    result = project_mvds(frozenset({"kurs", "nastavnik"}), FDS_KNU, MVDS_KNU)
    # kurs ↠ nastavnik treba da bude prisutna
    assert len(result) > 0

# projekcija na skup koji ne sadrži rhs → MVD se filtrira
def test_project_mvds_drops_irrelevant():
    # projekcija na {nastavnik, udzbenik} — kurs nije tu, lhs postaje {}
    result = project_mvds(frozenset({"nastavnik", "udzbenik"}), FDS_KNU, MVDS_KNU)
    # proj_lhs = {} ∩ {nastavnik, udzbenik} = {}, proj_rhs može biti neprazan
    # ali trivijalna MVD (prazni lhs) se ne filtrira ovde, samo rhs={}
    lhs_list = [lhs for lhs, _ in result]
    assert frozenset({"kurs"}) not in lhs_list

# FZ se konvertuju u MVD i projektuju
def test_project_mvds_includes_fd_derived():
    fds = [(frozenset({"A"}), frozenset({"B"}))]
    result = project_mvds(frozenset({"A", "B", "C"}), fds, [])
    # A → B implicira A ↠ B, treba da bude u rezultatu
    lhs_list = [lhs for lhs, _ in result]
    assert frozenset({"A"}) in lhs_list

# prazne MVD i FZ → prazna projekcija
def test_project_mvds_empty():
    result = project_mvds(frozenset({"A", "B"}), [], [])
    assert result == []


# --- find_4nf_violation ---

# klasičan primer — kurs ↠ nastavnik krši 4NF
def test_find_4nf_violation_classic():
    violation = find_4nf_violation(ATTRS_KNU, FDS_KNU, MVDS_KNU)
    assert violation is not None

# lhs narušavajuće MVD je 'kurs'
def test_find_4nf_violation_lhs_is_kurs():
    violation = find_4nf_violation(ATTRS_KNU, FDS_KNU, MVDS_KNU)
    lhs, _ = violation
    assert lhs == frozenset({"kurs"})

# R(A,B,C), MVD A ↠ B → narušava 4NF
def test_find_4nf_violation_abc():
    violation = find_4nf_violation(ATTRS_ABC, FDS_ABC, MVDS_ABC)
    assert violation is not None

# R(A,B) sa A→B → A je superključ → 4NF nije narušena
def test_find_4nf_violation_none_when_superkey():
    violation = find_4nf_violation(ATTRS_AB, FDS_AB, MVDS_AB)
    assert violation is None

# prazne MVD i FZ → nema narušavanja
def test_find_4nf_violation_none_no_deps():
    violation = find_4nf_violation(frozenset({"A", "B", "C"}), [], [])
    assert violation is None

# trivijalna MVD (Y ⊆ X) → ne krši 4NF
def test_find_4nf_violation_none_trivial():
    mvds = [(frozenset({"A", "B"}), frozenset({"A"}))]  # A ⊆ AB → trivijalna
    violation = find_4nf_violation(frozenset({"A", "B", "C"}), [], mvds)
    assert violation is None

# trivijalna MVD (X ∪ Y = R) → ne krši 4NF
def test_find_4nf_violation_none_covers_all():
    mvds = [(frozenset({"A", "B"}), frozenset({"C"}))]  # AB ∪ C = ABC = R
    violation = find_4nf_violation(frozenset({"A", "B", "C"}), [], mvds)
    assert violation is None


# --- is_4nf ---

# klasičan primer — nije u 4NF
def test_is_4nf_false_classic():
    assert is_4nf(ATTRS_KNU, FDS_KNU, MVDS_KNU) == False

# R(A,B) sa A→B — jeste u 4NF (A je superključ)
def test_is_4nf_true_superkey():
    assert is_4nf(ATTRS_AB, FDS_AB, MVDS_AB) == True

# bez zavisnosti — uvek u 4NF
def test_is_4nf_true_no_deps():
    assert is_4nf(frozenset({"A", "B", "C"}), [], []) == True

# jednoatributna relacija — uvek u 4NF
def test_is_4nf_single_attr():
    assert is_4nf(frozenset({"A"}), [], []) == True
