"""LA FÁBRICA DE CHELIOS — un comando por episodio.

    python fabrica.py episodios/dia-002/guion.json

Pasos: La Voz (narración + tiempos) → El Animador (proyecto HyperFrames) → render →
El Cortador (partes de TikTok + miniatura) → textos de publicación.
Todo queda en salidas/dia-XXX/.

Opciones:
    --solo-proyecto   arma el proyecto y se detiene (para revisar en el editor: npx hyperframes preview)
    --sin-render      reutiliza un render ya hecho
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "motor"))

import voz  # noqa: E402
import montar  # noqa: E402
import cortador  # noqa: E402


def mmss(t):
    t = int(round(t))
    return f"{t // 60:02d}:{t % 60:02d}"


def preparar_proyecto(pj):
    pj.mkdir(parents=True, exist_ok=True)
    (pj / "hyperframes.json").write_text(json.dumps({
        "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
        "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
        "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
        "media": {"autoProxy": True}, "authoringSkill": "hyperframes"}, indent=2), encoding="utf-8")
    (pj / "meta.json").write_text(json.dumps({"id": pj.name, "name": pj.name}), encoding="utf-8")
    (pj / "package.json").write_text(json.dumps({
        "name": pj.name, "private": True, "type": "module",
        "scripts": {"dev": "npx --yes hyperframes@0.9.11 preview", "check": "npx --yes hyperframes@0.9.11 check",
                    "render": "npx --yes hyperframes@0.9.11 render"}}, indent=2), encoding="utf-8")


def textos(guion, caps, salida, total):
    pub = guion.get("publicacion", {})
    d = guion["dia"]
    n = len(caps)
    capitulos = "\n".join(f"{mmss(c['inicio'] if i else 0)} {c['titulo']}" for i, c in enumerate(caps))
    tags = " ".join(pub.get("hashtags", []))
    lineas = [f"# Publicación · Día {d}", "",
              "## YouTube (video completo)", "",
              f"**Título:** {pub.get('youtube_titulo', guion['titulo'])}", "",
              "**Descripción:**", "", "```", pub.get("youtube_descripcion", "").strip(), "", "Capítulos:", capitulos, "", tags, "```", "",
              f"Duración: {mmss(total)} · Miniatura: `dia-{d:03d}-miniatura-youtube.png`", "",
              "## TikTok (partes)", ""]
    for i, c in enumerate(caps):
        txt = (pub.get("tiktok", []) + [""] * n)[i]
        lineas += [f"### Parte {c['parte']}/{n} · {c['titulo']}", "", "```", f"{txt} (Parte {c['parte']}/{n})".strip(), "", tags, "```", ""]
    (salida / "textos-publicacion.md").write_text("\n".join(lineas), encoding="utf-8")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if not args:
        sys.exit(__doc__)
    guion_path = Path(args[0]).resolve()
    guion = json.loads(guion_path.read_text(encoding="utf-8"))
    d = guion["dia"]
    build = RAIZ / "build" / f"dia-{d:03d}"
    pj = RAIZ / "build" / f"proyecto-dia-{d:03d}"
    salida = RAIZ / "salidas" / f"dia-{d:03d}"
    salida.mkdir(parents=True, exist_ok=True)

    print("1/5  La Voz…")
    t = voz.construir(guion_path, build)
    print(f"     {t['total']:.1f} s de narración")
    print("2/5  El Animador…")
    preparar_proyecto(pj)
    montar.montar(guion_path, build, pj)
    if "--solo-proyecto" in flags:
        print(f"Proyecto listo en {pj}. Revísalo con: cd {pj} && npx hyperframes preview")
        return
    video = salida / f"dia-{d:03d}-youtube-completo.mp4"
    if "--sin-render" not in flags or not video.exists():
        print("3/5  Render (paciencia)…")
        env = dict(os.environ)
        if not env.get("HYPERFRAMES_BROWSER_PATH"):
            for c in ("/usr/bin/google-chrome", "/usr/bin/chromium"):
                if Path(c).exists():
                    env["HYPERFRAMES_BROWSER_PATH"] = c
        crudo = salida / f"_crudo-dia-{d:03d}.mp4"
        workers = str(max(1, min(4, os.cpu_count() or 2)))
        r = subprocess.run(["npx", "--yes", "hyperframes@0.9.11", "render", "-o", str(crudo), "--fps", "30", "--crf", "19",
                            "--workers", workers, "--quiet"], cwd=pj, env=env, shell=(os.name == "nt"))
        if r.returncode != 0:
            sys.exit("El render falló. Prueba: npx hyperframes doctor")
        # volumen estándar para redes (-15 LUFS, pico -1.5 dBTP); el video se copia sin recomprimir
        r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(crudo), "-c:v", "copy", "-af",
                            "loudnorm=I=-15:TP=-1.5:LRA=11,aresample=48000", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                            "-movflags", "+faststart", str(video)])
        if r.returncode != 0:
            sys.exit("Falló la normalización de audio (ffmpeg)")
        crudo.unlink(missing_ok=True)
    print("4/5  El Cortador…")
    cortador.cortar(video, build, salida, d)
    pub = guion.get("publicacion", {})
    cortador.a_png(cortador.html_miniatura(f"{d:03d}", pub.get("miniatura_1", guion["titulo"]), pub.get("miniatura_2", "")),
                   salida / f"dia-{d:03d}-miniatura-youtube.png", 1280, 720)
    print("5/5  Textos de publicación…")
    caps = json.loads((build / "capitulos.json").read_text(encoding="utf-8"))
    textos(guion, caps["capitulos"], salida, caps["total"])
    shutil.rmtree(salida / "_tmp", ignore_errors=True)
    print(f"\nListo: {salida}")
    for f in sorted(salida.iterdir()):
        print("  ·", f.name)


if __name__ == "__main__":
    main()
