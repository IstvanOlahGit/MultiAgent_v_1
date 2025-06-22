from fastapi.routing import APIRouter

fireflies_router = APIRouter(
    prefix="/fireflies", tags=["fireflies"]
)

from . import views