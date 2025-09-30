from fastapi import APIRouter, UploadFile
from fastapi.responses import JSONResponse
import os
from datetime import datetime

router = APIRouter()
DATA_DIR = "data"
os.makedirs(f"{DATA_DIR}/Files", exist_ok=True)
os.makedirs(f"{DATA_DIR}/Output", exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile):
    file_extension = file.filename.lower().split('.')[-1]
    
    if file_extension not in ["dxf", "dwg"]:
        return {"error": "Only DXF and DWG files are allowed."}

    file_path = os.path.join(f"{DATA_DIR}/Files", file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    
    return {
        "message": f"{file_extension.upper()} file uploaded successfully. Conversion will happen on download.",
        "file_name": file.filename,
        "file_type": file_extension
    }


@router.get("/files")
async def list_uploaded_files():
    files = []
    
    if os.path.exists(f"{DATA_DIR}/Files"):
        for filename in os.listdir(f"{DATA_DIR}/Files"):
            if filename.lower().endswith(('.dxf', '.dwg')):
                file_path = os.path.join(f"{DATA_DIR}/Files", filename)
                file_stat = os.stat(file_path)
                
                file_info = {
                    "filename": filename,
                    "file_type": filename.lower().split('.')[-1],
                    "size_bytes": file_stat.st_size,
                    "size_mb": round(file_stat.st_size / (1024 * 1024), 2),
                    "uploaded_at": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    "download_links": {
                        "shapefile": f"/pydxf/shp/download?filename={filename}",
                        "geojson": f"/pydxf/geojson/download?filename={filename}"
                    }
                }
                files.append(file_info)
    
    files.sort(key=lambda x: x["uploaded_at"], reverse=True)
    
    return {
        "total_files": len(files),
        "files": files
    }
