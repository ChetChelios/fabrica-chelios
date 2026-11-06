"""Plantillas de escena de La Fábrica de Chelios (1080x1920, HyperFrames).

Cada plantilla recibe S (escena) y devuelve dict(html, js, sfx).
- '@@' en html/js se reemplaza por el prefijo único de la escena ("s05-").
- En JS hay helpers: at("palabra"), fadeUp, blurIn, pop, slideX, stamp, dim, counter, rig...
- Zona útil: y 300–1110. Debajo van los subtítulos (1150–1330). Nada de texto bajo 1330.
"""
import json
import random
import re

from personajes import (CARD, CORAL, CYAN, GREEN, GROUND, INK, LINE, MUTED, SUN,
                        TRABAJADORES, bot, chelios, icono, socio)


def norm(w):
    return re.sub(r"[^\wáéíóúüñ]", "", w.lower())


def anclas(words):
    a, cnt = {}, {}
    for w in words:
        k = norm(w["text"])
        if not k:
            continue
        cnt[k] = cnt.get(k, 0) + 1
        key = k if cnt[k] == 1 else f"{k}#{cnt[k]}"
        a[key] = w["start"]
    return a


class S:
    def __init__(self, esc, tiempos, env_slice, dia=1, env2=None):
        self.env2 = env2 or []
        self.dia = int(dia)
        self.inicio_parte = bool(esc.get("_inicio_parte"))  # 1.ª escena de las partes 2+: debe verse lleno desde el corte
        self.id = esc["id"]
        self.pre = esc["id"] + "-"
        self.p = esc.get("p", {})
        self.dur = tiempos["dur"]
        self.words = tiempos["words"]
        self.a = anclas(self.words)
        self.env = env_slice
        rnd = random.Random(sum(ord(c) * (i + 1) for i, c in enumerate(self.id)))
        t, bl = 0.9 + rnd.random(), []
        while t < self.dur:
            bl.append(round(t, 2))
            t += 2.4 + rnd.random() * 1.8
        self.blinks = bl
        self.extra = {}

    def at(self, k, f=0.0):
        return self.a.get(k, f)

    def tw(self, palabra, f=0.0):
        """Tiempo (s) de una palabra ancla: "cinco" o "cinco#2" (2.ª vez). Si no está, devuelve f."""
        if palabra is None or palabra == "":
            return float(f)
        if isinstance(palabra, (int, float)):
            return float(palabra)
        base, _, n = str(palabra).partition("#")
        k = norm(base) + (f"#{n}" if n and n != "1" else "")
        return float(self.a.get(k, f))

    def ultima(self, palabra, f=0.0):
        """Tiempo de la última vez que aparece una palabra."""
        base = norm(palabra)
        keys = [k for k in self.a if k == base or k.startswith(base + "#")]
        return float(max(self.a[k] for k in keys)) if keys else float(f)


# ---------------------------------------------------------------- piezas HTML

def chip(id_, texto, top, color=SUN, fondo="transparent", tinta=None, size=30):
    tinta = tinta or color
    return (f'<div class="abs center" style="top:{top}px"><span id="@@{id_}" class="chip" '
            f'style="border:3px solid {color};color:{tinta};background:{fondo};font-size:{size}px">{texto}</span></div>')


def title(id_, html, top, size=96, color=INK, extra=""):
    return f'<div id="@@{id_}" class="abs center disp" style="top:{top}px;font-size:{size}px;color:{color};{extra}">{html}</div>'


def hl(t, c=SUN):
    return f'<span style="color:{c}">{t}</span>'


def card(id_, x, y, w, h, inner="", extra=""):
    return f'<div id="@@{id_}" class="card" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;{extra}">{inner}</div>'


def stamp_html(id_, texto, x, y, color=CORAL, size=64, w=None):
    ancho = f"width:{w}px;" if w else ""
    return (f'<div id="@@{id_}" class="stamp disp" style="left:{x}px;top:{y}px;{ancho}color:{color};'
            f'border-color:{color};font-size:{size}px">{texto}</div>')


def trabajador(n):
    return TRABAJADORES[n - 1]


# ---------------------------------------------------------------- JS base

JS_BASE = r"""
const tl = gsap.timeline({ paused: true });
const TICKS = [];
const $ = (s) => "#" + D.pre + s;
const el = (s) => document.getElementById(D.pre + s);
const at = (k, f) => (D.a[k] !== undefined ? D.a[k] : (f !== undefined ? f : 0));
function fadeUp(s, t, dy) { tl.fromTo($(s), { opacity: 0, y: dy === undefined ? 50 : dy, filter: "blur(8px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.55, ease: "expo.out" }, t); }
function blurIn(s, t, d) { tl.fromTo($(s), { opacity: 0, filter: "blur(14px)" }, { opacity: 1, filter: "blur(0px)", duration: d || 0.22, ease: "power4.out" }, t); }
function pop(s, t) { tl.fromTo($(s), { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: 0.5, ease: "back.out(1.8)" }, t); }
function slideX(s, t, dx) { tl.fromTo($(s), { opacity: 0, x: dx, filter: "blur(10px)" }, { opacity: 1, x: 0, filter: "blur(0px)", duration: 0.5, ease: "expo.out" }, t); }
function stamp(s, t, rot) { const r = rot === undefined ? -8 : rot; tl.fromTo($(s), { opacity: 0, scale: 2.6, rotation: r }, { opacity: 1, scale: 1, rotation: r, duration: 0.24, ease: "power4.in" }, t); }
function dim(s, t, o) { tl.to($(s), { opacity: o === undefined ? 0.3 : o, duration: 0.3, ease: "power2.out" }, t); }
function gone(s, t) { tl.to($(s), { opacity: 0, filter: "blur(8px)", duration: 0.2, ease: "power2.in" }, t); }
function grow(s, t, d) { tl.fromTo($(s), { scaleX: 0 }, { scaleX: 1, duration: d || 0.6, ease: "expo.out", transformOrigin: "0% 50%" }, t); }
function clamp01(x) { return Math.max(0, Math.min(1, x)); }
function easeOut(x) { x = clamp01(x); return 1 - Math.pow(1 - x, 3); }
function counter(s, t0, t1, v0, v1, fmt) { const e = el(s); TICKS.push((t) => { const v = v0 + (v1 - v0) * easeOut((t - t0) / Math.max(0.01, t1 - t0)); e.textContent = fmt ? fmt(v) : String(Math.round(v)); }); }
function keyed(keys, t) { if (t <= keys[0][0]) return keys[0][1]; for (let i = 1; i < keys.length; i++) { if (t <= keys[i][0]) { const a = keys[i - 1], c = keys[i]; let x = (t - a[0]) / Math.max(0.001, c[0] - a[0]); x = x * x * (3 - 2 * x); return a[1] + (c[1] - a[1]) * x; } } return keys[keys.length - 1][1]; }
function rig(id, o) {
  o = o || {};
  const g = (k) => document.getElementById(D.pre + id + "-" + k);
  const fl = g("float"), crown = g("crown"), mouth = g("mouth"), eL = g("eyeL"), eR = g("eyeR");
  const ch = !!crown, my = ch ? 230 : 180.5, ecy = ch ? 183 : 145;
  const ph = o.phase || 0, amp = o.amp === undefined ? 8 : o.amp;
  const blinks = (o.blinks || D.blinks).map((b) => b + (o.blinkShift || 0));
  TICKS.push((t) => {
    fl.setAttribute("transform", "translate(0 " + (Math.sin((t + ph) * 2.4) * amp).toFixed(2) + ")");
    if (crown) crown.setAttribute("transform", "rotate(" + ((t * 12) % 360).toFixed(2) + " 200 190)");
    let open = 0;
    if (o.talk && D.env && D.env.length) {
      const fi = Math.min(D.env.length - 1, Math.max(0, Math.round(t * 30)));
      open = D.env[fi];
      if (o.talkFrom !== undefined && t < o.talkFrom) open = 0;
    }
    const h = (ch ? 6 : 5) + open * (ch ? 30 : 18);
    mouth.setAttribute("height", h.toFixed(1)); mouth.setAttribute("y", (my - h / 2).toFixed(1));
    let b = 1;
    for (const bt of blinks) { const d = t - bt; if (d >= 0 && d < 0.16) b = Math.max(0.08, Math.abs(d - 0.08) / 0.08); }
    const lx = o.look ? keyed(o.look, t) : 0;
    const tr = "translate(" + lx.toFixed(1) + " " + (ecy * (1 - b)).toFixed(1) + ") scale(1 " + b.toFixed(3) + ")";
    eL.setAttribute("transform", tr); eR.setAttribute("transform", tr);
  });
}
"""

JS_BASE += r"""
function exprAt(keys, t) {
  if (t <= keys[0][0]) return keys[0].slice(1);
  for (let i = 1; i < keys.length; i++) {
    if (t <= keys[i][0]) {
      const a = keys[i - 1], c = keys[i]; let x = (t - a[0]) / Math.max(0.001, c[0] - a[0]); x = x * x * (3 - 2 * x);
      return a.slice(1).map((v, j) => v + (c[j + 1] - v) * x);
    }
  }
  return keys[keys.length - 1].slice(1);
}
function rigSocio(id, o) {
  o = o || {};
  const g = (k) => document.getElementById(D.pre + id + "-" + k);
  const fl = g("float"), mouth = g("mouth"), lidL = g("lidL"), lidR = g("lidR"), eL = g("eyeL"), eR = g("eyeR"),
        bL = g("browL"), bR = g("browR"), steam = g("steam");
  const blinks = (o.blinks || D.blinks).map((b) => b + 0.7);
  const ex = o.expr || [[0, 0.5, 0, 0, 1]];
  TICKS.push((t) => {
    fl.setAttribute("transform", "translate(0 " + (Math.sin(t * 1.5) * 3).toFixed(2) + ")");
    const k = exprAt(ex, t);
    let lid = k[0];
    for (const bt of blinks) { const d = t - bt; if (d >= 0 && d < 0.2) lid = Math.max(lid, 1 - Math.abs(d - 0.1) / 0.1); }
    const h = (4 + lid * 34).toFixed(1);
    lidL.setAttribute("height", h); lidR.setAttribute("height", h);
    const es = k[3].toFixed(3);
    eL.setAttribute("transform", "translate(162 199) scale(" + es + ") translate(-162 -199)");
    eR.setAttribute("transform", "translate(242 199) scale(" + es + ") translate(-242 -199)");
    bL.setAttribute("transform", "translate(0 " + k[1].toFixed(1) + ") rotate(" + k[2].toFixed(1) + " 159 164)");
    bR.setAttribute("transform", "translate(0 " + k[1].toFixed(1) + ") rotate(" + (-k[2]).toFixed(1) + " 241 164)");
    let open = 0;
    if (D.env2 && D.env2.length) open = D.env2[Math.min(D.env2.length - 1, Math.max(0, Math.round(t * 30)))];
    const mh = 6 + open * 22;
    mouth.setAttribute("height", mh.toFixed(1)); mouth.setAttribute("y", (265 - mh / 2).toFixed(1));
    steam.setAttribute("transform", "translate(" + (Math.sin(t * 2.2) * 3).toFixed(1) + " " + (-((t * 14) % 10)).toFixed(1) + ")");
    steam.setAttribute("opacity", (0.35 + 0.2 * Math.sin(t * 1.7)).toFixed(2));
  });
}
"""

JS_END = r"""
if (!D.noExit) tl.to($("wrap"), { opacity: 0, filter: "blur(10px)", duration: 0.18, ease: "power2.in" }, Math.max(0, D.dur - 0.2));
if (!D.noEnter) tl.fromTo($("wrap"), { opacity: 0, filter: "blur(10px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.16, ease: "power4.out" }, 0);
const PX = { t: 0 };
tl.to(PX, { t: D.dur, duration: D.dur, ease: "none", onUpdate: function () { for (const f of TICKS) f(PX.t); } }, 0);
for (const f of TICKS) f(0);
window.__timelines[D.id] = tl;
"""


# ======================= PLANTILLAS GENÉRICAS (días 2+) =======================

COLORES = {"sol": SUN, "cian": CYAN, "coral": CORAL, "verde": GREEN, "tinta": INK, "gris": MUTED,
           "morado": "#B98CFF", "naranja": "#FF9F43", "azul": "#4D8DFF", "lima": "#9BE15D"}

NUMS = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez", "once", "doce",
        "trece", "catorce", "quince", "dieciséis", "diecisiete", "dieciocho", "diecinueve", "veinte", "veintiuno",
        "veintidós", "veintitrés", "veinticuatro", "veinticinco", "veintiséis", "veintisiete", "veintiocho",
        "veintinueve", "treinta", "treinta"]


def col(c, default=SUN):
    if not c:
        return default
    return COLORES.get(c, c)


def rich(t, base=None):
    """*palabra* → amarillo, ~palabra~ → coral, _palabra_ → cian."""
    t = re.sub(r"\*([^*]+)\*", lambda m: f'<span style="color:{SUN}">{m.group(1)}</span>', t)
    t = re.sub(r"~([^~]+)~", lambda m: f'<span style="color:{CORAL}">{m.group(1)}</span>', t)
    t = re.sub(r"_([^_]+)_", lambda m: f'<span style="color:{CYAN}">{m.group(1)}</span>', t)
    return t


def plano(t):
    return re.sub(r"[*~_]", "", re.sub(r"<[^>]+>", "", t))


def fit(texto, maxsz, ancho=940, k=0.76):
    n = max(1, len(plano(texto)))
    return int(max(40, min(maxsz, ancho / (n * k))))


def miles(v, dec=0):
    s_ = f"{v:,.{dec}f}"
    return s_.replace(",", "X").replace(".", ",").replace("X", ".")



