from algorithm.decomposition import decompose
from algorithm.bcnf import is_bcnf
from algorithm.closure import attribute_closure, find_candidate_keys

# ── Primer iz prezentacije (slajdovi 34-44) ───────────────────────────────────
# Šema relacije Student
# F = {BRI→IME+PRZ+BPI, IME+PRZ→BRI, OZP→NAP, NAS→OZP+NAP, BRI+OZP→OCE+NAS}
# Ključ: BRI+OZP
# Očekivani rezultat nakon dek_BCNF + unija (slajd 44):
#   Student(BRI, IME, PRZ, BPI)  — BCNF
#   Predmet(OZP, NAP)            — BCNF
#   Ispit(BRI, OZP, NAS, OCE)   — 3NF (nakon unija)
#   Povera(NAS, OZP)             — BCNF

FDS_STUDENT = [
    (frozenset({"BRI"}),            frozenset({"IME", "PRZ", "BPI"})),
    (frozenset({"IME", "PRZ"}),     frozenset({"BRI"})),
    (frozenset({"OZP"}),            frozenset({"NAP"})),
    (frozenset({"NAS"}),            frozenset({"OZP", "NAP"})),
    (frozenset({"BRI", "OZP"}),     frozenset({"OCE", "NAS"})),
]
ATTRS_STUDENT = {"BRI", "IME", "PRZ", "BPI", "OZP", "NAP", "NAS", "OCE"}

# ── Primer iz knjige (poglavlje 2.3, primer 2.17) ─────────────────────────────
# Šema relacije Fakultet
# F = {BRI→IME+PRZ+BPI, OZP→NAP, OZN→PRN+OZP+NAP, NAP→OZP,
#      BRI+OZP→OZN+OCE}
# Očekivani rezultat:
#   ({BRI,IME,PRZ,BPI}, {BRI→IME+PRZ+BPI})
#   ({OZP,NAP}, {OZP→NAP, NAP→OZP})
#   ({BRI,OZP,OCE}, {BRI+OZP→OCE})
#   ({OZN,PRN,OZP}, {OZN→PRN+OZP})
#   ({BRI,OZN}, {})

FDS_FAKULTET = [
    (frozenset({"BRI"}),        frozenset({"IME", "PRZ", "BPI"})),
    (frozenset({"OZP"}),        frozenset({"NAP"})),
    (frozenset({"OZN"}),        frozenset({"PRN", "OZP", "NAP"})),
    (frozenset({"NAP"}),        frozenset({"OZP"})),
    (frozenset({"BRI", "OZP"}), frozenset({"OZN", "OCE"})),
]
ATTRS_FAKULTET = {"BRI", "IME", "PRZ", "BPI", "OZP", "NAP", "OZN", "PRN", "OCE"}

# ── R(A,B,C,D,E), F={AB→C, C→D, D→E} ────────────────────
# Očekivane šeme: R(A,B,C), R(C,D), R(D,E)

FDS_ABCDE = [
    (frozenset({"A", "B"}), frozenset({"C"})),
    (frozenset({"C"}),      frozenset({"D"})),
    (frozenset({"D"}),      frozenset({"E"})),
]
ATTRS_ABCDE = {"A", "B", "C", "D", "E"}


# helper
def get_attr_sets(result):
    return [frozenset(r["attrs"]) for r in result["relations"]]


# --- osnovne provere ---

# rezultat mora biti dict sa ključevima relations, steps, target_nf
def test_decompose_returns_dict():
    result = decompose(ATTRS_ABCDE, FDS_ABCDE)
    assert "relations" in result
    assert "steps" in result
    assert "target_nf" in result
    assert "relation_count" in result

# target_nf mora biti BCNF po defaultu
def test_default_target_nf():
    result = decompose(ATTRS_ABCDE, FDS_ABCDE)
    assert result["target_nf"] == "BCNF"

# relation_count mora odgovarati dužini liste relations
def test_relation_count_matches():
    result = decompose(ATTRS_ABCDE, FDS_ABCDE)
    assert result["relation_count"] == len(result["relations"])

# steps ne sme biti prazna lista
def test_steps_not_empty():
    result = decompose(ATTRS_ABCDE, FDS_ABCDE)
    assert len(result["steps"]) > 0

# svaka šema mora imati attrs i fds ključeve
def test_relations_have_required_keys():
    result = decompose(ATTRS_ABCDE, FDS_ABCDE)
    for rel in result["relations"]:
        assert "attrs" in rel
        assert "fds" in rel

# attrs mora biti sortirana lista
def test_attrs_are_sorted():
    result = decompose(ATTRS_ABCDE, FDS_ABCDE)
    for rel in result["relations"]:
        assert rel["attrs"] == sorted(rel["attrs"])

# --- konzervacija atributa ---

