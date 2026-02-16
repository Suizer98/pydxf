import os
import aspose.cad as cad
from aspose.cad.imageoptions import DxfOptions


def convert_dwg_to_dxf(dwg_file, dxf_file):
    try:
        image = cad.Image.load(dwg_file)
        dxf_options = DxfOptions()
        dxf_options.text_as_lines = False
        dxf_options.pretty_formatting = False
        dxf_options.convert_text_beziers = True
        dxf_options.merge_lines_inside_contour = False
        dxf_options.bezier_point_count = 16

        image.save(dxf_file, dxf_options)
        print(f"Success: {dxf_file}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    dwg_file = "path/to/your/file.dwg"
    dxf_file = "path/to/output/file.dxf"
    convert_dwg_to_dxf(dwg_file, dxf_file)