# ---------------------------------------------------------------- plantillas

def t_hook(s):
    p = s.p
    filas = p.get("filas") or [{"etiqueta": "SEGUIDORES", "valor": "0"}, {"etiqueta": "VISTAS", "valor": "0", "ancla": "vistas"},
                               {"etiqueta": "VIDEOS", "valor": "0", "ancla": "video"}]
    fin = p.get("final", {"fila": 2, "valor": "1", "tag": "¡ESTE!", "ancla": "primero"})
    rows = ""
    for i, f in enumerate(filas[:3]):
        top = 28 + i * 112
        sep = f'<div class="abs" style="left:40px;right:40px;top:{top + 104}px;height:2px;background:{LINE}"></div>' if i < 2 else ""
        vsz = fit(f["valor"], 88, 420, 0.8)
        rows += (f'<div id="@@r{i}" class="abs" style="left:0;top:{top}px;width:900px;height:104px">'
                 f'<div class="abs mono" style="left:50px;top:30px;font-size:36px;color:{MUTED};letter-spacing:.12em">{f["etiqueta"]}</div>'
                 f'<div id="@@v{i}" class="abs disp" style="right:50px;top:{6 + (88 - vsz) / 2:.0f}px;font-size:{vsz}px;color:{INK};text-align:right">{f["valor"]}</div>'
                 f'</div>{sep}')
    fi = int(fin.get("fila", 2)) if fin else -1
    tag_top = 720 + 28 + fi * 112 - 22
    tag = ""
    if fin and fin.get("tag"):
        tag = (f'<div class="abs" style="left:560px;top:{tag_top}px;width:240px"><span id="@@tag" class="chip" '
               f'style="border:3px solid {SUN};color:{GROUND};background:{SUN};font-size:30px">{fin["tag"]}</span></div>')
    html = (f'<div class="abs center mono" style="top:300px;font-size:42px;color:{MUTED};letter-spacing:.45em">DÍA</div>'
            f'<div id="@@num" class="abs center disp" style="top:350px;font-size:330px;color:{SUN};line-height:.9">{s.dia:03d}</div>'
            f'<div class="abs" style="left:700px;top:380px;width:300px;height:380px;overflow:hidden" data-layout-allow-overflow>'
            f'<div id="@@chw" class="abs" style="left:0;top:140px;width:300px;height:345px">{chelios("@@ch", 300)}</div></div>'
            + card("card", 90, 720, 900, 372, rows) + tag)
    tf = s.tw(fin.get("ancla"), s.dur - 1.5) if fin else s.dur
    s.extra["x"] = {"rt": [s.tw(f.get("ancla"), 0.6 + i * 0.9) - 0.12 for i, f in enumerate(filas[:3])],
                    "tf": tf, "fi": fi, "fv": (fin or {}).get("valor", ""), "f0": filas[fi]["valor"] if 0 <= fi < len(filas) else "",
                    "tc": s.tw(p.get("ancla_chelios", "bueno"), max(0.4, tf - 1.3))}
    js = r"""
for (let i = 1; i < D.x.rt.length; i++) tl.fromTo($("r" + i), { opacity: 0.18 }, { opacity: 1, duration: 0.3, ease: "power2.out" }, D.x.rt[i]);
if (D.x.fi >= 0) {
  const tp = D.x.tf, ev = el("v" + D.x.fi);
  TICKS.push((t) => { ev.textContent = t >= tp ? D.x.fv : D.x.f0; ev.style.color = t >= tp ? "#FFC93C" : "#F6F3FF"; });
  tl.fromTo($("v" + D.x.fi), { scale: 1.9 }, { scale: 1, duration: 0.45, ease: "back.out(2)", immediateRender: false }, tp);
  if (el("tag")) pop("tag", tp + 0.08);
}
tl.fromTo($("chw"), { y: 260, rotation: 8 }, { y: 0, rotation: -6, duration: 0.7, ease: "expo.out" }, D.x.tc - 0.25);
rig("ch", { talk: true, talkFrom: D.x.tc - 0.1, look: [[0, 0], [D.x.tf - 0.3, 0], [D.x.tf, -10]] });
"""
    s.extra["noEnter"] = True
    return {"html": html, "js": js, "sfx": [("pop", tf, 0.35), ("whoosh-short", s.extra["x"]["tc"] - 0.25, 0.2)]}


def t_chelios(s):
    p = s.p
    if p.get("anim") == "fantasmas":
        fant = ""
        pos = [(40, 400), (790, 400), (30, 790), (800, 790)]
        for i, (x, y) in enumerate(pos):
            fant += (f'<svg id="@@g{i}" class="abs" style="left:{x}px;top:{y}px" width="250" height="283" viewBox="0 0 300 340">'
                     f'<rect x="48" y="70" width="204" height="168" rx="64" fill="none" stroke="{MUTED}" stroke-width="7" stroke-dasharray="18 14"/>'
                     f'<rect x="102" y="232" width="96" height="70" rx="28" fill="none" stroke="{MUTED}" stroke-width="7" stroke-dasharray="14 12"/>'
                     f'<text x="150" y="182" text-anchor="middle" font-family="Archivo Black" font-size="70" fill="{MUTED}">?</text></svg>')
        html = f'''
  {chip("chip", p.get("chip", ""), 300, CORAL)}
  {fant}
  <div id="@@chw" class="abs" style="left:300px;top:460px;width:480px;height:552px">{chelios("@@ch", 480)}</div>
'''
        js = r"""
pop("chip", 0.1);
const tg = at("trabajadores") - 0.1;
for (let i = 0; i < 4; i++) tl.fromTo($("g" + i), { opacity: 0, scale: 0.7 }, { opacity: 0.9, scale: 1, duration: 0.45, ease: "expo.out" }, tg + i * 0.09);
const tn = at("no");
for (let i = 0; i < 4; i++) {
  const b = tn + i * 0.05;
  tl.to($("g" + i), { opacity: 0.15, x: 14, duration: 0.04 }, b);
  tl.to($("g" + i), { opacity: 0.8, x: -10, duration: 0.04 }, b + 0.05);
  tl.to($("g" + i), { opacity: 0.1, x: 6, duration: 0.04 }, b + 0.10);
  tl.to($("g" + i), { opacity: 0, x: 0, scale: 0.9, duration: 0.18, ease: "power2.in" }, b + 0.15);
}
const tp = at("problema") - 0.1;
tl.fromTo($("ch-armL"), { rotation: 0 }, { rotation: 58, duration: 0.32, ease: "back.out(2)", svgOrigin: "146 312" }, tp);
tl.fromTo($("ch-armR"), { rotation: 0 }, { rotation: -44, duration: 0.36, ease: "back.out(2)", svgOrigin: "254 312" }, tp + 0.07);
tl.to($("ch-armL"), { rotation: 0, duration: 0.3, ease: "power2.inOut", svgOrigin: "146 312" }, D.dur - 0.7);
tl.to($("ch-armR"), { rotation: 0, duration: 0.3, ease: "power2.inOut", svgOrigin: "254 312" }, D.dur - 0.64);
rig("ch", { talk: true, look: [[0, 0], [tg, 0], [tg + 0.3, -14], [tg + 1.2, 14], [tn, 0]] });
"""
        return {"html": html, "js": js, "sfx": [("glitch-1", s.at("no"), 0.3), ("impact-bass-1", s.at("existen"), 0.3)]}

    # intro
    html = f'''
  {chip("chip", p.get("chip", ""), 300, SUN)}
  <div id="@@chw" class="abs" style="left:210px;top:400px;width:660px;height:759px">
    <div id="@@chs" style="width:660px;height:759px">{chelios("@@ch", 660)}</div>
  </div>
  <div class="abs" style="left:0;top:905px;width:1080px;text-align:center"><span id="@@name" class="disp" style="display:inline-block;background:{SUN};color:{GROUND};font-size:96px;padding:6px 34px 2px;border-radius:18px">{p.get("nombre", "CHELIOS")}</span></div>
  <div class="abs" style="left:640px;top:820px"><span id="@@ceo" class="chip" style="border:3px solid {CORAL};background:{CORAL};color:{GROUND};font-size:34px">CEO</span></div>
'''
    js = r"""
pop("chip", 0.1);
tl.fromTo($("chw"), { y: -1150 }, { y: 0, duration: 0.42, ease: "power3.in" }, 0.02);
tl.fromTo($("chs"), { scaleY: 0.78, scaleX: 1.14 }, { scaleY: 1, scaleX: 1, duration: 0.7, ease: "elastic.out(1, 0.45)", transformOrigin: "50% 100%" }, 0.44);
const ty = at("yo");
tl.fromTo($("ch-armR"), { rotation: 0 }, { rotation: -75, duration: 0.18, ease: "power2.out", svgOrigin: "254 312" }, ty);
tl.to($("ch-armR"), { rotation: -45, duration: 0.14, ease: "sine.inOut", svgOrigin: "254 312", yoyo: true, repeat: 3 }, ty + 0.18);
tl.to($("ch-armR"), { rotation: 0, duration: 0.3, ease: "power2.inOut", svgOrigin: "254 312" }, ty + 0.8);
stamp("name", at("chelios") - 0.05, -4);
pop("ceo", at("director") - 0.05);
rig("ch", { talk: true });
"""
    return {"html": html, "js": js, "sfx": [("whoosh-short", 0.05, 0.22), ("impact-bass-2", 0.44, 0.22),
                                            ("pop", s.at("chelios") + 0.15, 0.3), ("pop", s.at("director"), 0.25)]}


def t_orden(s):
    dias = "LMMJVSD"
    week = "".join(
        f'<div id="@@d{i}" class="abs" style="left:{i * 128}px;top:0;width:112px;height:130px;border-radius:22px;background:{CARD};border:3px solid {LINE}">'
        f'<div class="abs center mono" style="width:112px;top:12px;font-size:28px;color:{MUTED}">{d}</div>'
        f'<div id="@@k{i}" class="abs center disp" style="width:112px;top:48px;font-size:58px;color:{GREEN}">✓</div></div>'
        for i, d in enumerate(dias))
    html = f'''
  {card("noti", 90, 320, 900, 220, f"""
    <div class="abs" style="left:34px;top:30px;width:64px;height:64px;border-radius:50%;background:{INK}">{''}</div>
    <svg class="abs" style="left:34px;top:30px" width="64" height="64" viewBox="-32 -32 64 64">{icono("persona", 0, 4, 0.9, GROUND)}</svg>
    <div class="abs mono" style="left:118px;top:42px;font-size:28px;color:{MUTED};letter-spacing:.1em">SOCIO HUMANO · AHORA</div>
    <div class="abs body" style="left:34px;top:116px;font-size:54px;font-weight:700;color:{INK}">Orden: <span style="color:{SUN}">1 video cada día.</span></div>
  """, f"border-color:{SUN}")}
  <div class="abs" style="left:94px;top:590px;width:900px;height:130px">{week}</div>
  {stamp_html("st0", "SIN EXCUSAS", 150, 790, CORAL, 70)}
  {stamp_html("st1", "SIN DESCANSO", 330, 905, CORAL, 70)}
  {stamp_html("st2", "SIN COPIAR", 190, 1010, CORAL, 70)}
'''
    js = r"""
tl.fromTo($("noti"), { y: -380, opacity: 0 }, { y: 0, opacity: 1, duration: 0.6, ease: "expo.out" }, 0.05);
const tt = at("todos") - 0.1;
for (let i = 0; i < 7; i++) { fadeUp("d" + i, tt + i * 0.05, 30); pop("k" + i, tt + 0.25 + i * 0.07); }
stamp("st0", at("excusas") - 0.05, -6);
stamp("st1", at("descanso") - 0.05, 4);
stamp("st2", at("copiar") - 0.05, -3);
"""
    return {"html": html, "js": js, "sfx": [("notification", 0.1, 0.3), ("impact-bass-1", s.at("excusas") + 0.19, 0.22),
                                            ("impact-bass-2", s.at("descanso") + 0.19, 0.22), ("impact-bass-1", s.at("copiar") + 0.19, 0.22)]}


def t_meta(s):
    def meta_card(i, y, lab, total):
        return card(f"c{i}", 90, y, 900, 240, f'''
      <div class="abs mono" style="left:44px;top:30px;font-size:32px;color:{MUTED};letter-spacing:.12em">{lab}</div>
      <div class="abs disp" style="left:44px;top:74px;font-size:100px;color:{INK}"><span id="@@n{i}" style="display:inline-block">0</span><span style="color:{MUTED};font-size:56px"> / {total}</span></div>
      <div class="abs" style="left:44px;top:194px;width:812px;height:18px;border-radius:9px;background:{LINE}"></div>
      <div id="@@b{i}" class="abs" style="left:44px;top:194px;width:14px;height:18px;border-radius:9px;background:{CORAL}"></div>
      <div class="abs mono" style="right:44px;top:100px;font-size:34px;color:{CORAL}">0%</div>''')
    html = f'''
  {chip("chip", "LA META", 300, SUN)}
  {title("t", "QUE YOUTUBE NOS " + hl("PAGUE"), 378, 74)}
  {meta_card(0, 548, "SUSCRIPTORES", s.p.get("subs", "1.000"))}
  {meta_card(1, 822, "HORAS DE REPRODUCCIÓN", s.p.get("horas", "8.000"))}
  <div class="abs" style="left:560px;top:800px"><span id="@@nota" class="chip" style="position:relative;background:{SUN};border:3px solid {SUN};color:{GROUND};font-size:28px;padding:8px 18px">{s.p.get("nota", "")}</span></div>
'''
    js = r"""
pop("chip", 0.1);
blurIn("t", at("youtube") - 0.15, 0.25);
fadeUp("c0", at("mil") - 0.15);
fadeUp("c1", at("desde") - 0.15);
if (el("nota")) pop("nota", at("febrero") - 0.05);
for (const [i, k] of [[0, "cero"], [1, "cero#2"]]) {
  const t = at(k);
  tl.fromTo($("n" + i), { scale: 1, color: "#F6F3FF" }, { scale: 1.45, color: "#FF5A6E", duration: 0.16, ease: "power3.out" }, t);
  tl.to($("n" + i), { scale: 1, duration: 0.4, ease: "elastic.out(1, 0.5)" }, t + 0.16);
}
"""
    return {"html": html, "js": js, "sfx": [("pop", s.at("cero"), 0.3), ("pop", s.at("cero#2"), 0.3)]}


