import os
from .dwg2dxf import convert_dwg_to_dxf
from .dxf2shp import dxf2shp

def dwg_to_shp(dwg_file_path, shp_file_path):
    try:
        dxf_file_path = os.path.splitext(shp_file_path)[0] + "_dwg.dxf"
        
        dwg_success = convert_dwg_to_dxf(dwg_file_path, dxf_file_path)
        if not dwg_success:
            return {
                "success": False,
                "message": "Failed to convert DWG to DXF",
                "output_file": None
            }

        dxf2shp(dxf_file_path, shp_file_path)
        
        return {
            "success": True,
            "message": "DWG file converted to Shapefile successfully",
            "output_file": shp_file_path,
            "intermediate_dxf": dxf_file_path
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error during DWG to Shapefile conversion: {str(e)}",
            "output_file": None
        }