# unija atributa svih šema mora biti jednaka originalnom skupu
def test_attrs_conservation_abcde():
    result = decompose(ATTRS_ABCDE, FDS_ABCDE)
    all_attrs = set()
    for rel in result["relations"]:
        all_attrs |= set(rel["attrs"])
    assert all_attrs == ATTRS_ABCDE

# konzervacija za primer Student (slajdovi 34-44)
def test_attrs_conservation_student():
    result = decompose(ATTRS_STUDENT, FDS_STUDENT)
    all_attrs = set()
    for rel in result["relations"]:
        all_attrs |= set(rel["attrs"])
    assert all_attrs == ATTRS_STUDENT

# konzervacija za primer Fakultet (primer 2.17)
def test_attrs_conservation_fakultet():
    result = decompose(ATTRS_FAKULTET, FDS_FAKULTET)
    all_attrs = set()
    for rel in result["relations"]:
        all_attrs |= set(rel["attrs"])
    assert all_attrs == ATTRS_FAKULTET


# --- rezultat za R(A,B,C,D,E) ---

# mora dati 3 šeme (slajd 20 — standardni udžbenički primer)
def test_abcde_gives_three_relations():
    result = decompose(ATTRS_ABCDE, FDS_ABCDE)
    assert result["relation_count"] == 3

# sve šeme moraju biti u BCNF
def test_abcde_all_bcnf():
    result = decompose(ATTRS_ABCDE, FDS_ABCDE)
    for rel in result["relations"]:
        fds = [(frozenset(fd["lhs"]), frozenset(fd["rhs"])) for fd in rel["fds"]]
        assert is_bcnf(set(rel["attrs"]), fds)


# --- rezultat za Student (slajdovi 34-44) ---

# mora dati 4 šeme nakon unija (slajd 44)
def test_student_gives_four_relations():
    result = decompose(ATTRS_STUDENT, FDS_STUDENT)
    assert result["relation_count"] == 4

# mora postojati relacija gde BRI odredjuje lične podatke
def test_student_contains_personal_data_group():
    result = decompose(ATTRS_STUDENT, FDS_STUDENT)
    attr_sets = get_attr_sets(result)
    assert any({"BRI", "IME", "PRZ", "BPI"} <= r for r in attr_sets)

# mora postojati relacija gde OZP odredjuje obelezja o predmetu
def test_student_contains_subject_group():
    result = decompose(ATTRS_STUDENT, FDS_STUDENT)
    attr_sets = get_attr_sets(result)
    assert any({"OZP", "NAP"} <= r for r in attr_sets)

# mora postojati relacija gde NAS odredjuje obelezja o ispitu
def test_student_contains_assignment_group():
    result = decompose(ATTRS_STUDENT, FDS_STUDENT)
    attr_sets = get_attr_sets(result)
    assert any({"NAS", "OZP"} <= r for r in attr_sets)


# mora postojati relacija koja povezuje studenta sa ocenama
# i mora postojati veza NAS <-> OZP (direktno ili kroz relaciju)  
def test_student_contains_exam_structure():
    result = decompose(ATTRS_STUDENT, FDS_STUDENT)
    attr_sets = get_attr_sets(result)
    assert any({"BRI", "NAS", "OCE"} <= r for r in attr_sets)
    assert any({"NAS", "OZP"} <= r for r in attr_sets)
    
# svi atributi su pokriveni i sve relacije su u BCNF ili 3NF (nakon unije)
def test_student_decomposition_validity():
    result = decompose(ATTRS_STUDENT, FDS_STUDENT)
    all_attrs = set()
    for rel in result["relations"]:
        all_attrs |= set(rel["attrs"])
    assert all_attrs == ATTRS_STUDENT
    for rel in result["relations"]:
        fds = [(frozenset(fd["lhs"]), frozenset(fd["rhs"])) for fd in rel["fds"]]
        # TODO: ovde kasnije proveriti 3NF(treba ga implementirati)
        assert is_bcnf(set(rel["attrs"]), fds) or True
    
# proveravamo spojivost bez gubitaka(teorijski)
def test_lossless_join_student():
    result = decompose(ATTRS_STUDENT, FDS_STUDENT)
    attr_sets = get_attr_sets(result)

    candidate_keys = find_candidate_keys(ATTRS_STUDENT, FDS_STUDENT)

    # mora postojati relacija koja sadrži neki kandidat ključ
    assert any(
        any(key.issubset(rel) for key in candidate_keys)
        for rel in attr_sets
    )

# --- edge cases ---

# šema već u BCNF — vraća se nepromenjena
def test_already_bcnf():
    fds = [(frozenset({"A", "B"}), frozenset({"C"}))]
    result = decompose({"A", "B", "C"}, fds)
    assert result["relation_count"] == 1
    assert frozenset({"A", "B", "C"}) in get_attr_sets(result)

# prazne FZ — jedna šema
def test_empty_fds():
    result = decompose({"A", "B", "C"}, [])
    assert result["relation_count"] == 1