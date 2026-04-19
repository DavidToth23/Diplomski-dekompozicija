from algorithm.dek_4nf import dek_4nf
from algorithm.mvd import is_4nf
from algorithm.normal_forms import project_fds

# ── Primer 1: Klasičan 4NF primer ────────────────────────────────────────────
# R(kurs, nastavnik, udzbenik)
# MVD: kurs ↠ nastavnik, kurs ↠ udzbenik
# Ključ: {kurs, nastavnik, udzbenik}
# Očekivane šeme u 4NF: R(kurs, nastavnik), R(kurs, udzbenik)

ATTRS_KNU = frozenset({"kurs", "nastavnik", "udzbenik"})
FDS_KNU = []
MVDS_KNU = [
    (frozenset({"kurs"}), frozenset({"nastavnik"})),
    (frozenset({"kurs"}), frozenset({"udzbenik"})),
]
RELATIONS_KNU = [{"attrs": ATTRS_KNU, "fds": []}]

# ── Primer 2: R(A,B,C), MVD A ↠ B ───────────────────────────────────────────
# Očekivane šeme: R(A,B), R(A,C)

ATTRS_ABC = frozenset({"A", "B", "C"})
FDS_ABC = []
MVDS_ABC = [(frozenset({"A"}), frozenset({"B"}))]
RELATIONS_ABC = [{"attrs": ATTRS_ABC, "fds": []}]

# ── Primer 3: Šema već u 4NF ─────────────────────────────────────────────────
# R(A,B), FZ A→B — A je superključ, nema MVD narušavanja

ATTRS_AB = frozenset({"A", "B"})
FDS_AB = [(frozenset({"A"}), frozenset({"B"}))]
MVDS_NONE = []
RELATIONS_AB = [{"attrs": ATTRS_AB, "fds": FDS_AB}]

# ── Primer 4: Više šema, jedna treba dekompoziciju ───────────────────────────
# R1(kurs, nastavnik, udzbenik) — narušava 4NF
# R2(A, B) sa A→B — već u 4NF

RELATIONS_MIXED = [
    {"attrs": ATTRS_KNU, "fds": []},
    {"attrs": ATTRS_AB, "fds": FDS_AB},
]


# helper
def get_attr_sets(relations):
    return [frozenset(r["attrs"]) for r in relations]


# --- osnovne provere ---

# rezultat mora biti lista
def test_dek_4nf_returns_list():
    result, _ = dek_4nf(RELATIONS_KNU, FDS_KNU, MVDS_KNU)
    assert isinstance(result, list)

# steps ne sme biti prazna lista
def test_steps_not_empty():
    _, steps = dek_4nf(RELATIONS_KNU, FDS_KNU, MVDS_KNU)
    assert len(steps) > 0

# prvi korak mora biti init_4nf, poslednji done_4nf
def test_steps_first_and_last():
    _, steps = dek_4nf(RELATIONS_KNU, FDS_KNU, MVDS_KNU)
    assert steps[0]["phase"] == "init_4nf"
    assert steps[-1]["phase"] == "done_4nf"

# svaka šema mora imati attrs i fds ključeve
def test_relations_have_required_keys():
    result, _ = dek_4nf(RELATIONS_KNU, FDS_KNU, MVDS_KNU)
    for rel in result:
        assert "attrs" in rel
        assert "fds" in rel


# --- klasičan primer kurs-nastavnik-udzbenik ---

# mora dati tačno 2 šeme
def test_knu_gives_two_relations():
    result, _ = dek_4nf(RELATIONS_KNU, FDS_KNU, MVDS_KNU)
    assert len(result) == 2

# mora sadržati R(kurs, nastavnik)
def test_knu_contains_kurs_nastavnik():
    result, _ = dek_4nf(RELATIONS_KNU, FDS_KNU, MVDS_KNU)
    assert frozenset({"kurs", "nastavnik"}) in get_attr_sets(result)

# mora sadržati R(kurs, udzbenik)
def test_knu_contains_kurs_udzbenik():
    result, _ = dek_4nf(RELATIONS_KNU, FDS_KNU, MVDS_KNU)
    assert frozenset({"kurs", "udzbenik"}) in get_attr_sets(result)

# unija atributa mora biti jednaka originalnom skupu
def test_knu_attrs_conservation():
    result, _ = dek_4nf(RELATIONS_KNU, FDS_KNU, MVDS_KNU)
    all_attrs = set()
    for rel in result:
        all_attrs |= rel["attrs"]
    assert all_attrs == ATTRS_KNU

