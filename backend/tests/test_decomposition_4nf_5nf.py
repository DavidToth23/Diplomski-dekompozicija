from algorithm.decomposition import decompose
from algorithm.mvd import is_4nf
from algorithm.dek_5nf import find_5nf_violation
from algorithm.normal_forms import is_bcnf
from algorithm.closure import find_candidate_keys

# ── Primer 1: 4NF — kurs-nastavnik-udzbenik ──────────────────────────────────
# Klasičan udžbenički primer za 4NF.
# Relacija ModeliraPredmet(kurs, nastavnik, udzbenik)
# MVD: kurs ↠ nastavnik  (nastavnici su nezavisni od udžbenika)
#      kurs ↠ udzbenik   (udžbenici su nezavisni od nastavnika)
# Nema FZ (cela torka je ključ).
# Očekivano: R(kurs, nastavnik), R(kurs, udzbenik)

ATTRS_KNU = {"kurs", "nastavnik", "udzbenik"}
FDS_KNU = []
MVDS_KNU = [
    (frozenset({"kurs"}), frozenset({"nastavnik"})),
    (frozenset({"kurs"}), frozenset({"udzbenik"})),
]

# ── Primer 2: 4NF sa FZ i MVD ────────────────────────────────────────────────
# R(radnik, projekat, lokacija, telefon)
# FZ: radnik → telefon (radnik determiniše telefon)
# MVD: radnik ↠ projekat (radnik radi na više projekata nezavisno od lokacije)
#      radnik ↠ lokacija (radnik stanuje na više lokacija)
# Ključ: {radnik, projekat, lokacija}

ATTRS_RPLT = {"radnik", "projekat", "lokacija", "telefon"}
FDS_RPLT = [(frozenset({"radnik"}), frozenset({"telefon"}))]
MVDS_RPLT = [
    (frozenset({"radnik"}), frozenset({"projekat"})),
    (frozenset({"radnik"}), frozenset({"lokacija"})),
]

# ── Primer 3: 5NF — tročlana JD ──────────────────────────────────────────────
# R(A,B,C), JD: ⊳◁({A,B}, {B,C}, {A,C})
# Nema FZ, nema MVD narušavanja u smislu 4NF (trivijalna pokrivenost).
# Očekivano: R(A,B), R(B,C), R(A,C)

ATTRS_ABC = {"A", "B", "C"}
FDS_ABC = []
MVDS_NONE = []
JDS_ABC = [
    [frozenset({"A", "B"}), frozenset({"B", "C"}), frozenset({"A", "C"})]
]

# ── Primer 4: 5NF — kurs-profesor-tekst ──────────────────────────────────────
# Realan primer iz literature.
# R(kurs, profesor, tekst)
# JD: ⊳◁({kurs,profesor}, {profesor,tekst}, {kurs,tekst})
# Nema FZ — ključ je cela torka.
# Dekompozicija na tri binarne relacije.

ATTRS_KPT = {"kurs", "profesor", "tekst"}
FDS_KPT = []
MVDS_KPT = []
JDS_KPT = [
    [frozenset({"kurs", "profesor"}), frozenset({"profesor", "tekst"}), frozenset({"kurs", "tekst"})]
]

# ── Primer 5: Sve faze zajedno — BCNF → 4NF → 5NF ───────────────────────────
# R(A,B,C,D,E)
# FZ: A → B  (narušava BCNF u originalnoj relaciji)
# MVD: A ↠ C (narušava 4NF po dekompoziciji BCNF)
# JD: ⊳◁({A,C,D}, {A,C,E}) na šemi R(A,C,D,E) (narušava 5NF)

ATTRS_FULL = {"A", "B", "C", "D", "E"}
FDS_FULL = [(frozenset({"A"}), frozenset({"B"}))]
MVDS_FULL = [(frozenset({"A"}), frozenset({"C"}))]
JDS_FULL = [
    [frozenset({"A", "C", "D"}), frozenset({"A", "C", "E"})]
]


