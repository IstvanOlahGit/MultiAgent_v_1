from fastapi.routing import APIRouter

fireflies_router = APIRouter(
    prefix="/fireflies", tags=["slack"]
)

from . import views