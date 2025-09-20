import os

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

from app.conv_music import import_music


app = FastAPI()

if not os.path.exists("temp"):
    os.makedirs("temp")


@app.post("/import_music")
async def import_music_api( music_file: UploadFile = File(...)):

    with open(f"temp/{music_file.filename}", "wb") as f:
        f.write(await music_file.read())
    music_path = f"temp/{music_file.filename}"
    status = await import_music(music_path)
    if status:
        return {"message": "乐曲导入成功"}
    else:
        return {"message": "乐曲导入失败"}
