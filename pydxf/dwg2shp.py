"""
ERROR 6: libopencad 0.3.4 does not support this version of CAD file.
Supported formats are:
DWG R2000 [ACAD1015]
"""

from osgeo import ogr
import os


dwg_file_path = os.path.join(os.getcwd(), "WO_1901_015", "KHT00219_P1.dwg")
print(f"file path is {dwg_file_path}")

# Open the DXF file
dwg_datasource = ogr.Open(dwg_file_path)
print(dwg_datasource)
