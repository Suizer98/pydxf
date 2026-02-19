from os import path
from osgeo import ogr, gdal
import re

LABEL_STYLE_KEYS = {
    "f": "label_font",
    "s": "label_size",
    "t": "label_text",
    "a": "label_angle",
    "c": "label_color",
    "b": "label_bold",
    "it": "label_italic",
    "p": "label_anchor",
    "dx": "label_offset_x",
    "dy": "label_offset_y",
}

ANNOTATION_FIELDS = [
    "label_text",
    "label_font",
    "label_size",
    "label_angle",
    "label_color",
    "label_bold",
    "label_italic",
    "label_anchor",
    "label_offset_x",
    "label_offset_y",
    "ogr_style",
]


def parse_style_string(style_string):
    """Extract label properties from an OGR style string like
    LABEL(f:"Arial",s:2.5g,t:"Hello World",a:45,c:#000000)
    """
    if not style_string:
        return {}

    result = {}
    label_match = re.search(r"LABEL\((.+)\)", style_string)
    if not label_match:
        return {}

    params = label_match.group(1)
    for token in re.finditer(r'(\w+):("(?:[^"\\]|\\.)*"|[^,)]+)', params):
        key = token.group(1)
        value = token.group(2).strip('"')
        # Strip unit suffixes like "g" (ground units) or "pt" (points)
        if key in ("s", "dx", "dy"):
            value = re.sub(r"[a-zA-Z]+$", "", value)
        if key in LABEL_STYLE_KEYS:
            result[LABEL_STYLE_KEYS[key]] = value

    return result


def convert(dxfFile, gpkgFile, layerFilter=".*"):
    gdal.PushErrorHandler("CPLQuietErrorHandler")

    if path.exists(gpkgFile):
        drv = ogr.GetDriverByName("GPKG")
        drv.DeleteDataSource(gpkgFile)

    drv = ogr.GetDriverByName("GPKG")
    ds = ogr.Open(dxfFile)
    if ds is None:
        gdal.PopErrorHandler()
        return -1

    gpkg_ds = drv.CreateDataSource(gpkgFile)
    if gpkg_ds is None:
        gdal.PopErrorHandler()
        return 1

    geometry_features = {}
    field_names = set()
    has_labels = False

    for layer in ds:
        layer_name = layer.GetName()
        p = re.compile(layerFilter)
        if p.search(layer_name) is None:
            continue

        lyr = ds.GetLayerByName(layer_name)
        lyr.ResetReading()
        feat_defn = lyr.GetLayerDefn()

        for i in range(feat_defn.GetFieldCount()):
            field_defn = feat_defn.GetFieldDefn(i)
            field_names.add(field_defn.GetName())

        for feat in lyr:
            geom = feat.GetGeometryRef()
            if geom is None:
                continue

            style_string = feat.GetStyleString()
            label_props = parse_style_string(style_string)
            if label_props:
                has_labels = True

            geom_name = geom.GetGeometryName()
            if geom_name not in geometry_features:
                geometry_features[geom_name] = []
            geometry_features[geom_name].append(
                (feat.Clone(), layer_name, style_string, label_props)
            )

    for geom_type, features in geometry_features.items():
        layer_name = f"{geom_type.lower()}"
        gpkg_layer = gpkg_ds.CreateLayer(layer_name, None, ogr.wkbUnknown)

        gpkg_layer.CreateField(ogr.FieldDefn("source_layer", ogr.OFTString))

        for fn in sorted(field_names):
            gpkg_layer.CreateField(ogr.FieldDefn(fn, ogr.OFTString))

        if has_labels:
            for af in ANNOTATION_FIELDS:
                gpkg_layer.CreateField(ogr.FieldDefn(af, ogr.OFTString))

        for feat, src_layer_name, style_string, label_props in features:
            new_feat = ogr.Feature(gpkg_layer.GetLayerDefn())
            new_feat.SetGeometry(feat.GetGeometryRef())
            new_feat.SetField("source_layer", src_layer_name)

            feat_defn = feat.GetDefnRef()
            for fn in sorted(field_names):
                idx = feat_defn.GetFieldIndex(fn)
                if idx >= 0:
                    new_feat.SetField(fn, feat.GetField(idx))

            if has_labels:
                if style_string:
                    new_feat.SetField("ogr_style", style_string)
                for key, value in label_props.items():
                    new_feat.SetField(key, value)

            gpkg_layer.CreateFeature(new_feat)

    gpkg_ds = None
    gdal.PopErrorHandler()
    return 0


def dxf2gpkg(dxf_file_path=None, gpkg_file_path=None):
    dxf_name = dxf_file_path
    target_name = gpkg_file_path
    dxf_layer_filter = ".*"
    res = convert(dxf_name, target_name, dxf_layer_filter)
    if res == 0:
        gpkgdir, gpkgfile = path.split(target_name)
        print(f"{gpkgdir} {gpkgfile} is created")
    else:
        print("Error occurred! Please check file format.")
