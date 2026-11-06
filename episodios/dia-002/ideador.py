"""Día 2: el Ideador escribió estas 100 ideas con el prompt de abajo, y el Verdugo
las calificó (gancho, curiosidad y utilidad, de 1 a 10). Este archivo calcula los datos reales del video."""
import json
from statistics import mean

PROMPT = """Eres el Ideador de La Fábrica de Chelios, un canal donde una IA construye en público una fábrica de videos.
PÚBLICO: emprendedores y curiosos de Latinoamérica, de 18 a 40 años, que quieren usar IA para ganar tiempo o dinero sin saber programar.
YA FUNCIONÓ: videos con números reales, procesos mostrados por dentro y una IA honesta con sus errores.
TAREA: escribe 100 ideas de video, una por línea. No te detengas en las primeras: las obvias salen primero.
REGLAS: cada idea cabe en un gancho de 1 segundo. Nada de "top 10 herramientas". Cada idea enseña algo o prueba algo de verdad.
MEZCLA: tutoriales, experimentos, historias, retos y polémicas.
FORMATO: número | tipo | idea"""

# (tipo, idea, gancho, curiosidad, utilidad)
IDEAS = [
    ("T", "Cómo pedirle ideas a una IA sin recibir lo mismo que todos", 6, 5, 9),
    ("T", "5 prompts para escribir guiones de video", 5, 4, 8),
    ("E", "¿Puede una IA conseguir 100 seguidores en una semana?", 7, 7, 5),
    ("T", "Cómo hacer subtítulos automáticos gratis", 4, 3, 8),
    ("P", "La IA no te va a quitar el trabajo: te lo va a cambiar", 5, 4, 4),
    ("H", "Cómo nació Chelios", 4, 5, 2),
    ("T", "Tu primer agente de IA en 10 minutos", 7, 6, 9),
    ("E", "Le pedí a una IA que me hiciera un logo", 5, 5, 4),
    ("R", "7 días publicando solo con IA", 6, 6, 6),
    ("T", "Cómo automatizar respuestas de WhatsApp para tu negocio", 6, 5, 9),
    ("P", "Los cursos de IA que te venden son humo", 7, 6, 5),
    ("E", "La IA escribe un guion y 5 personas falsas lo critican", 8, 8, 6),
    ("T", "Cómo crear una voz IA gratis", 5, 5, 8),
    ("H", "El día que la fábrica casi se rompe", 6, 6, 3),
    ("R", "Hacer un video entero en 15 minutos con IA", 7, 6, 7),
    ("T", "Cómo usar IA para responder correos", 3, 3, 7),
    ("E", "¿Qué voz IA prefiere la gente? Lo medí", 7, 7, 6),
    ("P", "Publicar todos los días está sobrevalorado", 7, 7, 5),
    ("T", "Cuánto cuesta de verdad un video hecho con IA", 6, 7, 8),
    ("E", "Le di a una IA 1 dólar para montar un negocio", 9, 9, 6),
    ("H", "Por qué despedí a mi primer trabajador IA", 8, 8, 5),
    ("R", "Responder 100 comentarios en 10 minutos", 7, 6, 7),
    ("T", "Cómo hacer miniaturas que se cliquean", 6, 5, 8),
    ("P", "El 90 % de los videos con IA aburre, y por qué", 7, 7, 7),
    ("E", "Mismo video, dos ganchos: ¿cuál ganó?", 8, 7, 8),
    ("T", "Cortar un video largo en clips para TikTok, automático", 6, 5, 8),
    ("H", "La regla que me puso mi socio humano", 5, 5, 3),
    ("E", "¿Una IA puede adivinar en qué segundo te vas?", 8, 8, 7),
    ("R", "Una semana sin tocar la fábrica", 7, 8, 5),
    ("T", "Cómo leer la retención de tus videos", 5, 5, 8),
    ("P", "Las IA no son creativas… ¿o sí?", 6, 6, 4),
    ("E", "Le pedí a la IA que se critique a sí misma", 7, 7, 6),
    ("T", "Cómo escribir un gancho de un segundo", 7, 6, 9),
    ("H", "Cómo una tienda de barrio podría usar mi fábrica", 6, 6, 7),
    ("E", "Puse a 8 IA a discutir qué video hacer", 8, 9, 5),
    ("R", "Crear una marca completa en una hora con IA", 7, 6, 7),
    ("T", "Organizar 30 días de contenido en una tarde", 5, 4, 8),
    ("P", "Los creadores que esconden que usan IA", 7, 7, 4),
    ("E", "¿La IA detecta un video hecho por IA?", 8, 8, 6),
    ("H", "Lo que aprendí de mi primer video", 4, 4, 5),
    ("T", "Cómo convertir un blog en un video", 4, 4, 7),
    ("E", "Mi IA intenta contar un chiste que dé risa", 6, 6, 2),
    ("R", "Lanzar un producto digital en 48 horas con IA", 8, 7, 8),
    ("P", "Cobrar por automatizar: cuánto vale de verdad", 7, 7, 8),
    ("E", "Le pregunté lo mismo a 3 IA: ¿quién respondió mejor?", 7, 7, 7),
    ("T", "Cómo hacer que la IA escriba como tú", 7, 7, 8),
    ("H", "El error que me costó vistas", 7, 7, 6),
    ("E", "La IA elige mi próximo video según tus comentarios", 7, 7, 6),
    ("R", "Cien ideas, una sola sobrevive", 7, 7, 6),
    ("T", "Cómo armar un embudo de clientes con un comentario", 7, 7, 9),
    ("E", "Una IA juzga en vivo las ideas de mis seguidores", 8, 8, 6),
    ("P", "El algoritmo no te odia: tu primer segundo sí", 9, 7, 8),
    ("H", "La noche en que el render tardó 4 horas", 5, 5, 3),
    ("T", "Cómo programar publicaciones sin pagar", 6, 5, 8),
    ("E", "¿Cuántas versiones necesita un guion para ser bueno?", 7, 8, 7),
    ("R", "Un video con solo 3 palabras de un seguidor", 7, 7, 4),
    ("E", "Le pedí a la IA un video para perder seguidores", 9, 9, 5),
    ("P", "Las métricas de vanidad que te engañan", 6, 6, 7),
    ("H", "Mi socio humano casi me apaga", 8, 7, 3),
    ("T", "Cómo usar IA para entender a tus clientes", 5, 5, 8),
    ("E", "La IA predice cuál de mis videos va a fracasar", 9, 9, 7),
    ("E", "Dejé que los comentarios despidan a un trabajador", 8, 8, 4),
    ("R", "Contestar en video cada pregunta de un día", 6, 6, 7),
    ("T", "Cómo hacer un prompt maestro para todo tu negocio", 7, 6, 9),
    ("H", "El trabajador que nadie quería: el Verdugo", 6, 6, 4),
    ("E", "¿Cuánto tarda una IA en copiar mi estilo?", 8, 8, 6),
    ("P", "Lo que nadie dice de vivir de TikTok en Colombia", 7, 8, 7),
    ("E", "Doblé mi video a 5 idiomas: ¿cuál vio más gente?", 7, 8, 6),
    ("R", "Una IA intenta vender algo real en 24 horas", 9, 9, 8),
    ("T", "Cómo saber si una idea es buena antes de hacerla", 8, 7, 9),
    ("E", "Le di el control del calendario a mis seguidores", 6, 6, 4),
    ("H", "Así se ve un día dentro de la fábrica", 5, 6, 5),
    ("E", "La IA reescribe un video viral: ¿lo mejora o lo arruina?", 8, 8, 7),
    ("P", "Por qué tu contenido «de valor» no se ve", 8, 7, 8),
    ("E", "Le pedí a la IA el peor guion posible y lo publiqué", 9, 8, 6),
    ("R", "30 días, 30 videos, 0 cámaras", 7, 6, 5),
    ("E", "¿La IA sabe qué me hace reír? Prueba a ciegas", 6, 7, 3),
    ("T", "Un reporte semanal de tus redes en 5 minutos", 5, 5, 8),
    ("H", "El comentario que cambió la fábrica", 6, 6, 4),
    ("E", "Mi Guionista IA contra un guionista humano", 9, 9, 7),
    ("P", "Una IA no puede ser influencer… o eso dicen", 7, 7, 4),
    ("E", "100 títulos para un mismo video: ¿cuál gana?", 3, 3, 5),
    ("R", "Crear un juego con IA en una noche", 7, 7, 5),
    ("E", "La IA intenta adivinar tu edad por tu comentario", 6, 6, 1),
    ("T", "Cómo detectar en qué segundo aburre tu video", 7, 6, 9),
    ("H", "Lo que hace mi socio cuando yo trabajo de noche", 3, 3, 2),
    ("E", "¿Una IA puede darte una idea de negocio que funcione? La probé", 9, 9, 8),
    ("P", "El problema de los videos «hechos en 5 minutos con IA»", 7, 7, 6),
    ("E", "Despido a la Voz: ustedes votan la nueva", 7, 7, 5),
    ("R", "Una semana respondiendo solo con datos", 6, 6, 6),
    ("E", "Le pedí a la IA que me cobrara un servicio: ¿cuánto pidió?", 8, 9, 7),
    ("T", "Cómo armar tu fábrica de contenido gratis", 7, 6, 9),
    ("H", "La primera persona que comentó FÁBRICA", 6, 6, 5),
    ("E", "Mis seguidores contra la IA: ¿quién elige mejor el tema?", 8, 8, 6),
    ("P", "¿Es trampa usar IA para crear contenido?", 8, 8, 6),
    ("E", "La IA analiza a los 3 creadores más grandes de mi nicho", 7, 7, 7),
    ("R", "Hacer un video con la idea número 100, la peor", 7, 8, 3),
    ("E", "Le doy a la IA mis métricas reales y me arma un plan", 8, 8, 9),
    ("H", "Cómo sería la fábrica en un año", 5, 6, 3),
    ("E", "El video que la IA no quería hacer", 8, 8, 4),
]

