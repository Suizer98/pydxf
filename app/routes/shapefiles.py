from fastapi import APIRouter, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi import HTTPException

import os
import io
import zipfile

from app.features.dxf2shp import dxf2shp

router = APIRouter()

DATA_DIR = "data"
os.makedirs(f"{DATA_DIR}/Files", exist_ok=True)
os.makedirs(f"{DATA_DIR}/Output", exist_ok=True)


@router.get("/shp")
async def get_shapefiles(file_name: str):
    matching_shapefiles = []

    for root, _, files in os.walk(f"{DATA_DIR}/Output"):
        for file in files:
            if file.startswith(file_name) and file.endswith(".shp"):
                matching_shapefiles.append(file)

    if matching_shapefiles:
        return JSONResponse(content=matching_shapefiles, media_type="application/json")
    else:
        return {"error": "Matching shapefiles not found."}


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
        "shp_download_link": f"/pydxf/shp/download?{file.filename.replace('.dxf', '.shp')}",
    }


@router.get("/shp/download")
async def download_shapefiles(file_name: str):
    matching_shapefiles = []

    for root, _, files in os.walk(f"{DATA_DIR}/Output"):
        for file in files:
            if file.startswith(file_name) and file.endswith(".shp"):
                matching_shapefiles.append(file)

    if matching_shapefiles:
        if len(matching_shapefiles) == 1:
            # If there is only one matching shapefile, return it directly
            shapefile_path = os.path.join(f"{DATA_DIR}/Output", matching_shapefiles[0])
            return FileResponse(shapefile_path, media_type="application/octet-stream")

        # Create an in-memory ZIP archive
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for shapefile in matching_shapefiles:
                shapefile_path = os.path.join(f"{DATA_DIR}/Output", shapefile)
                # Add the shapefile to the ZIP archive
                zipf.write(shapefile_path, os.path.basename(shapefile_path))

        # Seek to the beginning of the buffer
        zip_buffer.seek(0)

        # Return the ZIP archive as a response
        return StreamingResponse(
            content=zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={file_name}.zip"},
        )
    else:
        raise HTTPException(status_code=404, detail="No matching shapefiles found.")
