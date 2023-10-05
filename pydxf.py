import os
from osgeo import ogr
import matplotlib.pyplot as plt

dxf_file_path = os.path.join(os.getcwd(), "WO_1901_015", "KHT00219_P1.dxf")
print(f"file path is {dxf_file_path}")

# Open the DXF file
dxf_datasource = ogr.Open(dxf_file_path)
print(dxf_datasource)

# Iterate through layers and plot features
for layer_idx in range(dxf_datasource.GetLayerCount()):
    layer = dxf_datasource.GetLayerByIndex(layer_idx)
    layer_name = layer.GetName()  # Get the name of the layer
    print(f"Layer {layer_idx + 1}: {layer_name}")

    # Iterate through features in the layer
    for feature in layer:
        geometry = feature.GetGeometryRef()
        x = []
        y = []

        if geometry.GetGeometryName() == 'LINESTRING':
            for i in range(geometry.GetPointCount()):
                x.append(geometry.GetX(i))
                y.append(geometry.GetY(i))

            # Plot the line
            plt.plot(x, y, label=f'Layer {layer_idx + 1}')

plt.xlabel('X')
plt.ylabel('Y')
plt.title('DXF File Visualization')
plt.legend()
plt.show()