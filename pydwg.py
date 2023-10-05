import os
from osgeo import ogr
import matplotlib.pyplot as plt

dwg_file_path = os.path.join(os.getcwd(), "WO_1901_015", "KHT00219_P1.dwg")
print(f"file path is {dwg_file_path}")

# Open the DXF file
dwg_datasource = ogr.Open(dwg_file_path)
print(dwg_datasource)
