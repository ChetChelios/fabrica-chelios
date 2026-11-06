# Corrida diaria de La Fábrica de Chelios

Instrucciones para la tarea programada de cada madrugada. Modo **automático con aviso**: se produce, se programa en Zernio y se le avisa al socio humano. Él puede cancelar en Zernio antes de la hora de publicación.

## 0. Preparar el entorno (unos 3 minutos)

```bash
cd fabrica-chelios
pip install --break-system-packages -q kokoro-onnx soundfile numpy scipy
npx --yes hyperframes@0.9.11 tts "hola" --voice em_alex -o /tmp/hola.wav   # descarga el modelo de voz la primera vez
export HYPERFRAMES_BROWSER_PATH=/usr/bin/google-chrome
```

Las fuentes, los efectos y GSAP ya vienen en `motor/`.

## 1. ¿Qué día es?

- Día N = (fecha de hoy en Bogotá − `inicio_dia_1` de `config.json`) + 1.
- Si `episodios/dia-NNN/guion.json` ya existe **y** el release `dia-NNN` ya está en GitHub, no se produce nada: solo se revisa que las publicaciones estén programadas en Zernio.

## 2. Escribir el guion del día

1. Lee `docs/biblia-serie-comedia.md` (personajes, tono, límites del humor) y el episodio de `docs/calendario-comedia.md` que toca hoy.
2. Lee el guion de ayer para encadenar la historia (el adelanto de ayer es el conflicto de hoy).
3. Toma como referencia de formato `episodios/dia-003/guion.json`.
4. Escribe `episodios/dia-NNN/guion.json`:
   - 3 partes; cada parte de **más de 1:00** y el total de **más de 3:00**.
   - La escena 1 es un `dialogo` con `"entrada": false` y un letrero `desde_inicio`.
   - Un remate cada 10–15 segundos. Cliffhanger al final de las partes 1 y 2.
   - **1 dato útil real** en la parte 3, con la plantilla `lista`.
   - Cierre con `manana` (el conflicto de mañana) y `cta` (palabra FÁBRICA).
   - Si el texto dice YouTube, TikTok o pone una palabra en mayúsculas, usa un campo `tts` con la palabra escrita como se pronuncia.
   - **Cero números inventados** sobre el canal. Si se muestran métricas, se sacan de Zernio (analytics).
5. Revisa el humor contra los límites de la biblia: nada de tragedias reales, enfermedades, grupos de personas ni gente real.

## 3. Producir

```bash
python3 motor/voz.py episodios/dia-NNN/guion.json build/dia-NNN      # mide la duración (TOTAL y partes)
python3 fabrica.py episodios/dia-NNN/guion.json --solo-proyecto
cd build/proyecto-dia-NNN && npx --yes hyperframes@0.9.11 check --json   # corregir errores de layout
npx --yes hyperframes@0.9.11 snapshot --at <tiempos> --no-end -o /tmp/snaps  # mirar los fotogramas
cd ../.. && python3 fabrica.py episodios/dia-NNN/guion.json             # render + cortes + miniatura + textos
```

Verifica:
- Duraciones: completo de más de 180 s y cada parte de TikTok de más de 60 s.
- Volumen de unos −15 LUFS.
- El primer fotograma de cada parte no está vacío.
- Los textos no se cortan y se leen a tiempo.

## 4. Publicar

```bash
python3 publicar.py NNN --fecha AAAA-MM-DD     # crea el release en GitHub y escribe salidas/dia-NNN/zernio.json
```

Después, con el conector de Zernio, envía cada entrada de `zernio.json` con `posts_create_post` (vía `call_tool`), con sus `args` tal cual. Antes de las de TikTok, haz una prueba con `dry_run: true`. Confirma con `posts_list_posts` que quedaron programadas.

## 5. Guardar y avisar

- `git add episodios/dia-NNN && git commit -m "Día NNN" && git push`.
- Avisa al socio humano con un mensaje corto y los videos:
  - título del episodio;
  - horarios de publicación;
  - qué hacer si quiere cancelar ("en Zernio, antes de las 6 p. m.").

## Si algo falla

- Si el render falla dos veces, no se publica nada: se le avisa al socio con el error.
- Si Zernio rechaza una publicación, se reintenta una vez; si vuelve a fallar, se avisa.
- Nunca se publica un video sin haber visto sus fotogramas.
