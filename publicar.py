"""El Publicador: sube los videos del día a GitHub (release pública) y arma lo que se envía a Zernio.

    python publicar.py 3 [--fecha 2026-11-05]

1. Crea el release `dia-003` en el repo y sube los .mp4 y la miniatura (URLs públicas).
2. Escribe salidas/dia-003/zernio.json: una publicación de YouTube (video completo) y una de
   TikTok por parte, con textos, horarios (hora Colombia) y ajustes (etiqueta IA en TikTok).
Claude envía cada entrada con el conector de Zernio (posts_create_post).
"""
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent


def mmss(t):
    t = int(round(t))
    return f"{t // 60:02d}:{t % 60:02d}"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    d = int(args[0])
    fecha = sys.argv[sys.argv.index("--fecha") + 1] if "--fecha" in sys.argv else date.today().isoformat()
    cfg = json.loads((RAIZ / "config.json").read_text(encoding="utf-8"))
    guion = json.loads((RAIZ / "episodios" / f"dia-{d:03d}" / "guion.json").read_text(encoding="utf-8"))
    caps = json.loads((RAIZ / "build" / f"dia-{d:03d}" / "capitulos.json").read_text(encoding="utf-8"))
    sal = RAIZ / "salidas" / f"dia-{d:03d}"
    archivos = sorted([p for p in sal.iterdir() if p.suffix in (".mp4", ".png")])
    tag = f"dia-{d:03d}"
    repo = cfg["repo"]

    # 1) release en GitHub (si ya existe, se reemplazan los archivos)
    existe = subprocess.run(["gh", "release", "view", tag, "-R", repo], capture_output=True).returncode == 0
    if not existe:
        subprocess.run(["gh", "release", "create", tag, "-R", repo, "-t", guion["titulo"],
                        "-n", f"Videos del {guion['titulo']}"], check=True)
    subprocess.run(["gh", "release", "upload", tag, "-R", repo, "--clobber", *map(str, archivos)], check=True)
    url = lambda nombre: f"https://github.com/{repo}/releases/download/{tag}/{nombre}"

    # 2) cargas para Zernio
    pub = guion.get("publicacion", {})
    tags_txt = " ".join(pub.get("hashtags", []))
    capitulos = "\n".join(f"{mmss(c['inicio'] if i else 0)} {c['titulo']}" for i, c in enumerate(caps["capitulos"]))
    tz = cfg["zona_horaria"]
    yt = cfg["youtube"]
    cargas = [{
        "nombre": "YouTube · video completo",
        "args": {
            "content": f"{pub.get('youtube_descripcion', '').strip()}\n\nCapítulos:\n{capitulos}\n\n{tags_txt}",
            "title": pub.get("youtube_titulo", guion["titulo"])[:100],
            "media_items": [{"type": "video", "url": url(f"dia-{d:03d}-youtube-completo.mp4"),
                             "thumbnail": url(f"dia-{d:03d}-miniatura-youtube.png")}],
            "platforms": [{"platform": "youtube", "accountId": cfg["zernio"]["youtube"],
                           "platformSpecificData": {"title": pub.get("youtube_titulo", guion["titulo"])[:100], **yt}}],
            "scheduled_for": f"{fecha}T{cfg['horarios']['youtube']}:00",
            "timezone": tz,
            "tags": [h.lstrip("#") for h in pub.get("hashtags", [])],
        }}]
    n = len(caps["capitulos"])
    textos_tt = pub.get("tiktok", [])
    for i, c in enumerate(caps["capitulos"]):
        hora = cfg["horarios"]["tiktok"][min(i, len(cfg["horarios"]["tiktok"]) - 1)]
        txt = (textos_tt[i] if i < len(textos_tt) else guion["titulo"])
        cargas.append({
            "nombre": f"TikTok · parte {c['parte']}/{n}",
            "args": {
                "content": f"{txt} (Parte {c['parte']}/{n})\n\n{tags_txt}",
                "media_items": [{"type": "video", "url": url(f"dia-{d:03d}-tiktok-parte-{c['parte']}de{n}.mp4")}],
                "platforms": [{"platform": "tiktok", "accountId": cfg["zernio"]["tiktok"]}],
                "tiktok_settings": {"privacyLevel": "PUBLIC_TO_EVERYONE", "allowComment": True, "allowDuet": True,
                                    "allowStitch": True, "contentPreviewConfirmed": True, "expressConsentGiven": True,
                                    "videoMadeWithAi": True},
                "scheduled_for": f"{fecha}T{hora}:00",
                "timezone": tz,
            }})
    (sal / "zernio.json").write_text(json.dumps(cargas, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Release {tag} listo con {len(archivos)} archivos. Cargas para Zernio en {sal / 'zernio.json'}")


if __name__ == "__main__":
    main()
