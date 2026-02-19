import os
from .dwg2dxf import convert_dwg_to_dxf
from .dxf2gpkg import dxf2gpkg


def dwg_to_gpkg(dwg_file_path, gpkg_file_path):
    try:
        dxf_file_path = os.path.splitext(gpkg_file_path)[0] + "_dwg.dxf"

        dwg_success = convert_dwg_to_dxf(dwg_file_path, dxf_file_path)
        if not dwg_success:
            return {
                "success": False,
                "message": "Failed to convert DWG to DXF",
                "output_file": None,
            }

        dxf2gpkg(dxf_file_path, gpkg_file_path)

        return {
            "success": True,
            "message": "DWG file converted to GeoPackage successfully",
            "output_file": gpkg_file_path,
            "intermediate_dxf": dxf_file_path,
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error during DWG to GeoPackage conversion: {str(e)}",
            "output_file": None,
        }