# helper
def get_attr_sets(result):
    return [frozenset(r["attrs"]) for r in result["relations"]]

def parse_fds(result):
    """Konvertuje fds iz formatted dict-a nazad u (frozenset, frozenset) parove."""
    return [
        (frozenset(fd["lhs"]), frozenset(fd["rhs"]))
        for rel in result["relations"]
        for fd in rel["fds"]
    ]


# ═══════════════════════════════════════════════════════════════════
# INTEGRACIJA — target_nf = "4NF"
# ═══════════════════════════════════════════════════════════════════

# --- struktura rezultata ---

def test_4nf_returns_correct_keys():
    result = decompose(ATTRS_KNU, FDS_KNU, "4NF", mvds=MVDS_KNU)
    assert "relations" in result
    assert "steps" in result
    assert "target_nf" in result
    assert "relation_count" in result

def test_4nf_target_nf_is_set():
    result = decompose(ATTRS_KNU, FDS_KNU, "4NF", mvds=MVDS_KNU)
    assert result["target_nf"] == "4NF"

def test_4nf_relation_count_matches():
    result = decompose(ATTRS_KNU, FDS_KNU, "4NF", mvds=MVDS_KNU)
    assert result["relation_count"] == len(result["relations"])

def test_4nf_attrs_are_sorted():
    result = decompose(ATTRS_KNU, FDS_KNU, "4NF", mvds=MVDS_KNU)
    for rel in result["relations"]:
        assert rel["attrs"] == sorted(rel["attrs"])

def test_4nf_steps_cover_all_phases():
    result = decompose(ATTRS_KNU, FDS_KNU, "4NF", mvds=MVDS_KNU)
    phases = [s["phase"] for s in result["steps"]]
    # mora proći kroz BCNF i 4NF faze
    assert "init" in phases         # dek_BCNF start
    assert "init_4nf" in phases     # dek_4NF start
    assert "done_4nf" in phases     # dek_4NF end


# --- kurs-nastavnik-udzbenik ---

def test_knu_gives_two_relations():
    result = decompose(ATTRS_KNU, FDS_KNU, "4NF", mvds=MVDS_KNU)
    assert result["relation_count"] == 2

def test_knu_contains_kurs_nastavnik():
    result = decompose(ATTRS_KNU, FDS_KNU, "4NF", mvds=MVDS_KNU)
    assert frozenset({"kurs", "nastavnik"}) in get_attr_sets(result)

def test_knu_contains_kurs_udzbenik():
    result = decompose(ATTRS_KNU, FDS_KNU, "4NF", mvds=MVDS_KNU)
    assert frozenset({"kurs", "udzbenik"}) in get_attr_sets(result)

def test_knu_attrs_conservation():
    result = decompose(ATTRS_KNU, FDS_KNU, "4NF", mvds=MVDS_KNU)
    all_attrs = set()
    for rel in result["relations"]:
        all_attrs |= set(rel["attrs"])
    assert all_attrs == ATTRS_KNU

def test_knu_all_relations_in_4nf():
    result = decompose(ATTRS_KNU, FDS_KNU, "4NF", mvds=MVDS_KNU)
    for rel in result["relations"]:
        fds = [(frozenset(fd["lhs"]), frozenset(fd["rhs"])) for fd in rel["fds"]]
        assert is_4nf(set(rel["attrs"]), fds, MVDS_KNU)


# --- radnik-projekat-lokacija-telefon ---

def test_rplt_attrs_conservation():
    result = decompose(ATTRS_RPLT, FDS_RPLT, "4NF", mvds=MVDS_RPLT)
    all_attrs = set()
    for rel in result["relations"]:
        all_attrs |= set(rel["attrs"])
    assert all_attrs == ATTRS_RPLT

def test_rplt_all_relations_in_bcnf():
    result = decompose(ATTRS_RPLT, FDS_RPLT, "4NF", mvds=MVDS_RPLT)
    for rel in result["relations"]:
        fds = [(frozenset(fd["lhs"]), frozenset(fd["rhs"])) for fd in rel["fds"]]
        assert is_bcnf(set(rel["attrs"]), fds)

