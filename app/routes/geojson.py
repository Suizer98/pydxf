from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse, JSONResponse

import os

from app.features.dxf2geojson import dxf2geojson

router = APIRouter()

DATA_DIR = "data"
os.makedirs(f"{DATA_DIR}/Files", exist_ok=True)
os.makedirs(f"{DATA_DIR}/Output", exist_ok=True)


@router.get("/geojson")
async def get_geojson(file_name: str):
    geojson_path = os.path.join(f"{DATA_DIR}/Output", file_name)
    if os.path.exists(geojson_path):
        with open(geojson_path, "r") as f:
            geojson_content = f.read()
        return JSONResponse(content=geojson_content, media_type="application/geo+json")
    else:
        return {"error": "GeoJSON file not found."}


@router.post("/geojson/upload")
async def upload_dxf_file(file: UploadFile):
    if not file.filename.lower().endswith(".dxf"):
        return {"error": "Only DXF files are allowed."}

    file_path = os.path.join(f"{DATA_DIR}/Files", file.filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    geojson_file_path = os.path.join(
        f"{DATA_DIR}/Output", file.filename.replace(".dxf", ".geojson")
    )
    dxf2geojson(file_path, geojson_file_path)

    return {
        "message": "File uploaded and converted successfully",
        "file_name": file.filename,
        "geojson_download_link": f"/pydxf/download/{file.filename.replace('.dxf', '.geojson')}",
    }


@router.get("/geojson/download")
async def download_geojson(file_name: str):
    geojson_path = os.path.join(f"{DATA_DIR}/Output", file_name)
    if os.path.exists(geojson_path):
        return FileResponse(
            geojson_path,
            media_type="application/geo+json",
            headers={"Content-Disposition": f"attachment; filename={file_name}"},
        )
    else:
        return {"error": "GeoJSON file not found."}
