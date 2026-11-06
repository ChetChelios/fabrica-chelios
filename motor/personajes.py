"""Chelios (CEO, robot-sol original) y los trabajadores de la fábrica, en SVG."""

INK = "#F6F3FF"
GROUND = "#0D0B24"
SUN = "#FFC93C"
CYAN = "#45E3FF"
CORAL = "#FF5A6E"
MUTED = "#8E89BF"
CARD = "#1A1640"
LINE = "#2C2760"
GREEN = "#5BE7A9"

TRABAJADORES = [
    {"n": 1, "nombre": "IDEADOR", "color": "#45E3FF", "icono": "bombillo"},
    {"n": 2, "nombre": "VERDUGO", "color": "#FF5A6E", "icono": "x"},
    {"n": 3, "nombre": "GUIONISTA", "color": "#B98CFF", "icono": "pluma"},
    {"n": 4, "nombre": "PÚBLICO", "color": "#5BE7A9", "icono": "ojo"},
    {"n": 5, "nombre": "LA VOZ", "color": "#9BE15D", "icono": "mic"},
    {"n": 6, "nombre": "ANIMADOR", "color": "#FF9F43", "icono": "pelicula"},
    {"n": 7, "nombre": "CORTADOR", "color": "#4D8DFF", "icono": "tijeras"},
    {"n": 8, "nombre": "ANALISTA", "color": "#E9E6FF", "icono": "grafica"},
]


def _shade(hexc, f):
    hexc = hexc.lstrip("#")
    r, g, b = (int(hexc[i:i + 2], 16) for i in (0, 2, 4))
    if f < 1:
        r, g, b = (int(c * f) for c in (r, g, b))
    else:
        r, g, b = (int(c + (255 - c) * (f - 1)) for c in (r, g, b))
    return "#%02X%02X%02X" % (r, g, b)


def icono(nombre, cx, cy, s=1.0, color="#FFFFFF"):
    """Icono simple centrado en (cx, cy), tamaño base ~60 px."""
    t = f'transform="translate({cx} {cy}) scale({s})"'
    d = {
        "bombillo": f'<circle cx="0" cy="-8" r="20" fill="{SUN}"/><rect x="-9" y="10" width="18" height="14" rx="3" fill="#D9D4FF"/><rect x="-6" y="-14" width="3" height="12" fill="#FFF3C4"/>',
        "x": f'<rect x="-26" y="-6" width="52" height="12" rx="6" fill="{color}" transform="rotate(45)"/><rect x="-26" y="-6" width="52" height="12" rx="6" fill="{color}" transform="rotate(-45)"/>',
        "pluma": f'<g transform="rotate(35)"><rect x="-7" y="-28" width="14" height="40" rx="4" fill="{color}"/><path d="M-7 12 L7 12 L0 28 Z" fill="#FFF"/></g>',
        "ojo": f'<path d="M-28 0 Q0 -24 28 0 Q0 24 -28 0 Z" fill="#FFF"/><circle cx="0" cy="0" r="10" fill="{color}"/><circle cx="0" cy="0" r="4" fill="{GROUND}"/>',
        "mic": f'<rect x="-10" y="-28" width="20" height="34" rx="10" fill="{color}"/><path d="M-18 -2 Q-18 18 0 18 Q18 18 18 -2" fill="none" stroke="#FFF" stroke-width="4"/><rect x="-2" y="18" width="4" height="10" fill="#FFF"/>',
        "pelicula": f'<rect x="-26" y="-18" width="52" height="36" rx="5" fill="{color}"/>' + "".join(f'<rect x="{x}" y="-14" width="6" height="6" rx="1" fill="{GROUND}"/><rect x="{x}" y="8" width="6" height="6" rx="1" fill="{GROUND}"/>' for x in (-20, -8, 4, 16)),
        "tijeras": f'<circle cx="-12" cy="14" r="9" fill="none" stroke="{color}" stroke-width="5"/><circle cx="12" cy="14" r="9" fill="none" stroke="{color}" stroke-width="5"/><rect x="-3" y="-28" width="6" height="40" rx="3" fill="#FFF" transform="rotate(18 0 8)"/><rect x="-3" y="-28" width="6" height="40" rx="3" fill="#FFF" transform="rotate(-18 0 8)"/>',
        "grafica": f'<rect x="-24" y="2" width="12" height="22" rx="2" fill="{color}"/><rect x="-6" y="-10" width="12" height="34" rx="2" fill="{color}"/><rect x="12" y="-24" width="12" height="48" rx="2" fill="{CYAN}"/>',
        "interrogacion": f'<text x="0" y="18" text-anchor="middle" font-family="Archivo Black" font-size="56" fill="{color}">?</text>',
        "persona": f'<circle cx="0" cy="-14" r="14" fill="{color}"/><path d="M-24 26 Q-24 2 0 2 Q24 2 24 26 Z" fill="{color}"/>',
    }[nombre]
    return f'<g {t}>{d}</g>'


