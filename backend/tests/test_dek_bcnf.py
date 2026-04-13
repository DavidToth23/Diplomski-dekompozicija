from algorithm.dek_bcnf import dek_bcnf
from algorithm.normal_forms import is_bcnf

# ── Primer 1: R(A,B,C,D,E), F = {AB→C, C→D, D→E} ───────────────────────────
# Ključ: AB
# Očekivane šeme u BCNF: R(A,B,C), R(C,D), R(D,E)

FDS_1 = [
    (frozenset({"A", "B"}), frozenset({"C"})),
    (frozenset({"C"}),      frozenset({"D"})),
    (frozenset({"D"}),      frozenset({"E"})),
]
ATTRS_1 = {"A", "B", "C", "D", "E"}

# ── Primer 2: R(A,B,C), F = {A→B, B→C} ──────────────────────────────────────
# Ključ: A
# Očekivane šeme u BCNF: R(A,B), R(B,C)

FDS_2 = [
    (frozenset({"A"}), frozenset({"B"})),
    (frozenset({"B"}), frozenset({"C"})),
]
ATTRS_2 = {"A", "B", "C"}

# ── Primer 3: R(A,B), F = {A→B} ──────────────────────────────────────────────
# Već u BCNF — treba da se vrati nepromenjena

FDS_3 = [
    (frozenset({"A"}), frozenset({"B"})),
]
ATTRS_3 = {"A", "B"}


# helper — izvlači skupove atributa iz rezultata
def get_attr_sets(relations):
    return [frozenset(r["attrs"]) for r in relations]


# --- osnovne provere ---

# rezultat mora biti lista
def test_dek_bcnf_returns_list():
    relations, steps = dek_bcnf(ATTRS_1, FDS_1)
    assert isinstance(relations, list)

# svaka šema u rezultatu mora biti u BCNF
def test_all_relations_in_bcnf():
    relations, _ = dek_bcnf(ATTRS_1, FDS_1)
    for rel in relations:
        assert is_bcnf(rel["attrs"], rel["fds"])

# unija atributa svih šema mora biti jednaka originalnom skupu
def test_attrs_conservation():
    relations, _ = dek_bcnf(ATTRS_1, FDS_1)
    all_attrs = set()
    for rel in relations:
        all_attrs |= rel["attrs"]
    assert all_attrs == ATTRS_1

# steps ne sme biti prazna lista
def test_steps_not_empty():
    _, steps = dek_bcnf(ATTRS_1, FDS_1)
    assert len(steps) > 0

# prvi korak mora biti init, poslednji done
def test_steps_first_and_last():
    _, steps = dek_bcnf(ATTRS_1, FDS_1)
    assert steps[0]["phase"] == "init"
    assert steps[-1]["phase"] == "done"


# --- šema već u BCNF ---

# R(A,B) sa A→B je već u BCNF — vraća jednu šemu
def test_already_bcnf():
    relations, _ = dek_bcnf(ATTRS_3, FDS_3)
    assert len(relations) == 1
    assert frozenset({"A", "B"}) in get_attr_sets(relations)

# šema bez FZ — uvek u BCNF
def test_no_fds():
    relations, _ = dek_bcnf({"A", "B", "C"}, [])
    assert len(relations) == 1


# --- dekompozicija R(A,B,C) ---

# mora dati tačno 2 šeme
def test_abc_gives_two_relations():
    relations, _ = dek_bcnf(ATTRS_2, FDS_2)
    assert len(relations) == 2

# atributi moraju biti konzervisani
def test_abc_attrs_conserved():
    relations, _ = dek_bcnf(ATTRS_2, FDS_2)
    all_attrs = set()
    for rel in relations:
        all_attrs |= rel["attrs"]
    assert all_attrs == ATTRS_2

# sve šeme moraju biti u BCNF
def test_abc_all_bcnf():
    relations, _ = dek_bcnf(ATTRS_2, FDS_2)
    for rel in relations:
        assert is_bcnf(rel["attrs"], rel["fds"])


# --- dekompozicija R(A,B,C,D,E) ---

# mora dati 3 šeme
def test_abcde_gives_three_relations():
    relations, _ = dek_bcnf(ATTRS_1, FDS_1)
    assert len(relations) == 3

# sve šeme moraju biti u BCNF
def test_abcde_all_bcnf():
    relations, _ = dek_bcnf(ATTRS_1, FDS_1)
    for rel in relations:
        assert is_bcnf(rel["attrs"], rel["fds"])

# atributi moraju biti konzervisani
def test_abcde_attrs_conserved():
    relations, _ = dek_bcnf(ATTRS_1, FDS_1)
    all_attrs = set()
    for rel in relations:
        all_attrs |= rel["attrs"]
    assert all_attrs == ATTRS_1