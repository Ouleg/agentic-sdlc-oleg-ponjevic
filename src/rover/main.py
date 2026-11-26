"""FastAPI application for the Rover Service (Ch. 5.1, Ch. 5.3)."""

from fastapi import FastAPI

from rover.adapters.route import router

app = FastAPI()
app.include_router(router)