def chelios(pre, ancho=400, extra=""):
    """Chelios: robot-sol con visor y corbata. viewBox 400x460. Ids con prefijo pre."""
    rayos = "".join(
        f'<rect x="191" y="14" width="18" height="46" rx="9" fill="#FFB020" transform="rotate({k * 30} 200 190)"/>'
        for k in range(12))
    alto = ancho * 460 / 400
    return f'''<svg id="{pre}" class="chelios" viewBox="0 0 400 460" width="{ancho:.0f}" height="{alto:.0f}" {extra} overflow="visible">
  <defs>
    <radialGradient id="{pre}-g" cx="38%" cy="28%" r="78%"><stop offset="0" stop-color="#FFE7A3"/><stop offset=".5" stop-color="#FFC93C"/><stop offset="1" stop-color="#EE9A00"/></radialGradient>
    <filter id="{pre}-b" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="12"/></filter>
    <filter id="{pre}-e" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <ellipse id="{pre}-glow" cx="200" cy="446" rx="120" ry="16" fill="{CYAN}" opacity=".45" filter="url(#{pre}-b)"/>
  <g id="{pre}-float">
    <g id="{pre}-crown">{rayos}</g>
    <g id="{pre}-body">
      <g id="{pre}-armL"><rect x="98" y="300" width="52" height="24" rx="12" fill="#E89400"/></g>
      <g id="{pre}-armR"><rect x="250" y="300" width="52" height="24" rx="12" fill="#E89400"/></g>
      <rect x="138" y="290" width="124" height="100" rx="40" fill="url(#{pre}-g)"/>
      <path d="M166 296 L200 324 L234 296 Z" fill="#FFF6E0"/>
      <rect x="192" y="312" width="16" height="13" rx="3" fill="#D93451"/>
      <path d="M200 322 L187 340 L200 384 L213 340 Z" fill="{CORAL}"/>
    </g>
    <g id="{pre}-head">
      <circle cx="200" cy="190" r="120" fill="url(#{pre}-g)"/>
      <ellipse cx="156" cy="118" rx="42" ry="18" fill="#FFFFFF" opacity=".38" transform="rotate(-28 156 118)"/>
      <rect x="102" y="136" width="196" height="122" rx="56" fill="#15123A" stroke="#2E2870" stroke-width="5"/>
      <g filter="url(#{pre}-e)">
        <rect id="{pre}-eyeL" x="150" y="158" width="30" height="50" rx="15" fill="{CYAN}"/>
        <rect id="{pre}-eyeR" x="220" y="158" width="30" height="50" rx="15" fill="{CYAN}"/>
        <rect id="{pre}-mouth" x="176" y="227" width="48" height="6" rx="3" fill="{CYAN}"/>
      </g>
      <circle cx="96" cy="250" r="13" fill="#FF7A59" opacity=".55"/>
      <circle cx="304" cy="250" r="13" fill="#FF7A59" opacity=".55"/>
    </g>
  </g>
</svg>'''


def bot(pre, color, icon, ancho=300, extra=""):
    """Trabajador: robot sin corona, color propio e icono de oficio. viewBox 300x340."""
    alto = ancho * 340 / 300
    osc = _shade(color, 0.72)
    cla = _shade(color, 1.35)
    return f'''<svg id="{pre}" class="bot" viewBox="0 0 300 340" width="{ancho:.0f}" height="{alto:.0f}" {extra} overflow="visible">
  <defs><filter id="{pre}-b" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9"/></filter></defs>
  <ellipse id="{pre}-glow" cx="150" cy="328" rx="86" ry="12" fill="{color}" opacity=".4" filter="url(#{pre}-b)"/>
  <g id="{pre}-float">
    <rect x="102" y="228" width="96" height="74" rx="30" fill="{osc}"/>
    <rect x="48" y="70" width="204" height="168" rx="64" fill="{color}"/>
    <ellipse cx="104" cy="98" rx="32" ry="12" fill="{cla}" opacity=".6" transform="rotate(-20 104 98)"/>
    <rect x="72" y="108" width="156" height="92" rx="42" fill="#15123A"/>
    <rect id="{pre}-eyeL" x="112" y="126" width="22" height="38" rx="11" fill="{CYAN}"/>
    <rect id="{pre}-eyeR" x="166" y="126" width="22" height="38" rx="11" fill="{CYAN}"/>
    <rect id="{pre}-mouth" x="134" y="178" width="32" height="5" rx="2.5" fill="{CYAN}"/>
    {icono(icon, 150, 26, 1.0, cla)}
  </g>
</svg>'''


