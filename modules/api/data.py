from fastapi import APIRouter

from .visualization import objects

router = APIRouter()


@router.get("/")
def get_data():
    return {"objects": objects}
