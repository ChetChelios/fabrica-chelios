"""Reconstruye los recursos binarios del motor (fuentes, GSAP, efectos) en un entorno nuevo.

Solo hace falta si `motor/fonts`, `motor/sfx` o `motor/gsap.min.js` no existen
(por ejemplo, al reconstruir la fábrica desde los documentos del proyecto de Claude).
Requiere haber ejecutado antes: npx hyperframes skills update  y  npx hyperframes --version
"""
import base64
import glob
import re
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path

MOTOR = Path(__file__).resolve().parent / "motor"


def fuentes():
    dst = MOTOR / "fonts"
    dst.mkdir(exist_ok=True)
    want = {"archivo-black:400": "ArchivoBlack-400.woff2", "space-mono:400": "SpaceMono-400.woff2",
            "space-mono:700": "SpaceMono-700.woff2", "outfit:400": "Outfit-400.woff2", "outfit:700": "Outfit-700.woff2"}
    for js in glob.glob(str(Path.home() / ".npm/_npx/*/node_modules/hyperframes/dist/*.js")):
        s = Path(js).read_text(encoding="utf-8", errors="ignore")
        if "EMBEDDED_FONT_DATA" not in s:
            continue
        for k, fn in want.items():
            m = re.search(r'"@fontsource/' + re.escape(k) + r':normal", "data:font/woff2;base64,([A-Za-z0-9+/=]+)"', s)
            if m:
                (dst / fn).write_bytes(base64.b64decode(m.group(1)))
        print("fuentes:", sorted(p.name for p in dst.iterdir()))
        return
    print("No encontré las fuentes: ejecuta primero `npx hyperframes --version`.")


def gsap():
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["npm", "pack", "gsap@3.15.0", "--silent"], cwd=d, check=True)
        with tarfile.open(next(Path(d).glob("gsap-*.tgz"))) as t:
            t.extract("package/dist/gsap.min.js", d)
        shutil.copy(Path(d) / "package/dist/gsap.min.js", MOTOR / "gsap.min.js")
    print("gsap listo")


def sfx():
    dst = MOTOR / "sfx"
    dst.mkdir(exist_ok=True)
    for base in [Path.home() / ".claude/skills/media-use/audio/assets/sfx", Path.home() / ".agents/skills/media-use/audio/assets/sfx"]:
        if base.exists():
            for f in base.iterdir():
                shutil.copy(f, dst / f.name)
            print("efectos:", len(list(dst.iterdir())))
            return
    print("No encontré los efectos: ejecuta `npx hyperframes skills update`.")


if __name__ == "__main__":
    if not (MOTOR / "fonts").exists():
        fuentes()
    if not (MOTOR / "gsap.min.js").exists():
        gsap()
    if not (MOTOR / "sfx").exists():
        sfx()
    print("ok")
