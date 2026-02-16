from osgeo import ogr
import os


def convert_to_geojson(dxfFile, geojsonFile):
    try:
        dxf_ds = ogr.Open(dxfFile)
        if dxf_ds is None:
            return -1

        geojson_drv = ogr.GetDriverByName("GeoJSON")
        if geojson_drv is None:
            return -1

        if os.path.exists(geojsonFile):
            geojson_drv.DeleteDataSource(geojsonFile)

        geojson_ds = geojson_drv.CreateDataSource(geojsonFile)
        if geojson_ds is None:
            return -1

        layer = geojson_ds.CreateLayer("features", None, ogr.wkbUnknown)

        feature_count = 0
        for dxf_layer in dxf_ds:
            dxf_layer.ResetReading()
            for feat in dxf_layer:
                geom = feat.GetGeometryRef()
                if geom is None:
                    continue

                new_feat = ogr.Feature(layer.GetLayerDefn())
                new_feat.SetGeometry(geom)
                layer.CreateFeature(new_feat)
                feature_count += 1

        print(f"Success: {geojsonFile} ({feature_count} features)")
        return 0

    except Exception as e:
        print(f"Error: {e}")
        return -1


def dxf2geojson(dxf_file_path=None, geojson_file_path=None):
    dxf_name = dxf_file_path
    target_name = geojson_file_path
    res = convert_to_geojson(dxf_name, target_name)
    if res == 0:
        print(f"{target_name} is created")
    else:
        print("Error occurred! Please check file format.")
