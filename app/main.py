from fastapi import FastAPI
from app.api.routes.images import router as image_router


app = FastAPI(
    title="Image Service API",
    version="1.0.0"
)

app.include_router(image_router)