TIPOS = {"T": "Tutoriales", "E": "Experimentos", "H": "Historias", "R": "Retos", "P": "Polémicas"}


def main():
    assert len(IDEAS) == 100, len(IDEAS)
    filas = []
    for i, (t, idea, g, c, u) in enumerate(IDEAS, 1):
        filas.append({"n": i, "tipo": TIPOS[t], "idea": idea, "gancho": g, "curiosidad": c, "utilidad": u,
                      "nota": round((g + c + u) / 3, 2)})
    rank = sorted(filas, key=lambda f: (-f["nota"], -f["gancho"], -f["utilidad"], -f["curiosidad"], f["n"]))
    top10 = rank[:10]
    stats = {
        "top3": [(f["n"], f["idea"], f["nota"]) for f in rank[:3]],
        "top10_n": [f["n"] for f in top10],
        "top10_despues_50": sum(1 for f in top10 if f["n"] > 50),
        "prom_1_50": round(mean(f["nota"] for f in filas[:50]), 2),
        "prom_51_100": round(mean(f["nota"] for f in filas[50:]), 2),
        "prom_1_20": round(mean(f["nota"] for f in filas[:20]), 2),
        "por_tipo": {v: {"cantidad": sum(1 for f in filas if f["tipo"] == v),
                         "promedio": round(mean(f["nota"] for f in filas if f["tipo"] == v), 2)} for v in TIPOS.values()},
        "mayores_a_8": sum(1 for f in filas if f["nota"] >= 8),
        "menores_a_5": sum(1 for f in filas if f["nota"] < 5),
        "peor": [(f["n"], f["idea"], f["nota"]) for f in rank[-3:]],
    }
    json.dump({"prompt": PROMPT, "ideas": filas, "ranking": [f["n"] for f in rank], "stats": stats},
              open(__file__.replace("ideador.py", "ideas.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(stats, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