# relacija radnik-telefon mora biti u rezultatu (iz BCNF faze)
def test_rplt_contains_radnik_telefon():
    result = decompose(ATTRS_RPLT, FDS_RPLT, "4NF", mvds=MVDS_RPLT)
    attr_sets = get_attr_sets(result)
    assert any({"radnik", "telefon"} <= r for r in attr_sets)


# --- 4NF bez MVD (isto kao BCNF) ---

def test_4nf_without_mvds_same_as_bcnf():
    result_bcnf = decompose(ATTRS_RPLT, FDS_RPLT, "BCNF")
    result_4nf = decompose(ATTRS_RPLT, FDS_RPLT, "4NF", mvds=[])
    # broj relacija mora biti isti (4NF bez MVD = BCNF)
    assert result_bcnf["relation_count"] == result_4nf["relation_count"]


# ═══════════════════════════════════════════════════════════════════
# INTEGRACIJA — target_nf = "5NF"
# ═══════════════════════════════════════════════════════════════════

# --- struktura rezultata ---

def test_5nf_returns_correct_keys():
    result = decompose(ATTRS_ABC, FDS_ABC, "5NF", join_deps=JDS_ABC)
    assert "relations" in result
    assert "steps" in result
    assert "target_nf" in result
    assert "relation_count" in result

def test_5nf_target_nf_is_set():
    result = decompose(ATTRS_ABC, FDS_ABC, "5NF", join_deps=JDS_ABC)
    assert result["target_nf"] == "5NF"

def test_5nf_steps_cover_all_phases():
    result = decompose(ATTRS_ABC, FDS_ABC, "5NF", join_deps=JDS_ABC)
    phases = [s["phase"] for s in result["steps"]]
    assert "init" in phases         # dek_BCNF
    assert "init_4nf" in phases     # dek_4NF
    assert "init_5nf" in phases     # dek_5NF
    assert "done_5nf" in phases


# --- R(A,B,C) sa JD ---

def test_abc_5nf_gives_three_relations():
    result = decompose(ATTRS_ABC, FDS_ABC, "5NF", join_deps=JDS_ABC)
    assert result["relation_count"] == 3

def test_abc_5nf_contains_ab():
    result = decompose(ATTRS_ABC, FDS_ABC, "5NF", join_deps=JDS_ABC)
    assert frozenset({"A", "B"}) in get_attr_sets(result)

def test_abc_5nf_contains_bc():
    result = decompose(ATTRS_ABC, FDS_ABC, "5NF", join_deps=JDS_ABC)
    assert frozenset({"B", "C"}) in get_attr_sets(result)

def test_abc_5nf_contains_ac():
    result = decompose(ATTRS_ABC, FDS_ABC, "5NF", join_deps=JDS_ABC)
    assert frozenset({"A", "C"}) in get_attr_sets(result)

def test_abc_5nf_attrs_conservation():
    result = decompose(ATTRS_ABC, FDS_ABC, "5NF", join_deps=JDS_ABC)
    all_attrs = set()
    for rel in result["relations"]:
        all_attrs |= set(rel["attrs"])
    assert all_attrs == ATTRS_ABC

def test_abc_5nf_no_violation_in_result():
    result = decompose(ATTRS_ABC, FDS_ABC, "5NF", join_deps=JDS_ABC)
    for rel in result["relations"]:
        fds = [(frozenset(fd["lhs"]), frozenset(fd["rhs"])) for fd in rel["fds"]]
        relevant_jds = [
            jd for jd in JDS_ABC
            if all(y.issubset(frozenset(rel["attrs"])) for y in jd)
        ]
        assert find_5nf_violation(frozenset(rel["attrs"]), fds, relevant_jds) is None


# --- kurs-profesor-tekst ---

def test_kpt_gives_three_relations():
    result = decompose(ATTRS_KPT, FDS_KPT, "5NF", join_deps=JDS_KPT)
    assert result["relation_count"] == 3

