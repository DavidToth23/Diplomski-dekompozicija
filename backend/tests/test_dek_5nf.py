from algorithm.dek_5nf import dek_5nf, find_5nf_violation, is_trivial_jd, jd_covers_relation

# ── Primer 1: R(A,B,C), JD: ⊳◁({A,B}, {B,C}, {A,C}) ────────────────────────────────────────────
# Nema FZ — nijedna komponenta nije superključ
# Očekivane šeme u 5NF: R(A,B), R(B,C), R(A,C)

ATTRS_ABC = frozenset({"A", "B", "C"})
FDS_ABC = []
JD_ABC = [
    [frozenset({"A", "B"}), frozenset({"B", "C"}), frozenset({"A", "C"})]
]
RELATIONS_ABC = [{"attrs": ATTRS_ABC, "fds": []}]

# ── Primer 2: R(A,B,C,D), JD: ⊳◁({A,B,C}, {A,B,D}) ─────────────────────────
# Pokriva R (unija = R), nijedna komponenta nije superključ (bez FZ)
# Očekivane šeme: R(A,B,C), R(A,B,D)

ATTRS_ABCD = frozenset({"A", "B", "C", "D"})
FDS_ABCD = []
JD_ABCD = [
    [frozenset({"A", "B", "C"}), frozenset({"A", "B", "D"})]
]
RELATIONS_ABCD = [{"attrs": ATTRS_ABCD, "fds": []}]

# ── Primer 3: JD je trivijalna (jedna komponenta = R) ────────────────────────
# ⊳◁({A,B,C}, {A,B,C}) — jedna komponenta = R → trivijalna

ATTRS_TRIVIAL = frozenset({"A", "B", "C"})
JD_TRIVIAL = [
    [frozenset({"A", "B", "C"}), frozenset({"A", "B"})]
]

# ── Primer 4: R(A,B) sa FZ A→B — A je superključ ─────────────────────────────
# JD čija komponenta sadrži superključ → ne krši 5NF

ATTRS_AB = frozenset({"A", "B"})
FDS_AB = [(frozenset({"A"}), frozenset({"B"}))]
JD_WITH_SUPERKEY = [
    [frozenset({"A", "B"}), frozenset({"A"})]
]
RELATIONS_AB = [{"attrs": ATTRS_AB, "fds": FDS_AB}]


# helper
def get_attr_sets(relations):
    return [frozenset(r["attrs"]) for r in relations]


# --- is_trivial_jd ---

# jedna komponenta = R → trivijalna
def test_trivial_jd_component_equals_r():
    jd = [frozenset({"A", "B", "C"}), frozenset({"A", "B"})]
    assert is_trivial_jd(jd, frozenset({"A", "B", "C"})) == True

# nijedna komponenta ne pokriva R → netrivijalna
def test_nontrivial_jd():
    jd = [frozenset({"A", "B"}), frozenset({"B", "C"}), frozenset({"A", "C"})]
    assert is_trivial_jd(jd, frozenset({"A", "B", "C"})) == False

# JD sa jednom komponentom jednakom R
def test_trivial_jd_single_full():
    jd = [frozenset({"A", "B", "C"})]
    assert is_trivial_jd(jd, frozenset({"A", "B", "C"})) == True


# --- jd_covers_relation ---

# unija komponenti = R → pokriva
def test_jd_covers_full():
    jd = [frozenset({"A", "B"}), frozenset({"B", "C"}), frozenset({"A", "C"})]
    assert jd_covers_relation(jd, frozenset({"A", "B", "C"})) == True

# unija komponenti ⊂ R → ne pokriva
def test_jd_does_not_cover():
    jd = [frozenset({"A", "B"}), frozenset({"A", "C"})]
    assert jd_covers_relation(jd, frozenset({"A", "B", "C", "D"})) == False

# pokriva tačno sa dva para
def test_jd_covers_two_components():
    jd = [frozenset({"A", "B", "C"}), frozenset({"A", "B", "D"})]
    assert jd_covers_relation(jd, frozenset({"A", "B", "C", "D"})) == True


# --- find_5nf_violation ---

# klasičan primer ABC sa JD — narušava 5NF
def test_find_5nf_violation_classic():
    violation = find_5nf_violation(ATTRS_ABC, FDS_ABC, JD_ABC)
    assert violation is not None

# narušavajuća JD ima 3 komponente
def test_find_5nf_violation_three_components():
    violation = find_5nf_violation(ATTRS_ABC, FDS_ABC, JD_ABC)
    assert len(violation) == 3

# trivijalna JD → nema narušavanja
def test_find_5nf_violation_none_trivial():
    violation = find_5nf_violation(ATTRS_TRIVIAL, [], JD_TRIVIAL)
    assert violation is None

# superključ komponenta → nema narušavanja
def test_find_5nf_violation_none_superkey():
    violation = find_5nf_violation(ATTRS_AB, FDS_AB, JD_WITH_SUPERKEY)
    assert violation is None

# bez JD → nema narušavanja
def test_find_5nf_violation_none_no_jd():
    violation = find_5nf_violation(ATTRS_ABC, FDS_ABC, [])
    assert violation is None

# JD ne pokriva R (unija komponenti ≠ R) → nema narušavanja
def test_find_5nf_violation_none_no_cover():
    jd = [[frozenset({"A", "B"}), frozenset({"B"})]]  # ne pokriva {A,B,C}
    violation = find_5nf_violation(frozenset({"A", "B", "C"}), [], jd)
    assert violation is None

