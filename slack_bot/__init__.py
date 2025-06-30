from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, HTTPException


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

    SECRET_TOKEN = "my_secret_token"

    @app.post("/api/webhook/recall")
    async def recall_webhook(request: Request):
        token = request.query_params.get("token")
        if token != SECRET_TOKEN:
            raise HTTPException(status_code=403, detail="Forbidden")

        data = await request.json()
        print("Received webhook event:")
        print(data)

        return {"status": "ok"}

    return app
