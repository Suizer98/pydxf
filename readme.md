# Pydxf & Pydwg

[[_TOC_]]

## Description
To enable showing of dxf and dwg engineering CAD files on webgis in the future, I am figuring solutions to allow this happen on the aplha backend first.

Tech stacks:
![Tech stacks](https://skillicons.dev/icons?i=fastapo,python,docker,ubuntu,bash,autocad)

### Local development

You may create your own local environment using command below:

```docker-compose up --build```

### Code formatting

To liaise with py code formatting tool *black* standard, run:

```docker exec pydxf black .```

Check and remove unused modules with *flake8*:

```docker exec pydxf flake8 .```
