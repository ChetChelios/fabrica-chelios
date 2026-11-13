"""Formato «lista editorial» de Chelios Noticias: fondo claro, título con acento en serif cursiva,
lista numerada a la izquierda y una tarjeta por dato, cada una en un ESTILO VISUAL distinto
(papel recortado, cómic, pixel art, neón, synthwave, plano). Cierra con la cuadrícula de todas las
tarjetas y «comenta PALABRA».

Guion (noticias/<slug>/guion.json):
  "formato": "lista", "slug", "voz", "marca", "chip",
  "titulo": "5 datos de <i>GTA 6</i>", "subtitulo": "(antes del 19 de noviembre)",
  "intro": {"texto", "tts"?},
  "items": [{"etiqueta", "estilo", "texto", "tts"?, "card": {...}}],   # 3 a 6 items
  "cta": {"texto", "tts"?, "palabra", "linea"}
Estilos y campos de "card":
  papel  · arriba, grande, abajo          (hoja de calendario de papel)
  comic  · grande, linea, nota            (estallido pop-art con puntos)
  pixel  · titulo, filas: [{texto, ok}]   (videojuego retro 8 bits)
  neon   · filas: [{texto, color, tachado?}], nota
  synth  · grande, linea, nota            (atardecer retro con rejilla)
  plano  · grande, linea, nota            (tarjeta tipográfica limpia)
"""
import json
import shutil
from pathlib import Path

from personajes import chelios

AQUI = Path(__file__).resolve().parent
GSAP = AQUI / "gsap.min.js"
SFX = AQUI / "sfx"
FUENTES = {
    "Instrument Serif": [("InstrumentSerif-Regular.ttf", "normal"), ("InstrumentSerif-Italic.ttf", "italic")],
    "Silkscreen": [("Silkscreen-Regular.ttf", "normal")],
    "Erica One": [("EricaOne-Regular.ttf", "normal")],
    "Big Shoulders": [("BigShoulders-Bold.ttf", "normal")],
    "Archivo Black": [("ArchivoBlack-400.woff2", "normal")],
    "Outfit": [("Outfit-700.woff2", "normal")],
    "Space Mono": [("SpaceMono-700.woff2", "normal")],
}

PAPEL, TINTA, GRIS, ACENTO = "#F2EEE6", "#1E1B24", "#A39E96", "#D9583B"
CW, CH, CX, CY = 600, 840, 420, 560  # tarjeta: ancho, alto, x, y


def esc_voz(guion):
    """Convierte el guion de lista en escenas para motor/voz.py (una escena por bloque)."""
    escenas = [{"id": "e0", "parte": 1, "tpl": "habla", **_tx(guion["intro"])}]
    for i, it in enumerate(guion["items"], 1):
        escenas.append({"id": f"e{i}", "parte": 1, "tpl": "habla", **_tx(it)})
    escenas.append({"id": "ecta", "parte": 1, "tpl": "habla", **_tx(guion["cta"])})
    return {"voz": guion.get("voz", "em_alex"), "velocidad": guion.get("velocidad", 1.0), "escenas": escenas}


def _tx(b):
    d = {"texto": b["texto"]}
    if b.get("tts"):
        d["tts"] = b["tts"]
    return d


# ------------------------------------------------------------------ tarjetas (cada una, un estilo)

def card_papel(c, p):
    return f'''<div class="abs" style="inset:0;background:#8CC9DD"></div>
<div class="abs" style="left:-60px;top:560px;width:760px;height:420px;border-radius:50%;background:#F7F1E3;box-shadow:0 -10px 0 #E9DFC8"></div>
<div class="abs" style="left:-120px;top:650px;width:520px;height:300px;border-radius:50%;background:#7DBF7A;box-shadow:0 -10px 0 #6AAA67"></div>
<div class="abs" style="left:330px;top:690px;width:460px;height:260px;border-radius:50%;background:#5EA65B"></div>
<div id="{p}sol" class="abs pop" style="left:430px;top:60px;width:120px;height:120px;border-radius:50%;background:#FFC93C;box-shadow:0 8px 0 #E8A90F"></div>
<div id="{p}hoja" class="abs pop" style="left:110px;top:170px;width:380px;height:440px;background:#FFFDF8;border-radius:18px;box-shadow:0 14px 0 #DCD3BF, 0 26px 40px rgba(0,0,0,.18);transform:rotate(-4deg)">
  <div class="abs" style="left:0;top:0;width:380px;height:110px;background:#E2513A;border-radius:18px 18px 0 0"></div>
  <div class="abs" style="left:0;top:28px;width:380px;text-align:center;font:400 54px 'Archivo Black';color:#FFF8EC;letter-spacing:.02em">{c.get("arriba", "")}</div>
  <div class="abs" style="left:0;top:118px;width:380px;text-align:center;font:400 230px/1 'Archivo Black';color:{TINTA}">{c.get("grande", "")}</div>
  <div class="abs" style="left:0;top:370px;width:380px;text-align:center;font:italic 400 46px 'Instrument Serif';color:#6B655C">{c.get("abajo", "")}</div>
</div>'''


