from algorithm.bcnf import project_fds, find_bcnf_violation, is_bcnf

FDS = [
    (frozenset({"A", "B"}), frozenset({"C"})),
    (frozenset({"C"}),      frozenset({"D"})),
    (frozenset({"D"}),      frozenset({"E"})),
]

# projekcija na ceo skup — FZ ostaju iste
def test_project_fds_full_set():
    attrs = {"A", "B", "C", "D", "E"}
    result = project_fds(attrs, FDS)
    lhs_set = [lhs for lhs, _ in result]
    assert frozenset({"A", "B"}) in lhs_set
    assert frozenset({"C"}) in lhs_set
    assert frozenset({"D"}) in lhs_set

# projekcija na {C,D,E} — C određuje D i E, D određuje E
def test_project_fds_subset():
    attrs = {"C", "D", "E"}
    result = project_fds(attrs, FDS)
    rhs_by_lhs = {lhs: rhs for lhs, rhs in result}
    assert "D" in rhs_by_lhs[frozenset({"C"})]
    assert "E" in rhs_by_lhs[frozenset({"D"})]

# projekcija na skup bez ikakvih FZ — rezultat je prazna lista
def test_project_fds_no_relevant_fds():
    attrs = {"A", "B"}
    result = project_fds(attrs, FDS)
    assert result == []

# projekcija sa praznim skupom FZ
def test_project_fds_empty_fds():
    result = project_fds({"A", "B", "C"}, [])
    assert result == []

# projekcija na prazan skup atributa
def test_project_fds_empty_attrs():
    result = project_fds(set(), FDS)
    assert result == []

# R(A,B,C,D,E) sa AB kao jedinim ključem — C→D krši BCNF
def test_find_bcnf_violation_exists():
    attrs = {"A", "B", "C", "D", "E"}
    violation = find_bcnf_violation(attrs, FDS)
    assert violation is not None

# R(C,D) — C je ključ, C→D ne krši BCNF
def test_find_bcnf_violation_none_cd():
    attrs = {"C", "D"}
    assert find_bcnf_violation(attrs, FDS) is None

# R(A,B,C) — AB je ključ, AB→C ne krši BCNF
def test_find_bcnf_violation_none_abc():
    attrs = {"A", "B", "C"}
    assert find_bcnf_violation(attrs, FDS) is None

# prazna lista FZ — nema narušavanja
def test_find_bcnf_violation_empty_fds():
    assert find_bcnf_violation({"A", "B", "C"}, []) is None

# cela relacija nije u BCNF
def test_is_bcnf_false():
    assert is_bcnf({"A", "B", "C", "D", "E"}, FDS) == False

# R(C,D) jeste u BCNF
def test_is_bcnf_true_cd():
    assert is_bcnf({"C", "D"}, FDS) == True

# R(A,B,C) jeste u BCNF
def test_is_bcnf_true_abc():
    assert is_bcnf({"A", "B", "C"}, FDS) == True

# relacija sa jednim atributom — uvek u BCNF
def test_is_bcnf_single_attr():
    assert is_bcnf({"A"}, FDS) == True

# prazne FZ — uvek u BCNF
def test_is_bcnf_empty_fds():
    assert is_bcnf({"A", "B", "C"}, []) == True