"""El Animador: arma el proyecto HyperFrames del episodio a partir de guion + tiempos."""
import json
import random
import shutil
import sys
from pathlib import Path

from personajes import CORAL, GROUND, INK, MUTED, SUN
from plantillas import escena_html, norm

AQUI = Path(__file__).resolve().parent
SFX_DIR = AQUI / "sfx"
GSAP = AQUI / "gsap.min.js"

SOCIO_TXT = "#9FEFFF"  # subtítulos del socio humano (cian claro); Chelios en blanco

CSS_GLOBAL = """
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #0D0B24; }
      #root { position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #0D0B24; }
      .wrap { position: absolute; inset: 0; }
      .abs { position: absolute; }
      .center { left: 0; width: 1080px; text-align: center; }
      .disp { font-family: 'Archivo Black', sans-serif; text-transform: uppercase; line-height: .95; letter-spacing: -.005em; }
      .mono { font-family: 'Space Mono', monospace; font-weight: 700; }
      .body { font-family: 'Outfit', sans-serif; }
      .card { position: absolute; background: #1A1640; border: 3px solid #2C2760; border-radius: 30px; box-shadow: 0 24px 60px rgba(0,0,0,.35); }
      .chip { display: inline-block; padding: 12px 28px; border-radius: 999px; font-family: 'Space Mono', monospace; font-weight: 700; letter-spacing: .08em; line-height: 1.1; white-space: nowrap; }
      .stamp { position: absolute; display: inline-block; padding: 10px 26px 4px; border: 7px solid; border-radius: 18px; background: rgba(13,11,36,.88); white-space: nowrap; }
"""


_DUR = {}


def dur_sfx(path):
    if path not in _DUR:
        import subprocess
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                             capture_output=True, text=True).stdout.strip()
        _DUR[path] = round(float(out or 1.0), 3)
    return _DUR[path]


def bg_html(total):
    rnd = random.Random(11)
    stars = ""
    data = []
    for i in range(46):
        x, y = rnd.randint(0, 1080), rnd.randint(0, 1920)
        sz = rnd.choice([3, 3, 4, 5])
        stars += f'<div id="bg-st{i}" class="abs" style="left:{x}px;top:{y}px;width:{sz}px;height:{sz}px;border-radius:50%;background:#CFCBFF"></div>'
        data.append([round(rnd.uniform(0.6, 2.2), 2), round(rnd.uniform(0, 6.28), 2)])
    return f'''<template>
  <style>#root {{ position: absolute; inset: 0; }}</style>
  <div id="root" data-composition-id="bg" data-width="1080" data-height="1920">
    <div id="bg-fill" class="abs" style="left:0;top:0;width:1080px;height:1920px;background:{GROUND}"></div>
    <div id="bg-g1" class="abs" style="left:-400px;top:-300px;width:1500px;height:1500px;background:radial-gradient(circle, rgba(98,64,255,.30) 0%, rgba(98,64,255,0) 62%)"></div>
    <div id="bg-g2" class="abs" style="left:200px;top:900px;width:1300px;height:1300px;background:radial-gradient(circle, rgba(69,227,255,.13) 0%, rgba(69,227,255,0) 60%)"></div>
    <div id="bg-dots" class="abs" style="left:0;top:0;width:1080px;height:1920px;background-image:radial-gradient(rgba(142,137,191,.20) 2px, transparent 2.6px);background-size:54px 54px"></div>
    {stars}
    <div id="bg-fw" class="abs" style="left:0;top:1310px;width:1080px;height:610px;overflow:hidden;perspective:520px" data-layout-ignore data-layout-allow-overflow>
      <div id="bg-floor" class="abs" style="left:-1100px;top:0;width:3280px;height:1500px;transform-origin:50% 0%;transform:rotateX(70deg);background-image:linear-gradient(rgba(120,90,255,.62) 3px, transparent 3px),linear-gradient(90deg, rgba(120,90,255,.62) 3px, transparent 3px);background-size:120px 120px"></div>
      <div class="abs" style="left:0;top:0;width:1080px;height:610px;background:linear-gradient(180deg, rgba(13,11,36,.9) 0%, rgba(13,11,36,0) 22%, rgba(13,11,36,0) 66%, rgba(13,11,36,.92) 100%)"></div>
    </div>
    <div id="bg-hz" class="abs" style="left:0;top:1300px;width:1080px;height:22px;background:radial-gradient(ellipse 50% 50% at 50% 50%, rgba(69,227,255,.55), rgba(69,227,255,0) 70%)" data-layout-ignore></div>
    <div id="bg-vig" class="abs" style="left:0;top:0;width:1080px;height:1920px;background:radial-gradient(ellipse 75% 60% at 50% 45%, rgba(0,0,0,0) 55%, rgba(3,2,10,.6) 100%)"></div>
  </div>
  <script>
  (function () {{
    const tl = gsap.timeline({{ paused: true }});
    const T = {total};
    tl.fromTo("#bg-g1", {{ x: 0, y: 0 }}, {{ x: 260, y: 420, duration: T, ease: "sine.inOut" }}, 0);
    tl.fromTo("#bg-g2", {{ x: 0, y: 0 }}, {{ x: -380, y: -300, duration: T, ease: "sine.inOut" }}, 0);
    tl.fromTo("#bg-dots", {{ y: 0 }}, {{ y: -54 * 12, duration: T, ease: "none" }}, 0);
    const S = {json.dumps(data)};
    const els = S.map((_, i) => document.getElementById("bg-st" + i));
    const P = {{ t: 0 }};
    const fl = document.getElementById("bg-floor");
    const f = () => {{ els.forEach((e, i) => {{ e.style.opacity = (0.15 + 0.55 * (0.5 + 0.5 * Math.sin(P.t * S[i][0] + S[i][1]))).toFixed(3); }}); fl.style.backgroundPosition = "0px " + ((P.t * 45) % 120).toFixed(2) + "px"; }};
    tl.to(P, {{ t: T, duration: T, ease: "none", onUpdate: f }}, 0);
    f();
    window.__timelines["bg"] = tl;
  }})();
  </script>
</template>
'''


