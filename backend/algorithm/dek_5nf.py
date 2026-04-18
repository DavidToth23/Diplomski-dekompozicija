from typing import List, Tuple, Set
from algorithm.normal_forms import project_fds
from algorithm.closure import attribute_closure
"""
Segment 'dek_5NF' algoritma dekompozicije.

Dekomponuje skup šema (dobijen nakon 4NF faze) na šeme u 5NF,
eliminišući zavisnosti spajanja (join dependencies — JD) koje krše 5NF.

Algoritam (prema pseudokodu):
    RADI dek_5NF ∀(Ri, Fi) ∈ T  DOK JE T ≠ ∅
        POSTAVI T ← T \ {(Ri, Fi)}
        AKO JE (∃⊳◁(Y1,...,Yk) ∈ J)
               ((Ri = ⋃Y_l) ∧ (∀Yi ∈ {Y1,...,Yk})(Ri ⊄ (Yi)_Fi⁺)) TADA
            RADI dek ∀Yi ∈ {Y1,...,Yk}
                POSTAVI T ← T ∪ {(Yi, F|Yi)}
            KRAJ RADI dek
        INAČE
            POSTAVI S ← S ∪ {(Ri, Fi)}
        KRAJ AKO
    KRAJ RADI dek_5NF

JD ⊳◁(Y1,...,Yk) važi u relaciji R ako je R jednaka spajanju projekcija
na Y1, ..., Yk. JD je trivijalna ako jedan od Yi = R.
"""


# JD se reprezentuje kao lista frozenset-ova komponenti
JoinDependency = List[frozenset]


def is_trivial_jd(jd: JoinDependency, attrs: frozenset) -> bool:
    """
    JD ⊳◁(Y1,...,Yk) je trivijalna ako je jedan od Yi jednak R (attrs).
    """
    return any(y == attrs for y in jd)


def jd_covers_relation(jd: JoinDependency, attrs: frozenset) -> bool:
    """
    Proverava da li JD pokriva relaciju: Ri = ⋃Yi.
    """
    return frozenset().union(*jd) == attrs


def find_5nf_violation(
    attrs: frozenset,
    fds: List[Tuple[frozenset, frozenset]],
    join_deps: List[JoinDependency]
) -> JoinDependency | None:
    """
    Traži JD ⊳◁(Y1,...,Yk) koja krši 5NF:
      1. Ri = ⋃Yi  (JD pokriva relaciju)
      2. ∀Yi ∈ {Y1,...,Yk}: Ri ⊄ (Yi)_Fi⁺  (nijedan Yi nije superključ)

    Uslov 2 osigurava da JD nije posledica neke FZ (tj. da je "prava" JD).
    """

    for jd in join_deps:
        # Uslov 1: JD pokriva relaciju
        if not jd_covers_relation(jd, attrs):
            continue

        # Trivijalna JD — preskoči
        if is_trivial_jd(jd, attrs):
            continue

        # JD mora imati bar 3 komponente (sa 2 je to MVD)
        if len(jd) < 2:
            continue

        # Uslov 2: nijedan Yi nije superključ
        all_non_superkey = True
        for yi in jd:
            yi_closure = frozenset(attribute_closure(yi, fds))
            if yi_closure >= attrs:
                all_non_superkey = False
                break

        if all_non_superkey:
            return jd

    return None


def dek_5nf(
    relations: List[dict],
    fds: List[Tuple[frozenset, frozenset]],
    join_deps: List[JoinDependency]
) -> Tuple[List[dict], List[dict]]:
    """
    Segment 'dek_5NF' algoritma dekompozicije.

    Prima listu šema (izlaz iz 4NF faze) i dekomponiše svaku
    koja ima JD narušavanje 5NF.

    Parametri:
        relations  — lista šema kao dict sa 'attrs' i 'fds'
        fds        — originalni skup FZ (za projekciju)
        join_deps  — skup zavisnosti spajanja J

    Vraća:
        relations  — lista šema u 5NF
        steps      — lista koraka za prikaz
    """
    # T — radni skup šema, S — finalni skup šema u 5NF
    T = list(relations)
    S = []
    steps = []

    steps.append({
        "phase": "init_5nf",
        "message": (
            f"Početak dek_5NF: "
            f"T = {[sorted(r['attrs']) for r in T]}"
        )
    })

    while T:
        current = T.pop(0)
        Ri = current["attrs"]
        Fi = current["fds"]

        ri_str = f"R({', '.join(sorted(Ri))})"

        # Filtriramo JD koje su relevantne za Ri
        # (komponente JD moraju biti podskup atributa Ri)
        relevant_jds = [
            jd for jd in join_deps
            if all(y.issubset(Ri) for y in jd)
        ]

        violation = find_5nf_violation(Ri, Fi, relevant_jds)

        if violation is not None:
            components_str = ", ".join(
                f"({', '.join(sorted(y))})" for y in violation
            )
            steps.append({
                "phase": "5nf_violation",
                "relation": sorted(Ri),
                "jd_components": [sorted(y) for y in violation],
                "message": (
                    f"✗ {ri_str} nije u 5NF — "
                    f"JD narušavajuće: ⊳◁[{components_str}]"
                )
            })

            # Dekomponujemo na komponente JD
            new_relations = []
            for yi in violation:
                fi_yi = project_fds(yi, Fi)
                new_relations.append({"attrs": yi, "fds": fi_yi})

                yi_str = f"R({', '.join(sorted(yi))})"
                steps.append({
                    "phase": "5nf_split_component",
                    "component": sorted(yi),
                    "message": f"  Dodajem komponentu: {yi_str}"
                })

            steps.append({
                "phase": "5nf_split",
                "components": [sorted(y) for y in violation],
                "message": (
                    f"  {ri_str} dekomponovan na "
                    f"{len(violation)} šeme"
                )
            })

            # Vraćamo komponente u T na dalju proveru
            T.extend(new_relations)

        else:
            # Šema je u 5NF — premještamo u S
            S.append(current)
            steps.append({
                "phase": "5nf_ok",
                "relation": sorted(Ri),
                "message": f"✓ {ri_str} je u 5NF → premještamo u S"
            })

    steps.append({
        "phase": "done_5nf",
        "relations": [sorted(r["attrs"]) for r in S],
        "message": (
            f"dek_5NF završen — "
            f"dobijeno {len(S)} šema relacija"
        )
    })

    return S, steps
