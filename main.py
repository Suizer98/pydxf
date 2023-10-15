from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from starlette.responses import RedirectResponse
import uvicorn

import os
from app.features.dxf2geojson import dxf2geojson

app = FastAPI()

# Define the directory to store uploaded DXF files
DATA_DIR = "data"
os.makedirs(f"{DATA_DIR}/Files", exist_ok=True)
os.makedirs(f"{DATA_DIR}/Output", exist_ok=True)


@app.get("/")
def read_root():
    # Redirect to the /docs/ endpoint
    return RedirectResponse(url="/docs/")


@app.get("/pydxf/")
def read_root():
    return {"This is an alpha backend code for converting dxf"}


@app.post("/pydxf/geojson/upload/")
async def upload_dxf_file(file: UploadFile):
    # Check if the file has a valid DXF extension
    if not file.filename.lower().endswith(".dxf"):
        return {"error": "Only DXF files are allowed."}

    # Create a unique filename for the uploaded file (you can use a more robust method)
    file_path = os.path.join(f"{DATA_DIR}/Files", file.filename)

    # Write the file to the 'data' directory
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


@app.get("/pydxf/geojson/download/")
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


if __name__ == "__main__":
    uvicorn.run(app)
# uvicorn main:app --reload