def hud_html(total, dia, t_cta):
    return f'''<template>
  <style>#root {{ position: absolute; inset: 0; }}</style>
  <div id="root" data-composition-id="hud" data-width="1080" data-height="1920">
    <div id="hud-w" class="abs" style="left:0;top:0;width:1080px;height:260px">
      <div class="abs" style="left:64px;top:196px;width:20px;height:20px;border-radius:50%;background:{SUN};box-shadow:0 0 18px {SUN}"></div>
      <div class="abs mono" style="left:98px;top:188px;font-size:28px;color:{MUTED};letter-spacing:.12em">LA FÁBRICA DE CHELIOS</div>
      <div class="abs" style="right:64px;top:180px"><span class="chip" style="border:3px solid {SUN};color:{SUN};font-size:28px;padding:8px 20px">DÍA {dia:03d}</span></div>
    </div>
  </div>
  <script>
  (function () {{
    const tl = gsap.timeline({{ paused: true }});
    tl.to("#hud-w", {{ opacity: 0, duration: 0.25, ease: "power2.in" }}, {max(0, t_cta - 0.1)});
    tl.to("#hud-w", {{ opacity: 0, duration: 0.01 }}, {total - 0.05});
    window.__timelines["hud"] = tl;
  }})();
  </script>
</template>
'''


def grupos(escenas_t, guion):
    """Agrupa palabras de 1 a 3 para subtítulos estilo reel."""
    out = []
    por_id = {e["id"]: e for e in guion["escenas"]}
    for et in escenas_t:
        g = por_id[et["id"]]
        hl = {norm(w) for w in g.get("hl", [])}
        kill = {norm(w) for w in g.get("kill", [])}
        claro = g["tpl"] == "cta"
        cur = []
        ws = et["words"]
        for i, w in enumerate(ws):
            cur.append(w)
            fin = w["text"][-1] in ".?!,:…;"
            largo = sum(len(x["text"]) for x in cur)
            sig = ws[i + 1] if i + 1 < len(ws) else None
            pausa = sig and (sig["start"] - w["end"]) > 0.15
            otro = sig and sig.get("quien", "chelios") != w.get("quien", "chelios")
            if fin or len(cur) == 3 or largo >= 15 or pausa or otro or sig is None:
                out.append({"scene": et["id"], "base": et["start"], "dur": et["dur"], "words": cur, "hl": hl, "kill": kill, "claro": claro})
                cur = []
    # tiempos absolutos
    res = []
    for i, g in enumerate(out):
        s = g["base"] + g["words"][0]["start"] - 0.06
        e = g["base"] + g["words"][-1]["end"] + 0.22
        nxt = out[i + 1] if i + 1 < len(out) else None
        if nxt:
            ns = nxt["base"] + nxt["words"][0]["start"] - 0.06
            e = min(e, ns)
        e = min(e, g["base"] + g["dur"] - 0.02)
        s = max(s, 0.18)
        res.append({**g, "s": round(s, 3), "e": round(e, 3)})
    return res


