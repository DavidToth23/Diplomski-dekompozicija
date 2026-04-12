from algorithm.closure import attribute_closure, is_superkey

FDS = [
    (frozenset({"A", "B"}), frozenset({"C"})),
    (frozenset({"C"}),      frozenset({"D"})),
    (frozenset({"D"}),      frozenset({"E"})),
]
R = {"A", "B", "C", "D", "E"}


# AB→C, C→D, D→E: iz {A,B} treba da stignemo do celog R
def test_closure_ab():
    assert attribute_closure({"A", "B"}, FDS) == {"A", "B", "C", "D", "E"}

# C→D, D→E: iz {C} ne možemo da dobijemo A i B
def test_closure_c():
    assert attribute_closure({"C"}, FDS) == {"C", "D", "E"}

# A se ne pojavljuje ni na jednoj levoj strani — ne može ništa da zaključi
def test_closure_single_no_fd():
    assert attribute_closure({"A"}, FDS) == {"A"}

# AB+ = cela relacija → AB je superključ
def test_is_superkey_true():
    assert is_superkey({"A", "B"}, R, FDS) == True

# C+ = {C,D,E} ≠ R → C nije superključ
def test_is_superkey_false():
    assert is_superkey({"C"}, R, FDS) == False

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

# is_superkey sa praznim skupom FZ — X je superključ samo ako je X = R
def test_is_superkey_empty_fds():
    assert is_superkey({"A", "B"}, {"A", "B"}, []) == True
    assert is_superkey({"A"}, {"A", "B"}, []) == False