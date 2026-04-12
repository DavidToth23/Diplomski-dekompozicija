from algorithm.fd_selection import check_p1, check_p2, check_p3, select_fd

# R(A,B,C,D), F = {A→B, C→D}
# Ključ: A+C
# A→B i C→D su BCNF narušavanja (A i C nisu superključevi)
FDS_ABCD = [
    (frozenset({"A"}), frozenset({"B"})),
    (frozenset({"C"}), frozenset({"D"})),
]
ATTRS_ABCD = {"A", "B", "C", "D"}

# R(A,B,C), F = {A→B, B→A, A→C}
# Ključevi: A, B
# B→A: zadovoljava P3, ali dekompozicijom se gubi A→C → P2 = False
FDS_LOSE = [
    (frozenset({"A"}), frozenset({"B"})),
    (frozenset({"B"}), frozenset({"A"})),
    (frozenset({"A"}), frozenset({"C"})),
]
ATTRS_LOSE = {"A", "B", "C"}

# R(A,B,C), F = {A→B, B→C, A→C}
# Ključ: A
# Šema nije u BCNF, A→B čuva sve FZ → P1 = True
FDS_P1 = [
    (frozenset({"A"}), frozenset({"B"})),
    (frozenset({"B"}), frozenset({"C"})),
    (frozenset({"A"}), frozenset({"C"})),
]
ATTRS_P1 = {"A", "B", "C"}

# R(A,B,C,D), F = {AB→C, AB→D, C→A, D→B}
# Ključevi: AB, CB, AD
# C→A: C nije superključ, ali dekompozicijom se gubi D→B → samo P3
FDS_P3_ONLY = [
    (frozenset({"A", "B"}), frozenset({"C"})),
    (frozenset({"A", "B"}), frozenset({"D"})),
    (frozenset({"C"}),      frozenset({"A"})),
    (frozenset({"D"}),      frozenset({"B"})),
]
ATTRS_P3_ONLY = {"A", "B", "C", "D"}


# --- check_p3 ---

# A→B u R(A,B,C,D): A nije superključ, FZ je netrivijalna → P3 = True
def test_check_p3_true():
    assert check_p3(frozenset({"A"}), "B", ATTRS_ABCD, FDS_ABCD) == True

# A+C je superključ R(A,B,C,D) → P3 = False
def test_check_p3_superkey():
    assert check_p3(frozenset({"A", "C"}), "B", ATTRS_ABCD, FDS_ABCD) == False

# trivijalna FZ: A→A → P3 = False
def test_check_p3_trivial():
    fds = [(frozenset({"A"}), frozenset({"A"}))]
    assert check_p3(frozenset({"A"}), "A", {"A", "B"}, fds) == False

# FZ obuhvata ceo R: R(A,B), A→B → Y∪{B} = {A,B} = R → P3 = False
def test_check_p3_full_set():
    fds = [(frozenset({"A"}), frozenset({"B"}))]
    assert check_p3(frozenset({"A"}), "B", {"A", "B"}, fds) == False

# prazne FZ — FZ ne važi, P3 = False
def test_check_p3_empty_fds():
    assert check_p3(frozenset({"A"}), "B", {"A", "B", "C"}, []) == False


# --- check_p2 ---

# A→B u R(A,B,C,D) čuva sve FZ → P2 = True
def test_check_p2_true():
    assert check_p2(frozenset({"A"}), "B", ATTRS_ABCD, FDS_ABCD) == True

# B→A u R(A,B,C) sa F={A→B, B→A, A→C}: dekompozicijom se gubi A→C → P2 = False
def test_check_p2_false_loses_fd():
    assert check_p2(frozenset({"B"}), "A", ATTRS_LOSE, FDS_LOSE) == False

# A+C je superključ → P3 = False → P2 = False
def test_check_p2_fails_if_p3_fails():
    assert check_p2(frozenset({"A", "C"}), "B", ATTRS_ABCD, FDS_ABCD) == False


# --- check_p1 ---

# A→B u R(A,B,C,D): čuva FZ i A je na kraju lanca → P1 = True
def test_check_p1_true():
    assert check_p1(frozenset({"A"}), "B", ATTRS_ABCD, FDS_ABCD) == True

# B→A u R(A,B,C): ne zadovoljava P2 → P1 = False
def test_check_p1_false():
    assert check_p1(frozenset({"B"}), "A", ATTRS_LOSE, FDS_LOSE) == False

# A+C je superključ → P2 = False → P1 = False
def test_check_p1_fails_if_p2_fails():
    assert check_p1(frozenset({"A", "C"}), "B", ATTRS_ABCD, FDS_ABCD) == False


# --- select_fd ---

# R(A,B,C,D): izabrana FZ mora zadovoljavati P1
def test_select_fd_p1():
    result = select_fd(ATTRS_ABCD, FDS_ABCD)
    assert result is not None
    lhs, attr = result
    assert check_p1(lhs, attr, ATTRS_ABCD, FDS_ABCD) == True

# R(A,B,C,D) sa F={AB→C, AB→D, C→A, D→B}: C→A zadovoljava samo P3
def test_select_fd_p3():
    result = select_fd(ATTRS_P3_ONLY, FDS_P3_ONLY)
    assert result is not None
    lhs, attr = result
    assert check_p3(lhs, attr, ATTRS_P3_ONLY, FDS_P3_ONLY) == True
    assert check_p2(lhs, attr, ATTRS_P3_ONLY, FDS_P3_ONLY) == False

# šema u BCNF — select_fd vraća None
def test_select_fd_bcnf():
    fds = [(frozenset({"A", "B"}), frozenset({"C"}))]
    assert select_fd({"A", "B", "C"}, fds) is None

# prazne FZ — select_fd vraća None
def test_select_fd_empty_fds():
    assert select_fd({"A", "B", "C"}, []) is None

# jedan atribut — uvek u BCNF
def test_select_fd_single_attr():
    fds = [(frozenset({"A"}), frozenset({"B"}))]
    assert select_fd({"A"}, fds) is None