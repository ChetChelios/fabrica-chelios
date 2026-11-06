# La Fábrica de Chelios

Convierte un guion (`guion.json`) en un video vertical completo para YouTube, sus partes para TikTok, la miniatura y los textos de publicación. Todo es gratis y corre en local: la voz es Kokoro y la animación es HyperFrames (HTML → video).

```
python fabrica.py episodios/dia-001/guion.json
```

Todo sale en `salidas/dia-001/`:

| Archivo | Para qué |
|---|---|
| `dia-001-youtube-completo.mp4` | Subirlo completo a YouTube (más de 3 min = video largo, suma horas) |
| `dia-001-tiktok-parte-1de3.mp4` … | Las partes para TikTok, con etiqueta "PARTE X/3" y tarjeta final |
| `dia-001-miniatura-youtube.png` | Miniatura de 1280x720 |
| `textos-publicacion.md` | Títulos, descripción, capítulos de YouTube y textos de TikTok |

## Los trabajadores (el código)

| Trabajador | Archivo | Qué hace |
|---|---|---|
| La Voz | `motor/voz.py` | Narra cada escena (es-419, voz `em_alex`) y calcula el tiempo de cada palabra |
| El Animador | `motor/montar.py`, `motor/plantillas.py`, `motor/personajes.py` | Arma el proyecto HyperFrames: fondo, escenas, subtítulos y efectos de sonido |
| El Cortador | `motor/cortador.py` | Corta las partes de TikTok y genera las portadas |
| (Ideador, Verdugo, Guionista, Público, Analista) | Claude | Escriben y evalúan el `guion.json` de cada día |

## Instalar en tu PC (una sola vez)

1. Instala **Python 3.10+**, **Node.js 22+**, **FFmpeg** y **Google Chrome**.
2. En esta carpeta:
   ```
   pip install kokoro-onnx soundfile numpy playwright
   python -m playwright install chromium
   npx hyperframes tts "hola" --voice em_alex
   ```
   El último comando descarga el modelo de voz (unos 300 MB) en `~/.cache/hyperframes/tts`.
3. Si el render no encuentra Chrome, define `HYPERFRAMES_BROWSER_PATH` con la ruta de tu Chrome.

## Hacer el episodio de mañana

1. Copia `episodios/dia-001/guion.json` a `episodios/dia-002/guion.json`.
2. Cambia `dia`, `titulo`, `partes`, `escenas` y `publicacion` (o pídeselo a Chelios en el proyecto de Claude).
3. Ejecuta `python fabrica.py episodios/dia-002/guion.json`.

Para revisar antes de renderizar: `python fabrica.py episodios/dia-002/guion.json --solo-proyecto` y después `cd build/proyecto-dia-002 && npx hyperframes preview`.

## Reglas del guion

- Cada escena tiene `id`, `parte` (1, 2 o 3), `tpl` (plantilla), `texto` (lo que se lee y se subtitula) y `p` (parámetros de la plantilla).
- `tts` es opcional: es la misma frase escrita para que la voz la pronuncie bien (`YouTube` → `yutub`). Debe tener **las mismas frases y la misma cantidad de palabras** que `texto`.
- `hl` son las palabras que se resaltan en amarillo y `kill` las que van en coral.
- Plantillas disponibles: `hook, chelios, orden, meta, plan, reglas, crew, agente, verdugo, publico, voz, cortador, octavo, despidos, analista, reemplazo, socio, reveal, manana, cta`. Las que usan anclas de palabras (`at("palabra")`) esperan ciertas palabras en el texto; mira `motor/plantillas.py`.
- Para que YouTube cuente el video como largo, el total debe pasar de **3:00**. Cada parte de TikTok debe pasar de **1:00**.

## Créditos

- Efectos de sonido: Pixabay Content License (`motor/sfx/CREDITS.md`).
- Fuentes: Archivo Black, Space Mono y Outfit (SIL Open Font License).
- Voz: Kokoro-82M (Apache 2.0). Animación: HyperFrames + GSAP.