def card_comic(c, p):
    puntos = "radial-gradient(rgba(0,0,0,.16) 3px, transparent 3.5px)"
    estrella = ",".join(f"{50 + (48 if k % 2 == 0 else 34) * __import__('math').cos(k * 3.14159 / 10):.1f}% "
                        f"{50 + (48 if k % 2 == 0 else 34) * __import__('math').sin(k * 3.14159 / 10):.1f}%" for k in range(20))
    return f'''<div class="abs" style="inset:0;background:#FFD23F;background-image:{puntos};background-size:22px 22px"></div>
<div class="abs" style="inset:0;background:repeating-conic-gradient(from 0deg at 50% 42%, rgba(255,255,255,.35) 0deg 7deg, rgba(255,255,255,0) 7deg 18deg)"></div>
<div id="{p}bum" class="abs pop" style="left:30px;top:120px;width:540px;height:470px;clip-path:polygon({estrella});background:#1E1B24"></div>
<div id="{p}bum2" class="abs pop" style="left:52px;top:142px;width:496px;height:426px;clip-path:polygon({estrella});background:#FF4F5E"></div>
<div id="{p}num" class="abs pop" style="left:0;top:250px;width:600px;text-align:center;font:400 {150 if len(c.get("grande", "")) <= 4 else 128}px/1 'Erica One';color:#FFF;-webkit-text-stroke:8px #1E1B24;paint-order:stroke fill;transform:rotate(-6deg)">{c.get("grande", "")}</div>
<div id="{p}cap" class="abs pop" style="left:60px;top:640px;width:480px;padding:18px 22px;background:#FFFDF2;border:6px solid #1E1B24;box-shadow:10px 10px 0 #1E1B24;font:400 38px/1.1 'Archivo Black';color:#1E1B24;text-align:center">{c.get("linea", "")}</div>
<div class="abs" style="left:0;top:790px;width:600px;text-align:center;font:700 22px 'Space Mono';color:#1E1B24">{c.get("nota", "")}</div>'''


