from os import path
from osgeo import ogr
import re


def convert(dxfFile, shpFile, layerFilter=".*"):
    # Check if the output shapefile already exists
    if path.exists(shpFile):
        # If it exists, delete it to replace it
        drv = ogr.GetDriverByName("ESRI Shapefile")
        drv.DeleteDataSource(shpFile)

    # Create the driver before the loop
    drv = ogr.GetDriverByName("ESRI Shapefile")

    # Open the DXF data source
    ds = ogr.Open(dxfFile)
    if ds is None:
        return -1

    unique_geometry_types = set()  # To store unique geometry types

    # Iterate through features in the layer and collect unique geometry types and field names
    field_names = set()  # To store unique field names

    for layer in ds:
        layer_name = layer.GetName()
        p = re.compile(layerFilter)
        if not p.search(layer_name) is None:
            lyr = ds.GetLayerByName(layer_name)
            lyr.ResetReading()
            feat_defn = lyr.GetLayerDefn()

            for i in range(feat_defn.GetFieldCount()):
                field_defn = feat_defn.GetFieldDefn(i)
                field_names.add(field_defn.GetName())

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
        lyro = do.CreateLayer("out", None, ogr.wkbUnknown)

        # Create fields in the output shapefile for all field names found in the DXF file
        for field_name in field_names:
            field_defn = ogr.FieldDefn(field_name, ogr.OFTString)
            lyro.CreateField(field_defn)

        # Find the layers containing the current geometry type and copy features to the corresponding shapefile
        for layer in ds:
            layer_name = layer.GetName()
            p = re.compile(layerFilter)
            if not p.search(layer_name) is None:
                lyr = ds.GetLayerByName(layer_name)
                lyr.ResetReading()
                for feat in lyr:
                    geom = feat.GetGeometryRef()
                    if geom is None:
                        continue
                    if geom.GetGeometryName() == geom_type:
                        feato = ogr.Feature(lyro.GetLayerDefn())
                        feato.SetGeometry(geom)

                        # Copy all fields from the DXF feature to the output shapefile feature
                        for field_name in field_names:
                            feato.SetField(field_name, feat.GetField(field_name))

                        lyro.CreateFeature(feato)

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
    if res == 0:
        # load the shape
        (shpdir, shpfile) = path.split(target_name)
        print(f"{shpdir} {shpfile} is created")
    else:
        print("Error occurred! Please check file format.")
