import os
import aspose.cad as cad
from aspose.cad.imageoptions import DxfOptions

dwg_file_path = os.path.join(os.getcwd(), "WO_1901_015", "KHT00219_P1.dwg")
dxf_file_path = os.path.splitext(dwg_file_path)[0] + "_aspose.dxf"

try:
    image = cad.Image.load(dwg_file_path)
    dxf_options = DxfOptions()
    image.save(dxf_file_path, dxf_options)
    print(f"Success: {dxf_file_path}")
except Exception as e:
    print(f"Error: {e}")
