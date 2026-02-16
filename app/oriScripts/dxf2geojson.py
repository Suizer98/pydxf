from osgeo import ogr
import os


def convert_dxf_to_geojson(dxf_file, geojson_file):
    try:
        dxf_ds = ogr.Open(dxf_file)
        if dxf_ds is None:
            return False

        geojson_drv = ogr.GetDriverByName("GeoJSON")
        if geojson_drv is None:
            return False

        if os.path.exists(geojson_file):
            geojson_drv.DeleteDataSource(geojson_file)

        geojson_ds = geojson_drv.CreateDataSource(geojson_file)
        if geojson_ds is None:
            return False

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

        print(f"Success: {geojson_file} ({feature_count} features)")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False


def dxf2geojson(dxf_file_path, geojson_file_path):
    convert_dxf_to_geojson(dxf_file_path, geojson_file_path)


if __name__ == "__main__":
    dxf_file = "path/to/your/file.dxf"
    geojson_file = "path/to/output/file.geojson"
    dxf2geojson(dxf_file, geojson_file)
