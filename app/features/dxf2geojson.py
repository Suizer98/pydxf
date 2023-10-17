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