# sve šeme moraju biti u 4NF
def test_knu_all_in_4nf():
    result, _ = dek_4nf(RELATIONS_KNU, FDS_KNU, MVDS_KNU)
    for rel in result:
        assert is_4nf(rel["attrs"], rel["fds"], MVDS_KNU)

# steps moraju sadržati fazu narušavanja
def test_knu_steps_contain_violation():
    _, steps = dek_4nf(RELATIONS_KNU, FDS_KNU, MVDS_KNU)
    phases = [s["phase"] for s in steps]
    assert "4nf_violation" in phases

# steps moraju sadržati fazu dekompozicije
def test_knu_steps_contain_split():
    _, steps = dek_4nf(RELATIONS_KNU, FDS_KNU, MVDS_KNU)
    phases = [s["phase"] for s in steps]
    assert "4nf_split" in phases


# --- R(A,B,C) sa MVD A ↠ B ---

# mora dati 2 šeme: R(A,B) i R(A,C)
def test_abc_gives_two_relations():
    result, _ = dek_4nf(RELATIONS_ABC, FDS_ABC, MVDS_ABC)
    assert len(result) == 2

# mora sadržati R(A,B)
def test_abc_contains_ab():
    result, _ = dek_4nf(RELATIONS_ABC, FDS_ABC, MVDS_ABC)
    assert frozenset({"A", "B"}) in get_attr_sets(result)

# mora sadržati R(A,C)
def test_abc_contains_ac():
    result, _ = dek_4nf(RELATIONS_ABC, FDS_ABC, MVDS_ABC)
    assert frozenset({"A", "C"}) in get_attr_sets(result)

# konzervacija atributa
def test_abc_attrs_conservation():
    result, _ = dek_4nf(RELATIONS_ABC, FDS_ABC, MVDS_ABC)
    all_attrs = set()
    for rel in result:
        all_attrs |= rel["attrs"]
    assert all_attrs == ATTRS_ABC


# --- šema već u 4NF ---

# vraća jednu šemu neizmenjenu
def test_already_4nf_returns_one():
    result, _ = dek_4nf(RELATIONS_AB, FDS_AB, MVDS_NONE)
    assert len(result) == 1

# atributi ostaju isti
def test_already_4nf_attrs_unchanged():
    result, _ = dek_4nf(RELATIONS_AB, FDS_AB, MVDS_NONE)
    assert frozenset({"A", "B"}) in get_attr_sets(result)

# steps sadrže 4nf_ok fazu
def test_already_4nf_steps_contain_ok():
    _, steps = dek_4nf(RELATIONS_AB, FDS_AB, MVDS_NONE)
    phases = [s["phase"] for s in steps]
    assert "4nf_ok" in phases

# steps ne sadrže fazu narušavanja
def test_already_4nf_no_violation_step():
    _, steps = dek_4nf(RELATIONS_AB, FDS_AB, MVDS_NONE)
    phases = [s["phase"] for s in steps]
    assert "4nf_violation" not in phases


# --- mešovite šeme ---

# R1 narušava, R2 ne — trebaju 3 šeme ukupno
def test_mixed_total_count():
    result, _ = dek_4nf(RELATIONS_MIXED, FDS_KNU, MVDS_KNU)
    assert len(result) == 3

# R2 (A,B) mora ostati netaknuta
def test_mixed_unchanged_relation_preserved():
    result, _ = dek_4nf(RELATIONS_MIXED, FDS_KNU, MVDS_KNU)
    assert frozenset({"A", "B"}) in get_attr_sets(result)


# --- edge cases ---

# prazna lista šema → prazna lista
def test_empty_relations():
    result, _ = dek_4nf([], [], [])
    assert result == []

# bez MVD → sve šeme ostaju nepromenjene
def test_no_mvds_returns_unchanged():
    result, _ = dek_4nf(RELATIONS_KNU, FDS_KNU, [])
    assert len(result) == 1
    assert frozenset({"kurs", "nastavnik", "udzbenik"}) in get_attr_sets(result)

# jednoatributna šema — uvek u 4NF
def test_single_attr_relation():
    relations = [{"attrs": frozenset({"A"}), "fds": []}]
    result, _ = dek_4nf(relations, [], [])
    assert len(result) == 1
