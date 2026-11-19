# Corrida diaria de Chelios Noticias · GTA 6

Instrucciones para la tarea programada de cada día. Un video vertical corto (40–70 s) con las novedades reales de GTA 6, publicado a las **6:00 p. m. (hora Colombia)** como YouTube Short y TikTok. Modo **automático con aviso**.

## 0. Entorno

```bash
cd fabrica-chelios
pip install --break-system-packages -q kokoro-onnx soundfile numpy scipy
export HYPERFRAMES_BROWSER_PATH=/usr/bin/google-chrome
```

Los procesos largos (render) se lanzan en segundo plano con `setsid nohup ... &` y se revisan con llamadas cortas: si una llamada se corta, el render sigue. **Nunca borres carpetas `salidas/<slug>/work-*` mientras haya un render activo** (mira antes con `ps aux | grep hyperframes`).

## 1. ¿Qué número toca?

- `N` = el número más alto en `noticias/gta6-NNN/` + 1. Slug: `gta6-NNN`.
- Antes de producir, revisa con `posts_list` (status `scheduled` y `published`) si ya hay un video de GTA 6 programado o publicado para **hoy** (fecha de Bogotá). Si lo hay, no se produce nada: solo se confirma y se termina sin avisar.

## 2. Investigar (obligatorio)

1. Busca en la web las noticias de GTA 6 de las **últimas 24–48 horas** (actualizaciones, parches, récords, guías útiles, problemas conocidos, anuncios de Rockstar, GTA Online, PC…). Usa varias búsquedas y lee las páginas.
2. Elige **5 datos verificables** que no hayan salido en los guiones anteriores (lee los últimos 2–3 guiones de `noticias/`).
3. Si no hay 5 novedades de verdad, completa con datos útiles comprobados (trucos de juego confirmados, ajustes recomendados por medios serios, curiosidades verificadas). **Nada de rumores presentados como hechos.** Si algo es rumor, no va.
4. Cada número en pantalla lleva su fuente en `fuentes` (medio + fecha).

## 3. Escribir el guion

- Copia el formato de `noticias/gta6-003/guion.json`: `formato: "lista"`, `tema: "synth"`, 5 `items` alternando `estilo` `synth` / `neon`, cards con `grande`/`linea`/`nota` o `filas`.
- Intro con gancho ("Ojo con el N"), CTA con la palabra GTA.
- Pronunciación en `tts`: GTA → "yitiéi", PlayStation → "Pleisteishon", Xbox → "Equisbox", PC → "pecé", 4K → "cuatro ka".
- Sin imágenes, logos ni personajes de Rockstar: solo las gráficas de la fábrica. Nada de spoilers de la historia sin avisarlo en la intro.
- `publicacion`: `youtube_titulo` (máx. 100, termina en "#Shorts"), `youtube_descripcion` (incluye "Hecho con IA…" y "no está afiliado a Rockstar Games ni a Take-Two"), `youtube_primer_comentario`, `tiktok`, `hashtags`.

## 4. Producir y revisar

```bash
python3 noticias.py noticias/gta6-NNN/guion.json --solo-proyecto
cd build/proyecto-gta6-NNN && npx --yes hyperframes@0.9.11 snapshot --at <0, una por tarjeta, cta> --no-end -o <scratchpad>
cd ../.. && python3 noticias.py noticias/gta6-NNN/guion.json      # render + audio a −15 LUFS
```

Mira los fotogramas: textos que no se corten ni se monten, primer fotograma lleno. Corrige y repite si hace falta.

## 5. Publicar

```bash
python3 noticias.py noticias/gta6-NNN/guion.json --publicar --fecha AAAA-MM-DD --hora 18:00
```

Si las 6:00 p. m. ya pasaron, usa `--hora` unos 10 minutos después de terminar. Luego, con Zernio: `validate_media` del video → `call_tool("posts_create_post", {...args TikTok..., "dry_run": true})` → enviar las 2 entradas de `salidas/gta6-NNN/zernio.json` con `call_tool("posts_create_post", args)` → confirmar con `posts_list` (status `scheduled`).

## 6. Guardar y avisar

- `git add noticias/gta6-NNN && git commit -m "Chelios Noticias: GTA 6 #NNN" && git push`.
- Aviso corto: título, los 5 datos en una línea, hora programada y "Si quieres quitarlo, bórralo en Zernio antes de las 6 p. m. o elimínalo después desde la app".

## Si algo falla

- Render falla dos veces o Zernio rechaza dos veces → no se publica; se avisa con el error.
- Nunca se publica sin haber mirado los fotogramas.
