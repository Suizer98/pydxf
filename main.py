from fastapi import FastAPI, File, UploadFile
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


@app.post("/pydxf/upload/")
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
    }


if __name__ == "__main__":
    uvicorn.run(app)
