import os
from os import path
from osgeo import ogr
import re


def convert(dxfFile, shpFile, layerFilter=".*"):
    if path.exists(shpFile):
        drv = ogr.GetDriverByName("ESRI Shapefile")
        drv.DeleteDataSource(shpFile)

    drv = ogr.GetDriverByName("ESRI Shapefile")
    ds = ogr.Open(dxfFile)
    if ds is None:
        return -1

    unique_geometry_types = set()

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
        shpdir, shpfile = path.split(target_name)
        print(f"{shpdir} {shpfile} is created")


def matplot(dxf_datasource):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 8))
    for layer_idx in range(dxf_datasource.GetLayerCount()):
        layer = dxf_datasource.GetLayerByIndex(layer_idx)
        layer.ResetReading()

        x_coords = []
        y_coords = []

        for feat in layer:
            geom = feat.GetGeometryRef()
            if geom is not None:
                if geom.GetGeometryType() == ogr.wkbPoint:
                    x, y, _ = geom.GetPoint()
                    x_coords.append(x)
                    y_coords.append(y)
                elif geom.GetGeometryType() in [
                    ogr.wkbLineString,
                    ogr.wkbMultiLineString,
                ]:
                    for i in range(geom.GetPointCount()):
                        x, y, _ = geom.GetPoint(i)
                        x_coords.append(x)
                        y_coords.append(y)

        if x_coords and y_coords:
            x = x_coords
            y = y_coords
            plt.plot(x, y, label=f"Layer {layer_idx + 1}")

    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("DXF File Visualization")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    dxf_file = "path/to/your/file.dxf"
    shp_file = "path/to/output/file.shp"
    convert(dxf_file, shp_file)
