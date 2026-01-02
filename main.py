from fastapi import FastAPI
from starlette.responses import RedirectResponse
from scalar_fastapi import get_scalar_api_reference

import uvicorn

from app.routes.geojson import router as geojson_router
from app.routes.shapefiles import router as shp_router
from app.routes.upload import router as upload_router

app = FastAPI()


@app.get("/")
def root_route():
    return RedirectResponse(url="/scalar/")


@app.get("/scalar/", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="PyDXF API Documentation",
        # Don't use proxy for local development - allows direct file uploads
        scalar_proxy_url="",
    )


@app.get("/pydxf/")
def main_route():
    return {"This is an alpha backend code for converting DXF"}


# Include the router under the '/pydxf' path
app.include_router(geojson_router, prefix="/pydxf")
app.include_router(shp_router, prefix="/pydxf")
app.include_router(upload_router, prefix="/pydxf")

if __name__ == "__main__":
    # uvicorn main:app --reload
    uvicorn.run(app)