def card_pixel(c, p):
    suelo = "".join(f'<div class="abs" style="left:{x}px;top:760px;width:60px;height:80px;background:{"#C84C0C" if (x // 60) % 2 else "#E09050"};box-shadow:inset -6px -6px 0 rgba(0,0,0,.25)"></div>' for x in range(0, 600, 60))
    nubes = "".join(f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px;height:30px;background:#FFF;box-shadow:{w // 4}px -24px 0 #FFF, {w // 2}px 0 0 #FFF"></div>' for x, y, w in ((40, 70, 80), (420, 40, 60)))
    filas = ""
    for i, f in enumerate(c.get("filas", [])):
        ok = f.get("ok")
        col = "#5BE75B" if ok else "#FF5050"
        filas += (f'<div id="{p}f{i}" class="abs pop" style="left:50px;top:{290 + i * 140}px;width:500px;height:110px;background:#1E1B24;'
                  f'box-shadow:0 0 0 6px #FFF, 0 0 0 12px #1E1B24, 10px 10px 0 12px rgba(0,0,0,.3)">'
                  f'<div class="abs" style="left:24px;top:30px;font:400 40px Silkscreen;color:#FFF">{f["texto"]}</div>'
                  f'<div class="abs" style="right:24px;top:24px;font:400 52px Silkscreen;color:{col}">{"OK" if ok else "X"}</div></div>')
    return f'''<div class="abs" style="inset:0;background:#5C94FC"></div>
{nubes}{suelo}
<div class="abs" style="left:0;top:170px;width:600px;text-align:center;font:400 54px 'Silkscreen';color:#FFF;text-shadow:6px 6px 0 #1E1B24">{c.get("titulo", "")}</div>
{filas}'''


def card_neon(c, p):
    filas = ""
    for i, f in enumerate(c.get("filas", [])):
        col = f.get("color", "#45E3FF")
        glow = f"0 0 6px {col}, 0 0 22px {col}, 0 0 48px {col}"
        tach = (f'<div id="{p}x{i}" class="abs" style="left:150px;top:{60}px;width:300px;height:10px;background:#FF3B6B;box-shadow:0 0 14px #FF3B6B;transform:rotate(-8deg)"></div>'
                if f.get("tachado") else "")
        filas += (f'<div id="{p}f{i}" class="abs pop" style="left:0;top:{150 + i * 190}px;width:600px;height:150px">'
                  f'<div class="abs" style="left:0;top:10px;width:600px;text-align:center;font:400 {120 if len(f["texto"]) <= 6 else 84}px/1 \'Big Shoulders\';color:#FFF;text-shadow:{glow};letter-spacing:.04em">{f["texto"]}</div>{tach}</div>')
    return f'''<div class="abs" style="inset:0;background:#0C0920"></div>
<div class="abs" style="inset:0;background-image:linear-gradient(rgba(255,255,255,.04) 2px, transparent 2px),linear-gradient(90deg, rgba(255,255,255,.04) 2px, transparent 2px);background-size:40px 40px"></div>
<div class="abs" style="left:40px;top:60px;width:520px;height:720px;border:5px solid #B98CFF;border-radius:30px;box-shadow:0 0 18px #B98CFF, inset 0 0 18px #B98CFF"></div>
{filas}
<div id="{p}nota" class="abs pop" style="left:0;top:700px;width:600px;text-align:center;font:italic 400 44px 'Instrument Serif';color:#FFC2D4;text-shadow:0 0 12px #FF3B6B">{c.get("nota", "")}</div>'''


def card_synth(c, p):
    franjas = "".join(f'<div class="abs" style="left:0;top:{150 + k * 22}px;width:300px;height:{4 + k * 2}px;background:#2A1446"></div>' for k in range(6))
    return f'''<div class="abs" style="inset:0;background:linear-gradient(180deg,#1B0B3A 0%,#5B1E78 38%,#E3477D 62%,#FFB05C 74%)"></div>
<div id="{p}sol" class="abs pop" style="left:150px;top:200px;width:300px;height:300px;border-radius:50%;overflow:hidden;background:linear-gradient(180deg,#FFE66B,#FF6F91)">{franjas}</div>
<div class="abs" style="left:0;top:560px;width:600px;height:280px;overflow:hidden;perspective:300px">
  <div class="abs" style="left:-300px;top:0;width:1200px;height:600px;transform-origin:50% 0;transform:rotateX(62deg);background:#1B0B3A;background-image:linear-gradient(#FF4FD8 3px, transparent 3px),linear-gradient(90deg,#FF4FD8 3px, transparent 3px);background-size:80px 60px"></div>
</div>
<div class="abs" style="left:0;top:540px;width:600px;height:6px;background:#FF9BE6;box-shadow:0 0 18px #FF4FD8"></div>
<div id="{p}t" class="abs pop" style="left:0;top:70px;width:600px;text-align:center;font:italic 400 110px/1 'Instrument Serif';color:#FFF;text-shadow:0 0 22px rgba(255,79,216,.8)">{c.get("grande", "")}</div>
<div id="{p}l" class="abs pop" style="left:0;top:600px;width:600px;text-align:center;font:400 46px 'Archivo Black';color:#FFF;text-shadow:0 4px 0 #5B1E78">{c.get("linea", "")}</div>
<div id="{p}n" class="abs pop" style="left:0;top:690px;width:600px;text-align:center;font:700 30px 'Space Mono';color:#FFE6F4">{c.get("nota", "")}</div>'''


def card_plano(c, p):
    return f'''<div class="abs" style="inset:0;background:#FFFDF8"></div>
<div id="{p}g" class="abs pop" style="left:0;top:200px;width:600px;text-align:center;font:italic 400 200px/1 'Instrument Serif';color:{ACENTO}">{c.get("grande", "")}</div>
<div id="{p}l" class="abs pop" style="left:60px;top:470px;width:480px;text-align:center;font:700 46px/1.15 'Outfit';color:{TINTA}">{c.get("linea", "")}</div>
<div class="abs" style="left:0;top:720px;width:600px;text-align:center;font:700 24px 'Space Mono';color:{GRIS}">{c.get("nota", "")}</div>'''


ESTILOS = {"papel": card_papel, "comic": card_comic, "pixel": card_pixel, "neon": card_neon, "synth": card_synth, "plano": card_plano}


def tarjeta(it, pre):
    return ESTILOS[it.get("estilo", "plano")](it.get("card", {}), pre)


# ------------------------------------------------------------------ proyecto

def montar(guion_path, build_dir, pj):
    guion = json.loads(Path(guion_path).read_text(encoding="utf-8"))
    t = json.loads((Path(build_dir) / "tiempos.json").read_text(encoding="utf-8"))
    pj = Path(pj)
    (pj / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    (pj / "assets" / "sfx").mkdir(parents=True, exist_ok=True)
    shutil.copy(Path(build_dir) / "narracion.wav", pj / "assets" / "narracion.wav")
    shutil.copy(GSAP, pj / "assets" / "gsap.min.js")
    ff = ""
    for fam, archivos in FUENTES.items():
        for a, estilo in archivos:
            shutil.copy(AQUI / "fonts" / a, pj / "assets" / "fonts" / a)
            peso = "700" if a.startswith(("Outfit-700", "SpaceMono-700")) else "400"
            ff += f"@font-face {{ font-family: '{fam}'; font-style: {estilo}; font-weight: {peso}; src: url('assets/fonts/{a}'); }}\n"

    total = round(t["total"] + guion["cta"].get("hold", 1.8), 3)  # la cuadrícula final se queda un momento
    E = {e["id"]: e for e in t["escenas"]}
    items = guion["items"]
    n = len(items)
    t_items = [E[f"e{i}"]["start"] for i in range(1, n + 1)]
    t_cta = E["ecta"]["start"]

    # lista numerada
    lista = ""
    for i, it in enumerate(items):
        lista += (f'<div id="li{i}" class="abs" style="left:56px;top:{600 + i * 74}px;width:340px;white-space:nowrap">'
                  f'<span class="mono" style="font-size:22px;color:{GRIS}">{i + 1:02d}</span>'
                  f'<span id="lt{i}" style="margin-left:18px;font:700 32px Outfit;color:{GRIS}">{it["etiqueta"]}</span></div>')
    # tarjetas
    cards = ""
    for i, it in enumerate(items):
        cards += (f'<div id="c{i}" class="abs tarjeta" style="left:{CX}px;top:{CY}px;width:{CW}px;height:{CH}px;opacity:0">'
                  f'{tarjeta(it, f"c{i}-")}</div>')
    # cuadrícula final
    esc_m = 0.29
    mw, mh = CW * esc_m, CH * esc_m
    cols = min(n, 3)
    filas = (n + cols - 1) // cols
    gx = (1080 - cols * mw - (cols - 1) * 22) / 2
    grid = ""
    for i, it in enumerate(items):
        r, k = divmod(i, cols)
        enfila = min(cols, n - r * cols)
        gx_f = (1080 - enfila * mw - (enfila - 1) * 22) / 2
        x, y = gx_f + k * (mw + 22), 470 + r * (mh + 22)
        grid += (f'<div id="g{i}" class="abs gi" style="left:{x:.0f}px;top:{y:.0f}px;width:{mw:.0f}px;height:{mh:.0f}px;opacity:0">'
                 f'<div class="abs tarjeta" style="left:0;top:0;width:{CW}px;height:{CH}px;transform:scale({esc_m});transform-origin:0 0">{tarjeta(it, f"g{i}-")}</div></div>')
    y_cta = 470 + filas * (mh + 22) + 40
    cta = guion["cta"]

    # subtítulos: grupos de hasta 4 palabras
    subs, js_subs = "", []
    gi = 0
    for et in t["escenas"]:
        ws, cur = et["words"], []
        for j, w in enumerate(ws):
            cur.append(w)
            fin = w["text"][-1] in ".?!,:;…"
            if fin or len(cur) == 4 or j == len(ws) - 1:
                s0 = et["start"] + cur[0]["start"] - 0.05
                s1 = et["start"] + cur[-1]["end"] + 0.15
                if j + 1 < len(ws):
                    s1 = min(s1, et["start"] + ws[j + 1]["start"] - 0.05)
                spans = "".join(f'<span id="sw{gi}-{k}" class="sw">{w2["text"]} </span>' for k, w2 in enumerate(cur))
                subs += f'<div id="sg{gi}" class="sg">{spans}</div>'
                js_subs.append(f'tl.fromTo("#sg{gi}", {{opacity:0}}, {{opacity:1, duration:0.01}}, {max(0.0, s0):.3f});')
                for k, w2 in enumerate(cur):
                    js_subs.append(f'tl.fromTo("#sw{gi}-{k}", {{opacity:.28}}, {{opacity:1, duration:0.08}}, {et["start"] + w2["start"] - 0.03:.3f});')
                js_subs.append(f'tl.set("#sg{gi}", {{opacity:0}}, {s1:.3f});')
                gi += 1
                cur = []

    js = []
    # entrada: todo visible desde el fotograma 0 (título + lista)
    js.append('tl.fromTo("#tit", {scale:1.04}, {scale:1, duration:0.6, ease:"expo.out"}, 0.02);')
    for i in range(n):
        ti = t_items[i]
        js.append(f'tl.to("#lt{i}", {{color:"{ACENTO}", duration:0.15}}, {ti - 0.1:.3f});')
        js.append(f'tl.fromTo("#li{i}", {{x:0}}, {{x:14, duration:0.3, ease:"back.out(2)"}}, {ti - 0.1:.3f});')
        fin = t_items[i + 1] if i + 1 < n else t_cta
        js.append(f'tl.to("#lt{i}", {{color:"{TINTA}", duration:0.15}}, {fin - 0.1:.3f});')
        js.append(f'tl.to("#li{i}", {{x:0, duration:0.2}}, {fin - 0.1:.3f});')
        rot = -3 if i % 2 else 3
        js.append(f'tl.fromTo("#c{i}", {{opacity:0, y:90, rotation:{rot}, scale:.9}}, {{opacity:1, y:0, rotation:0, scale:1, duration:0.55, ease:"back.out(1.5)"}}, {ti - 0.15:.3f});')
        js.append(f'tl.fromTo("#c{i} .pop", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:0.4, ease:"back.out(2)", stagger:0.22}}, {ti + 0.25:.3f});')
        js.append(f'tl.to("#c{i}", {{opacity:0, x:-160, rotation:-8, duration:0.35, ease:"power2.in"}}, {fin - 0.2:.3f});')
    # intro: tarjeta de portada (Chelios) mientras habla la intro
    js.append(f'tl.to("#portada", {{opacity:0, y:-40, duration:0.3}}, {t_items[0] - 0.25:.3f});')
    js.append('tl.fromTo("#portada .pop", {scale:.85}, {scale:1, duration:0.6, ease:"back.out(2)"}, 0.05);')
    # cierre
    js.append(f'tl.to(["#lista", "#tit"], {{opacity:0, y:-30, duration:0.3}}, {t_cta - 0.2:.3f});')
    js.append(f'tl.fromTo(".gi", {{opacity:0, y:50, scale:.8}}, {{opacity:1, y:0, scale:1, duration:0.4, ease:"back.out(1.8)", stagger:0.08}}, {t_cta:.3f});')
    js.append(f'tl.fromTo("#cta1", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.4}}, {t_cta + 0.4:.3f});')
    js.append(f'tl.fromTo("#cta2", {{opacity:0, scale:1.4}}, {{opacity:1, scale:1, duration:0.5, ease:"expo.out"}}, {t_cta + 0.7:.3f});')
    js.append(f'tl.fromTo("#cta3", {{opacity:0}}, {{opacity:1, duration:0.4}}, {t_cta + 1.2:.3f});')

    portada = (f'<div id="portada" class="abs" style="left:{CX}px;top:{CY}px;width:{CW}px;height:{CH}px;border-radius:28px;overflow:hidden;background:#FFC93C;box-shadow:0 30px 60px rgba(30,27,36,.18)">'
               f'<div class="abs" style="inset:0;background:repeating-conic-gradient(from 0deg at 50% 45%, #FFB61A 0deg 9deg, #FFC93C 9deg 18deg)"></div>'
               f'<div class="abs pop" style="left:130px;top:170px;width:340px;height:391px">{chelios("pc", 340)}</div>'
               f'<div class="abs" style="left:0;top:620px;width:600px;text-align:center;font:italic 400 64px \'Instrument Serif\';color:{TINTA}">{guion.get("portada", "")}</div></div>')

    sfx, fx = [], 0
    for ti in t_items:
        sfx.append(("whoosh-short", ti - 0.15, 0.2))
        sfx.append(("pop", ti + 0.3, 0.18))
    sfx += [("whoosh-cinematic", t_cta - 0.1, 0.22), ("impact-bass-1", t_cta + 0.7, 0.22)]
    audios = ""
    for nmb, ta, v in sfx:
        src = SFX / f"{nmb}.mp3"
        shutil.copy(src, pj / "assets" / "sfx" / src.name)
        import subprocess
        d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)],
                           capture_output=True, text=True).stdout.strip()
        audios += f'<audio id="fx{fx}" class="clip" src="assets/sfx/{src.name}" data-start="{max(0, ta):.3f}" data-duration="{d}" data-track-index="{2 + fx % 6}" data-volume="{v}"></audio>\n'
        fx += 1

    i_style = f"<i style=\"font:italic 400 124px/1 'Instrument Serif';color:{ACENTO};letter-spacing:0\">"
    titulo_html = guion["titulo"].replace("<i>", i_style)
    html = f'''<!doctype html>
<html lang="es" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<style>
{ff}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:1080px; height:1920px; overflow:hidden; background:{PAPEL}; }}
#root {{ position:relative; width:1080px; height:1920px; overflow:hidden; background:{PAPEL}; }}
.abs {{ position:absolute; }}
.mono {{ font-family:'Space Mono', monospace; font-weight:700; }}
.tarjeta {{ border-radius:28px; overflow:hidden; box-shadow:0 30px 60px rgba(30,27,36,.18), 0 0 0 2px rgba(30,27,36,.06); }}
.sg {{ position:absolute; left:60px; width:960px; top:1470px; text-align:center; font:700 54px/1.15 Outfit; color:{TINTA}; opacity:0; }}
.sw {{ display:inline; }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1080" data-height="1920">
  <div id="capa" class="clip" data-start="0" data-duration="{total}" data-track-index="0" style="position:absolute;inset:0">
    <div class="abs" style="inset:0;background-image:radial-gradient(rgba(30,27,36,.07) 1.6px, transparent 2px);background-size:40px 40px"></div>
    <div class="abs mono" style="left:60px;top:150px;font-size:24px;color:{GRIS};letter-spacing:.14em">● {guion.get("marca", "CHELIOS NOTICIAS")}</div>
    <div class="abs mono" style="right:60px;top:146px;font-size:24px;color:{ACENTO};border:2px solid {ACENTO};border-radius:999px;padding:4px 16px">{guion.get("chip", "")}</div>
    <div id="tit" class="abs" style="left:0;top:250px;width:1080px;text-align:center">
      <div style="font:700 96px/1 Outfit;color:{TINTA};letter-spacing:-.02em">{titulo_html}</div>
      <div style="margin-top:22px;font:italic 400 40px 'Instrument Serif';color:{GRIS}">{guion.get("subtitulo", "")}</div>
    </div>
    <div id="lista">{lista}{portada}{cards}</div>
    {grid}
    <div id="cta1" class="abs" style="left:0;top:{y_cta:.0f}px;width:1080px;text-align:center;font:italic 400 64px 'Instrument Serif';color:{TINTA}">comenta</div>
    <div id="cta2" class="abs" style="left:0;top:{y_cta + 60:.0f}px;width:1080px;text-align:center;font:italic 400 230px/1 'Instrument Serif';color:{ACENTO}">{cta["palabra"]}</div>
    <div id="cta3" class="abs" style="left:0;top:{y_cta + 300:.0f}px;width:1080px;text-align:center;font:700 38px Outfit;color:{GRIS}">{cta.get("linea", "")}</div>
    {subs}
  </div>
  <audio id="narr" class="clip" src="assets/narracion.wav" data-start="0" data-duration="{total}" data-track-index="1" data-volume="1"></audio>
{audios}</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
{chr(10).join(js_subs)}
window.__timelines["main"] = tl;
</script>
</body>
</html>
'''
    (pj / "index.html").write_text(html, encoding="utf-8")
    return total
