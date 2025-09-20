from fastapi import FastAPI
from pydantic import BaseModel

from app.conv_music import import_music


app = FastAPI()

class MusicFile(BaseModel):
    music_file: bytes


@app.post("/import_music")
async def import_music_api( music_file: MusicFile):
    status = await import_music(music_file.music_file)
    if status:
        return {"message": "乐曲导入成功"}
    else:
        return {"message": "乐曲导入失败"}
