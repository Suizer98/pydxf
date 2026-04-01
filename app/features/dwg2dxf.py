import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DwgConversionResult:
    success: bool
    duration_seconds: float = 0.0
    engine: str = "qcad"
    returncode: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    error_message: str = ""
    command: List[str] = field(default_factory=list)


def qcad_result(
    success: bool,
    elapsed: float,
    cmd: List[str],
    out: str,
    err: str,
    rc: Optional[int],
    err_msg: str = "",
) -> DwgConversionResult:
    if not success and not err_msg:
        err_msg = (err or out).strip() or (f"exit {rc}" if rc is not None else "")
    return DwgConversionResult(
        success=success,
        duration_seconds=elapsed,
        engine="qcad",
        returncode=rc,
        stdout=out or "",
        stderr=err or "",
        error_message=(err_msg or "")[:4000],
        command=list(cmd),
    )


def dwg_conversion_response_headers(result: Optional[DwgConversionResult]) -> dict:
    if result is None or not result.engine:
        return {}
    h = {
        "X-DWG-Conversion-Seconds": f"{result.duration_seconds:.3f}",
        "X-DWG-Conversion-Engine": result.engine,
        "X-DWG-Conversion-Note": "QCAD trial may add ~15s before work starts.",
        "X-DWG-Process-Return-Code": (
            str(result.returncode) if result.returncode is not None else ""
        ),
    }
    h = {k: v for k, v in h.items() if v}
    if not result.success and result.stderr:
        s = (
            " ".join(result.stderr.split())
            .encode("ascii", errors="replace")
            .decode("ascii")[:200]
        )
        if s:
            h["X-DWG-Stderr-Preview"] = s
    return h


def qcad_subprocess_env():
    env = os.environ.copy()
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    env.setdefault("XDG_RUNTIME_DIR", "/tmp/runtime-root")
    try:
        os.makedirs(env["XDG_RUNTIME_DIR"], mode=0o700, exist_ok=True)
    except OSError:
        pass
    return env


def run_qcad_dwg2dwg(qcad_home: str, dwg_in: str, dxf_out: str) -> DwgConversionResult:
    exe = os.path.join(qcad_home, "dwg2dwg")
    dwg_in, dxf_out = os.path.abspath(dwg_in), os.path.abspath(dxf_out)
    tmp = None
    fd, tmp = tempfile.mkstemp(suffix=".dxf", prefix="pydxf_", dir="/tmp")
    os.close(fd)
    cmd = [exe, "-f", "-o", tmp, dwg_in]
    t0 = time.monotonic()
    try:
        print(f"DWG→DXF: {dwg_in} → {dxf_out} (temp {tmp})")
        print(f"DWG→DXF command: {' '.join(cmd)}")
        p = subprocess.run(
            cmd,
            cwd=qcad_home,
            capture_output=True,
            text=True,
            env=qcad_subprocess_env(),
        )
        elapsed, out, err = time.monotonic() - t0, p.stdout or "", p.stderr or ""
        if out.strip():
            print(f"QCAD stdout: {out.strip()[:500]}")
        if err.strip():
            print(f"QCAD stderr: {err.strip()[:500]}")
        if p.returncode != 0:
            print(f"QCAD dwg2dwg failed ({p.returncode}): {(err or out)[:500]}")
            return qcad_result(False, elapsed, cmd, out, err, p.returncode)

        if not os.path.exists(tmp) or os.path.getsize(tmp) == 0:
            return qcad_result(
                False,
                elapsed,
                cmd,
                out,
                err,
                p.returncode,
                "No DXF output from QCAD.",
            )

        parent = os.path.dirname(dxf_out)
        if parent:
            os.makedirs(parent, exist_ok=True)
        shutil.copy2(tmp, dxf_out)
        ok = os.path.exists(dxf_out) and os.path.getsize(dxf_out) > 0
        if ok:
            print(f"DWG → DXF ok: {dxf_out} ({os.path.getsize(dxf_out)} bytes)")
        return qcad_result(
            ok,
            elapsed,
            cmd,
            out,
            err,
            p.returncode,
            "" if ok else f"Output missing or empty: {dxf_out}",
        )
    except Exception as e:
        print(f"DWG → DXF: {e}")
        return qcad_result(False, time.monotonic() - t0, cmd, "", "", None, str(e))
    finally:
        if tmp:
            try:
                os.unlink(tmp)
            except OSError:
                pass


def convert_dwg_to_dxf(dwg_file_path, dxf_file_path) -> DwgConversionResult:
    home = os.environ.get("QCAD_HOME", "").strip()
    exe = os.path.join(home, "dwg2dwg") if home else ""
    if not home or not os.path.isfile(exe) or not os.access(exe, os.X_OK):
        msg = "Set QCAD_HOME to QCAD install dir (needs dwg2dwg)."
        print(msg)
        return qcad_result(False, 0.0, [exe] if exe else [], "", "", None, msg)
    return run_qcad_dwg2dwg(home, dwg_file_path, dxf_file_path)


def dwg_to_dxf(dwg_file_path, dxf_file_path):
    base, ext = os.path.splitext(dxf_file_path)
    if not base.endswith("_dwg"):
        dxf_file_path = f"{base}_dwg{ext}"
    r = convert_dwg_to_dxf(dwg_file_path, dxf_file_path)
    return {
        "success": r.success,
        "message": (
            "DWG file converted to DXF successfully"
            if r.success
            else (r.error_message or "Failed to convert DWG to DXF")
        ),
        "output_file": dxf_file_path if r.success else None,
        "duration_seconds": r.duration_seconds,
        "engine": r.engine,
        "returncode": r.returncode,
        "stdout": r.stdout,
        "stderr": r.stderr,
    }
