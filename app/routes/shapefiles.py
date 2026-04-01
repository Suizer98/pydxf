import asyncio
import os
import shutil
import tempfile
import zipfile
from typing import Optional, Tuple

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.common import DATA_DIR, ensure_data_dirs
from app.features.dxf2shp import dxf2shp
from app.features.dwg2dxf import convert_dwg_to_dxf, dwg_conversion_response_headers

router = APIRouter()

shpSidecarExts = (".shp", ".shx", ".dbf", ".prj", ".cpg", ".sbn", ".sbx")


def shpZipName(baseFilename: str, sourceKind: str) -> str:
    """Archive name like mymap_dwg_shp.zip (avoids *.shp.zip confusing extractors)."""
    return f"{baseFilename}_{sourceKind}_shp.zip"


def addShapefileSidecarsToZip(
    zipf: zipfile.ZipFile, shpPath: str, seen: set[str]
) -> None:
    """Add one shapefile and its sidecars from the same directory (flat names in the zip)."""
    dirpath = os.path.dirname(shpPath)
    stem = os.path.basename(shpPath).replace(".shp", "")
    for name in os.listdir(dirpath):
        if not name.startswith(stem) or not name.endswith(shpSidecarExts):
            continue
        fp = os.path.join(dirpath, name)
        if not os.path.isfile(fp) or fp in seen:
            continue
        seen.add(fp)
        zipf.write(fp, name)


def listShpPathsInDir(dirpath: str, baseFilename: str) -> list[str]:
    out: list[str] = []
    for f in os.listdir(dirpath):
        if f.startswith(baseFilename) and f.endswith(".shp"):
            out.append(os.path.join(dirpath, f))
    return out


def existingZipForBase(baseFilename: str) -> Optional[Tuple[str, str]]:
    """Return (path, download name) for any cached zip for this base name, or None."""
    for kind in ("dwg", "dxf"):
        zipName = shpZipName(baseFilename, kind)
        zipPath = os.path.join(DATA_DIR, "Output", zipName)
        if os.path.exists(zipPath):
            return (zipPath, zipName)
    return None


@router.get("/shp/download")
async def downloadShapefiles(filename: str):
    ensure_data_dirs()
    dwgStep = None
    baseFilename = filename.replace(".shp", "")

    if filename.lower().endswith((".dxf", ".dwg")):
        originalFilename = filename
        baseFilename = filename.rsplit(".", 1)[0]

    originalFilePath = None
    sourceKind = None

    if "originalFilename" not in locals():
        originalFilename = baseFilename
        possibleExtensions = [".dwg", ".dxf"]
        for ext in possibleExtensions:
            candidate = os.path.join(DATA_DIR, "Files", originalFilename + ext)
            if os.path.exists(candidate):
                originalFilePath = candidate
                sourceKind = "dwg" if ext == ".dwg" else "dxf"
                break
    else:
        originalFilePath = os.path.join(f"{DATA_DIR}/Files", originalFilename)
        if os.path.exists(originalFilePath):
            fe = originalFilePath.lower().split(".")[-1]
            sourceKind = "dwg" if fe == "dwg" else "dxf"

    if sourceKind:
        zipName = shpZipName(baseFilename, sourceKind)
        zipPath = os.path.join(DATA_DIR, "Output", zipName)
        if os.path.exists(zipPath):
            if not originalFilePath or os.path.getmtime(zipPath) >= os.path.getmtime(
                originalFilePath
            ):
                return FileResponse(
                    zipPath,
                    media_type="application/zip",
                    filename=zipName,
                )

    if not originalFilePath or not os.path.exists(originalFilePath):
        orphan = existingZipForBase(baseFilename)
        if orphan:
            zp, zn = orphan
            return FileResponse(
                zp,
                media_type="application/zip",
                filename=zn,
            )
        raise HTTPException(
            status_code=404,
            detail="No uploaded file found for conversion.",
        )

    if sourceKind is None:
        raise HTTPException(
            status_code=500,
            detail="Could not determine whether the source is DWG or DXF.",
        )
    zipName = shpZipName(baseFilename, sourceKind)
    zipPath = os.path.join(DATA_DIR, "Output", zipName)

    tmpdir = tempfile.mkdtemp()
    cachedDwgDxfPath = os.path.join(DATA_DIR, "Output", f"{baseFilename}_dwg.dxf")
    try:
        if sourceKind == "dwg":
            dxfFilePath = os.path.join(tmpdir, f"{baseFilename}_dwg.dxf")
            shpFilePath = os.path.join(tmpdir, f"{baseFilename}_dwg.shp")
            if os.path.exists(cachedDwgDxfPath) and os.path.getmtime(
                cachedDwgDxfPath
            ) >= os.path.getmtime(originalFilePath):
                await asyncio.to_thread(shutil.copy2, cachedDwgDxfPath, dxfFilePath)
                dwgStep = None
            else:
                dwgStep = await asyncio.to_thread(
                    convert_dwg_to_dxf, originalFilePath, dxfFilePath
                )
                if not dwgStep.success:
                    raise HTTPException(
                        status_code=500, detail="Failed to convert DWG to DXF"
                    )
                await asyncio.to_thread(shutil.copy2, dxfFilePath, cachedDwgDxfPath)
            await asyncio.to_thread(dxf2shp, dxfFilePath, shpFilePath)
        else:
            dxfFilePath = os.path.join(tmpdir, f"{baseFilename}_dxf.dxf")
            shpFilePath = os.path.join(tmpdir, f"{baseFilename}_dxf.shp")
            await asyncio.to_thread(shutil.copy2, originalFilePath, dxfFilePath)
            await asyncio.to_thread(dxf2shp, dxfFilePath, shpFilePath)

        matchingShpPaths = listShpPathsInDir(tmpdir, baseFilename)
        if not matchingShpPaths:
            raise HTTPException(
                status_code=500,
                detail="Shapefile conversion produced no output.",
            )

        seenFiles: set[str] = set()
        with zipfile.ZipFile(zipPath, "w", zipfile.ZIP_DEFLATED) as zipf:
            for shpPath in matchingShpPaths:
                addShapefileSidecarsToZip(zipf, shpPath, seenFiles)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    return FileResponse(
        zipPath,
        media_type="application/zip",
        filename=zipName,
        headers=dwg_conversion_response_headers(dwgStep),
    )