def socio(pre, ancho=400, extra=""):
    """El socio humano: cansado, hoodie gris y café con el sol de Chelios. viewBox 400x560."""
    alto = ancho * 560 / 400
    piel, piel2 = "#C98B63", "#B07550"
    pelo = "#2A1D19"
    hood, hood2 = "#7C849C", "#5E6579"
    return f'''<svg id="{pre}" class="socio" viewBox="0 0 400 560" width="{ancho:.0f}" height="{alto:.0f}" {extra} overflow="visible">
  <defs>
    <filter id="{pre}-b" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="12"/></filter>
    <radialGradient id="{pre}-g" cx="40%" cy="30%" r="75%"><stop offset="0" stop-color="#D99C74"/><stop offset="1" stop-color="{piel2}"/></radialGradient>
  </defs>
  <ellipse cx="200" cy="548" rx="130" ry="14" fill="#000" opacity=".35" filter="url(#{pre}-b)"/>
  <g id="{pre}-float">
    <path d="M70 560 Q70 360 200 350 Q330 360 330 560 Z" fill="{hood}"/>
    <path d="M118 372 Q200 300 282 372 L262 400 Q200 352 138 400 Z" fill="{hood2}"/>
    <rect x="150" y="470" width="100" height="56" rx="16" fill="{hood2}" opacity=".7"/>
    <path d="M176 384 L170 452" stroke="#EDEFF7" stroke-width="5" stroke-linecap="round"/>
    <path d="M224 384 L230 452" stroke="#EDEFF7" stroke-width="5" stroke-linecap="round"/>
    <circle cx="170" cy="456" r="6" fill="#EDEFF7"/><circle cx="230" cy="456" r="6" fill="#EDEFF7"/>
    <rect x="178" y="300" width="44" height="60" rx="16" fill="{piel2}"/>
    <g id="{pre}-head">
      <ellipse cx="106" cy="214" rx="18" ry="26" fill="{piel2}"/><ellipse cx="294" cy="214" rx="18" ry="26" fill="{piel2}"/>
      <ellipse cx="200" cy="200" rx="96" ry="110" fill="url(#{pre}-g)"/>
      <path d="M104 182 Q100 92 170 80 Q178 58 204 74 Q226 56 240 82 Q302 92 298 176 Q286 128 252 120 Q262 140 246 146 Q232 118 206 116 Q214 136 196 140 Q186 116 160 120 Q130 128 104 182 Z" fill="{pelo}"/>
      <path d="M150 80 Q140 54 166 50 Q158 66 172 78 Z" fill="{pelo}"/>
      <path d="M232 74 Q248 46 270 60 Q252 64 248 82 Z" fill="{pelo}"/>
      <g id="{pre}-brows">
        <rect id="{pre}-browL" x="136" y="160" width="46" height="9" rx="4.5" fill="{pelo}"/>
        <rect id="{pre}-browR" x="218" y="160" width="46" height="9" rx="4.5" fill="{pelo}"/>
      </g>
      <g id="{pre}-eyes">
        <ellipse cx="160" cy="196" rx="20" ry="17" fill="#F7F4EF"/><ellipse cx="240" cy="196" rx="20" ry="17" fill="#F7F4EF"/>
        <circle id="{pre}-eyeL" cx="162" cy="199" r="9" fill="#2A1D19"/><circle id="{pre}-eyeR" cx="242" cy="199" r="9" fill="#2A1D19"/>
        <rect id="{pre}-lidL" x="138" y="176" width="44" height="20" rx="6" fill="{piel}"/>
        <rect id="{pre}-lidR" x="218" y="176" width="44" height="20" rx="6" fill="{piel}"/>
      </g>
      <path d="M142 218 Q160 228 178 218" stroke="#8C5E78" stroke-width="5" fill="none" stroke-linecap="round" opacity=".7"/>
      <path d="M222 218 Q240 228 258 218" stroke="#8C5E78" stroke-width="5" fill="none" stroke-linecap="round" opacity=".7"/>
      <path d="M196 214 Q192 236 202 240" stroke="{piel2}" stroke-width="5" fill="none" stroke-linecap="round"/>
      <rect id="{pre}-mouth" x="182" y="262" width="36" height="6" rx="3" fill="#5A2626"/>
    </g>
    <g id="{pre}-arm">
      <path d="M300 392 Q338 430 300 462 L246 456" stroke="{hood2}" stroke-width="36" fill="none" stroke-linecap="round"/>
      <ellipse cx="240" cy="448" rx="17" ry="19" fill="{piel2}"/>
      <g id="{pre}-mug">
        <rect x="236" y="402" width="64" height="74" rx="10" fill="#F2F2F5"/>
        <path d="M300 418 Q326 420 324 440 Q322 458 300 458" stroke="#F2F2F5" stroke-width="9" fill="none"/>
        <circle cx="268" cy="440" r="13" fill="{SUN}"/>
        <g id="{pre}-steam" opacity=".55">
          <path d="M252 392 Q244 378 252 364 Q260 350 252 336" stroke="#E9E6FF" stroke-width="5" fill="none" stroke-linecap="round"/>
          <path d="M270 392 Q262 376 270 360 Q278 344 270 328" stroke="#E9E6FF" stroke-width="5" fill="none" stroke-linecap="round"/>
          <path d="M288 392 Q280 378 288 364 Q296 350 288 336" stroke="#E9E6FF" stroke-width="5" fill="none" stroke-linecap="round"/>
        </g>
      </g>
      <rect x="228" y="430" width="16" height="30" rx="8" fill="{piel}"/>
    </g>
  </g>
</svg>'''
