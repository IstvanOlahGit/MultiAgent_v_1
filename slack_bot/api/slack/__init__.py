from fastapi.routing import APIRouter

slack_router = APIRouter(
    prefix="/slack/events", tags=["event"]
)

from . import views