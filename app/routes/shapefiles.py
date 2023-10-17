from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse, JSONResponse

import os

from app.features.dxf2shp import dxf2shp

router = APIRouter()

DATA_DIR = "data"
os.makedirs(f"{DATA_DIR}/Files", exist_ok=True)
os.makedirs(f"{DATA_DIR}/Output", exist_ok=True)


@router.post("/shp/upload")
async def upload_dxf_file(file: UploadFile):
    if not file.filename.lower().endswith(".dxf"):
        return {"error": "Only DXF files are allowed."}

    file_path = os.path.join(f"{DATA_DIR}/Files", file.filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    shp_file_path = os.path.join(
        f"{DATA_DIR}/Output", file.filename.replace(".dxf", ".shp")
    )
    dxf2shp(file_path, shp_file_path)

    return {
        "message": "File uploaded and converted successfully",
        "file_name": file.filename,
        "shp_download_link": f"/pydxf/shp/download?{file.filename.replace('.dxf', '')}",
    }
