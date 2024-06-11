# Pydxf & Pydwg

[[_TOC_]]

## Description
To enable showing of dxf and dwg engineering CAD files on webgis in the future.
This project demostrates a concept to spin up a mini converter api in backend as microservice.

Tech stacks:

![Tech stacks](https://skillicons.dev/icons?i=fastapi,python,docker,ubuntu,bash,autocad)

### How to access features

- Geojson
- Shapefile

1. Go to [http://localhost:8000/pydxf](http://localhost:8000/pydxf) and swagger-ui will be shown.
2. To upload dxf file and convert it, in swagger-ui go to [pydxf/geojson/upload](http://localhost:8000/pydxf/geojson/upload) part
3. After uploading, it will undergo conversion and store in `root/data` folder (or database as you customise it)
4. To download the geojson, go to swagger-ui part of [pydxf/geojson/download](http://localhost:8000/pydxf/geojson/download)

### Local development

You may create your own local environment using command below:

```docker-compose up --build```

### Code formatting

To liaise with py code formatting tool *black* standard, run:

```docker exec pydxf black .```

Check and remove unused modules with *flake8*:

```docker exec pydxf flake8 .```
