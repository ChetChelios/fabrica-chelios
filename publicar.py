"""El Publicador: sube los videos del día a GitHub y arma lo que se envía a Zernio.

    python publicar.py 3 [--fecha 2026-11-05] [--horas 20:30,21:00,21:30,22:00]

1. Sube los .mp4 y la miniatura a una rama propia del repo (`videos-dia-003`), que da URLs públicas
   en raw.githubusercontent.com. Las ramas de videos de más de 7 días se borran.
   (Desde las sesiones de Claude no se pueden crear releases; las ramas sí.)
2. Escribe salidas/dia-003/zernio.json: una publicación de YouTube (video completo) y una de
   TikTok por parte, con textos, horarios (hora Colombia) y ajustes (etiqueta IA en TikTok).
   --horas cambia los horarios de ese día: la primera es YouTube y las siguientes, las partes de TikTok.
Claude envía cada entrada con el conector de Zernio (posts_create_post).
"""
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
GUARDAR_DIAS = 7


def mmss(t):
    t = int(round(t))
    return f"{t // 60:02d}:{t % 60:02d}"


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


def subir_videos(repo, d, archivos):
    """Crea (o reemplaza) la rama videos-dia-NNN con solo los archivos del día y la sube."""
    rama = f"videos-dia-{d:03d}"
    with tempfile.TemporaryDirectory() as tmp:
        carpeta = Path(tmp) / f"dia-{d:03d}"
        carpeta.mkdir()
        for p in archivos:
            shutil.copy2(p, carpeta / p.name)
        git("init", "-q", "-b", rama, cwd=tmp)
        git("remote", "add", "origin", f"https://github.com/{repo}", cwd=tmp)
        git("add", ".", cwd=tmp)
        git("-c", "user.name=Fábrica de Chelios", "-c", "user.email=fabrica@users.noreply.github.com",
            "commit", "-q", "-m", f"Videos Día {d}", cwd=tmp)
        git("push", "-q", "--force", "origin", rama, cwd=tmp)
        # limpiar ramas de videos viejas
        remotas = git("ls-remote", "--heads", "origin", "videos-dia-*", cwd=tmp)
        for linea in remotas.splitlines():
            nombre = linea.split("refs/heads/")[-1]
            try:
                n = int(nombre.rsplit("-", 1)[-1])
            except ValueError:
                continue
            if n <= d - GUARDAR_DIAS:
                subprocess.run(["git", "push", "-q", "origin", "--delete", nombre], cwd=tmp)
    return lambda nombre: f"https://raw.githubusercontent.com/{repo}/{rama}/dia-{d:03d}/{nombre}"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    valores = {sys.argv[i]: sys.argv[i + 1] for i in range(1, len(sys.argv) - 1) if sys.argv[i].startswith("--")}
    args = [a for a in args if a not in valores.values()]
    d = int(args[0])
    fecha = valores.get("--fecha", date.today().isoformat())
    cfg = json.loads((RAIZ / "config.json").read_text(encoding="utf-8"))
    horarios = cfg["horarios"]
    if "--horas" in valores:
        h = valores["--horas"].split(",")
        horarios = {"youtube": h[0], "tiktok": h[1:] or horarios["tiktok"]}
    guion = json.loads((RAIZ / "episodios" / f"dia-{d:03d}" / "guion.json").read_text(encoding="utf-8"))
    caps = json.loads((RAIZ / "build" / f"dia-{d:03d}" / "capitulos.json").read_text(encoding="utf-8"))
    sal = RAIZ / "salidas" / f"dia-{d:03d}"
    archivos = sorted([p for p in sal.iterdir() if p.suffix in (".mp4", ".png")])
    repo = cfg["repo"]

    # 1) videos públicos en GitHub
    url = subir_videos(repo, d, archivos)

    # 2) cargas para Zernio
    pub = guion.get("publicacion", {})
    tags_txt = " ".join(pub.get("hashtags", []))
    capitulos = "\n".join(f"{mmss(c['inicio'] if i else 0)} {c['titulo']}" for i, c in enumerate(caps["capitulos"]))
    tz = cfg["zona_horaria"]
    yt = cfg["youtube"]
    titulo_yt = pub.get("youtube_titulo", guion["titulo"])[:100]
    datos_yt = {"title": titulo_yt, **yt}
    if pub.get("youtube_primer_comentario"):
        datos_yt["firstComment"] = pub["youtube_primer_comentario"]
    cargas = [{
        "nombre": "YouTube · video completo",
        "args": {
            "title": titulo_yt,
            "content": f"{pub.get('youtube_descripcion', '').strip()}\n\nCapítulos:\n{capitulos}\n\n{tags_txt}",
            "media_items": [{"type": "video", "mimeType": "video/mp4",
                             "url": url(f"dia-{d:03d}-youtube-completo.mp4"),
                             "thumbnail": url(f"dia-{d:03d}-miniatura-youtube.png")}],
            "platforms": [{"platform": "youtube", "accountId": cfg["zernio"]["youtube"],
                           "platformSpecificData": datos_yt}],
            "scheduled_for": f"{fecha}T{horarios['youtube']}:00",
            "timezone": tz,
            "tags": [h.lstrip("#") for h in pub.get("hashtags", [])],
        }}]
    n = len(caps["capitulos"])
    textos_tt = pub.get("tiktok", [])
    for i, c in enumerate(caps["capitulos"]):
        hora = horarios["tiktok"][min(i, len(horarios["tiktok"]) - 1)]
        txt = (textos_tt[i] if i < len(textos_tt) else guion["titulo"])
        cargas.append({
            "nombre": f"TikTok · parte {c['parte']}/{n}",
            "args": {
                "content": f"{txt} (Parte {c['parte']}/{n})\n\n{tags_txt}",
                "media_items": [{"type": "video", "mimeType": "video/mp4",
                                 "url": url(f"dia-{d:03d}-tiktok-parte-{c['parte']}de{n}.mp4")}],
                "platforms": [{"platform": "tiktok", "accountId": cfg["zernio"]["tiktok"]}],
                "tiktok_settings": {"privacyLevel": "PUBLIC_TO_EVERYONE", "allowComment": True, "allowDuet": True,
                                    "allowStitch": True, "contentPreviewConfirmed": True, "expressConsentGiven": True,
                                    "videoMadeWithAi": True},
                "scheduled_for": f"{fecha}T{hora}:00",
                "timezone": tz,
            }})
    (sal / "zernio.json").write_text(json.dumps(cargas, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Videos del día {d} en la rama videos-dia-{d:03d} ({len(archivos)} archivos). "
          f"Cargas para Zernio en {sal / 'zernio.json'}")


if __name__ == "__main__":
    main()
