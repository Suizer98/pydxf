import asyncio
import io
import os
import shutil

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import zipfile
from app.common import DATA_DIR, ensure_data_dirs
from app.features.dxf2shp import dxf2shp
from app.features.dwg2dxf import convert_dwg_to_dxf, dwg_conversion_response_headers

router = APIRouter()


@router.get("/shp/download")
async def download_shapefiles(filename: str):
    ensure_data_dirs()
    dwg_step = None
    base_filename = filename.replace(".shp", "")
    shp_filename = f"{base_filename}.shp"

    if filename.lower().endswith((".dxf", ".dwg")):
        original_filename = filename
        base_filename = filename.rsplit(".", 1)[0]
        shp_filename = f"{base_filename}.shp"

    matching_shapefiles = []
    for root, _, files in os.walk(f"{DATA_DIR}/Output"):
        for file in files:
            if file.startswith(base_filename) and file.endswith(".shp"):
                matching_shapefiles.append(file)

    if not matching_shapefiles:
        if "original_filename" not in locals():
            original_filename = base_filename
            possible_extensions = [".dwg", ".dxf"]
            for ext in possible_extensions:
                original_file_path = os.path.join(
                    f"{DATA_DIR}/Files", original_filename + ext
                )
                if os.path.exists(original_file_path):
                    break
        else:
            original_file_path = os.path.join(f"{DATA_DIR}/Files", original_filename)

        if os.path.exists(original_file_path):
            file_extension = original_file_path.lower().split(".")[-1]

            if file_extension == "dwg":
                dxf_filename = f"{base_filename}_dwg.dxf"
                dxf_file_path = os.path.join(f"{DATA_DIR}/Output", dxf_filename)
                shp_file_path_dwg = os.path.join(
                    f"{DATA_DIR}/Output", f"{base_filename}_dwg.shp"
                )

                dwg_step = await asyncio.to_thread(
                    convert_dwg_to_dxf, original_file_path, dxf_file_path
                )
                if not dwg_step.success:
                    raise HTTPException(
                        status_code=500, detail="Failed to convert DWG to DXF"
                    )

                await asyncio.to_thread(dxf2shp, dxf_file_path, shp_file_path_dwg)
            else:
                dxf_filename = f"{base_filename}_dxf.dxf"
                dxf_file_path = os.path.join(f"{DATA_DIR}/Output", dxf_filename)
                shp_file_path_dxf = os.path.join(
                    f"{DATA_DIR}/Output", f"{base_filename}_dxf.shp"
                )

                await asyncio.to_thread(shutil.copy2, original_file_path, dxf_file_path)
                await asyncio.to_thread(dxf2shp, dxf_file_path, shp_file_path_dxf)

            for root, _, files in os.walk(f"{DATA_DIR}/Output"):
                for file in files:
                    if file.startswith(base_filename) and file.endswith(".shp"):
                        matching_shapefiles.append(file)

        if not matching_shapefiles:
            raise HTTPException(
                status_code=404, detail="No matching files found for conversion."
            )

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for shapefile in matching_shapefiles:
            base_name = shapefile.replace(".shp", "")
            for root, _, files in os.walk(f"{DATA_DIR}/Output"):
                for file in files:
                    if file.startswith(base_name) and file.endswith(
                        (".shp", ".shx", ".dbf", ".prj", ".cpg", ".sbn", ".sbx")
                    ):
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, file)

    zip_buffer.seek(0)
    out_headers = {
        "Content-Disposition": f"attachment; filename={base_filename}.zip",
        **dwg_conversion_response_headers(dwg_step),
    }
    return StreamingResponse(
        content=zip_buffer,
        media_type="application/zip",
        headers=out_headers,
    )
