from os import path
from osgeo import ogr, gdal
import re


def convert(dxfFile, shpFile, layerFilter=".*"):
    gdal.PushErrorHandler("CPLQuietErrorHandler")

    if path.exists(shpFile):
        drv = ogr.GetDriverByName("ESRI Shapefile")
        drv.DeleteDataSource(shpFile)

    drv = ogr.GetDriverByName("ESRI Shapefile")
    ds = ogr.Open(dxfFile)
    if ds is None:
        gdal.PopErrorHandler()
        return -1

    unique_geometry_types = set()
    field_names = set()

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

            for feat in lyr:
                geom = feat.GetGeometryRef()
                if geom is None:
                    continue
                unique_geometry_types.add(geom.GetGeometryName())

    for geom_type in unique_geometry_types:
        shp_layer_file = shpFile.replace(".shp", f"_{geom_type}.shp")
        do = drv.CreateDataSource(shp_layer_file)
        if do is None:
            gdal.PopErrorHandler()
            return 1
        lyro = do.CreateLayer("out", None, ogr.wkbUnknown)

        for field_name in field_names:
            field_defn = ogr.FieldDefn(field_name, ogr.OFTString)
            lyro.CreateField(field_defn)

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

                        feat_defn = feat.GetDefnRef()
                        for field_name in field_names:
                            idx = feat_defn.GetFieldIndex(field_name)
                            if idx >= 0:
                                feato.SetField(field_name, feat.GetField(idx))

                        lyro.CreateFeature(feato)

    gdal.PopErrorHandler()
    return 0


def dxf2shp(dxf_file_path=None, shp_file_path=None):
    dxf_name = dxf_file_path
    target_name = shp_file_path
    dxf_layer_filter = ".*"
    res = convert(dxf_name, target_name, dxf_layer_filter)
    if res == 0:
        shpdir, shpfile = path.split(target_name)
        print(f"{shpdir} {shpfile} is created")
    else:
        print("Error occurred! Please check file format.")
