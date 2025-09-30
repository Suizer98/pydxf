import os
import aspose.cad as cad
from aspose.cad.imageoptions import DxfOptions
import sys
sys.path.append('/app')
from app.oriScripts.dxf2shp import convert as dxf2shp

def dwg_to_shp(dwg_file_path, shp_file_path):
    try:
        dxf_file_path = os.path.splitext(dwg_file_path)[0] + "_converted.dxf"
        
        image = cad.Image.load(dwg_file_path)
        dxf_options = DxfOptions()
        dxf_options.text_as_lines = False
        dxf_options.pretty_formatting = False
        dxf_options.convert_text_beziers = True
        dxf_options.merge_lines_inside_contour = False
        dxf_options.bezier_point_count = 16
        
        image.save(dxf_file_path, dxf_options)
        
        result = dxf2shp(dxf_file_path, shp_file_path)
        
        if result == 0:
            print(f"Success: {shp_file_path}")
            return True
        else:
            print("Conversion failed")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    dwg_file_path = "path/to/your/file.dwg"
    shp_file_path = "path/to/output/file.shp"
    dwg_to_shp(dwg_file_path, shp_file_path)