def test_kpt_attrs_conservation():
    result = decompose(ATTRS_KPT, FDS_KPT, "5NF", join_deps=JDS_KPT)
    all_attrs = set()
    for rel in result["relations"]:
        all_attrs |= set(rel["attrs"])
    assert all_attrs == ATTRS_KPT

def test_kpt_contains_kurs_profesor():
    result = decompose(ATTRS_KPT, FDS_KPT, "5NF", join_deps=JDS_KPT)
    assert frozenset({"kurs", "profesor"}) in get_attr_sets(result)

def test_kpt_contains_profesor_tekst():
    result = decompose(ATTRS_KPT, FDS_KPT, "5NF", join_deps=JDS_KPT)
    assert frozenset({"profesor", "tekst"}) in get_attr_sets(result)

def test_kpt_contains_kurs_tekst():
    result = decompose(ATTRS_KPT, FDS_KPT, "5NF", join_deps=JDS_KPT)
    assert frozenset({"kurs", "tekst"}) in get_attr_sets(result)


# ═══════════════════════════════════════════════════════════════════
# INTEGRACIJA — sve faze zajedno (BCNF → 4NF → 5NF)
# ═══════════════════════════════════════════════════════════════════

def test_full_pipeline_attrs_conservation():
    result = decompose(ATTRS_FULL, FDS_FULL, "5NF", mvds=MVDS_FULL, join_deps=JDS_FULL)
    all_attrs = set()
    for rel in result["relations"]:
        all_attrs |= set(rel["attrs"])
    assert all_attrs == ATTRS_FULL

def test_full_pipeline_has_all_phase_steps():
    result = decompose(ATTRS_FULL, FDS_FULL, "5NF", mvds=MVDS_FULL, join_deps=JDS_FULL)
    phases = [s["phase"] for s in result["steps"]]
    assert "init" in phases
    assert "init_4nf" in phases
    assert "init_5nf" in phases

def test_full_pipeline_all_relations_in_bcnf():
    result = decompose(ATTRS_FULL, FDS_FULL, "5NF", mvds=MVDS_FULL, join_deps=JDS_FULL)
    for rel in result["relations"]:
        fds = [(frozenset(fd["lhs"]), frozenset(fd["rhs"])) for fd in rel["fds"]]
        assert is_bcnf(set(rel["attrs"]), fds)


# ═══════════════════════════════════════════════════════════════════
# EDGE CASES
# ═══════════════════════════════════════════════════════════════════

# 5NF bez JD i MVD — isto kao BCNF
def test_5nf_without_deps_same_as_bcnf():
    fds = [(frozenset({"A"}), frozenset({"B"})), (frozenset({"B"}), frozenset({"C"}))]
    result_bcnf = decompose({"A", "B", "C"}, fds, "BCNF")
    result_5nf = decompose({"A", "B", "C"}, fds, "5NF", mvds=[], join_deps=[])
    assert result_bcnf["relation_count"] == result_5nf["relation_count"]

# šema već u 5NF — vraća se nepromenjena
def test_5nf_already_normalized():
    fds = [(frozenset({"A"}), frozenset({"B"}))]
    result = decompose({"A", "B"}, fds, "5NF", mvds=[], join_deps=[])
    assert result["relation_count"] == 1
    assert frozenset({"A", "B"}) in get_attr_sets(result)

# 4NF sa praznom relacijom — dek_BCNF vraca jednu praznu semu, sto je ispravno
def test_4nf_empty_attrs_set():
    result = decompose(set(), [], "4NF", mvds=[])
    all_attrs = set()
    for rel in result["relations"]:
        all_attrs |= set(rel["attrs"])
    assert all_attrs == set()

# relation_count uvek odgovara dužini liste
def test_5nf_relation_count_always_matches():
    result = decompose(ATTRS_KPT, FDS_KPT, "5NF", join_deps=JDS_KPT)
    assert result["relation_count"] == len(result["relations"])