def captions_html(gs):
    divs, js = [], []
    for gi, g in enumerate(gs):
        texto = " ".join(w["text"] for w in g["words"])
        n = len(texto)
        fs = 96 if n <= 11 else 86 if n <= 16 else 74
        socio = g["words"][0].get("quien") == "socio"
        col = GROUND if g["claro"] else (SOCIO_TXT if socio else INK)
        spans = []
        for wi, w in enumerate(g["words"]):
            k = norm(w["text"])
            c = col
            if k in {norm(x) for x in g["hl"]} or w["text"] in g["hl"]:
                c = "#C2185B" if g["claro"] else SUN
            if k in g["kill"] or w["text"] in g["kill"]:
                c = "#C2185B" if g["claro"] else CORAL
            spans.append(f'<span id="cg{gi}w{wi}" class="cw" style="color:{c}">{w["text"].upper()}</span>')
        sh = "none" if g["claro"] else "0 5px 0 rgba(0,0,0,.45), 0 0 26px rgba(13,11,36,.75)"
        divs.append(f'<div id="cg{gi}" class="cg disp" style="font-size:{fs}px;text-shadow:{sh}">{" ".join(spans)}</div>')
        js.append(f'tl.fromTo("#cg{gi}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01 }}, {g["s"]});')
        for wi, w in enumerate(g["words"]):
            t = max(g["s"], g["base"] + w["start"] - 0.04)
            js.append(f'tl.fromTo("#cg{gi}w{wi}", {{ opacity: 0, scale: 0.82, filter: "blur(6px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.14, ease: "power4.out" }}, {t:.3f});')
        js.append(f'tl.to("#cg{gi}", {{ opacity: 0, duration: 0.08, ease: "power2.in" }}, {max(g["s"] + 0.05, g["e"] - 0.08):.3f});')
        js.append(f'tl.set("#cg{gi}", {{ opacity: 0, visibility: "hidden" }}, {g["e"]:.3f});')
    return f'''<template>
  <style>
    #root {{ position: absolute; inset: 0; }}
    .cg {{ position: absolute; left: 60px; width: 960px; top: 1168px; text-align: center; line-height: 1.04; overflow: visible; opacity: 0; }}
    .cw {{ display: inline-block; margin: 0 .06em; }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
    {"".join(divs)}
  </div>
  <script>
  (function () {{
    const tl = gsap.timeline({{ paused: true }});
    {chr(10).join(js)}
    window.__timelines["captions"] = tl;
  }})();
  </script>
</template>
'''


