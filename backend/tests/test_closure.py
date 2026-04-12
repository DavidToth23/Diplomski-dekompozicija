from algorithm.closure import attribute_closure, is_superkey

# primer koji koristimo kroz ceo projekat
FDS = [
    (frozenset({"A", "B"}), frozenset({"C"})),
    (frozenset({"C"}),      frozenset({"D"})),
    (frozenset({"D"}),      frozenset({"E"})),
]
R = {"A", "B", "C", "D", "E"}


def test_closure_ab():
    assert attribute_closure({"A", "B"}, FDS) == {"A", "B", "C", "D", "E"}

def test_closure_c():
    assert attribute_closure({"C"}, FDS) == {"C", "D", "E"}

def test_closure_single_no_fd():
    assert attribute_closure({"A"}, FDS) == {"A"}

def test_is_superkey_true():
    assert is_superkey({"A", "B"}, R, FDS) == True

def test_is_superkey_false():
    assert is_superkey({"C"}, R, FDS) == False