# ABCD primer — narušava 5NF
def test_find_5nf_violation_abcd():
    violation = find_5nf_violation(ATTRS_ABCD, FDS_ABCD, JD_ABCD)
    assert violation is not None


# --- dek_5nf ---

# rezultat mora biti lista
def test_dek_5nf_returns_list():
    result, _ = dek_5nf(RELATIONS_ABC, FDS_ABC, JD_ABC)
    assert isinstance(result, list)

# steps ne sme biti prazna
def test_steps_not_empty():
    _, steps = dek_5nf(RELATIONS_ABC, FDS_ABC, JD_ABC)
    assert len(steps) > 0

# prvi korak mora biti init_5nf, poslednji done_5nf
def test_steps_first_and_last():
    _, steps = dek_5nf(RELATIONS_ABC, FDS_ABC, JD_ABC)
    assert steps[0]["phase"] == "init_5nf"
    assert steps[-1]["phase"] == "done_5nf"

# svaka šema mora imati attrs i fds
def test_relations_have_required_keys():
    result, _ = dek_5nf(RELATIONS_ABC, FDS_ABC, JD_ABC)
    for rel in result:
        assert "attrs" in rel
        assert "fds" in rel


# --- klasičan primer R(A,B,C) ---

# mora dati 3 šeme
def test_abc_gives_three_relations():
    result, _ = dek_5nf(RELATIONS_ABC, FDS_ABC, JD_ABC)
    assert len(result) == 3

# mora sadržati sve tri komponente JD
def test_abc_contains_ab():
    result, _ = dek_5nf(RELATIONS_ABC, FDS_ABC, JD_ABC)
    assert frozenset({"A", "B"}) in get_attr_sets(result)

def test_abc_contains_bc():
    result, _ = dek_5nf(RELATIONS_ABC, FDS_ABC, JD_ABC)
    assert frozenset({"B", "C"}) in get_attr_sets(result)

def test_abc_contains_ac():
    result, _ = dek_5nf(RELATIONS_ABC, FDS_ABC, JD_ABC)
    assert frozenset({"A", "C"}) in get_attr_sets(result)

# konzervacija atributa
def test_abc_attrs_conservation():
    result, _ = dek_5nf(RELATIONS_ABC, FDS_ABC, JD_ABC)
    all_attrs = set()
    for rel in result:
        all_attrs |= rel["attrs"]
    assert all_attrs == ATTRS_ABC

# steps moraju sadržati fazu narušavanja
def test_abc_steps_contain_violation():
    _, steps = dek_5nf(RELATIONS_ABC, FDS_ABC, JD_ABC)
    phases = [s["phase"] for s in steps]
    assert "5nf_violation" in phases

# steps moraju sadržati fazu dekompozicije
def test_abc_steps_contain_split():
    _, steps = dek_5nf(RELATIONS_ABC, FDS_ABC, JD_ABC)
    phases = [s["phase"] for s in steps]
    assert "5nf_split" in phases


# --- R(A,B,C,D) primer ---

# mora dati 2 šeme
def test_abcd_gives_two_relations():
    result, _ = dek_5nf(RELATIONS_ABCD, FDS_ABCD, JD_ABCD)
    assert len(result) == 2

# mora sadržati R(A,B,C)
def test_abcd_contains_abc():
    result, _ = dek_5nf(RELATIONS_ABCD, FDS_ABCD, JD_ABCD)
    assert frozenset({"A", "B", "C"}) in get_attr_sets(result)

# mora sadržati R(A,B,D)
def test_abcd_contains_abd():
    result, _ = dek_5nf(RELATIONS_ABCD, FDS_ABCD, JD_ABCD)
    assert frozenset({"A", "B", "D"}) in get_attr_sets(result)


# --- šema već u 5NF ---

# bez JD → šema ostaje nepromenjena
def test_already_5nf_no_jd():
    result, _ = dek_5nf(RELATIONS_AB, FDS_AB, [])
    assert len(result) == 1
    assert frozenset({"A", "B"}) in get_attr_sets(result)

# steps sadrže 5nf_ok fazu
def test_already_5nf_steps_contain_ok():
    _, steps = dek_5nf(RELATIONS_AB, FDS_AB, [])
    phases = [s["phase"] for s in steps]
    assert "5nf_ok" in phases

# steps ne sadrže fazu narušavanja
def test_already_5nf_no_violation_step():
    _, steps = dek_5nf(RELATIONS_AB, FDS_AB, [])
    phases = [s["phase"] for s in steps]
    assert "5nf_violation" not in phases

# JD čija komponenta je superključ → šema ostaje nepromenjena
def test_superkey_jd_no_decomposition():
    result, _ = dek_5nf(RELATIONS_AB, FDS_AB, JD_WITH_SUPERKEY)
    assert len(result) == 1


# --- edge cases ---

# prazna lista šema → prazna lista
def test_empty_relations():
    result, _ = dek_5nf([], [], [])
    assert result == []

# JD čije komponente nisu podskup atributa šeme → filtrira se
def test_jd_with_foreign_attrs_ignored():
    # JD sadrži atribut X koji nije u šemi R(A,B)
    jd = [[frozenset({"A", "X"}), frozenset({"X", "B"})]]
    result, _ = dek_5nf(RELATIONS_AB, FDS_AB, jd)
    # JD se ignoriše jer X nije u {A,B}
    assert len(result) == 1
