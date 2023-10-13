import os
from os import path
from osgeo import ogr
import matplotlib.pyplot as plt
import sys
import re

dxf_file_path = os.path.join(os.getcwd(), "WO_1901_015", "KHT00219_P1.dxf")
shp_file_path = os.path.splitext(dxf_file_path)[0] + ".shp"

# Open the DXF file
dxf_datasource = ogr.Open(dxf_file_path)
print(dxf_datasource)


def convert(dxfFile, shpFile, layerFilter=".*"):
    # Check if the output shapefile already exists
    if path.exists(shpFile):
        # If it exists, delete it to replace it
        drv = ogr.GetDriverByName("ESRI Shapefile")
        drv.DeleteDataSource(shpFile)

    # Create the driver before the loop
    drv = ogr.GetDriverByName("ESRI Shapefile")

    # open datasource
    ds = ogr.Open(dxfFile)
    if ds is None:
        return -1

    unique_geometry_types = set()  # To store unique geometry types

    # Find all layers in the DXF file and iterate through them
    for layer in ds:
        layer_name = layer.GetName()  # Get the name of the layer
        p = re.compile(layerFilter)
        if not p.search(layer_name) is None:
            lyr = ds.GetLayerByName(layer_name)
            lyr.ResetReading()
            feat_defn = lyr.GetLayerDefn()
            fid = {}
            # find Layer & EntityHandle column in input
            for i in range(feat_defn.GetFieldCount()):
                field_defn = feat_defn.GetFieldDefn(i)
                if field_defn.GetName() == "Layer":
                    fid["Layer"] = i
                elif field_defn.GetName() == "EntityHandle":
                    fid["EntityHandle"] = i

            # Iterate through features in the layer and collect unique geometry types
            for feat in lyr:
                geom = feat.GetGeometryRef()
                if geom is None:
                    continue
                unique_geometry_types.add(geom.GetGeometryName())

    # Create a separate shapefile for each unique geometry type
    for geom_type in unique_geometry_types:
        shp_layer_file = shpFile.replace(".shp", f"_{geom_type}.shp")
        do = drv.CreateDataSource(shp_layer_file)
        if do is None:
            return 1
        lyro = do.CreateLayer(
            "out", None, ogr.wkbUnknown
        )  # Use ogr.wkbUnknown to accept any geometry type
        if lyro is None:
            return 1
        # add two fields to output LAYER and ENTITYHAND
        field_defn = ogr.FieldDefn("LAYER", ogr.OFTString)
        field_defn.SetWidth(32)
        if lyro.CreateField(field_defn) != 0:
            return 1
        field_defn = ogr.FieldDefn("ENTITYHAND", ogr.OFTString)
        field_defn.SetWidth(8)
        if lyro.CreateField(field_defn) != 0:
            return 1

        # Find the layers containing the current geometry type and copy features to the corresponding shapefile
        for layer in ds:
            layer_name = layer.GetName()
            p = re.compile(layerFilter)
            if not p.search(layer_name) is None:
                lyr = ds.GetLayerByName(layer_name)
                lyr.ResetReading()
                feat_defn = lyr.GetLayerDefn()
                fid = {}
                for i in range(feat_defn.GetFieldCount()):
                    field_defn = feat_defn.GetFieldDefn(i)
                    if field_defn.GetName() == "Layer":
                        fid["Layer"] = i
                    elif field_defn.GetName() == "EntityHandle":
                        fid["EntityHandle"] = i

                for feat in lyr:
                    geom = feat.GetGeometryRef()
                    if geom is None:
                        continue
                    if geom.GetGeometryName() == geom_type:
                        feato = ogr.Feature(lyro.GetLayerDefn())
                        feato.SetGeometry(geom)
                        feato.SetField("LAYER", feat.GetField(fid["Layer"]))
                        feato.SetField("ENTITYHAND", feat.GetField(fid["EntityHandle"]))
                        lyro.CreateFeature(feato)

    ds = None
    dso = None
    return 0


# conversion
def dxf2shp(dxf_file_path=None, shp_file_path=None):
    dxf_name = dxf_file_path
    target_name = shp_file_path
    # enter geometry type ogr.wkbPoint | ogr.wkbLineString | ogr.wkbPolygon
    # shp_type = ogr.wkbLineString
    # enter regexp to filter layers
    dxf_layer_filter = ".*"
    res = convert(dxf_name, target_name, dxf_layer_filter)
    print(res)
    if res == 0:
        # load the shape
        (shpdir, shpfile) = path.split(target_name)
        print(f"{shpdir} {shpfile} is created")


def matplot(dxf_datasource=None):
    # Iterate through layers and plot features
    for layer_idx in range(dxf_datasource.GetLayerCount()):
        layer = dxf_datasource.GetLayerByIndex(layer_idx)
        layer_name = layer.GetName()  # Get the name of the layer
        print(f"Layer {layer_idx + 1}: {layer_name}")

        # Iterate through features in the layer
        for feature in layer:
            geometry = feature.GetGeometryRef()
            x = []
            y = []

            if geometry.GetGeometryName() == "LINESTRING":
                for i in range(geometry.GetPointCount()):
                    x.append(geometry.GetX(i))
                    y.append(geometry.GetY(i))

                # Plot the line
                plt.plot(x, y, label=f"Layer {layer_idx + 1}")

    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("DXF File Visualization")
    plt.legend()
    plt.show()


# matplot(dxf_datasource)
dxf2shp(dxf_file_path, shp_file_path)
