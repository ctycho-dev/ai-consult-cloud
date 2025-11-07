from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware


def add_cors_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://localhost:8010",
            "http://localhost:5010"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )