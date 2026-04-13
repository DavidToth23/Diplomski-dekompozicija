from algorithm.dek_union import dek_union
from algorithm.normal_forms import project_fds

# ── Primer 1: šeme sa ekvivalentnim ključevima ───────────────────────────────
# R(C,B), R(B,D), R(B,E) — sve imaju B kao ključ
# Očekujemo spajanje u R(C,B,D,E)

FDS_MAIN = [
    (frozenset({"B"}),        frozenset({"D", "E", "C"})),
    (frozenset({"F"}),        frozenset({"G"})),
    (frozenset({"H"}),        frozenset({"F"})),
    (frozenset({"B", "F"}),   frozenset({"I", "H"})),
]

RELATIONS_MAIN = [
    {"attrs": frozenset({"C", "B"}),        "fds": project_fds({"C", "B"}, FDS_MAIN)},
    {"attrs": frozenset({"B", "D"}),        "fds": project_fds({"B", "D"}, FDS_MAIN)},
    {"attrs": frozenset({"B", "E"}),        "fds": project_fds({"B", "E"}, FDS_MAIN)},
    {"attrs": frozenset({"G", "F"}),        "fds": project_fds({"G", "F"}, FDS_MAIN)},
    {"attrs": frozenset({"B", "H", "I"}),   "fds": project_fds({"B", "H", "I"}, FDS_MAIN)},
    {"attrs": frozenset({"H", "F"}),        "fds": project_fds({"H", "F"}, FDS_MAIN)},
]

# ── Primer 2: R(A,B,C), F = {A→B, B→C} ──────────────────────────────────────
# R(A,B) i R(B,C) — nemaju ekvivalentne ključeve
# Očekujemo da ostanu razdvojene

FDS_ABC = [
    (frozenset({"A"}), frozenset({"B"})),
    (frozenset({"B"}), frozenset({"C"})),
]

RELATIONS_ABC = [
    {"attrs": frozenset({"A", "B"}), "fds": project_fds({"A", "B"}, FDS_ABC)},
    {"attrs": frozenset({"B", "C"}), "fds": project_fds({"B", "C"}, FDS_ABC)},
]

# helper
def get_attr_sets(relations):
    return [frozenset(r["attrs"]) for r in relations]


# --- osnovne provere ---

def test_dek_union_returns_list():
    result, _ = dek_union(RELATIONS_MAIN, FDS_MAIN)
    assert isinstance(result, list)

def test_steps_not_empty():
    _, steps = dek_union(RELATIONS_MAIN, FDS_MAIN)
    assert len(steps) > 0

def test_steps_first_and_last():
    _, steps = dek_union(RELATIONS_MAIN, FDS_MAIN)
    assert steps[0]["phase"] == "init"
    assert steps[-1]["phase"] == "done"


# --- spajanje šema ---

def test_merge_gives_four_relations():
    result, _ = dek_union(RELATIONS_MAIN, FDS_MAIN)
    assert len(result) == 4

def test_merged_relation_contains_all_attrs():
    result, _ = dek_union(RELATIONS_MAIN, FDS_MAIN)
    assert frozenset({"C", "B", "D", "E"}) in get_attr_sets(result)

def test_other_relations_unchanged():
    result, _ = dek_union(RELATIONS_MAIN, FDS_MAIN)
    attr_sets = get_attr_sets(result)
    assert frozenset({"G", "F"}) in attr_sets
    assert frozenset({"B", "H", "I"}) in attr_sets
    assert frozenset({"H", "F"}) in attr_sets

def test_steps_contain_merge():
    _, steps = dek_union(RELATIONS_MAIN, FDS_MAIN)
    phases = [s["phase"] for s in steps]
    assert "merge" in phases


# --- bez spajanja ---

def test_no_merge_when_no_equivalent_keys():
    result, _ = dek_union(RELATIONS_ABC, FDS_ABC)
    assert len(result) == 2

def test_no_merge_steps():
    _, steps = dek_union(RELATIONS_ABC, FDS_ABC)
    phases = [s["phase"] for s in steps]
    assert "merge" not in phases


# --- edge cases ---

def test_single_relation():
    relations = [{"attrs": frozenset({"A", "B"}), "fds": []}]
    result, _ = dek_union(relations, [])
    assert len(result) == 1
    assert frozenset({"A", "B"}) in get_attr_sets(result)

def test_empty_relations():
    result, _ = dek_union([], [])
    assert result == []