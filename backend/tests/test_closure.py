from algorithm.closure import attribute_closure, is_superkey, find_candidate_keys
from itertools import combinations

FDS = [
    (frozenset({"A", "B"}), frozenset({"C"})),
    (frozenset({"C"}),      frozenset({"D"})),
    (frozenset({"D"}),      frozenset({"E"})),
]
R = {"A", "B", "C", "D", "E"}

# --- attribute_closure ---

# AB→C, C→D, D→E: iz {A,B} treba da stignemo do celog R
def test_closure_ab():
    assert attribute_closure({"A", "B"}, FDS) == {"A", "B", "C", "D", "E"}

# C→D, D→E: iz {C} ne možemo da dobijemo A i B
def test_closure_c():
    assert attribute_closure({"C"}, FDS) == {"C", "D", "E"}

# A se ne pojavljuje ni na jednoj levoj strani — ne može ništa da zaključi
def test_closure_single_no_fd():
    assert attribute_closure({"A"}, FDS) == {"A"}
    
# prazan skup atributa — nema šta da se zaključi, rezultat je prazan skup
def test_closure_empty_set():
    assert attribute_closure(set(), FDS) == set()

# prazan skup FZ — nema šta da se primeni, zatvaranje = početni skup
def test_closure_empty_fds():
    assert attribute_closure({"A", "B"}, []) == {"A", "B"}

# ceo skup kao ulaz — zatvaranje ne može da poraste, vraća isti skup
def test_closure_full_set():
    assert attribute_closure({"A", "B", "C", "D", "E"}, FDS) == {"A", "B", "C", "D", "E"}

# steps mehanizam - proveravamo da li se koraci beleže
def test_closure_steps_recorded():
    steps = []
    attribute_closure({"A", "B"}, FDS, steps)
    assert len(steps) > 0
    assert steps[0]["action"] == "init"
    assert steps[-1]["action"] == "result"

# steps je None by default - ne sme da puca
def test_closure_no_steps_by_default():
    result = attribute_closure({"A", "B"}, FDS)
    assert result == {"A", "B", "C", "D", "E"}
    
# --- is_superkey ---

# AB+ = cela relacija → AB je superključ
def test_is_superkey_true():
    assert is_superkey({"A", "B"}, R, FDS) == True

# C+ = {C,D,E} ≠ R → C nije superključ
def test_is_superkey_false():
    assert is_superkey({"C"}, R, FDS) == False

# is_superkey sa praznim skupom FZ — X je superključ samo ako je X = R
def test_is_superkey_empty_fds():
    assert is_superkey({"A", "B"}, {"A", "B"}, []) == True
    assert is_superkey({"A"}, {"A", "B"}, []) == False

# --- find_candidate_keys ---

# R(A,B,C,D,E) sa F={AB→C, C→D, D→E}: jedini kandidat ključ je AB
def test_candidate_keys_single():
    keys = find_candidate_keys(R, FDS)
    assert len(keys) == 1
    assert frozenset({"A", "B"}) in keys

# R(A,B,C) sa F={A→B, B→A}: dva ekvivalentna ključa — A i B
def test_candidate_keys_multiple():
    fds = [
        (frozenset({"A"}), frozenset({"B"})),
        (frozenset({"B"}), frozenset({"A"})),
    ]
    keys = find_candidate_keys({"A", "B", "C"}, fds)
    assert frozenset({"A", "C"}) in keys
    assert frozenset({"B", "C"}) in keys

# bez FZ — jedini ključ je ceo skup atributa
def test_candidate_keys_no_fds():
    keys = find_candidate_keys({"A", "B", "C"}, [])
    assert keys == [frozenset({"A", "B", "C"})]

# R(A,B) sa F={A→B}: jedini ključ je A
def test_candidate_keys_simple():
    fds = [(frozenset({"A"}), frozenset({"B"}))]
    keys = find_candidate_keys({"A", "B"}, fds)
    assert len(keys) == 1
    assert frozenset({"A"}) in keys

# svi kandidat ključevi moraju biti superključevi
def test_candidate_keys_are_superkeys():
    keys = find_candidate_keys(R, FDS)
    for key in keys:
        assert is_superkey(key, R, FDS)

# nijedan pravi podskup kandidat ključa ne sme biti superključ
def test_candidate_keys_are_minimal():
    keys = find_candidate_keys(R, FDS)
    for key in keys:
        for size in range(1, len(key)):
            for subset in combinations(sorted(key), size):
                assert not is_superkey(frozenset(subset), R, FDS)