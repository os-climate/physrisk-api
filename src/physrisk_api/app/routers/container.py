"""Endpoints and DI helpers for managing the dependency-injector container."""

from fastapi import APIRouter
from physrisk_api.app.container import create_container

router = APIRouter(tags=["container"])
container = create_container()


def requester():
    """Provide a Requester instance resolved from the DI container."""
    # We mainly use FastAPI's own dependency injection via Depends, but dependencies can have access to
    #  dependency_injector's declarative container.
    return container.requester()


@router.get(
    "/api/reset",
    summary="Reset the container singletons",
    description="Reset the container singletons which are used to create the requester. This is mainly for developing purposes.",
)
def reset():
    """Reset container singletons and return a success message."""
    container.reset_singletons()
    return "Reset successful"
