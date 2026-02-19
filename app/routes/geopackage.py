from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from app.features.dxf2gpkg import dxf2gpkg
from app.features.dwg2dxf import convert_dwg_to_dxf

router = APIRouter()
DATA_DIR = "data"
os.makedirs(f"{DATA_DIR}/Files", exist_ok=True)
os.makedirs(f"{DATA_DIR}/Output", exist_ok=True)


@router.get("/gpkg/download")
async def download_geopackage(filename: str):
    base_filename = filename.replace(".gpkg", "")

    if filename.lower().endswith((".dxf", ".dwg")):
        original_filename = filename
        base_filename = filename.rsplit(".", 1)[0]
        gpkg_filename = f"{base_filename}.gpkg"
    else:
        gpkg_filename = f"{base_filename}.gpkg"

    gpkg_file_path = os.path.join(f"{DATA_DIR}/Output", gpkg_filename)

    if not os.path.exists(gpkg_file_path):
        if "original_filename" not in locals():
            original_filename = base_filename
            possible_extensions = [".dxf", ".dwg"]
            original_file_path = None
            file_extension = None

            for ext in possible_extensions:
                test_path = os.path.join(f"{DATA_DIR}/Files", original_filename + ext)
                if os.path.exists(test_path):
                    original_file_path = test_path
                    file_extension = ext
                    break
        else:
            original_file_path = os.path.join(f"{DATA_DIR}/Files", original_filename)
            file_extension = "." + original_filename.lower().split(".")[-1]

        if not original_file_path or not os.path.exists(original_file_path):
            raise HTTPException(
                status_code=404,
                detail=f"No uploaded file found for '{base_filename}'. Please upload a DXF or DWG file first.",
            )

        try:
            if file_extension == ".dwg":
                dxf_file_path = os.path.join(
                    f"{DATA_DIR}/Output", base_filename + "_dwg.dxf"
                )
                if convert_dwg_to_dxf(original_file_path, dxf_file_path):
                    dxf2gpkg(dxf_file_path, gpkg_file_path)
                else:
                    raise HTTPException(
                        status_code=500, detail="Failed to convert DWG to DXF"
                    )
            else:
                dxf2gpkg(original_file_path, gpkg_file_path)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to convert to GeoPackage: {str(e)}",
            )

        if not os.path.exists(gpkg_file_path):
            raise HTTPException(
                status_code=500,
                detail="GeoPackage conversion failed - no output file created.",
            )

    return FileResponse(
        gpkg_file_path,
        media_type="application/geopackage+sqlite3",
        headers={"Content-Disposition": f"attachment; filename={gpkg_filename}"},
    )
