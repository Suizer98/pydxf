import os
import aspose.cad as cad
from aspose.cad.imageoptions import DxfOptions

def convert_dwg_to_dxf(dwg_file_path, dxf_file_path):
    try:
        image = cad.Image.load(dwg_file_path)
        dxf_options = DxfOptions()
        dxf_options.text_as_lines = False
        dxf_options.pretty_formatting = False
        dxf_options.convert_text_beziers = True
        dxf_options.merge_lines_inside_contour = False
        dxf_options.bezier_point_count = 16
        
        image.save(dxf_file_path, dxf_options)
        return True
    except Exception as e:
        print(f"Error converting DWG to DXF: {e}")
        return False

def dwg_to_dxf(dwg_file_path, dxf_file_path):
    success = convert_dwg_to_dxf(dwg_file_path, dxf_file_path)
    
    if success:
        return {
            "success": True,
            "message": "DWG file converted to DXF successfully",
            "output_file": dxf_file_path
        }
    else:
        return {
            "success": False,
            "message": "Failed to convert DWG to DXF",
            "output_file": None
        }
