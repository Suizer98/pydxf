from fastapi.responses import StreamingResponse
from fastapi import HTTPException, APIRouter
import os
import io
import zipfile
from app.features.dxf2shp import dxf2shp
from app.features.dwg2shp import dwg_to_shp

router = APIRouter()
DATA_DIR = "data"
os.makedirs(f"{DATA_DIR}/Files", exist_ok=True)
os.makedirs(f"{DATA_DIR}/Output", exist_ok=True)

@router.get("/shp/download")
async def download_shapefiles(filename: str):
    base_filename = filename.replace(".shp", "")
    shp_filename = f"{base_filename}.shp"
    
    if filename.lower().endswith(('.dxf', '.dwg')):
        original_filename = filename
        base_filename = filename.rsplit('.', 1)[0]
        shp_filename = f"{base_filename}.shp"
    
    matching_shapefiles = []
    for root, _, files in os.walk(f"{DATA_DIR}/Output"):
        for file in files:
            if file.startswith(base_filename) and file.endswith(".shp"):
                matching_shapefiles.append(file)

    if not matching_shapefiles:
        if 'original_filename' not in locals():
            original_filename = base_filename
            possible_extensions = [".dxf", ".dwg"]
            for ext in possible_extensions:
                original_file_path = os.path.join(f"{DATA_DIR}/Files", original_filename + ext)
                if os.path.exists(original_file_path):
                    break
        else:
            original_file_path = os.path.join(f"{DATA_DIR}/Files", original_filename)
            
        if os.path.exists(original_file_path):
            file_extension = original_file_path.lower().split('.')[-1]
            
            if file_extension == "dwg":
                dxf_filename = f"{base_filename}_dwg.dxf"
                dxf_file_path = os.path.join(f"{DATA_DIR}/Output", dxf_filename)
                shp_file_path_dwg = os.path.join(f"{DATA_DIR}/Output", f"{base_filename}_dwg.shp")
                
                from app.features.dwg2dxf import convert_dwg_to_dxf
                dwg_success = convert_dwg_to_dxf(original_file_path, dxf_file_path)
                if not dwg_success:
                    raise HTTPException(status_code=500, detail="Failed to convert DWG to DXF")
                
                dxf2shp(dxf_file_path, shp_file_path_dwg)
            else:
                dxf_filename = f"{base_filename}_dxf.dxf"
                dxf_file_path = os.path.join(f"{DATA_DIR}/Output", dxf_filename)
                shp_file_path_dxf = os.path.join(f"{DATA_DIR}/Output", f"{base_filename}_dxf.shp")
                
                import shutil
                shutil.copy2(original_file_path, dxf_file_path)
                dxf2shp(dxf_file_path, shp_file_path_dxf)
            
            for root, _, files in os.walk(f"{DATA_DIR}/Output"):
                for file in files:
                    if file.startswith(base_filename) and file.endswith(".shp"):
                        matching_shapefiles.append(file)
        
        if not matching_shapefiles:
            raise HTTPException(status_code=404, detail="No matching files found for conversion.")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for shapefile in matching_shapefiles:
            base_name = shapefile.replace(".shp", "")
            for root, _, files in os.walk(f"{DATA_DIR}/Output"):
                for file in files:
                    if file.startswith(base_name) and file.endswith(('.shp', '.shx', '.dbf', '.prj', '.cpg', '.sbn', '.sbx')):
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, file)

    zip_buffer.seek(0)
    return StreamingResponse(
        content=zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={base_filename}.zip"},
    )
