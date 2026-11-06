"""La Voz: sintetiza la narración por escena y calcula el tiempo de cada palabra.

Kokoro (local, gratis) en español latino (es-419). Se sintetiza frase por frase,
se unen con pausas propias y las palabras se reparten dentro de cada frase por
sílabas, así los subtítulos caen sobre la voz sin necesidad de transcribir.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

SR = 24000
FPS = 30
LEAD = 0.14          # silencio al inicio de cada escena
LEAD_PARTE = 0.62    # inicio de las partes 2+ (el corte de TikTok entra a los 0.42 s)
TAIL = 0.30          # silencio al final de cada escena
PAUSA = {".": 0.26, "?": 0.30, "!": 0.26, ":": 0.30, "…": 0.55}

MODEL = Path.home() / ".cache/hyperframes/tts/models/kokoro-v1.0.onnx"
VOICES = Path.home() / ".cache/hyperframes/tts/voices/voices-v1.0.bin"


def _kokoro():
    from kokoro_onnx import Kokoro
    if not MODEL.exists():
        sys.exit("Falta el modelo de voz. Ejecuta una vez: npx hyperframes tts \"hola\" --voice em_alex")
    return Kokoro(str(MODEL), str(VOICES))


def frases(texto):
    """Divide en frases conservando la puntuación final ('.', '?', '!', ':', '…')."""
    partes = re.findall(r"[^.?!:…]+[.?!:…]*", texto)
    return [p.strip() for p in partes if p.strip()]


def silabas(palabra):
    limpia = re.sub(r"[^a-záéíóúüñ]", "", palabra.lower())
    grupos = re.findall(r"[aeiouáéíóúü]+", limpia)
    return max(1, len(grupos))


def repartir(palabras, dur):
    """Reparte la duración de una frase entre sus palabras (por sílabas + pausas de coma)."""
    unidades, huecos = [], []
    for w in palabras:
        unidades.append(silabas(w) + 0.35)
        huecos.append(0.9 if re.search(r"[,;]$", w) else 0.0)
    total = sum(unidades) + sum(huecos)
    k = dur / total
    t, out = 0.0, []
    for w, u, h in zip(palabras, unidades, huecos):
        out.append((t, t + u * k))
        t += (u + h) * k
    return out


def voz_socio(k, texto, voz, vel):
    """El socio humano: más grave y más lento (no ha dormido). Pitch -10 % por re-muestreo."""
    from scipy.signal import resample_poly
    a, _ = k.create(texto, voice=voz, lang="es-419", speed=vel * 1.03)
    return resample_poly(a.astype(np.float64), 10, 9).astype(np.float32)


def construir(guion_path, salida_dir):
    guion = json.loads(Path(guion_path).read_text(encoding="utf-8"))
    salida = Path(salida_dir)
    salida.mkdir(parents=True, exist_ok=True)
    k = _kokoro()
    voces = {"chelios": guion.get("voz", "em_alex"), "socio": guion.get("voz_socio", "em_santa")}
    vel = float(guion.get("velocidad", 1.0))

    pistas = {"chelios": [], "socio": []}   # una pista por personaje (para mover cada boca)
    t_escena = 0.0
    escenas = []
    parte_prev = None
    for esc in guion["escenas"]:
        # una escena es un monólogo ("texto", de Chelios salvo "quien") o un "dialogo" de varias líneas
        lineas = esc.get("dialogo") or [{"v": esc.get("quien", "chelios"), "texto": esc["texto"], "tts": esc.get("tts")}]
        # la primera escena de las partes 2+ arranca con más aire: el corte de TikTok
        # entra 0.42 s después, ya con el título en pantalla y sin cortar la voz
        lead = LEAD_PARTE if (parte_prev is not None and esc["parte"] != parte_prev) else LEAD
        parte_prev = esc["parte"]
        bloques = {"chelios": [np.zeros(int(lead * SR), dtype=np.float32)], "socio": [np.zeros(int(lead * SR), dtype=np.float32)]}

        def poner(quien, audio):
            for q in bloques:
                bloques[q].append(audio if q == quien else np.zeros(len(audio), dtype=np.float32))

        t = lead
        palabras = []
        ultima_pausa = 0.0
        for li, ln in enumerate(lineas):
            quien = ln.get("v", "chelios")
            texto = ln["texto"]
            tts = ln.get("tts") or texto
            fr_txt, fr_tts = frases(texto), frases(tts)
            if len(fr_txt) != len(fr_tts):
                sys.exit(f"{esc['id']}: 'texto' y 'tts' deben tener las mismas frases")
            if li > 0 and quien != lineas[li - 1].get("v", "chelios"):
                cambio = 0.12  # respiro extra al cambiar de personaje
                poner(quien, np.zeros(int(cambio * SR), dtype=np.float32))
                t += cambio
            for ft, fs in zip(fr_txt, fr_tts):
                wt, ws = ft.split(), fs.split()
                if len(wt) != len(ws):
                    sys.exit(f"{esc['id']}: misma cantidad de palabras en texto y tts: «{ft}» / «{fs}»")
                if quien == "socio":
                    a = voz_socio(k, fs, voces["socio"], vel)
                else:
                    a, _ = k.create(fs, voice=voces["chelios"], lang="es-419", speed=vel)
                    a = a.astype(np.float32)
                d = len(a) / SR
                for w, (s0, e0) in zip(wt, repartir(wt, d)):
                    palabras.append({"text": w, "start": round(t + s0, 3), "end": round(t + e0, 3), "quien": quien})
                poner(quien, a)
                t += d
                ultima_pausa = PAUSA.get(ft[-1], 0.18)
                poner(quien, np.zeros(int(ultima_pausa * SR), dtype=np.float32))
                t += ultima_pausa
        # quitar la última pausa de frase y poner la cola de escena
        for q in bloques:
            bloques[q][-1] = np.zeros(int(TAIL * SR), dtype=np.float32)
        t = t - ultima_pausa + TAIL
        hold = float(esc.get("p", {}).get("hold", 0))
        if hold:
            for q in bloques:
                bloques[q].append(np.zeros(int(hold * SR), dtype=np.float32))
            t += hold
        a_ch = np.concatenate(bloques["chelios"])
        a_so = np.concatenate(bloques["socio"])
        dur = len(a_ch) / SR
        escenas.append({
            "id": esc["id"], "parte": esc["parte"], "tpl": esc["tpl"],
            "start": round(t_escena, 3), "dur": round(dur, 3),
            "words": palabras,  # tiempos relativos a la escena (con "quien")
        })
        pistas["chelios"].append(a_ch)
        pistas["socio"].append(a_so)
        t_escena += dur

    ch = np.concatenate(pistas["chelios"])
    so = np.concatenate(pistas["socio"])
    narr = ch + so
    pico = max(1e-6, np.abs(narr).max())
    narr = narr / pico * 0.89   # normalizar a -1 dBFS de pico
    sf.write(salida / "narracion.wav", narr, SR)

    def envolvente(x):
        hop = SR // FPS
        n = len(x) // hop + 1
        e = np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2)) if i * hop < len(x) else 0 for i in range(n)])
        ref = np.percentile(e[e > 1e-4], 95) if np.any(e > 1e-4) else 1.0
        return [round(float(v), 2) for v in np.clip(e / max(1e-6, ref), 0, 1)]

    data = {"total": round(t_escena, 3), "fps": FPS, "escenas": escenas,
            "envolvente": envolvente(ch), "envolvente_socio": envolvente(so)}
    (salida / "tiempos.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


if __name__ == "__main__":
    d = construir(sys.argv[1], sys.argv[2])
    partes = {}
    for e in d["escenas"]:
        partes.setdefault(e["parte"], 0)
        partes[e["parte"]] += e["dur"]
        print(f"{e['id']} parte {e['parte']}  inicio {e['start']:7.2f}  dur {e['dur']:5.2f}")
    print("TOTAL", d["total"], {k: round(v, 1) for k, v in partes.items()})
