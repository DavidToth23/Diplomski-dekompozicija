from fastapi import HTTPException
from typing import List, Set
from models import FunctionalDependency


def validate_fd_attributes(attributes: Set[str], fds: List[FunctionalDependency]):
    for fd in fds:
        all_fd_attrs = set(fd.lhs) | set(fd.rhs)
        unknown = all_fd_attrs - attributes

        if unknown:
            fd_display = f"{', '.join(sorted(fd.lhs))} → {', '.join(sorted(fd.rhs))}"
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Funkcionalna zavisnost '{fd_display}' sadrži obeležja "
                    f"{sorted(unknown)} koja nisu u skupu obeležja relacije."
                )
            )