from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app() -> FastAPI:
    app = FastAPI()

    from slack_bot.api.slack import slack_router
    app.include_router(slack_router, tags=["slack"])

    from slack_bot.api.fireflies import fireflies_router
    app.include_router(fireflies_router, tags=["fireflies"])


    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def read_root():
        return {"report": "Hello world!"}

    return app
