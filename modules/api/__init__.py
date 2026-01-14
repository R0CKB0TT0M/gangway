from fastapi import FastAPI

from . import animations, config, data, visualization

app = FastAPI()

app.include_router(visualization.router, prefix="/visualization")
app.include_router(config.router, prefix="/config")
app.include_router(data.router, prefix="/data")
app.include_router(animations.router, prefix="/animations")
