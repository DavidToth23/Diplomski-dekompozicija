"""
Segment 'dek_4NF' algoritma dekompozicije.

Dekomponuje skup šema (dobijen nakon BCNF + unija faze) na šeme u 4NF,
eliminišući višeznačne zavisnosti koje krše 4NF.

Algoritam (prema pseudokodu):
    RADI dek_4NF ∀(Ri, Fi) ∈ S DOK JE S ≠ ∅
        POSTAVI S ← S \ {(Ri, Fi)}
        IZRAČUNAJ M|Ri  (projektovane MVD na Ri)
        AKO JE (∃Y ↠→ Z ∈ M|Ri)(Z ⊄ Y) ∧ (Ri bez YZ ≠ ∅) ∧ (Ri ⊄ Y_Fi⁺) TADA
            POSTAVI S ← S ∪ {(YZ, F|YZ), (Y(Ri\Z), F|Y(Ri\Z))}
        INAČE
            POSTAVI T ← T ∪ {(Ri, Fi)}
        KRAJ AKO
    KRAJ RADI dek_4NF
"""
from typing import List, Tuple, Set
from algorithm.normal_forms import project_fds
from algorithm.closure import attribute_closure
from algorithm.mvd import project_mvds


def dek_4nf(
    relations: List[dict],
    fds: List[Tuple[frozenset, frozenset]],
    mvds: List
) -> Tuple[List[dict], List[dict]]:
    """
    Segment 'dek_4NF' algoritma dekompozicije.

    Prima listu šema (izlaz iz faze unije) i dekomponuje svaku
    koja nije u 4NF, koristeći MVD narušavanja.

    Parametri:
        relations — lista šema kao dict sa 'attrs' i 'fds'
        fds       — originalni skup FZ (za projekciju)
        mvds      — skup višeznačnih zavisnosti M

    Vraća:
        relations — lista šema u 4NF
        steps     — lista koraka za prikaz
    """
    # S — radni skup šema koje još treba proveriti
    # T — finalni skup šema u 4NF (odgovara T u pseudokodu)
    S = list(relations)
    T = []
    steps = []

    steps.append({
        "phase": "init_4nf",
        "message": (
            f"Početak dek_4NF: "
            f"S = {[sorted(r['attrs']) for r in S]}"
        )
    })

    while S:
        current = S.pop(0)
        Ri = current["attrs"]
        Fi = current["fds"]

        ri_str = f"R({', '.join(sorted(Ri))})"

        # Računamo M|Ri — projektovane MVD na atribute Ri
        projected_mvds = project_mvds(Ri, Fi, mvds)

        # Tražimo MVD koja krši 4NF:
        # (∃Y ↠ Z ∈ M|Ri)(Z ⊄ Y) ∧ (Ri bez YZ ≠ ∅) ∧ (Ri ⊄ YFi⁺)
        violation = _find_4nf_violation_strict(Ri, Fi, projected_mvds)

        if violation is not None:
            Y, Z = violation
            YZ = Y | Z
            Y_Ri_minus_Z = Y | (Ri - Z)

            y_str = f"{{{', '.join(sorted(Y))}}}"
            z_str = f"{{{', '.join(sorted(Z))}}}"

            steps.append({
                "phase": "4nf_violation",
                "relation": sorted(Ri),
                "mvd_lhs": sorted(Y),
                "mvd_rhs": sorted(Z),
                "message": (
                    f"✗ {ri_str} nije u 4NF — "
                    f"MVD narušavajuće: {y_str} ↠ {z_str}"
                )
            })

            # Formiramo dve nove šeme:
            # R1 = YZ sa projekcijom FZ
            # R2 = Y ∪ (Ri bez Z) sa projekcijom FZ
            f_yz = project_fds(YZ, Fi)
            f_y_rimz = project_fds(Y_Ri_minus_Z, Fi)

            r1_str = f"R({', '.join(sorted(YZ))})"
            r2_str = f"R({', '.join(sorted(Y_Ri_minus_Z))})"

            steps.append({
                "phase": "4nf_split",
                "r1": sorted(YZ),
                "r2": sorted(Y_Ri_minus_Z),
                "message": f"  Delimo na: {r1_str} i {r2_str}"
            })

            # Vraćamo u S na dalju proveru
            S.append({"attrs": YZ, "fds": f_yz})
            S.append({"attrs": Y_Ri_minus_Z, "fds": f_y_rimz})

        else:
            # Šema je u 4NF — premeštamo u T
            T.append(current)
            steps.append({
                "phase": "4nf_ok",
                "relation": sorted(Ri),
                "message": f"✓ {ri_str} je u 4NF → premještamo u T"
            })

    steps.append({
        "phase": "done_4nf",
        "relations": [sorted(r["attrs"]) for r in T],
        "message": (
            f"dek_4NF završen — "
            f"dobijeno {len(T)} šema relacija"
        )
    })

    return T, steps


def _find_4nf_violation_strict(
    attrs: frozenset,
    fds: List[Tuple[frozenset, frozenset]],
    projected_mvds: List
) -> tuple | None:
    """
    Traži MVD Y ↠ Z koja krši 4NF prema uslovima iz pseudokoda:
      1. Z ⊄ Y  (netrivijalna u smislu podskupa)
      2. Ri bez YZ ≠ ∅  (postoje atributi van Y ∪ Z)
      3. Ri ⊄ YFi⁺  (Y nije superključ — ne determiniše sve)

    Ovaj stroži uslov osigurava da dekompozicija ima smisla i da
    ne razlaže šemu na isuviše sitne delove.
    """

    for Y, Z in projected_mvds:
        # Uslov 1: Z ⊄ Y (netrivijalna)
        if Z.issubset(Y):
            continue

        # Uslov 2: postoje atributi van Y ∪ Z
        if not (attrs - (Y | Z)):
            continue

        # Uslov 3: Y nije superključ
        y_closure = frozenset(attribute_closure(Y, fds))
        if y_closure >= attrs:
            continue

        return (Y, Z)

    return None
