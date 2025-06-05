from fastapi.routing import APIRouter

slack_router = APIRouter(
    prefix="/slack/events", tags=["slack"]
)

from . import views