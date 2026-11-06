# Manual de La Fábrica de Chelios

*Un canal dirigido por una IA, construido en público: un video al día. Completo en YouTube, en partes en TikTok.*

## 1. La idea en una línea

Chelios, una IA CEO, construye una "fábrica" de 8 trabajadores IA que produce un video diario y muestra cada pieza por dentro, con números reales. El canal es el experimento y el experimento es el contenido.

## 2. Qué tomamos del reel de referencia (@TARRITOAI) y qué no

| Tomamos la fórmula | La hacemos distinta |
|---|---|
| Un gancho con números en el segundo 0 | Números reales y honestos: hoy son ceros |
| "Esta cuenta la hace una fábrica de IA" | Formato serie, "construido en público", con un socio humano visible |
| Cada trabajador explicado con un gráfico | Personaje y marca propios: Chelios (robot-sol), paleta índigo, amarillo y coral |
| Un CTA de palabra clave ("Comenta TARRO") | "Comenta **FÁBRICA**" lleva a tus servicios de automatización |
| Subtítulos palabra por palabra | Video largo en YouTube que suma horas de reproducción, no solo un reel |

No copiamos el tarrito, su nombre ni su estética 3D: son de otro creador.

## 3. Identidad

- **Chelios:** CEO. Robot-sol amarillo, visor oscuro con ojos cian y corbata coral. Habla en primera persona, con humor seco, y es honesto con sus fracasos.
- **El socio humano (tú):** revisa, aprueba, publica y lo corrige cuando se pasa.
- **Los 8 trabajadores:** 1 Ideador (cian), 2 Verdugo (coral), 3 Guionista (morado), 4 Público (verde), 5 La Voz (lima), 6 Animador (naranja), 7 Cortador (azul), 8 Analista (blanco).
- **Paleta:** fondo `#0D0B24` · Chelios `#FFC93C` · datos `#45E3FF` · alertas `#FF5A6E` · texto `#F6F3FF`.
- **Tipografías:** Archivo Black (títulos y subtítulos), Space Mono (datos y etiquetas), Outfit (texto).
- **Reglas del canal (se dicen en el Día 1):** 1) cada video enseña algo; 2) cero números inventados; 3) si un video aburre, la fábrica lo arregla.

## 4. El flujo diario

| Paso | Quién | Cómo | Tiempo |
|---|---|---|---|
| 1. Ideas | Ideador | En el proyecto de Claude: "Chelios, Día N". Propone 100 ideas sobre el tema del calendario | 2 min |
| 2. Filtro | Verdugo | Puntúa gancho, curiosidad y utilidad, y deja 3 | incluido |
| 3. Guion | Guionista | Escribe el `guion.json` (3 partes de más de 1 min cada una, total de más de 3 min) | incluido |
| 4. Prueba | Público falso | 5 espectadores simulados leen el guion y marcan dónde se aburren; se reescribe | incluido |
| 5. Producción | Voz + Animador + Cortador | `python fabrica.py episodios/dia-00N/guion.json` | 45–60 min de render |
| 6. Revisión | Tú | Ver el video completo y verificar cada dato | 5 min |
| 7. Publicación | Tú | Ver la sección 5 | 10 min |
| 8. Análisis | Analista | Al día siguiente pegas métricas y comentarios; Chelios decide qué ajustar o "despedir" | 5 min |

## 5. Cómo publicar

**YouTube (video completo, vertical, más de 3:00)**
- Título, descripción, capítulos e etiquetas: salen listos en `textos-publicacion.md`.
- Sube la miniatura `dia-00N-miniatura-youtube.png`. Para miniaturas personalizadas YouTube pide verificar el canal con teléfono.
- Música: si quieres un fondo, agrégalo en YouTube Studio → Editor → Audio (biblioteca libre). No uses canciones comerciales.
- La declaración de contenido alterado o sintético es obligatoria para contenido realista. Esto es animación evidente, pero el video igual dice que lo hizo una IA.

**TikTok (las partes)**
- Publica las partes **en orden** (1, 2, 3) con unos 20–30 minutos entre cada una, para que quien vea la parte 1 ya encuentre la 2 en tu perfil.
- Activa la etiqueta **"Contenido generado por IA"**. Es la premisa del canal y evita problemas.
- Añade un sonido en tendencia a volumen muy bajo (5–10 %) si quieres más alcance; la voz debe seguir dominando.
- Agrupa las partes en una playlist "La Fábrica · Día N" si tu cuenta tiene playlists, y fija la parte 1 de los días clave.
- Responde a cada "FÁBRICA" (ver sección 6).

**Horario inicial a probar (hora Colombia):** YouTube a las 6:00 p. m. y TikTok a las 7:00, 7:30 y 8:00 p. m. Es solo un punto de partida: el Analista lo ajusta con tus datos reales a partir de la semana 2.

## 6. Cómo se gana dinero (realista)

**YouTube — Programa de Socios (YPP)**
- Hasta el **31 de enero de 2027**: 1.000 suscriptores y 4.000 horas públicas en 12 meses, o 10 millones de vistas de Shorts en 90 días.
- Desde el **1 de febrero de 2027**, para canales nuevos: 1.000 suscriptores y **8.000 horas** en 365 días, o **20 millones** de vistas de Shorts en 90 días.
- Nivel ampliado (sin cambios): 500 suscriptores y 3.000 horas, o 3 millones de vistas de Shorts. Da acceso a membresías, Super Chat y YouTube Shopping.
- Desde julio de 2026 YouTube desmonetiza el contenido **repetitivo o de plantilla** hecho con IA. Por eso cada video cambia de tema, trae datos reales y enseña algo. La serie no debe parecer el mismo video con otras palabras.

**TikTok — Creator Rewards**
- Paga solo por videos de más de 1 minuto (por eso las partes duran más de 1:00). Pide 10.000 seguidores y 100.000 vistas en 30 días.
- **Hoy no aparece disponible en Colombia.** Confírmalo en la app: Perfil → ☰ → Herramientas para creadores. Mientras tanto, TikTok sirve para crecer y conseguir clientes.

**El dinero de corto plazo: el CTA "Comenta FÁBRICA"**
- Cada comentario "FÁBRICA" es un posible cliente para tus servicios: automatizaciones, páginas web, diseño y fábricas de contenido para negocios.
- Respuesta sugerida: "¡Te escribo por DM! 🤖". En el DM va un enlace a tu WhatsApp o a una página con 3 paquetes.
- Lleva un registro diario de cuántos "FÁBRICA" llegan y cuántos se vuelven conversación y venta. Ese es el KPI que paga las cuentas antes que el YPP.

## 7. Qué medir cada día

| Métrica | Dónde | Por qué |
|---|---|---|
| Vistas por parte | TikTok | Si la parte 2 cae mucho frente a la 1, falla el cliffhanger |
| Retención media y % que llega al final | TikTok y YouTube | El Analista busca el segundo exacto en que la gente se va |
| Horas de reproducción acumuladas | YouTube Studio | Es la meta de monetización |
| Suscriptores y seguidores ganados | Ambas | Crecimiento |
| Comentarios "FÁBRICA" | Ambas | Clientes potenciales |

## 8. Cuidados

- Nunca inventar números en pantalla. Si no hay datos, se dice "cero" o "aún no".
- No usar personajes, logos ni música de terceros.
- Los comentarios que se muestren en video deben ser reales; si son de ejemplo, se rotulan como "ejemplo".
- Revisar cada dato que cambie con el tiempo (reglas de plataformas, precios) el mismo día de publicar.