def montar(guion_path, build_dir, proyecto_dir):
    guion = json.loads(Path(guion_path).read_text(encoding="utf-8"))
    tiempos = json.loads((Path(build_dir) / "tiempos.json").read_text(encoding="utf-8"))
    pj = Path(proyecto_dir)
    (pj / "compositions").mkdir(parents=True, exist_ok=True)
    (pj / "assets" / "sfx").mkdir(parents=True, exist_ok=True)
    shutil.copy(Path(build_dir) / "narracion.wav", pj / "assets" / "narracion.wav")
    shutil.copy(GSAP, pj / "assets" / "gsap.min.js")
    env = tiempos["envolvente"]
    env2 = tiempos.get("envolvente_socio") or [0] * len(env)
    total = tiempos["total"]
    por_id = {e["id"]: e for e in guion["escenas"]}

    hosts, audios, fx_i = [], [], 0
    t_cta = total
    for et in tiempos["escenas"]:
        esc = por_id[et["id"]]
        if esc["tpl"] == "cta":
            t_cta = et["start"]
        f0 = int(round(et["start"] * 30))
        f1 = int(round((et["start"] + et["dur"]) * 30)) + 1
        prev = tiempos["escenas"][tiempos["escenas"].index(et) - 1] if tiempos["escenas"].index(et) > 0 else None
        if prev is not None and prev["parte"] != et["parte"]:
            esc = {**esc, "_inicio_parte": True}
        doc, sfx = escena_html(esc, et, env[f0:f1], guion["dia"], env2[f0:f1])
        (pj / "compositions" / f"{et['id']}.html").write_text(doc, encoding="utf-8")
        hosts.append(f'      <div id="{et["id"]}" data-composition-id="{et["id"]}" data-composition-src="compositions/{et["id"]}.html" '
                     f'data-start="{et["start"]}" data-duration="{et["dur"]}" data-track-index="1" data-track-kind="graphics" '
                     f'data-width="1080" data-height="1920" style="z-index:2"></div>')
        # whoosh de corte entre escenas (rotando 3 tomas), salvo donde la plantilla ya pone uno
        nombres = {n for n, _, _ in sfx}
        if et["start"] > 0 and not any(n.startswith("whoosh") and t < 0.3 for n, t, _ in sfx):
            sfx.append((["whoosh-short", "whoosh", "whoosh-short"][fx_i % 3], 0.0, 0.12))
        for n, t, v in sfx:
            src = SFX_DIR / f"{n}.mp3"
            if not src.exists():
                continue
            shutil.copy(src, pj / "assets" / "sfx" / f"{n}.mp3")
            ta = round(et["start"] + t, 3)
            audios.append(f'      <audio id="fx{fx_i}" class="clip" src="assets/sfx/{n}.mp3" data-start="{ta}" data-duration="{dur_sfx(src)}" data-track-index="{5 + fx_i % 6}" data-volume="{v}"></audio>')
            fx_i += 1

    (pj / "compositions" / "bg.html").write_text(bg_html(total), encoding="utf-8")
    (pj / "compositions" / "hud.html").write_text(hud_html(total, guion["dia"], t_cta), encoding="utf-8")
    gs = grupos(tiempos["escenas"], guion)
    (pj / "compositions" / "captions.html").write_text(captions_html(gs), encoding="utf-8")

    index = f'''<!doctype html>
<html lang="es" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/gsap.min.js"></script>
    <style>{CSS_GLOBAL}    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1080" data-height="1920">
      <div id="bg" data-composition-id="bg" data-composition-src="compositions/bg.html" data-start="0" data-duration="{total}" data-track-index="0" data-track-kind="graphics" data-width="1080" data-height="1920" style="z-index:1"></div>
{chr(10).join(hosts)}
      <div id="hud" data-composition-id="hud" data-composition-src="compositions/hud.html" data-start="0" data-duration="{total}" data-track-index="2" data-track-kind="graphics" data-width="1080" data-height="1920" style="z-index:3"></div>
      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{total}" data-track-index="3" data-track-kind="captions" data-width="1080" data-height="1920" style="z-index:4"></div>
      <audio id="narr" class="clip" src="assets/narracion.wav" data-start="0" data-duration="{total}" data-track-index="4" data-volume="1"></audio>
{chr(10).join(audios)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
'''
    (pj / "index.html").write_text(index, encoding="utf-8")
    # capítulos para TikTok / YouTube
    caps, t0 = [], None
    partes = guion.get("partes", {})
    for et in tiempos["escenas"]:
        if not caps or caps[-1]["parte"] != et["parte"]:
            off = 0.0 if not caps else 0.42  # entra con el título ya visible (la voz empieza a los 0.62 s)
            caps.append({"parte": et["parte"], "titulo": partes.get(str(et["parte"]), ""), "inicio": round(et["start"] + off, 3),
                         "escena": et["start"]})
    for i, c in enumerate(caps):
        c["fin"] = caps[i + 1]["escena"] if i + 1 < len(caps) else total
    (Path(build_dir) / "capitulos.json").write_text(json.dumps({"total": total, "capitulos": caps}, ensure_ascii=False, indent=2), encoding="utf-8")
    return total, len(gs), fx_i


if __name__ == "__main__":
    print(montar(sys.argv[1], sys.argv[2], sys.argv[3]))
