import yaml
from fastapi import APIRouter

from ..animations import to_dict
from ..config import CONFIG

router = APIRouter()


@router.get("/")
def get_config():
    return {
        "projection": {
            "src_points": CONFIG.SRC_POINTS,
            "dst_points": CONFIG.DST_POINTS,
            "floor": CONFIG.FLOOR,
        },
        "leds": {
            "target_weight": CONFIG.TARGET_WEIGHT,
            "offset_x": CONFIG.OFFSET_X,
            "offset_y": CONFIG.OFFSET_Y,
        },
        "strips": [
            {
                "index": s.index,
                "len": s.len,
                "start": [s.start.x, s.start.y],
                "end": [s.end.x, s.end.y],
            }
            for s in CONFIG.STRIPS
        ],
        "animations": {
            "idle": to_dict(CONFIG.IDLE_ANIMATION),
            "object": to_dict(CONFIG.OBJECT_ANIMATION),
        },
    }


@router.put("/")
def update_config(new_config: dict):
    with open(CONFIG.path, "w") as f:
        yaml.dump(new_config, f)
    CONFIG.load()
    return {"message": "Config updated successfully"}
