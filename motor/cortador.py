"""El Cortador: video completo → partes para TikTok (+ portadas y miniatura de YouTube).

Uso: python motor/cortador.py <video_completo.mp4> <build_dir> <salida_dir> <dia>
Lee build_dir/capitulos.json (lo escribe montar.py).
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from personajes import CORAL, CYAN, GROUND, INK, MUTED, SUN, chelios

AQUI = Path(__file__).resolve().parent
FONTS = AQUI / "fonts"
SFX = AQUI / "sfx"
FIN_SEG = 1.5  # duración de la tarjeta "sigue en la parte X"


def css_fuentes():
    f = lambda n: (FONTS / n).as_uri()
    return f"""
@font-face {{ font-family: 'Archivo Black'; src: url('{f("ArchivoBlack-400.woff2")}'); }}
@font-face {{ font-family: 'Space Mono'; font-weight: 400; src: url('{f("SpaceMono-400.woff2")}'); }}
@font-face {{ font-family: 'Space Mono'; font-weight: 700; src: url('{f("SpaceMono-700.woff2")}'); }}
@font-face {{ font-family: 'Outfit'; font-weight: 700; src: url('{f("Outfit-700.woff2")}'); }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
.disp {{ font-family: 'Archivo Black'; text-transform: uppercase; line-height: .95; }}
.mono {{ font-family: 'Space Mono'; font-weight: 700; }}
"""


def fondo():
    return f'''<div style="position:absolute;inset:0;background:{GROUND}"></div>
<div style="position:absolute;left:-300px;top:-200px;width:1500px;height:1500px;background:radial-gradient(circle, rgba(98,64,255,.35) 0%, rgba(98,64,255,0) 62%)"></div>
<div style="position:absolute;inset:0;background-image:radial-gradient(rgba(142,137,191,.2) 2px, transparent 2.6px);background-size:54px 54px"></div>'''


def html_insignia(i, n, titulo):
    return f'''<html><head><style>{css_fuentes()} body {{ width:1080px;height:1920px;background:transparent; }}</style></head><body>
<div style="position:absolute;left:46px;top:170px;display:inline-block;min-width:520px;background:{GROUND};border:3px solid {SUN};border-radius:999px;padding:10px 26px;white-space:nowrap" class="mono">
<span style="color:{GROUND};background:{SUN};border-radius:999px;padding:2px 14px;font-size:28px">PARTE {i}/{n}</span>
<span style="color:{INK};font-size:28px;letter-spacing:.06em;margin-left:12px">{titulo.upper()}</span></div></body></html>'''


def html_final(i_sig, n, titulo):
    return f'''<html><head><style>{css_fuentes()} body {{ width:1080px;height:1920px;position:relative;overflow:hidden; }}</style></head><body>
{fondo()}
<div style="position:absolute;left:0;width:1080px;top:330px;text-align:center;font-size:40px;color:{MUTED};letter-spacing:.3em" class="mono">CONTINÚA EN LA</div>
<div style="position:absolute;left:0;width:1080px;top:400px;text-align:center;font-size:205px;color:{SUN}" class="disp">PARTE {i_sig}</div>
<div style="position:absolute;left:0;width:1080px;top:640px;text-align:center;font-size:54px;color:{INK}" class="disp">{titulo}</div>
<div style="position:absolute;left:290px;top:740px">{chelios("c", 500)}</div>
<div style="position:absolute;left:0;width:1080px;top:1210px;text-align:center"><span class="mono" style="display:inline-block;background:{SUN};color:{GROUND};font-size:44px;padding:16px 40px;border-radius:999px">EN MI PERFIL →</span></div>
</body></html>'''


def html_miniatura(dia, linea1, linea2):
    return f'''<html><head><style>{css_fuentes()} body {{ width:1280px;height:720px;position:relative;overflow:hidden;background:{GROUND} }}</style></head><body>
<div style="position:absolute;left:-200px;top:-300px;width:1300px;height:1300px;background:radial-gradient(circle, rgba(98,64,255,.45) 0%, rgba(98,64,255,0) 62%)"></div>
<div style="position:absolute;right:-120px;top:-60px;width:900px;height:900px;background:radial-gradient(circle, rgba(255,201,60,.35) 0%, rgba(255,201,60,0) 60%)"></div>
<div style="position:absolute;inset:0;background-image:radial-gradient(rgba(142,137,191,.2) 2px, transparent 2.6px);background-size:48px 48px"></div>
<div style="position:absolute;left:60px;top:60px"><span class="mono" style="display:inline-block;background:{SUN};color:{GROUND};font-size:40px;padding:8px 26px;border-radius:999px">DÍA {dia}</span></div>
<div class="disp" style="position:absolute;left:60px;top:170px;width:760px;font-size:104px;color:{INK};line-height:.98">{linea1}</div>
<div class="disp" style="position:absolute;left:60px;top:500px;width:760px;font-size:62px;color:{SUN}">{linea2}</div>
<div style="position:absolute;left:770px;top:80px">{chelios("c", 520)}</div>
</body></html>'''


def a_png(html, salida, w=1080, h=1920, transparente=False):
    from playwright.sync_api import sync_playwright
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tf:
        tf.write(html)
        ruta = tf.name
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.goto(Path(ruta).as_uri())
        pg.wait_for_timeout(250)
        pg.evaluate("document.fonts.ready")
        pg.screenshot(path=str(salida), omit_background=transparente)
        b.close()


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2500:])
        sys.exit(f"ffmpeg falló: {' '.join(cmd[:6])}…")


def cortar(video, build_dir, salida, dia):
    caps = json.loads((Path(build_dir) / "capitulos.json").read_text(encoding="utf-8"))["capitulos"]
    salida = Path(salida)
    tmp = salida / "_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    n = len(caps)
    hechos = []
    for k, c in enumerate(caps):
        i = c["parte"]
        ins = tmp / f"insignia_{i}.png"
        a_png(html_insignia(i, n, c["titulo"]), ins, transparente=True)
        out = salida / f"dia-{dia:03d}-tiktok-parte-{i}de{n}.mp4"
        cmd = ["ffmpeg", "-y", "-ss", f"{c['inicio']:.3f}", "-to", f"{c['fin']:.3f}", "-i", str(video), "-i", str(ins)]
        enc = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "-r", "30",
               "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart"]
        if k + 1 < n:
            fin = tmp / f"final_{i}.png"
            sig = caps[k + 1]
            a_png(html_final(sig["parte"], n, sig["titulo"]), fin)
            cmd += ["-loop", "1", "-framerate", "30", "-t", str(FIN_SEG), "-i", str(fin),
                    "-i", str(SFX / "whoosh-short.mp3"),
                    "-f", "lavfi", "-t", str(FIN_SEG), "-i", "anullsrc=r=48000:cl=stereo"]
            fc = ("[0:v][1:v]overlay=0:0,setsar=1,fps=30,format=yuv420p[v0];"
                  "[2:v]fade=t=in:st=0:d=0.15,setsar=1,fps=30,format=yuv420p[v1];"
                  "[0:a]aresample=48000,aformat=channel_layouts=stereo[a0];"
                  "[3:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.45[w];"
                  "[4:a][w]amix=inputs=2:duration=first:normalize=0[a1];"
                  "[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]")
        else:
            fc = ("[0:v][1:v]overlay=0:0,setsar=1,fps=30,format=yuv420p[v];"
                  "[0:a]aresample=48000,aformat=channel_layouts=stereo[a]")
        cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[a]"] + enc + [str(out)]
        run(cmd)
        hechos.append(out)
        print("listo", out.name)
    return hechos


if __name__ == "__main__":
    video, build_dir, salida, dia = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    cortar(video, build_dir, salida, dia)
