"""CHELIOS NOTICIAS — videos cortos de tendencias (sin el socio), un solo video vertical para TikTok y YouTube Shorts.

    python noticias.py noticias/gta6-001/guion.json                # voz + proyecto + render
    python noticias.py noticias/gta6-001/guion.json --solo-proyecto
    python noticias.py noticias/gta6-001/guion.json --publicar --fecha 2026-11-13 [--hora 18:00]

El guion es como el de la serie, pero con "serie": "noticias", "slug" (p. ej. "gta6-001"),
"hud_marca" / "hud_chip" (el letrero de arriba) y todas las escenas en la parte 1.
Con "formato": "lista" usa el formato editorial de motor/editorial.py (fondo claro, lista numerada y una
tarjeta por dato, cada una en un estilo visual distinto). Conviene alternar formatos para no aburrir.
Reglas: cada número en pantalla lleva su fuente en "fuentes" (va a la descripción); nada de imágenes,
logos ni personajes de otras marcas: solo las gráficas de la fábrica.

--publicar sube el video a la rama videos-<slug> y escribe salidas/<slug>/zernio.json
(1 YouTube Short + 1 TikTok, a la hora de config.json → noticias.hora, o --hora).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "motor"))

import voz  # noqa: E402
import montar  # noqa: E402
import editorial  # noqa: E402
from fabrica import preparar_proyecto  # noqa: E402


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


def producir(guion_path, solo_proyecto=False):
    guion = json.loads(guion_path.read_text(encoding="utf-8"))
    slug = guion["slug"]
    build, pj, salida = RAIZ / "build" / slug, RAIZ / "build" / f"proyecto-{slug}", RAIZ / "salidas" / slug
    salida.mkdir(parents=True, exist_ok=True)
    lista = guion.get("formato") == "lista"
    print("1/3  La Voz…")
    if lista:  # formato lista editorial: la voz lee intro + items + cierre
        build.mkdir(parents=True, exist_ok=True)
        gv = build / "guion-voz.json"
        gv.write_text(json.dumps(editorial.esc_voz(guion), ensure_ascii=False), encoding="utf-8")
        t = voz.construir(gv, build)
    else:
        t = voz.construir(guion_path, build)
    print(f"     {t['total']:.1f} s de narración")
    print("2/3  El Animador…")
    if pj.exists():
        shutil.rmtree(pj)
    preparar_proyecto(pj)
    if lista:
        editorial.montar(guion_path, build, pj)
    else:
        montar.montar(guion_path, build, pj)
    if solo_proyecto:
        print(f"Proyecto listo en {pj}")
        return
    print("3/3  Render…")
    env = dict(os.environ)
    if not env.get("HYPERFRAMES_BROWSER_PATH"):
        for c in ("/usr/bin/google-chrome", "/usr/bin/chromium"):
            if Path(c).exists():
                env["HYPERFRAMES_BROWSER_PATH"] = c
    crudo, video = salida / f"_crudo-{slug}.mp4", salida / f"{slug}.mp4"
    workers = str(max(1, min(4, os.cpu_count() or 2)))
    r = subprocess.run(["npx", "--yes", "hyperframes@0.9.11", "render", "-o", str(crudo), "--fps", "30", "--crf", "19",
                        "--workers", workers, "--quiet"], cwd=pj, env=env)
    if r.returncode != 0:
        sys.exit("El render falló.")
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(crudo), "-c:v", "copy", "-af",
                        "loudnorm=I=-15:TP=-1.5:LRA=11,aresample=48000", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                        "-movflags", "+faststart", str(video)])
    if r.returncode != 0:
        sys.exit("Falló la normalización de audio (ffmpeg)")
    crudo.unlink(missing_ok=True)
    print(f"Listo: {video}")


def publicar(guion_path, fecha, hora=None):
    guion = json.loads(guion_path.read_text(encoding="utf-8"))
    cfg = json.loads((RAIZ / "config.json").read_text(encoding="utf-8"))
    slug, repo = guion["slug"], cfg["repo"]
    hora = hora or cfg.get("noticias", {}).get("hora", "18:00")
    salida = RAIZ / "salidas" / slug
    video = salida / f"{slug}.mp4"
    rama = f"videos-{slug}"
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / slug).mkdir()
        shutil.copy2(video, Path(tmp) / slug / video.name)
        git("init", "-q", "-b", rama, cwd=tmp)
        git("remote", "add", "origin", f"https://github.com/{repo}", cwd=tmp)
        git("add", ".", cwd=tmp)
        git("-c", "user.name=Fábrica de Chelios", "-c", "user.email=fabrica@users.noreply.github.com",
            "commit", "-q", "-m", f"Video {slug}", cwd=tmp)
        git("push", "-q", "--force", "origin", rama, cwd=tmp)
    url = f"https://raw.githubusercontent.com/{repo}/{rama}/{slug}/{video.name}"
    pub = guion["publicacion"]
    tags_txt = " ".join(pub.get("hashtags", []))
    fuentes = "\n".join(f"· {f}" for f in guion.get("fuentes", []))
    titulo = pub["youtube_titulo"][:100]
    tz = cfg["zona_horaria"]
    datos_yt = {"title": titulo, **cfg["youtube"]}
    if pub.get("youtube_primer_comentario"):
        datos_yt["firstComment"] = pub["youtube_primer_comentario"]
    cargas = [
        {"nombre": "YouTube · Short", "args": {
            "title": titulo,
            "content": f"{pub['youtube_descripcion'].strip()}\n\nFuentes:\n{fuentes}\n\n{tags_txt}",
            "media_items": [{"type": "video", "mimeType": "video/mp4", "url": url}],
            "platforms": [{"platform": "youtube", "accountId": cfg["zernio"]["youtube"], "platformSpecificData": datos_yt}],
            "scheduled_for": f"{fecha}T{hora}:00", "timezone": tz,
            "tags": [h.lstrip("#") for h in pub.get("hashtags", [])]}},
        {"nombre": "TikTok", "args": {
            "content": f"{pub['tiktok']}\n\n{tags_txt}",
            "media_items": [{"type": "video", "mimeType": "video/mp4", "url": url}],
            "platforms": [{"platform": "tiktok", "accountId": cfg["zernio"]["tiktok"]}],
            "tiktok_settings": {"privacyLevel": "PUBLIC_TO_EVERYONE", "allowComment": True, "allowDuet": True,
                                "allowStitch": True, "contentPreviewConfirmed": True, "expressConsentGiven": True,
                                "videoMadeWithAi": True},
            "scheduled_for": f"{fecha}T{hora}:00", "timezone": tz}},
    ]
    (salida / "zernio.json").write_text(json.dumps(cargas, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Video en {url}\nCargas para Zernio en {salida / 'zernio.json'}")


def main():
    argv = sys.argv[1:]
    if not argv or argv[0].startswith("--"):
        sys.exit(__doc__)
    val = lambda k, d=None: argv[argv.index(k) + 1] if k in argv else d
    gp = Path(argv[0]).resolve()
    if "--publicar" in argv:
        publicar(gp, val("--fecha", date.today().isoformat()), val("--hora"))
    else:
        producir(gp, "--solo-proyecto" in argv)


if __name__ == "__main__":
    main()
