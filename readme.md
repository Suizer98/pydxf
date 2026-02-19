# Pydxf & Pydwg

[[_TOC_]]

## Description
Convert DXF and DWG engineering CAD files to GeoJSON, Shapefile, and GeoPackage formats for web GIS applications.
This project provides a microservice API for on-demand conversion of CAD files.

Tech stacks:

![Tech stacks](https://skillicons.dev/icons?i=fastapi,python,docker,ubuntu,bash,autocad)

### Features

- DWG Support: Convert DWG files using LibreDWG
- DXF Support: Convert DXF files using OGR
- Output Formats: GeoJSON, Shapefile, and GeoPackage
- Annotation Support: GeoPackage output preserves text/label attributes from DXF annotations

### API Endpoints

1. Upload: `POST /pydxf/upload` - Upload DXF or DWG files
2. List Files: `GET /pydxf/files` - List uploaded files with download links
3. Download GeoJSON: `GET /pydxf/geojson/download?filename=file.dxf` - Download as GeoJSON
4. Download Shapefile: `GET /pydxf/shp/download?filename=file.dwg` - Download as Shapefile (ZIP)
5. Download GeoPackage: `GET /pydxf/gpkg/download?filename=file.dxf` - Download as GeoPackage

### How to use

1. Go to [http://localhost:8000/docs](http://localhost:8000/docs) for Swagger UI, or go to [http://localhost:8000/scalar/](http://localhost:8000/scalar/) for Scalar API documentation
2. Upload DXF or DWG files using the upload endpoint
3. Download converted files using the download endpoints
4. Files are stored in `data/Files/` and converted outputs in `data/Output/`

### Local development

Start the service:
```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000/pydxf`

### Dependencies

- LibreDWG: For DWG to DXF conversion
- GDAL/OGR: For DXF processing and GeoJSON/Shapefile/GeoPackage output
- FastAPI: Web framework
- Docker: Containerization

### Code formatting

Format code with *black*:
```bash
docker exec pydxf black .
```

Check code quality with *flake8*:
```bash
docker exec pydxf flake8 .
```
