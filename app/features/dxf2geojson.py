import geopandas as gpd


def convert_to_geojson(dxfFile, geojsonFile):
    gdf = gpd.read_file(dxfFile)

    # Save to a single GeoJSON file
    gdf.to_file(geojsonFile, driver="GeoJSON")

    return 0


def dxf2geojson(dxf_file_path=None, geojson_file_path=None):
    dxf_name = dxf_file_path
    target_name = geojson_file_path
    res = convert_to_geojson(dxf_name, target_name)
    if res == 0:
        print(f"{target_name} is created")
    else:
        print("Error occurred! Please check file format.")


# import os
# dxf_file_path = os.path.join(os.getcwd(), "WO_1901_015", "KHT00219_P1.dxf")
# geojson_file_path = os.path.splitext(dxf_file_path)[0] + ".geojson"
# dxf2geojson(dxf_file_path, geojson_file_path)
