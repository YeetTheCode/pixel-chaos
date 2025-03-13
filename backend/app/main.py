from fastapi import FastAPI

from app.api.routes import canvas

# Initialize app
app = FastAPI(title="Canvas API")

# CORS middleware

# Include routers
app.include_router(canvas.router, prefix="/api", tags=["canvas"])


@app.get("/")
async def root():
    return {"message": "Canvas API is running"}
