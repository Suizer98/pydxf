import os
import subprocess


def convert_dwg_to_dxf(dwg_file_path, dxf_file_path):
    try:
        result = subprocess.run(
            ["dwg2dxf", "-o", dxf_file_path, dwg_file_path],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            print(f"dwg2dxf stderr: {result.stderr}")
            return False

        return os.path.exists(dxf_file_path)
    except FileNotFoundError:
        print("Error: dwg2dxf command not found. Is LibreDWG installed?")
        return False
    except subprocess.TimeoutExpired:
        print("Error: DWG to DXF conversion timed out")
        return False
    except Exception as e:
        print(f"Error converting DWG to DXF: {e}")
        return False


def dwg_to_dxf(dwg_file_path, dxf_file_path):
    base, ext = os.path.splitext(dxf_file_path)
    if not base.endswith("_dwg"):
        dxf_file_path = f"{base}_dwg{ext}"

    success = convert_dwg_to_dxf(dwg_file_path, dxf_file_path)

    if success:
        return {
            "success": True,
            "message": "DWG file converted to DXF successfully",
            "output_file": dxf_file_path,
        }
    else:
        return {
            "success": False,
            "message": "Failed to convert DWG to DXF",
            "output_file": None,
        }