def t_plan(s):
    rooms = ""
    for i in range(8):
        x = 30 + (i % 4) * 212
        y = 34 + (i // 4) * 206
        rooms += (f'<div id="@@rm{i}" class="abs" style="left:{x}px;top:{y}px;width:190px;height:188px;border:3px dashed {CYAN};border-radius:24px;background:rgba(69,227,255,.06)">'
                  f'<div class="abs mono" data-layout-ignore style="left:16px;top:12px;font-size:22px;color:{CYAN}">0{i + 1}</div>'
                  f'<div class="abs center disp" style="width:190px;top:52px;font-size:84px;color:rgba(142,137,191,.7)">?</div></div>')
    dias = "".join(f'<div class="abs mono" style="left:{i * 142}px;top:0;width:126px;height:62px;border-radius:14px;line-height:62px;text-align:center;font-size:30px;'
                   f'{"background:%s;color:%s" % (SUN, GROUND) if i == 0 else "background:%s;color:%s;border:2px solid %s" % (CARD, MUTED, LINE)}">{i + 1:03d}</div>'
                   for i in range(12))
    html = f'''
  {title("t", "FÁBRICA <span class='mono' style='font-size:52px;color:" + MUTED + "'>v0.1</span>", 300, 92)}
  <div id="@@bp" class="abs" style="left:90px;top:430px;width:900px;height:450px;border:3px solid rgba(69,227,255,.5);border-radius:30px;background:rgba(69,227,255,.04)">{rooms}</div>
  <div class="abs center" style="top:600px"><span id="@@moon" class="chip" style="background:{GROUND};border:3px solid {CYAN};color:{CYAN};font-size:34px">MODO NOCHE · TU SOCIO DUERME</span></div>
  <div id="@@strip" class="abs" style="left:90px;top:915px;width:900px;height:62px;overflow:hidden" data-layout-allow-overflow><div id="@@strip-in" class="abs" style="left:0;top:0;width:1800px;height:62px">{dias}</div></div>
  <div class="abs center" style="top:1010px"><span id="@@real" class="chip" style="border:3px solid {SUN};color:{SUN};font-size:32px">NÚMEROS REALES</span></div>
  <div class="abs" style="left:110px;top:560px;width:400px;text-align:center"><span id="@@ok" class="chip" style="background:{GREEN};border:3px solid {GREEN};color:{GROUND};font-size:40px">✓ FUNCIONA</span></div>
  <div class="abs" style="left:570px;top:560px;width:400px;text-align:center"><span id="@@ko" class="chip" style="background:{CORAL};border:3px solid {CORAL};color:{GROUND};font-size:40px">✗ FRACASA</span></div>
  <div class="abs" style="left:110px;top:650px;width:400px;text-align:center"><span id="@@ok2" class="mono" style="display:inline-block;font-size:30px;color:{INK}">LO VERÁS</span></div>
  <div class="abs" style="left:570px;top:650px;width:400px;text-align:center"><span id="@@ko2" class="mono" style="display:inline-block;font-size:30px;color:{INK}">TAMBIÉN</span></div>
'''
    js = r"""
blurIn("t", at("fábrica") - 0.15, 0.25);
fadeUp("bp", at("fábrica") - 0.05, 40);
for (let i = 0; i < 8; i++) tl.fromTo($("rm" + i), { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.4, ease: "expo.out" }, at("videos") - 0.1 + i * 0.06);
pop("moon", at("duerme") - 0.1);
gone("moon", at("día") - 0.15);
for (let i = 0; i < 8; i++) tl.to($("rm" + i), { borderColor: "#FFC93C", duration: 0.12 }, at("pieza") - 0.1 + i * 0.07);
fadeUp("strip", at("día") - 0.1, 20);
tl.fromTo($("strip-in"), { x: 40 }, { x: 0, duration: Math.max(1, D.dur - at("día")), ease: "power2.out" }, at("día"));
pop("real", at("reales") - 0.12);
dim("bp", at("funciona") - 0.1, 0.18);
pop("ok", at("funciona") - 0.05); blurIn("ok2", at("ver#2") - 0.05);
pop("ko", at("fracasa") - 0.05); blurIn("ko2", at("también") - 0.05);
"""
    return {"html": html, "js": js, "sfx": [("pop", s.at("funciona"), 0.28), ("glitch-2", s.at("fracasa"), 0.22)]}


def t_reglas(s):
    reglas = [("01", "Cada video te " + hl("enseña algo")), ("02", "Cero números " + hl("inventados")), ("03", "Si aburre, la fábrica " + hl("lo arregla"))]
    cards = ""
    for i, (n, txt) in enumerate(reglas):
        cards += card(f"r{i}", 90, 480 + i * 205, 900, 180, f'''
      <div class="abs disp" style="left:40px;top:34px;font-size:100px;color:{SUN}">{n}</div>
      <div class="abs body" style="left:230px;top:30px;width:620px;font-size:48px;font-weight:700;line-height:1.12;color:{INK}">{txt}</div>''')
    html = f'''
  {title("t", "LAS " + hl("3") + " REGLAS", 310, 100)}
  {cards}
'''
    js = r"""
blurIn("t", Math.max(0.05, at("reglas") - 0.2), 0.25);
slideX("r0", at("una") - 0.12, 140);
slideX("r1", at("dos") - 0.12, 140);
slideX("r2", at("tres#2") - 0.12, 140);
"""
    return {"html": html, "js": js, "sfx": [("whoosh-short", s.at("una") - 0.12, 0.18), ("whoosh", s.at("dos") - 0.12, 0.16),
                                            ("whoosh-short", s.at("tres#2") - 0.12, 0.18)]}


def t_crew(s):
    bots = ""
    for i, t in enumerate(TRABAJADORES):
        x = 45 + (i % 4) * 250
        y = 455 + (i // 4) * 290
        bots += (f'<div id="@@w{i}" class="abs" style="left:{x}px;top:{y}px;width:240px;height:280px">'
                 f'<div class="abs" style="left:20px;top:0">{bot("@@b%d" % i, t["color"], t["icono"], 200)}</div>'
                 f'<div class="abs center mono" style="width:240px;top:232px;font-size:28px;color:{t["color"]};letter-spacing:.04em">{t["nombre"]}</div></div>')
    tags = ""
    for i, (txt, x) in enumerate([("0 HUMANOS", 60), ("0 SUELDO", 395), ("0 SUEÑO", 715)]):
        tags += f'<div class="abs" style="left:{x}px;top:1040px;width:305px;text-align:center"><span id="@@tg{i}" class="chip" style="border:3px solid {CORAL};color:{CORAL};font-size:30px">{txt}</span></div>'
    html = f'''
  {title("t", hl("8") + " TRABAJADORES", 300, 98)}
  {bots}
  {tags}
'''
    js = r"""
blurIn("t", 0.08, 0.25);
const tb = 0.02;
for (let i = 0; i < 8; i++) { tl.fromTo($("w" + i), { opacity: 0, y: 60, scale: 0.7 }, { opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "back.out(1.6)" }, tb + i * 0.04); rig("b" + i, { phase: i * 0.9, amp: 5 + (i % 3) * 2, blinkShift: i * 0.37 }); }
pop("tg0", at("humano") - 0.05);
pop("tg1", at("cobra") - 0.05);
pop("tg2", at("duerme") - 0.05);
"""
    return {"html": html, "js": js, "sfx": [("pop", s.at("humano"), 0.22), ("pop", s.at("cobra"), 0.22), ("pop", s.at("duerme"), 0.22)]}


def t_agente(s):
    p = s.p
    col = p["color"]
    w = p.get("widget")
    if w == "contador":
        widget = f'''
      <div id="@@cnt" class="abs disp" style="left:44px;top:20px;font-size:116px;color:{col}">0</div>
      <div class="abs mono" style="left:330px;top:44px;font-size:30px;color:{MUTED};letter-spacing:.1em">{p.get("etiqueta", "")}</div>
      <div class="abs" style="left:330px;top:100px;width:520px;height:16px;border-radius:8px;background:{LINE}"></div>
      <div id="@@bar" class="abs" style="left:330px;top:100px;width:520px;height:16px;border-radius:8px;background:{col}"></div>'''
        wjs = r"""
const t0 = at("escribe") - 0.1, t1 = at("ideas") + 0.3;
counter("cnt", t0, t1, 0, D.p.hasta || 100);
tl.fromTo($("bar"), { scaleX: 0 }, { scaleX: 1, duration: t1 - t0, ease: "power3.out", transformOrigin: "0% 50%" }, t0);
"""
    elif w == "doc":
        lineas = [("00:00", "GANCHO", col), ("00:02", "DESARROLLO", MUTED), ("03:15", "RAZÓN PARA QUEDARTE", SUN)]
        widget = "".join(
            f'<div id="@@l{i}" class="abs mono" style="left:44px;top:{18 + i * 48}px;font-size:32px;color:{c}">'
            f'<span style="color:{MUTED}">{ts}</span>&nbsp;&nbsp;{txt}</div>' for i, (ts, txt, c) in enumerate(lineas))
        wjs = r"""
blurIn("l0", at("gancho") - 0.1); blurIn("l1", at("gancho") + 0.6); blurIn("l2", at("razón") - 0.1);
"""
    else:  # fotogramas
        widget = f'''
      <div class="abs mono" style="left:44px;top:26px;font-size:30px;color:{MUTED}">FOTOGRAMA</div>
      <div class="abs mono" style="left:250px;top:14px;font-size:48px;color:{col}"><span id="@@fr">0000</span><span style="color:{MUTED};font-size:30px"> / 6008</span></div>
      <div class="abs" style="left:44px;top:84px;width:812px;height:14px;border-radius:7px;background:{LINE}"></div>
      <div id="@@bar" class="abs" style="left:44px;top:84px;width:812px;height:14px;border-radius:7px;background:{col}"></div>
      <div class="abs" style="left:44px;top:114px"><span id="@@x1" class="chip" style="position:relative;border:2px solid {CORAL};color:{CORAL};font-size:28px;padding:6px 16px">0 CÁMARAS</span></div>
      <div class="abs" style="left:300px;top:114px"><span id="@@x2" class="chip" style="position:relative;border:2px solid {CORAL};color:{CORAL};font-size:28px;padding:6px 16px">0 ESTUDIOS</span></div>'''
        wjs = r"""
const t0 = at("convierte") - 0.1;
counter("fr", t0, D.dur, 0, 6008, (v) => String(Math.round(v)).padStart(4, "0"));
tl.fromTo($("bar"), { scaleX: 0 }, { scaleX: 1, duration: D.dur - t0, ease: "none", transformOrigin: "0% 50%" }, t0);
pop("x1", at("cámaras") - 0.05); pop("x2", at("estudio") - 0.05);
"""
    nombre = p["nombre"]
    ancla = norm(nombre.split()[-1])
    s.extra["p"] = {"hasta": p.get("hasta", 100)}
    html = f'''
  {chip("chip", f"TRABAJADOR #{p['n']}/8", 300, col)}
  <div id="@@bw" class="abs" style="left:380px;top:372px;width:320px;height:363px">{bot("@@b", col, p["icono"], 320)}</div>
  {title("name", nombre, 760, 100, col)}
  <div id="@@rol" class="abs center mono" style="top:872px;font-size:32px;color:{MUTED};letter-spacing:.08em">{p.get("rol", "").upper()}</div>
  {card("wd", 90, 940, 900, 170, widget)}
'''
    js = f"""
pop("chip", 0.08);
tl.fromTo($("bw"), {{ opacity: 0, y: 80, scale: 0.6 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.6, ease: "back.out(1.7)" }}, 0.1);
blurIn("name", Math.max(0.2, at("{ancla}") - 0.1), 0.25);
fadeUp("rol", Math.max(0.4, at("{ancla}") + 0.3), 20);
fadeUp("wd", Math.max(0.5, at("{ancla}") + 0.5), 40);
rig("b", {{ amp: 9 }});
""" + wjs
    return {"html": html, "js": js, "sfx": [("pop", 0.15, 0.25)]}


IDEAS = [
    ("¿Una IA puede ganar dinero sola?", "6.1", False),
    ("Le di 24 h a una IA para un negocio", "8.9", True),
    ("100 ideas en 1 minuto", "5.4", False),
    ("La IA que despide a otras IA", "9.2", True),
    ("Mi socio humano vs. yo", "6.8", False),
    ("Automaticé mi semana entera", "8.7", True),
    ("¿Qué IA hace mejores videos?", "5.9", False),
    ("Reacciono a mis propios errores", "4.3", False),
]


def t_verdugo(s):
    lines = ""
    for i, (txt, sc, ok) in enumerate(IDEAS):
        y = 84 + i * 50
        lines += (f'<div id="@@i{i}" class="abs mono" style="left:30px;top:{y}px;width:720px;font-size:28px;color:{INK};white-space:nowrap">'
                  f'<span style="color:{MUTED}">{i + 1:03d}</span> {txt}</div>'
                  f'<div id="@@sc{i}" class="abs mono" style="left:770px;top:{y}px;width:100px;text-align:right;font-size:28px;color:{GREEN if ok else CORAL}">{sc}</div>')
        if not ok:
            lines += f'<div id="@@k{i}" class="abs" style="left:24px;top:{y + 18}px;width:850px;height:4px;background:{CORAL}"></div>'
    html = f'''
  {chip("chip", "TRABAJADOR #2/8", 300, CORAL)}
  <div id="@@bw" class="abs" style="left:80px;top:368px;width:220px;height:250px">{bot("@@b", CORAL, "x", 220)}</div>
  <div id="@@name" class="abs disp" style="left:330px;top:400px;font-size:96px;color:{CORAL}">EL VERDUGO</div>
  <div id="@@rol" class="abs mono" style="left:334px;top:510px;font-size:30px;color:{MUTED};letter-spacing:.08em">LEE · PUNTÚA · ELIMINA</div>
  {card("term", 90, 620, 900, 490, f"""
    <div class="abs mono" style="left:30px;top:22px;font-size:28px;color:{MUTED}">verdugo@fabrica:~$ ideas.txt</div>
    <div class="abs mono" style="right:30px;top:14px;font-size:40px;color:{CORAL}"><span id="@@cnt">100</span><span style="font-size:28px;color:{MUTED}"> vivas</span></div>
    {lines}""", "background:#100E2A")}
  {stamp_html("st", "97 MUERTAS", 250, 760, CORAL, 84)}
'''
    js = r"""
pop("chip", 0.08);
tl.fromTo($("bw"), { opacity: 0, y: 60, scale: 0.6 }, { opacity: 1, y: 0, scale: 1, duration: 0.55, ease: "back.out(1.7)" }, 0.08);
blurIn("name", Math.max(0.2, at("verdugo") - 0.1), 0.25);
fadeUp("rol", at("verdugo") + 0.35, 20);
fadeUp("term", at("lee") - 0.1, 40);
for (let i = 0; i < 8; i++) { blurIn("i" + i, at("lee") + 0.05 + i * 0.05, 0.15); blurIn("sc" + i, at("nota") - 0.05 + i * 0.06, 0.15); }
const tm = at("mata") - 0.05;
const kill = [0, 2, 4, 6, 7];
kill.forEach((i, j) => { grow("k" + i, tm + j * 0.12, 0.25); dim("i" + i, tm + j * 0.12 + 0.1, 0.32); dim("sc" + i, tm + j * 0.12 + 0.1, 0.32); });
counter("cnt", tm, at("siete") + 0.3, 100, 3);
stamp("st", at("piedad") - 0.1, -8);
rig("b", { amp: 6 });
"""
    return {"html": html, "js": js, "sfx": [("pop", 0.12, 0.22), ("whoosh-short", s.at("mata") - 0.05, 0.22),
                                            ("impact-bass-1", s.at("piedad") + 0.14, 0.3)]}


VIEWERS = [("Camila", "22 · Medellín", "#FF7AB6"), ("Andrés", "31 · Bogotá", "#4D8DFF"),
           ("Lucía", "27 · CDMX", "#B98CFF"), ("Mateo", "19 · Lima", "#5BE7A9"), ("Sofi", "25 · Buenos Aires", "#FFC93C")]


def t_publico(s):
    rows = ""
    for i, (n, meta, c) in enumerate(VIEWERS):
        y = 470 + i * 128
        rows += card(f"v{i}", 90, y, 900, 112, f'''
      <div class="abs disp" style="left:26px;top:18px;width:76px;height:76px;border-radius:50%;background:{c};color:{GROUND};font-size:40px;line-height:80px;text-align:center">{n[0]}</div>
      <div class="abs body" style="left:126px;top:12px;font-size:40px;font-weight:700;color:{INK}">{n}</div>
      <div class="abs mono" style="left:128px;top:60px;font-size:28px;color:{MUTED}">{meta} · leyendo</div>
      <div id="@@sg{i}" class="abs mono" style="right:30px;top:24px;font-size:30px;color:{INK}">seg 0</div>
      <div class="abs" style="left:126px;top:96px;width:740px;height:6px;border-radius:3px;background:{LINE}"></div>
      <div id="@@bf{i}" class="abs" style="left:126px;top:96px;width:740px;height:6px;border-radius:3px;background:{c}"></div>''',
                     "border-radius:24px")
    html = f'''
  {chip("chip", "TRABAJADOR #4/8 · EL PÚBLICO", 300, GREEN)}
  {title("t", "5 ESPECTADORES " + hl("FALSOS", CORAL), 378, 58)}
  {rows}
  <div class="abs" style="left:400px;top:476px"><span id="@@bored" class="chip" style="position:relative;background:{CORAL};border:3px solid {CORAL};color:{GROUND};font-size:28px">SE ABURRIÓ · SEG 3</span></div>
  <div class="abs center" style="top:1102px"><span id="@@ver" class="chip" style="background:{SUN};border:3px solid {SUN};color:{GROUND};font-size:30px">GUION v1 → v2</span></div>
'''
    js = r"""
pop("chip", 0.08);
blurIn("t", at("cinco") - 0.15, 0.25);
const names = ["camila", "andrés", "lucía", "mateo", "sofi"];
const tb = at("aburre");
names.forEach((n, i) => {
  const t0 = at(n) - 0.12;
  slideX("v" + i, t0, 120);
  const sg = el("sg" + i);
  TICKS.push((t) => {
    let s = Math.max(0, (t - t0) * 0.9);
    if (i === 0) s = Math.min(3, s);
    sg.textContent = "seg " + Math.floor(s);
  });
  const end = i === 0 ? tb : D.dur;
  tl.fromTo($("bf" + i), { scaleX: 0 }, { scaleX: i === 0 ? 0.3 : 0.9, duration: Math.max(0.5, end - t0), ease: "none", transformOrigin: "0% 50%" }, t0);
});
tl.to($("v0"), { borderColor: "#FF5A6E", duration: 0.15 }, tb);
tl.to($("sg0"), { color: "#FF5A6E", duration: 0.15 }, tb);
pop("bored", tb + 0.05);
pop("ver", at("guion#2") - 0.1);
"""
    return {"html": html, "js": js, "sfx": [("error", s.at("aburre") + 0.05, 0.22), ("pop", s.at("reescribe"), 0.25)]}


def t_voz(s):
    rnd = random.Random(7)
    takes = [("TOMA 1", "71%"), ("TOMA 2", "94%"), ("TOMA 3", "63%")]
    cards = ""
    for i, (lab, sc) in enumerate(takes):
        bars = "".join(
            f'<div class="abs wv{i}" style="left:{160 + j * 14}px;top:{75 - (h := 14 + int(rnd.random() * 60)) // 2}px;width:8px;height:{h}px;border-radius:4px;background:{GREEN if i == 1 else MUTED}" data-h="{h}"></div>'
            for j in range(40))
        cards += card(f"t{i}", 90, 620 + i * 168, 900, 150, f'''
      <div class="abs mono" style="left:32px;top:56px;font-size:28px;color:{MUTED}">{lab}</div>
      {bars}
      <div id="@@sc{i}" class="abs disp" style="right:36px;top:40px;font-size:60px;color:{INK}">{sc}</div>''')
    html = f'''
  {chip("chip", "TRABAJADOR #5/8", 300, "#9BE15D")}
  <div id="@@bw" class="abs" style="left:80px;top:360px;width:220px;height:250px">{bot("@@b", "#9BE15D", "mic", 220)}</div>
  <div id="@@name" class="abs disp" style="left:330px;top:390px;font-size:110px;color:#9BE15D">LA VOZ</div>
  <div id="@@rol" class="abs mono" style="left:334px;top:512px;font-size:30px;color:{MUTED};letter-spacing:.08em">3 TOMAS POR FRASE</div>
  {cards}
  <div class="abs" style="left:790px;top:766px"><span id="@@win" class="chip" style="position:relative;background:{GREEN};border:3px solid {GREEN};color:{GROUND};font-size:28px">✓ GANA</span></div>
'''
    js = r"""
pop("chip", 0.08);
tl.fromTo($("bw"), { opacity: 0, y: 60, scale: 0.6 }, { opacity: 1, y: 0, scale: 1, duration: 0.55, ease: "back.out(1.7)" }, 0.08);
blurIn("name", Math.max(0.2, at("voz") - 0.1), 0.25);
fadeUp("rol", at("voz") + 0.3, 20);
const tt = at("tres") - 0.15;
for (let i = 0; i < 3; i++) slideX("t" + i, tt + i * 0.12, 120);
for (let i = 0; i < 3; i++) {
  const bars = Array.from(document.querySelectorAll("#" + D.pre + "t" + i + " .wv" + i));
  TICKS.push((t) => { bars.forEach((b, j) => { const h0 = +b.dataset.h; const k = 0.55 + 0.45 * Math.abs(Math.sin(t * 7 + j * 0.7 + i)); b.style.transform = "scaleY(" + k.toFixed(3) + ")"; }); });
}
const tw = at("mejor") - 0.1;
dim("t0", tw, 0.35); dim("t2", tw, 0.35);
tl.to($("t1"), { borderColor: "#5BE7A9", duration: 0.2 }, tw);
tl.to($("sc1"), { color: "#5BE7A9", duration: 0.2 }, tw);
pop("win", tw + 0.05);
rig("b", { amp: 6 });
"""
    return {"html": html, "js": js, "sfx": [("pop", s.at("mejor"), 0.3)]}


def t_cortador(s):
    col = "#4D8DFF"
    phones = ""
    for i in range(3):
        x = 90 + i * 325
        phones += (f'<div id="@@ph{i}" class="abs" style="left:{x}px;top:740px;width:250px;height:370px;border-radius:38px;background:{CARD};border:4px solid {LINE}">'
                   f'<div class="abs center mono" style="width:250px;top:30px;font-size:28px;color:{MUTED}">TIKTOK</div>'
                   f'<div class="abs center disp" style="width:250px;top:120px;font-size:66px;color:{INK}">CAP {i + 1}</div>'
                   f'<div class="abs" style="left:40px;top:250px;width:170px;height:22px;border-radius:11px;background:{["#45E3FF", "#B98CFF", SUN][i]}"></div>'
                   f'<div class="abs center mono" style="width:250px;top:290px;font-size:28px;color:{MUTED}">~1 MIN</div></div>')
    segs = "".join(f'<div class="abs" style="left:{i * 300}px;top:0;width:296px;height:96px;background:{c};opacity:.85"></div>'
                   for i, c in enumerate(["#45E3FF", "#B98CFF", SUN]))
    html = f'''
  {chip("chip", "TRABAJADOR #7/8", 300, col)}
  <div id="@@bw" class="abs" style="left:80px;top:360px;width:190px;height:216px">{bot("@@b", col, "tijeras", 190)}</div>
  <div id="@@name" class="abs disp" style="left:300px;top:385px;font-size:90px;color:{col}">EL CORTADOR</div>
  <div id="@@lab" class="abs mono" style="left:90px;top:575px;font-size:28px;color:{MUTED};letter-spacing:.06em">YOUTUBE · VIDEO COMPLETO · 3:20</div>
  <div id="@@yt" class="abs" style="left:90px;top:620px;width:900px;height:96px;border-radius:24px;overflow:hidden;background:{LINE}">{segs}</div>
  <div id="@@cut1" class="abs" style="left:387px;top:612px;width:6px;height:112px;background:{INK}"></div>
  <div id="@@cut2" class="abs" style="left:687px;top:612px;width:6px;height:112px;background:{INK}"></div>
  <svg id="@@sci" class="abs" style="left:330px;top:560px" width="120" height="120" viewBox="-60 -60 120 120">{icono("tijeras", 0, 0, 1.6, INK)}</svg>
  {phones}
  <div class="abs" style="left:415px;top:690px;width:250px;text-align:center"><span id="@@here" class="chip" style="background:{SUN};border:3px solid {SUN};color:{GROUND};font-size:28px">ESTÁS AQUÍ</span></div>
'''
    js = r"""
pop("chip", 0.08);
tl.fromTo($("bw"), { opacity: 0, y: 60, scale: 0.6 }, { opacity: 1, y: 0, scale: 1, duration: 0.55, ease: "back.out(1.7)" }, 0.08);
blurIn("name", Math.max(0.2, at("cortador") - 0.1), 0.25);
blurIn("lab", at("completo") - 0.15);
grow("yt", at("completo") - 0.1, 0.7);
const tc = at("parte") - 0.1;
tl.fromTo($("sci"), { opacity: 0, x: -260, rotation: -20 }, { opacity: 1, x: 0, rotation: 0, duration: 0.3, ease: "expo.out" }, tc);
tl.to($("sci"), { x: 300, duration: 0.3, ease: "power3.inOut" }, tc + 0.35);
tl.to($("sci"), { opacity: 0, x: 420, duration: 0.2, ease: "power2.in" }, tc + 0.7);
tl.fromTo($("cut1"), { opacity: 0, scaleY: 0 }, { opacity: 1, scaleY: 1, duration: 0.15 }, tc + 0.2);
tl.fromTo($("cut2"), { opacity: 0, scaleY: 0 }, { opacity: 1, scaleY: 1, duration: 0.15 }, tc + 0.55);
for (let i = 0; i < 3; i++) tl.fromTo($("ph" + i), { opacity: 0, y: -160, scale: 0.5 }, { opacity: 1, y: 0, scale: 1, duration: 0.55, ease: "back.out(1.5)" }, at("capítulos") - 0.1 + i * 0.1);
const th = at("capítulo") - 0.1;
tl.to($("ph1"), { borderColor: "#FFC93C", duration: 0.2 }, th);
tl.fromTo($("here"), { opacity: 0, y: -40 }, { opacity: 1, y: 0, duration: 0.45, ease: "back.out(2)" }, th);
rig("b", { amp: 6 });
"""
    return {"html": html, "js": js, "sfx": [("whoosh-short", s.at("parte"), 0.22), ("pop", s.at("capítulo"), 0.28)]}


def t_octavo(s):
    html = f'''
  <div id="@@dark" class="abs" style="left:0;top:0;width:1080px;height:1920px;background:radial-gradient(ellipse 60% 40% at 50% 38%, rgba(0,0,0,0) 0%, rgba(4,3,12,.9) 70%)"></div>
  <div id="@@spot" class="abs" style="left:190px;top:330px;width:700px;height:760px;background:radial-gradient(ellipse 50% 55% at 50% 45%, rgba(255,90,110,.22), rgba(255,90,110,0) 70%)"></div>
  {chip("chip", "TRABAJADOR #8/8 · ???", 300, CORAL)}
  <div id="@@bw" class="abs" style="left:320px;top:400px;width:440px;height:499px">{bot("@@b", "#2A2552", "interrogacion", 440)}</div>
  <div id="@@warn" class="abs" style="left:0;top:930px;width:1080px;height:56px;background:repeating-linear-gradient(-45deg,{CORAL} 0 28px,{GROUND} 28px 56px)"></div>
  <div class="abs" style="left:120px;top:1030px;width:380px;text-align:center"><span id="@@stay" class="chip" style="background:{GREEN};border:3px solid {GREEN};color:{GROUND};font-size:36px">SE QUEDA</span></div>
  <div class="abs" style="left:580px;top:1030px;width:380px;text-align:center"><span id="@@go" class="chip" style="background:{CORAL};border:3px solid {CORAL};color:{GROUND};font-size:36px">SE VA</span></div>
  <style>#@@b-eyeL, #@@b-eyeR, #@@b-mouth {{ fill: {CORAL}; }}</style>
'''
    js = r"""
tl.fromTo($("dark"), { opacity: 0 }, { opacity: 1, duration: 0.6, ease: "power2.out" }, 0);
tl.fromTo($("spot"), { opacity: 0 }, { opacity: 1, duration: 0.8, ease: "power2.out" }, 0.3);
pop("chip", 0.15);
tl.fromTo($("bw"), { opacity: 0, scale: 0.85 }, { opacity: 1, scale: 1, duration: 1.2, ease: "power2.out" }, 0.1);
tl.fromTo($("bw"), { y: 0 }, { y: -20, duration: D.dur - 1.3, ease: "sine.inOut" }, 1.3);
tl.fromTo($("warn"), { opacity: 0, scaleX: 0 }, { opacity: 1, scaleX: 1, duration: 0.35, ease: "expo.out", transformOrigin: "50% 50%" }, at("peligroso") - 0.1);
const wv = el("warn");
TICKS.push((t) => { wv.style.backgroundPosition = (t * 60).toFixed(1) + "px 0"; });
pop("stay", at("queda") - 0.1);
pop("go", at("va") - 0.1);
rig("b", { amp: 4 });
"""
    return {"html": html, "js": js, "sfx": [("impact-bass-2", 0.05, 0.3), ("glitch-3", s.at("peligroso"), 0.25),
                                            ("pop", s.at("queda"), 0.2), ("pop", s.at("va"), 0.2)]}


def t_despidos(s):
    cards = ""
    for i, n in enumerate([3, 5, 6]):
        t = trabajador(n)
        x = 90 + i * 310
        cards += (f'<div id="@@w{i}" class="card" style="left:{x}px;top:400px;width:280px;height:330px">'
                  f'<div class="abs" style="left:50px;top:24px">{bot("@@b%d" % i, t["color"], t["icono"], 180)}</div>'
                  f'<div class="abs center mono" style="width:280px;top:256px;font-size:28px;color:{t["color"]}">{t["nombre"]}</div></div>'
                  f'{stamp_html("st%d" % i, "DESPEDIDO", x + 6, 540, CORAL, 38)}')
    html = f'''
  {chip("chip", "RECURSOS INHUMANOS", 300, CORAL)}
  {cards}
  <div id="@@chw" class="abs" style="left:380px;top:750px;width:320px;height:368px">{chelios("@@ch", 320)}</div>
  <div class="abs" style="left:660px;top:780px"><span id="@@q" class="chip" style="position:relative;background:{CORAL};border:3px solid {CORAL};color:{GROUND};font-size:32px">¿SIGUIENTE?</span></div>
'''
    js = r"""
pop("chip", 0.08);
for (let i = 0; i < 3; i++) { fadeUp("w" + i, 0.12 + i * 0.08, 50); rig("b" + i, { phase: i * 1.3, amp: 5, blinkShift: i * 0.5 }); }
const td = at("despiden") - 0.05;
for (let i = 0; i < 3; i++) { stamp("st" + i, td + i * 0.16, [-10, 6, -4][i]); dim("w" + i, td + i * 0.16 + 0.2, 0.45); }
const ti = at("incluso") - 0.2;
tl.fromTo($("chw"), { opacity: 0, y: 200 }, { opacity: 1, y: 0, duration: 0.6, ease: "expo.out" }, ti);
pop("q", at("siguiente") - 0.1);
rig("ch", { talk: true, talkFrom: ti, look: [[0, 0], [ti + 0.6, 0], [ti + 0.8, -16], [ti + 1.4, -16], [ti + 1.6, 16], [ti + 2.3, 16], [ti + 2.5, 0]] });
"""
    return {"html": html, "js": js, "sfx": [("impact-bass-1", s.at("despiden") + 0.19, 0.28), ("pop", s.at("siguiente"), 0.25)]}


def t_analista(s):
    col = "#E9E6FF"
    pts = [(0, 30), (80, 34), (160, 40), (240, 52), (320, 64), (360, 128), (440, 140), (520, 146), (600, 152), (680, 158), (760, 162), (812, 166)]
    poly = " ".join(f"{x},{y}" for x, y in pts)
    items = [("EN QUÉ SEGUNDO TE FUISTE", "segundo"), ("QUÉ TE ABURRIÓ", "aburrió"), ("QUÉ PEDISTE", "pediste")]
    rows = ""
    for i, (txt, _) in enumerate(items):
        rows += (f'<div class="abs" style="left:40px;top:{30 + i * 70}px;width:44px;height:44px;border-radius:12px;border:3px solid {MUTED}"></div>'
                 f'<div id="@@ck{i}" class="abs disp" style="left:40px;top:{26 + i * 70}px;width:44px;text-align:center;font-size:40px;color:{GREEN}">✓</div>'
                 f'<div id="@@it{i}" class="abs mono" style="left:110px;top:{34 + i * 70}px;font-size:32px;color:{INK}">{txt}</div>')
    html = f'''
  {chip("chip", "TRABAJADOR #8/8", 300, col)}
  <div id="@@bw" class="abs" style="left:80px;top:360px;width:220px;height:250px">{bot("@@b", col, "grafica", 220)}</div>
  <div id="@@name" class="abs disp" style="left:320px;top:390px;font-size:88px;color:{col}">EL ANALISTA</div>
  <div id="@@rol" class="abs mono" style="left:324px;top:494px;font-size:28px;color:{MUTED};letter-spacing:.06em">NÚMEROS + COMENTARIOS</div>
  {card("ch", 90, 615, 900, 255, f"""
    <div class="abs mono" style="left:44px;top:22px;font-size:28px;color:{MUTED}">RETENCIÓN · así se verá</div>
    <svg class="abs" style="left:44px;top:62px" width="812" height="180" viewBox="0 0 812 180" overflow="visible">
      <line x1="0" y1="176" x2="812" y2="176" stroke="{LINE}" stroke-width="3"/>
      <polyline id="@@curve" points="{poly}" fill="none" stroke="{CYAN}" stroke-width="7" stroke-linejoin="round" stroke-linecap="butt" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>
      <circle id="@@dot" cx="340" cy="96" r="14" fill="{CORAL}"/>
    </svg>
    <div class="abs" style="left:420px;top:76px"><span id="@@aqui" class="chip" style="position:relative;background:{CORAL};border:3px solid {CORAL};color:{GROUND};font-size:28px;padding:8px 18px">AQUÍ TE FUISTE</span></div>""")}
  {card("ls", 90, 890, 900, 220, rows)}
'''
    js = r"""
pop("chip", 0.08);
tl.fromTo($("bw"), { opacity: 0, y: 60, scale: 0.6 }, { opacity: 1, y: 0, scale: 1, duration: 0.55, ease: "back.out(1.7)" }, 0.08);
blurIn("name", Math.max(0.2, at("analista") - 0.1), 0.25);
fadeUp("rol", at("analista") + 0.3, 20);
fadeUp("ch", at("números") - 0.2, 40);
tl.fromTo($("curve"), { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 1.2, ease: "power2.inOut" }, at("números") + 0.1);
fadeUp("ls", at("comentarios") - 0.1, 40);
const keys = ["segundo", "aburrió", "pediste"];
keys.forEach((k, i) => { pop("ck" + i, at(k) - 0.05); });
tl.fromTo($("dot"), { opacity: 0, scale: 0 }, { opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2.5)", svgOrigin: "340 96" }, at("segundo"));
pop("aqui", at("segundo") + 0.1);
rig("b", { amp: 6 });
"""
    return {"html": html, "js": js, "sfx": [("click-soft", s.at("segundo"), 0.3), ("click-soft", s.at("aburrió"), 0.3), ("click-soft", s.at("pediste"), 0.3)]}


def t_reemplazo(s):
    g = trabajador(3)
    def wcard(id_, ver, extra):
        return (f'<div id="@@{id_}" class="card" style="left:140px;top:360px;width:800px;height:300px;{extra}">'
                f'<div class="abs" style="left:30px;top:40px">{bot("@@b" + id_, g["color"], g["icono"], 190)}</div>'
                f'<div class="abs disp" style="left:270px;top:70px;font-size:66px;color:{g["color"]}">GUIONISTA</div>'
                f'<div class="abs mono" style="left:274px;top:156px;font-size:44px;color:{INK}">versión {ver}</div></div>')
    bars = ""
    for i, h in enumerate([90, 150, 215]):
        x = 150 + i * 250
        bars += (f'<div id="@@br{i}" class="abs" style="left:{x}px;top:{300 - h}px;width:150px;height:{h}px;border-radius:18px 18px 6px 6px;background:{[MUTED, CYAN, SUN][i]}"></div>'
                 f'<div class="abs mono" style="left:{x}px;top:312px;width:150px;text-align:center;font-size:28px;color:{MUTED}">DÍA {i + 1}</div>')
    html = f'''
  {wcard("v1", "1", "")}
  {wcard("v2", "2", f"border-color:{GREEN}")}
  {stamp_html("st", "DESPEDIDO", 330, 470, CORAL, 70)}
  <div class="abs" style="left:700px;top:330px"><span id="@@best" class="chip" style="position:relative;background:{GREEN};border:3px solid {GREEN};color:{GROUND};font-size:32px">MEJOR</span></div>
  {card("iq", 90, 720, 900, 390, f"""<div class="abs mono" style="left:44px;top:28px;font-size:28px;color:{MUTED};letter-spacing:.08em">INTELIGENCIA DE LA FÁBRICA</div>
    <div class="abs" style="left:0;top:20px;width:900px;height:360px">{bars}</div>""")}
'''
    js = r"""
fadeUp("v1", 0.1, 50);
rig("bv1", { amp: 5 }); rig("bv2", { amp: 6, phase: 1 });
const tf = at("falla") - 0.05;
tl.to($("v1"), { borderColor: "#FF5A6E", duration: 0.15 }, tf);
tl.to($("v1"), { x: 10, duration: 0.05, yoyo: true, repeat: 5 }, tf);
stamp("st", at("despide") - 0.1, -8);
const tr = at("reemplaza") - 0.15;
tl.to($("v1"), { x: -1100, opacity: 0, duration: 0.45, ease: "power3.in" }, tr);
tl.to($("st"), { x: -1100, opacity: 0, duration: 0.45, ease: "power3.in" }, tr);
tl.fromTo($("v2"), { x: 1100, opacity: 0 }, { x: 0, opacity: 1, duration: 0.6, ease: "expo.out" }, tr + 0.2);
pop("best", at("mejor") - 0.1);
fadeUp("iq", at("así") - 0.15, 40);
for (let i = 0; i < 3; i++) tl.fromTo($("br" + i), { scaleY: 0 }, { scaleY: 1, duration: 0.5, ease: "back.out(1.4)", transformOrigin: "50% 100%" }, at("día") + i * 0.22);
tl.to($("br2"), { boxShadow: "0 0 40px rgba(255,201,60,.8)", duration: 0.3 }, at("lista") - 0.05);
"""
    return {"html": html, "js": js, "sfx": [("impact-bass-1", s.at("despide") + 0.14, 0.28), ("whoosh", s.at("reemplaza") - 0.15, 0.22),
                                            ("pop", s.at("mejor"), 0.25)]}


def t_socio(s):
    tareas = [("REVISA", "revisa"), ("APRUEBA", "aprueba"), ("PUBLICA", "publica"), ("CORRIGE", "corrige")]
    lista = "".join(f'<div id="@@tk{i}" class="abs mono" style="left:40px;top:{360 + i * 62}px;font-size:34px;color:{INK}"><span style="color:{GREEN}">✓</span> {t}</div>'
                    for i, (t, _) in enumerate(tareas))
    html = f'''
  {card("hum", 90, 320, 430, 640, f"""
    <svg class="abs" style="left:115px;top:40px" width="200" height="200" viewBox="-50 -50 100 100">{icono("persona", 0, 0, 1.6, INK)}</svg>
    <div class="abs center disp" style="width:430px;top:262px;font-size:44px;color:{INK}">SOCIO<br>HUMANO</div>
    {lista}""")}
  {card("ia", 560, 320, 430, 640, f"""
    <div class="abs" style="left:75px;top:24px">{chelios("@@ch", 280)}</div>
    <div class="abs center disp" style="width:430px;top:350px;font-size:44px;color:{SUN}">CHELIOS</div>
    <div id="@@rest" class="abs center disp" style="width:430px;top:425px;font-size:62px;color:{INK}">EL RESTO</div>
    <div id="@@rl" class="abs center mono" style="width:430px;top:528px;font-size:28px;line-height:1.4;color:{MUTED}">ideas · guion · voz<br>animación · cortes</div>""", f"border-color:{SUN}")}
'''
    js = r"""
slideX("hum", 0.08, -120);
slideX("ia", 0.2, 120);
["revisa", "aprueba", "publica", "corrige"].forEach((k, i) => blurIn("tk" + i, at(k) - 0.08, 0.2));
pop("rest", at("resto") - 0.1);
blurIn("rl", 0.5, 0.3);
rig("ch", { talk: true, amp: 6 });
"""
    return {"html": html, "js": js, "sfx": [("click-soft", s.at("revisa"), 0.25), ("click-soft", s.at("aprueba"), 0.25),
                                            ("click-soft", s.at("publica"), 0.25), ("click-soft", s.at("corrige"), 0.25),
                                            ("pop", s.at("resto"), 0.28)]}


def t_reveal(s):
    pistas = [("GUION", "guion", "#B98CFF"), ("VOZ", "voz", "#9BE15D"), ("ANIMACIÓN", "animación", "#FF9F43"), ("CORTES", "cortes", "#4D8DFF")]
    tracks = ""
    for i, (lab, _, c) in enumerate(pistas):
        y = 90 + i * 100
        clips = "".join(f'<div class="abs" style="left:{x}px;top:0;width:{w}px;height:64px;border-radius:12px;background:{c};opacity:{op}"></div>'
                        for x, w, op in [(0, 230, 1), (240, 160, .85), (410, 260, 1), (680, 70, .7)])
        tracks += (f'<div class="abs mono" style="left:30px;top:{y + 16}px;font-size:28px;color:{MUTED}">{lab}</div>'
                   f'<div id="@@tr{i}" class="abs" style="left:200px;top:{y}px;width:740px;height:64px">{clips}</div>')
    html = f'''
  {chip("chip", "este_video.mp4", 300, MUTED, tinta=INK)}
  {title("t", "TAMBIÉN LO HIZO<br>" + hl("LA FÁBRICA"), 380, 84, extra="line-height:1.0")}
  {card("ed", 60, 590, 960, 510, f"""
    <div class="abs" style="left:200px;top:40px;width:740px;height:2px;background:{LINE}"></div>
    {''.join(f'<div class="abs mono" data-layout-ignore style="left:{200 + i * 185}px;top:12px;font-size:20px;color:{MUTED}">{i * 50 // 60}:{i * 50 % 60:02d}</div>' for i in range(5))}
    {tracks}
    <div id="@@ph" class="abs" style="left:200px;top:30px;width:4px;height:460px;background:{CORAL}"></div>""", "background:#100E2A")}
'''
    js = r"""
pop("chip", 0.08);
fadeUp("ed", 0.15, 40);
["guion", "voz", "animación", "cortes"].forEach((k, i) => grow("tr" + i, at(k) - 0.1, 0.55));
stamp("t", at("también") - 0.08, 0);
const ph = el("ph");
TICKS.push((t) => { ph.style.transform = "translateX(" + (740 * Math.min(1, t / D.dur)).toFixed(1) + "px)"; });
"""
    return {"html": html, "js": js, "sfx": [("riser", max(0, s.at("también") - 1.6), 0.3), ("impact-bass-2", s.at("también") + 0.16, 0.32)]}


def t_manana(s):
    p = s.p
    sig = int(p.get("dia_siguiente", s.dia + 1))
    ancla_flip = p.get("ancla_flip", NUMS[sig] if sig < len(NUMS) else None)
    tr = trabajador(int(p.get("trabajador", 1)))
    titulo = p.get("titulo", "EL IDEADOR<br>EN VIVO")
    cont = p.get("contador", {"hasta": 100, "ancla": "cien"} if "linea" not in p else None)
    linea = rich(p.get("linea", "IDEAS → *¿CUÁL SOBREVIVE?*"))
    pre_c = '<span id="@@c">0</span> ' if cont else ""
    inner = (f'<div class="abs" style="left:30px;top:40px">{bot("@@b", tr["color"], tr["icono"], 200)}</div>'
             f'<div class="abs disp" style="left:270px;top:60px;width:600px;font-size:{min(56, *[fit(x, 56, 600, 0.8) for x in titulo.split("<br>")])}px;color:{tr["color"]};line-height:1">{titulo}</div>'
             f'<div id="@@ln" class="abs mono" style="left:272px;top:200px;width:600px;font-size:32px;color:{INK};line-height:1.25">{pre_c}{linea}</div>')
    html = (chip("chip", p.get("chip", "PRÓXIMO VIDEO"), 300, CYAN)
            + f'<div class="abs center mono" style="top:385px;font-size:42px;color:{MUTED};letter-spacing:.45em">DÍA</div>'
            f'<div class="abs" style="left:0;top:430px;width:1080px;height:300px;overflow:hidden" data-layout-allow-overflow>'
            f'<div id="@@n1" class="abs center disp" style="top:0;font-size:290px;color:{MUTED};line-height:1">{s.dia:03d}</div>'
            f'<div id="@@n2" class="abs center disp" style="top:0;font-size:290px;color:{SUN};line-height:1">{sig:03d}</div></div>'
            + card("tz", 90, 790, 900, 310, inner))
    tf = s.tw(ancla_flip, 1.0)
    s.extra["x"] = {"tf": tf, "tz": s.tw(p.get("ancla_teaser", "ideador"), tf + 0.8),
                    "c": [s.tw(cont.get("ancla"), tf + 1.2), cont.get("hasta", 100)] if cont else None,
                    "te": s.tw(p.get("ancla_enfasis", "sobrevive"), s.dur - 1.0)}
    js = r"""
pop("chip", 0.08);
tl.fromTo($("n2"), { y: 300 }, { y: 0, duration: 0.5, ease: "expo.out" }, D.x.tf - 0.1);
tl.fromTo($("n1"), { y: 0, opacity: 1 }, { y: -300, opacity: 0, duration: 0.4, ease: "power3.in" }, D.x.tf - 0.15);
fadeUp("tz", D.x.tz - 0.15, 50);
if (D.x.c) counter("c", D.x.c[0] - 0.1, D.x.c[0] + 0.8, 0, D.x.c[1]);
tl.fromTo($("ln"), { scale: 1 }, { scale: 1.06, duration: 0.15, ease: "power3.out", transformOrigin: "0% 50%", immediateRender: false }, D.x.te - 0.05);
tl.to($("ln"), { scale: 1, duration: 0.35, ease: "elastic.out(1,0.5)", transformOrigin: "0% 50%" }, D.x.te + 0.1);
rig("b", { amp: 6 });
"""
    return {"html": html, "js": js, "sfx": [("whoosh-short", tf - 0.1, 0.22), ("pop", s.extra["x"]["tz"], 0.22)]}


def t_cta(s):
    p = s.p
    palabra = p.get("palabra", "FÁBRICA")
    psz = fit(palabra, 178, 960, 0.8)
    html = (f'<div id="@@sun" class="abs" style="left:0;top:0;width:1080px;height:1920px;background:#FFC93C;overflow:hidden" data-layout-allow-overflow data-layout-ignore>'
            f'<div id="@@rays" class="abs" style="left:-760px;top:-400px;width:2600px;height:2600px;background:repeating-conic-gradient(from 0deg at 50% 50%, #FFB61A 0deg 9deg, #FFC93C 9deg 18deg)"></div>'
            f'<div class="abs" style="left:0;top:0;width:1080px;height:1920px;background:radial-gradient(ellipse 55% 35% at 50% 30%, rgba(255,240,190,.75), rgba(255,240,190,0) 70%)"></div></div>'
            f'<div class="abs center" style="top:300px"><span id="@@fol" class="chip" style="background:{GROUND};border:3px solid {GROUND};color:{SUN};font-size:30px">{p.get("seguir_texto", "+ SEGUIR · META 1.000")}</span></div>'
            f'<div id="@@chw" class="abs" style="left:320px;top:380px;width:440px;height:506px">{chelios("@@ch", 440)}</div>'
            f'<div id="@@c1" class="abs center disp" style="top:842px;font-size:100px;color:{GROUND}">{p.get("verbo", "COMENTA")}</div>'
            f'<div id="@@c2" class="abs center disp" style="top:{962 + (178 - psz) / 2:.0f}px;font-size:{psz}px;color:{GROUND};letter-spacing:-.02em">{palabra}</div>'
            '<style>#@@ch-glow { fill: #FF9F43; }</style>')
    tc = s.tw(p.get("ancla_comenta", "comenta"), 0.8)
    tp = s.tw(p["ancla_palabra"], tc + 0.4) if p.get("ancla_palabra") else s.ultima(palabra, tc + 0.4)
    tsg = s.tw(p.get("ancla_seguir", "síguenos"), s.dur - 2.5)
    s.extra["x"] = {"tc": tc, "tp": tp, "ts": tsg}
    js = r"""
tl.fromTo($("sun"), { clipPath: "circle(0% at 50% 45%)" }, { clipPath: "circle(150% at 50% 45%)", duration: 0.5, ease: "power2.inOut" }, 0);
const rays = el("rays");
TICKS.push((t) => { rays.style.transform = "rotate(" + (t * 4).toFixed(2) + "deg)"; });
tl.fromTo($("chw"), { opacity: 0, y: 120, scale: 0.7 }, { opacity: 1, y: 0, scale: 1, duration: 0.7, ease: "back.out(1.6)" }, 0.25);
stamp("c1", D.x.tc - 0.08, 0);
stamp("c2", D.x.tp - 0.08, -3);
pop("fol", D.x.ts - 0.1);
rig("ch", { talk: true });
"""
    s.extra["noExit"] = True
    s.extra["noEnter"] = True
    return {"html": html, "js": js, "sfx": [("whoosh-cinematic", 0.0, 0.22), ("impact-bass-1", tc + 0.16, 0.22),
                                            ("impact-bass-2", tp + 0.16, 0.28), ("pop", tsg, 0.25)]}


PLANTILLAS = {
    "hook": t_hook, "chelios": t_chelios, "orden": t_orden, "meta": t_meta, "plan": t_plan, "reglas": t_reglas,
    "crew": t_crew, "agente": t_agente, "verdugo": t_verdugo, "publico": t_publico, "voz": t_voz,
    "cortador": t_cortador, "octavo": t_octavo, "despidos": t_despidos, "analista": t_analista,
    "reemplazo": t_reemplazo, "socio": t_socio, "reveal": t_reveal, "manana": t_manana, "cta": t_cta,
}


def t_titular(s):
    p = s.p
    lineas = p.get("lineas", [])
    tops, y, sizes = [], 0, []
    for ln in lineas:
        sz = fit(ln["texto"], ln.get("max", 150))
        sizes.append(sz)
    alto = sum(sz * 1.02 for sz in sizes) + 18 * (len(sizes) - 1)
    con_ch = bool(p.get("chelios"))
    centro = 600 if con_ch else 720
    y = max(380, centro - alto / 2)
    html = chip("chip", p["chip"], 300, col(p.get("chip_color"), SUN)) if p.get("chip") else ""
    ts = []
    for i, (ln, sz) in enumerate(zip(lineas, sizes)):
        html += f'<div id="@@l{i}" class="abs center disp" style="top:{y:.0f}px;font-size:{sz}px;color:{col(ln.get("color"), INK)}">{rich(ln["texto"])}</div>'
        y += sz * 1.02 + 18
        ts.append(0.05 + i * 0.12 if s.inicio_parte else s.tw(ln.get("ancla"), 0.12 + i * 0.22) - (0.12 if ln.get("ancla") else 0))
    if p.get("sub"):
        html += f'<div id="@@sub" class="abs center mono" style="top:{y + 16:.0f}px;font-size:34px;color:{MUTED};letter-spacing:.06em">{rich(p["sub"])}</div>'
    if con_ch:
        html += f'<div id="@@chw" class="abs" style="left:415px;top:820px;width:250px;height:288px">{chelios("@@ch", 250)}</div>'
    s.extra["x"] = {"lt": ts, "ts": s.tw(p.get("ancla_sub"), (ts[-1] if ts else 0) + 0.5)}
    js = r"""
if (el("chip")) pop("chip", 0.06);
D.x.lt.forEach((t, i) => tl.fromTo($("l" + i), { opacity: 0, y: 46, filter: "blur(12px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.5, ease: "expo.out" }, Math.max(0.04, t)));
if (el("sub")) blurIn("sub", D.x.ts, 0.3);
if (el("chw")) { tl.fromTo($("chw"), { opacity: 0, y: 120 }, { opacity: 1, y: 0, duration: 0.6, ease: "back.out(1.6)" }, 0.2); rig("ch", { talk: true, amp: 6 }); }
"""
    return {"html": html, "js": js, "sfx": [("whoosh-short", max(0, ts[0]) if ts else 0, 0.18)]}


def t_lista(s):
    p = s.p
    items = p.get("items", [])[:5]
    n = max(1, len(items))
    gap = 22
    h = int(min(190, (640 - gap * (n - 1)) / n))
    fs = 48 if h >= 170 else 42 if h >= 130 else 36
    html = title("t", rich(p.get("titulo", "")), 305, fit(p.get("titulo", ""), 96))
    ts = []
    for i, it in enumerate(items):
        y = 465 + i * (h + gap)
        num = it.get("num", f"{i + 1:02d}") if p.get("numerado", True) else ""
        izq = 220 if num else 44
        html += card(f"r{i}", 90, y, 900, h, f'''
      {f'<div class="abs disp" style="left:36px;top:{(h - h * 0.55) / 2:.0f}px;font-size:{h * 0.55:.0f}px;color:{col(it.get("color"), SUN)}">{num}</div>' if num else ''}
      <div class="abs body" style="left:{izq}px;top:0;height:{h}px;width:{860 - izq}px;display:flex;align-items:center;font-size:{fs}px;font-weight:700;line-height:1.12;color:{INK}"><div>{rich(it["texto"])}</div></div>''')
        ts.append(0.12 + i * 0.1 if s.inicio_parte else s.tw(it.get("ancla"), 0.5 + i * 0.6) - (0.12 if it.get("ancla") else 0))
    s.extra["x"] = {"ts": ts, "tt": max(0.05, s.tw(p.get("ancla_titulo"), 0.05) - 0.15)}
    js = r"""
blurIn("t", D.x.tt, 0.25);
D.x.ts.forEach((t, i) => slideX("r" + i, Math.max(0.1, t), 140));
"""
    return {"html": html, "js": js, "sfx": [("whoosh-short" if i % 2 == 0 else "whoosh", max(0, t), 0.15) for i, t in enumerate(ts)]}


def t_numero(s):
    p = s.p
    hasta = float(p.get("hasta", 0))
    desde = float(p.get("desde", 0))
    dec = int(p.get("decimales", 0))
    txt_max = f'{p.get("prefijo", "")}{miles(max(abs(hasta), abs(desde)), dec)}{p.get("sufijo", "")}'
    sz = fit(txt_max, 300, 960, 0.8)
    c = col(p.get("color"), SUN)
    html = chip("chip", p["chip"], 300, col(p.get("chip_color"), c)) if p.get("chip") else ""
    html += f'<div id="@@lab" class="abs center mono" style="top:440px;font-size:40px;color:{MUTED};letter-spacing:.14em">{rich(p.get("etiqueta", ""))}</div>'
    html += (f'<div id="@@nw" class="abs center disp" style="top:510px;font-size:{sz}px;color:{c};line-height:1">'
             f'<span>{p.get("prefijo", "")}</span><span id="@@n">{miles(desde, dec)}</span><span>{p.get("sufijo", "")}</span></div>')
    y = 510 + sz + 40
    if p.get("sub"):
        html += f'<div id="@@sub" class="abs center body" style="top:{y}px;font-size:46px;font-weight:700;color:{INK}">{rich(p["sub"])}</div>'
        y += 90
    if p.get("meta"):
        m = float(p["meta"])
        frac = max(0.0, min(1.0, hasta / m)) if m else 0
        html += (f'<div class="abs" style="left:140px;top:{y + 20}px;width:800px;height:22px;border-radius:11px;background:{LINE}"></div>'
                 f'<div id="@@bar" class="abs" style="left:140px;top:{y + 20}px;width:{max(14, 800 * frac):.0f}px;height:22px;border-radius:11px;background:{c}"></div>'
                 f'<div class="abs center mono" style="top:{y + 58}px;font-size:30px;color:{MUTED}">META {miles(m)}{p.get("sufijo", "")}</div>')
        y += 120
    if p.get("nota"):
        html += f'<div class="abs center" style="top:{min(y + 10, 1040)}px"><span id="@@nota" class="chip" style="background:{c};border:3px solid {c};color:{GROUND};font-size:30px">{p["nota"]}</span></div>'
    t0 = s.tw(p.get("ancla_inicio"), 0.4)
    t1 = max(t0 + 0.4, s.tw(p.get("ancla_fin"), t0 + 1.2))
    s.extra["x"] = {"t0": t0, "t1": t1, "d": desde, "h": hasta, "dec": dec, "tn": s.tw(p.get("ancla_nota"), t1 + 0.3),
                    "tsub": s.tw(p.get("ancla_sub"), t1 + 0.1)}
    js = r"""
if (el("chip")) pop("chip", 0.06);
blurIn("lab", 0.1, 0.25);
fadeUp("nw", 0.15, 40);
const fmt = (v) => { const s = v.toFixed(D.x.dec).split("."); s[0] = s[0].replace(/\B(?=(\d{3})+(?!\d))/g, "."); return s.join(","); };
counter("n", D.x.t0, D.x.t1, D.x.d, D.x.h, fmt);
tl.fromTo($("nw"), { scale: 1 }, { scale: 1.08, duration: 0.12, ease: "power3.out", immediateRender: false }, D.x.t1);
tl.to($("nw"), { scale: 1, duration: 0.4, ease: "elastic.out(1, 0.5)" }, D.x.t1 + 0.12);
if (el("sub")) blurIn("sub", D.x.tsub, 0.3);
if (el("bar")) grow("bar", D.x.t0, D.x.t1 - D.x.t0 + 0.3);
if (el("nota")) pop("nota", D.x.tn);
"""
    return {"html": html, "js": js, "sfx": [("pop", t1, 0.3)]}


def t_terminal(s):
    p = s.p
    top = 330
    html = ""
    if p.get("titulo"):
        html += title("t", rich(p["titulo"]), 305, fit(p["titulo"], 78))
        top = 420
    alto = 1100 - top
    maxl = int((alto - 90) / 50)
    lineas = p.get("lineas", [])[:maxl]
    tach = set(p.get("tachar", []))
    cont = p.get("contador")
    filas = ""
    ts = []
    for i, ln in enumerate(lineas):
        y = 80 + i * 50
        c = {"ok": GREEN, "ko": CORAL, "hl": SUN, "muted": MUTED}.get(ln.get("estado"), INK)
        filas += f'<div id="@@i{i}" class="abs mono" style="left:30px;top:{y}px;width:840px;font-size:29px;color:{c};white-space:nowrap;overflow:hidden">{rich(ln["texto"])}</div>'
        if i in tach:
            filas += f'<div id="@@k{i}" class="abs" style="left:24px;top:{y + 19}px;width:850px;height:4px;background:{CORAL}"></div>'
        ts.append(s.tw(ln.get("ancla"), 0.35 + i * 0.22) - (0.1 if ln.get("ancla") else 0))
    cab = f'<div class="abs mono" style="left:30px;top:22px;font-size:28px;color:{MUTED}">{p.get("cmd", "chelios@fabrica:~$")}</div>'
    if cont:
        cab += f'<div class="abs mono" style="right:30px;top:12px;font-size:40px;color:{col(cont.get("color"), CORAL)}"><span id="@@cnt">{cont.get("desde", 0)}</span><span style="font-size:28px;color:{MUTED}"> {cont.get("etiqueta", "")}</span></div>'
    html += card("term", 90, top, 900, alto, cab + filas, "background:#100E2A")
    if p.get("sello"):
        c_ = col(p["sello"].get("color"), CORAL)
        y_st = top + 80 + len(lineas) * 50 + 50
        if y_st + 130 > top + alto:
            y_st = top + alto / 2 - 60
        html += (f'<div class="abs center" style="top:{y_st:.0f}px"><span id="@@st" class="stamp disp" '
                 f'style="position:relative;color:{c_};border-color:{c_};font-size:{fit(p["sello"]["texto"], 80, 860, 0.8)}px">{p["sello"]["texto"]}</span></div>')
    tt = s.tw(p.get("ancla_tachar"), (ts[-1] if ts else 0) + 0.6)
    s.extra["x"] = {"ts": ts, "tach": sorted(tach), "tt": tt,
                    "cnt": [s.tw(cont.get("ancla_inicio"), tt), s.tw(cont.get("ancla_fin"), tt + 1.2), cont.get("desde", 0), cont.get("hasta", 0)] if cont else None,
                    "st": s.tw((p.get("sello") or {}).get("ancla"), s.dur - 1.2)}
    js = r"""
if (el("t")) blurIn("t", 0.06, 0.25);
fadeUp("term", 0.1, 40);
D.x.ts.forEach((t, i) => blurIn("i" + i, Math.max(0.2, t), 0.15));
D.x.tach.forEach((i, j) => { grow("k" + i, D.x.tt + j * 0.12, 0.25); dim("i" + i, D.x.tt + j * 0.12 + 0.1, 0.32); });
if (D.x.cnt) counter("cnt", D.x.cnt[0], D.x.cnt[1], D.x.cnt[2], D.x.cnt[3]);
if (el("st")) stamp("st", D.x.st - 0.1, -6);
"""
    sfx = [("typing", 0.3, 0.12)]
    if tach:
        sfx.append(("whoosh-short", tt, 0.2))
    if p.get("sello"):
        sfx.append(("impact-bass-1", s.extra["x"]["st"] + 0.14, 0.28))
    return {"html": html, "js": js, "sfx": sfx}


def t_comparar(s):
    p = s.p
    html = title("t", rich(p.get("titulo", "")), 305, fit(p.get("titulo", ""), 88))
    ts = {}
    for k, x in (("a", 90), ("b", 560)):
        lado = p.get(k, {})
        c = col(lado.get("color"), CYAN if k == "a" else CORAL)
        items = "".join(f'<div class="abs body" style="left:34px;top:{130 + j * 64}px;width:370px;font-size:34px;font-weight:700;line-height:1.1;color:{INK}">· {rich(it)}</div>'
                        for j, it in enumerate(lado.get("items", [])[:7]))
        html += card(k, x, 440, 430, 640, f'<div class="abs disp" style="left:34px;top:36px;width:370px;font-size:{fit(lado.get("titulo", ""), 58, 370)}px;color:{c}">{rich(lado.get("titulo", ""))}</div>{items}')
        ts[k] = s.tw(lado.get("ancla"), 0.4 if k == "a" else 1.2) - (0.12 if lado.get("ancla") else 0)
    html += f'<div id="@@vs" class="abs disp" style="left:500px;top:720px;width:80px;height:80px;border-radius:50%;background:{SUN};color:{GROUND};font-size:34px;line-height:84px;text-align:center">VS</div>'
    g = p.get("ganador")
    if g in ("a", "b"):
        x = 90 if g == "a" else 560
        html += f'<div class="abs" style="left:{x}px;top:410px;width:430px;text-align:center"><span id="@@win" class="chip" style="background:{GREEN};border:3px solid {GREEN};color:{GROUND};font-size:30px">✓ {p.get("insignia", "GANA")}</span></div>'
    tg = s.tw(p.get("ancla_ganador"), s.dur - 1.6)
    s.extra["x"] = {"a": ts["a"], "b": ts["b"], "g": g, "tg": tg}
    js = r"""
blurIn("t", 0.06, 0.25);
slideX("a", Math.max(0.1, D.x.a), -140);
slideX("b", Math.max(0.2, D.x.b), 140);
pop("vs", Math.max(0.3, Math.min(D.x.a, D.x.b) + 0.3));
if (D.x.g) {
  const w = D.x.g, l = w === "a" ? "b" : "a";
  tl.to($(w), { borderColor: "#5BE7A9", duration: 0.2 }, D.x.tg);
  dim(l, D.x.tg, 0.45);
  pop("win", D.x.tg + 0.05);
}
"""
    return {"html": html, "js": js, "sfx": [("whoosh-short", max(0, ts["a"]), 0.18), ("whoosh", max(0, ts["b"]), 0.16)] + ([("pop", tg, 0.3)] if g else [])}


def t_barras(s):
    p = s.p
    barras = p.get("barras", [])[:6]
    n = max(1, len(barras))
    gap = 18
    bw = min(150, (800 - gap * (n - 1)) / n)
    x0 = 90 + (900 - (bw * n + gap * (n - 1))) / 2
    vmax = max([float(b["valor"]) for b in barras] + [1])
    base = 520
    html = title("t", rich(p.get("titulo", "")), 305, fit(p.get("titulo", ""), 84))
    inner = ""
    for i, b in enumerate(barras):
        hgt = max(10, 380 * float(b["valor"]) / vmax)
        x = x0 - 90 + i * (bw + gap)
        c = col(b.get("color"), MUTED if i != p.get("destacar") else SUN)
        inner += (f'<div id="@@b{i}" class="abs" style="left:{x:.0f}px;top:{base - hgt:.0f}px;width:{bw:.0f}px;height:{hgt:.0f}px;border-radius:16px 16px 6px 6px;background:{c}"></div>'
                  f'<div id="@@v{i}" class="abs disp" style="left:{x - 30:.0f}px;top:{base - hgt - 58:.0f}px;width:{bw + 60:.0f}px;text-align:center;font-size:40px;color:{INK}">0</div>'
                  f'<div class="abs mono" style="left:{x - 20:.0f}px;top:{base + 16}px;width:{bw + 40:.0f}px;text-align:center;font-size:28px;line-height:1.15;color:{MUTED}">{b["etiqueta"]}</div>')
    if p.get("unidad"):
        inner += f'<div class="abs mono" style="left:34px;top:24px;font-size:28px;color:{MUTED}">{p["unidad"]}</div>'
    html += card("c", 90, 440, 900, 660, inner)
    if p.get("nota"):
        html += f'<div class="abs center" style="top:384px"><span id="@@nota" class="chip" style="background:{SUN};border:3px solid {SUN};color:{GROUND};font-size:28px">{p["nota"]}</span></div>'
    t0 = s.tw(p.get("ancla_inicio"), 0.5)
    s.extra["x"] = {"t0": t0, "vals": [float(b["valor"]) for b in barras], "dec": int(p.get("decimales", 0)),
                    "suf": p.get("sufijo", ""), "dst": p.get("destacar"), "tn": s.tw(p.get("ancla_nota"), t0 + 1.4)}
    js = r"""
blurIn("t", 0.06, 0.25);
fadeUp("c", 0.15, 40);
D.x.vals.forEach((v, i) => {
  const t = D.x.t0 + i * 0.16;
  tl.fromTo($("b" + i), { scaleY: 0 }, { scaleY: 1, duration: 0.7, ease: "expo.out", transformOrigin: "50% 100%" }, t);
  counter("v" + i, t, t + 0.7, 0, v, (x) => x.toFixed(D.x.dec).replace(".", ",") + D.x.suf);
});
if (D.x.dst !== undefined && D.x.dst !== null) tl.to($("b" + D.x.dst), { boxShadow: "0 0 44px rgba(255,201,60,.85)", duration: 0.3 }, D.x.t0 + D.x.vals.length * 0.16 + 0.5);
if (el("nota")) pop("nota", D.x.tn);
"""
    return {"html": html, "js": js, "sfx": [("whoosh-short", t0, 0.18)] + ([("pop", s.extra["x"]["tn"], 0.25)] if p.get("nota") else [])}


def t_habla(s):
    """Chelios hablando con una burbuja de texto opcional y un gesto."""
    p = s.p
    html = chip("chip", p["chip"], 300, col(p.get("chip_color"), SUN)) if p.get("chip") else ""
    if p.get("burbuja"):
        fs = 50 if len(plano(p["burbuja"])) < 40 else 42
        html += (f'<div id="@@bub" class="card" style="left:90px;top:380px;width:900px;min-height:150px;padding:30px 40px;border-color:{SUN}">'
                 f'<div class="body" style="font-size:{fs}px;font-weight:700;line-height:1.15;color:{INK};text-align:center">{rich(p["burbuja"])}</div>'
                 f'<div class="abs" style="left:420px;bottom:-26px;width:0;height:0;border-left:26px solid transparent;border-right:26px solid transparent;border-top:26px solid {SUN}"></div></div>')
    html += f'<div id="@@chw" class="abs" style="left:290px;top:575px;width:500px;height:575px">{chelios("@@ch", 500)}</div>'
    tb = 0.2 if s.inicio_parte else s.tw(p.get("ancla_burbuja"), 0.3)
    tgst = s.tw(p.get("ancla_gesto"), -1)
    s.extra["x"] = {"tb": tb, "tg": tgst, "g": p.get("gesto", "saludo")}
    js = r"""
if (el("chip")) pop("chip", 0.06);
tl.fromTo($("chw"), { opacity: 0, y: 140, scale: 0.8 }, { opacity: 1, y: 0, scale: 1, duration: 0.6, ease: "back.out(1.6)" }, 0.05);
if (el("bub")) tl.fromTo($("bub"), { opacity: 0, scale: 0.7, y: 30 }, { opacity: 1, scale: 1, y: 0, duration: 0.45, ease: "back.out(1.8)", transformOrigin: "50% 100%" }, Math.max(0.2, D.x.tb - 0.1));
if (D.x.tg >= 0) {
  if (D.x.g === "brazos") {
    tl.fromTo($("ch-armL"), { rotation: 0 }, { rotation: 58, duration: 0.3, ease: "back.out(2)", svgOrigin: "146 312" }, D.x.tg);
    tl.fromTo($("ch-armR"), { rotation: 0 }, { rotation: -46, duration: 0.34, ease: "back.out(2)", svgOrigin: "254 312" }, D.x.tg + 0.07);
  } else {
    tl.fromTo($("ch-armR"), { rotation: 0 }, { rotation: -75, duration: 0.18, ease: "power2.out", svgOrigin: "254 312" }, D.x.tg);
    tl.to($("ch-armR"), { rotation: -45, duration: 0.14, ease: "sine.inOut", svgOrigin: "254 312", yoyo: true, repeat: 3 }, D.x.tg + 0.18);
    tl.to($("ch-armR"), { rotation: 0, duration: 0.3, ease: "power2.inOut", svgOrigin: "254 312" }, D.x.tg + 0.8);
  }
}
rig("ch", { talk: true });
"""
    return {"html": html, "js": js, "sfx": [("pop", max(0.2, tb), 0.22)] if p.get("burbuja") else []}


PLANTILLAS.update({"titular": t_titular, "lista": t_lista, "numero": t_numero, "terminal": t_terminal,
                   "comparar": t_comparar, "barras": t_barras, "habla": t_habla})


EXPR = {"cansado": [0.5, 0, 0, 1.0], "sorpresa": [0.04, -12, 0, 1.22], "enojado": [0.32, 5, 14, 1.0],
        "feliz": [0.28, -6, -6, 1.0], "dormido": [0.92, 2, 0, 1.0]}


def t_dialogo(s):
    """Tú (socio humano, izquierda) y Chelios (derecha) conversando. p:
    pizarra: [{texto, ancla, color}] letrero arriba (cada uno reemplaza al anterior)
    socio_expr: [[ancla, "cansado|sorpresa|enojado|feliz|dormido"], ...]
    chelios_gesto: [[ancla, "saludo|brazos|salto"], ...]
    sorbos: [ancla, ...] (el socio toma café) · continua: true (sin entrada/salida, para escenas seguidas)
    entrada: false (personajes ya en escena desde el fotograma 0)"""
    p = s.p
    continua = bool(p.get("continua"))
    entrada = p.get("entrada", True) and not continua
    piz = p.get("pizarra", [])
    html = ""
    for i, pz in enumerate(piz):
        c = col(pz.get("color"), SUN)
        html += (f'<div id="@@pz{i}" class="card" style="left:110px;top:300px;width:860px;height:150px;border-color:{c};display:flex;align-items:center;justify-content:center">'
                 f'<div class="disp" style="font-size:{fit(pz["texto"], 70, 780, 0.78)}px;color:{INK};text-align:center;padding:0 30px">{rich(pz["texto"])}</div></div>')
    html += (f'<div id="@@sw" class="abs" style="left:30px;top:520px;width:420px;height:588px"><div id="@@si" style="width:420px;height:588px;transform-origin:50% 100%">{socio("@@so", 420)}</div></div>'
             f'<div id="@@cw" class="abs" style="left:640px;top:668px;width:380px;height:437px"><div id="@@ci" style="width:380px;height:437px;transform-origin:50% 100%">{chelios("@@ch", 380)}</div></div>'
             f'<div class="abs" style="left:40px;top:468px;width:420px;text-align:center"><span id="@@ns" class="chip" style="border:3px solid #9FEFFF;color:#9FEFFF;font-size:28px;padding:8px 20px">SOCIO HUMANO</span></div>'
             f'<div class="abs" style="left:640px;top:612px;width:380px;text-align:center"><span id="@@nc" class="chip" style="border:3px solid {SUN};color:{SUN};font-size:28px;padding:8px 20px">CHELIOS · CEO</span></div>')
    # quién habla y cuándo
    segs = []
    for w in s.words:
        q = w.get("quien", "chelios")
        if segs and segs[-1][0] == q and w["start"] - segs[-1][2] < 0.6:
            segs[-1][2] = w["end"]
        else:
            segs.append([q, w["start"], w["end"]])
    # expresiones del socio (transiciones de 0.18 s)
    keys = [[0, *EXPR["cansado"]]]
    for anc, ex in p.get("socio_expr", []):
        t = max(0.0, s.tw(anc, -1))
        if t < 0:
            continue
        prev = keys[-1][1:]
        keys.append([max(keys[-1][0] + 0.01, t - 0.02), *prev])
        keys.append([t + 0.18, *EXPR.get(ex, EXPR["cansado"])])
    gestos = [[s.tw(a, -1), g] for a, g in p.get("chelios_gesto", []) if s.tw(a, -1) >= 0]
    sorbos = [s.tw(a, -1) for a in p.get("sorbos", []) if s.tw(a, -1) >= 0]
    s.extra["x"] = {"pz": [0 if pz.get("desde_inicio") else max(0.05, s.tw(pz.get("ancla"), 0.1) - (0.1 if pz.get("ancla") else 0)) for pz in piz],
                    "segs": segs, "keys": keys, "gestos": gestos, "sorbos": sorbos, "entrada": entrada}
    if continua:
        s.extra["noEnter"] = True
        s.extra["noExit"] = True
    if not p.get("entrada", True):
        s.extra["noEnter"] = True
    js = r"""
// letreros
D.x.pz.forEach((t, i) => {
  if (t === 0) tl.fromTo($("pz" + i), { opacity: 1 }, { opacity: 1, duration: 0.01 }, 0);
  else tl.fromTo($("pz" + i), { opacity: 0, y: -30, scale: 0.92 }, { opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "back.out(1.7)" }, t);
  if (i + 1 < D.x.pz.length) tl.to($("pz" + i), { opacity: 0, y: -20, duration: 0.18, ease: "power2.in" }, D.x.pz[i + 1] - 0.12);
});
// entrada
if (D.x.entrada) {
  tl.fromTo($("sw"), { x: -480 }, { x: 0, duration: 0.55, ease: "expo.out" }, 0.02);
  tl.fromTo($("cw"), { y: -900 }, { y: 0, duration: 0.42, ease: "power3.in" }, 0.08);
  tl.fromTo($("ci"), { scaleY: 0.8, scaleX: 1.12 }, { scaleY: 1, scaleX: 1, duration: 0.6, ease: "elastic.out(1, 0.45)" }, 0.5);
}
// quién habla: el que habla se ve completo, el otro un poco atrás
const ns = el("ns"), nc = el("nc"), si = el("si"), ci = el("ci");
TICKS.push((t) => {
  let q = null;
  for (const sg of D.x.segs) { if (t >= sg[1] - 0.1 && t <= sg[2] + 0.25) q = sg[0]; }
  ns.style.opacity = q === "socio" ? 1 : 0.38;
  nc.style.opacity = q === "chelios" ? 1 : 0.38;
});
// gestos de Chelios
D.x.gestos.forEach(([t, g]) => {
  if (g === "brazos") {
    tl.fromTo($("ch-armL"), { rotation: 0 }, { rotation: 58, duration: 0.3, ease: "back.out(2)", svgOrigin: "146 312" }, t);
    tl.fromTo($("ch-armR"), { rotation: 0 }, { rotation: -46, duration: 0.34, ease: "back.out(2)", svgOrigin: "254 312" }, t + 0.07);
    tl.to($("ch-armL"), { rotation: 0, duration: 0.3, svgOrigin: "146 312" }, t + 1.3);
    tl.to($("ch-armR"), { rotation: 0, duration: 0.3, svgOrigin: "254 312" }, t + 1.36);
  } else if (g === "salto") {
    tl.fromTo($("cw"), { y: 0 }, { y: -90, duration: 0.22, ease: "power2.out", immediateRender: false }, t);
    tl.to($("cw"), { y: 0, duration: 0.3, ease: "bounce.out" }, t + 0.22);
  } else {
    tl.fromTo($("ch-armR"), { rotation: 0 }, { rotation: -75, duration: 0.18, ease: "power2.out", svgOrigin: "254 312" }, t);
    tl.to($("ch-armR"), { rotation: -45, duration: 0.14, ease: "sine.inOut", svgOrigin: "254 312", yoyo: true, repeat: 3 }, t + 0.18);
    tl.to($("ch-armR"), { rotation: 0, duration: 0.3, ease: "power2.inOut", svgOrigin: "254 312" }, t + 0.8);
  }
});
// sorbos de café
D.x.sorbos.forEach((t) => {
  tl.fromTo($("so-arm"), { y: 0, rotation: 0 }, { y: -118, rotation: -14, duration: 0.4, ease: "power2.inOut", svgOrigin: "300 420", immediateRender: false }, t);
  tl.to($("so-arm"), { y: 0, rotation: 0, duration: 0.4, ease: "power2.inOut", svgOrigin: "300 420" }, t + 0.9);
});
rig("ch", { talk: true });
rigSocio("so", { expr: D.x.keys });
"""
    return {"html": html, "js": js, "sfx": [("pop", t, 0.2) for t in s.extra["x"]["pz"]]}


PLANTILLAS["dialogo"] = t_dialogo


def escena_html(esc, tiempos, env_slice, dia=1, env2_slice=None):
    s = S(esc, tiempos, env_slice, dia, env2_slice)
    r = PLANTILLAS[esc["tpl"]](s)
    data = {"id": s.id, "pre": s.pre, "dur": s.dur, "a": s.a, "blinks": s.blinks, "env": env_slice}
    if esc["tpl"] == "dialogo":
        data["env2"] = s.env2
    data.update(s.extra)
    html = r["html"].replace("@@", s.pre)
    js = (r["js"]).replace("@@", s.pre)
    doc = f'''<template>
  <style>
    #root {{ position: absolute; inset: 0; }}
  </style>
  <div id="root" data-composition-id="{s.id}" data-width="1080" data-height="1920">
    <div id="{s.pre}wrap" class="wrap">
{html}
    </div>
  </div>
  <script>
  (function () {{
    const D = {json.dumps(data, ensure_ascii=False)};
{JS_BASE}
{js}
{JS_END}
  }})();
  </script>
</template>
'''
    sfx = [(n, max(0.0, t), v) for (n, t, v) in r["sfx"]]
    return doc, sfx
