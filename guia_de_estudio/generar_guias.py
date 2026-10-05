# -*- coding: utf-8 -*-
"""
Genera la guía de estudio del equipo (versiones corregidas al 04-10-2026):
  guia_de_estudio/Guion_Presentacion_Titulacion_2025.pdf
  guia_de_estudio/Guia_Defensa_Titulacion_2025.pdf
Todas las cifras se leen de output/tablas/*.csv (R/run_all.R y R/exploratorio/x04_...).
Uso (desde la raíz del proyecto):  python guia_de_estudio/generar_guias.py
"""
import csv, os, subprocess, sys
from html import escape

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "informe"))
# Reutiliza la lectura de tablas y el formato numérico del generador del informe
from generar_documentos import (num, ent, pp, kg, kd, bit, chq, orx, ef, aj, met, vif, sens,
                                efecto, kv, peor_g, mejor_g, derecho, n_mod, prev_fuera)

SALIDA = os.path.dirname(os.path.abspath(__file__))
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
URL_DASH = "https://mikhassdev.github.io/Mineria_de_Datos_EV3/"

with open(os.path.join(RAIZ, "output", "tablas", "verificaciones.csv"), encoding="utf-8") as fh:
    V = {r["indicador"]: r["valor"] for r in csv.DictReader(fh)}

B = {b["paso"]: b for b in bit}
total_elim = int(chq["Registros totales"]) - int(kg["n"])
pct_elim = 100 * total_elim / int(chq["Registros totales"])
oD, oN = orx["area_conocimientoDerecho"], orx["macrozonaNorte"]
cft, semi = sens["grupo_instCFT · técnica"], sens["modalidad_jornadaSemipresencial u otra"]
plan = sens["tipo_plan_carrPlan Especial"]
ipp, ipt, ut = (sens["grupo_instIP · profesional"], sens["grupo_instIP · técnica"],
                sens["grupo_instUniversidad · técnica"])
vif_max = max(float(v["GVIF_ajustado"]) for v in vif)
odds_atraso = (prev_fuera / 100) / (1 - prev_fuera / 100)
e = lambda v, n: efecto(v, n)["dif_vs_ref_pp"]

# ------------------------------------------------------------------ estilos
CSS = """
@page { size: Letter; margin: 2cm 2.2cm; }
body { font-family: Calibri, 'Segoe UI', Arial, sans-serif; font-size: 11pt; color: #1F2328; line-height: 1.38; }
h1 { font-family: Cambria, Georgia, serif; font-size: 22pt; margin: 0 0 2pt; color: #1F2328; }
.sub { color: #5A5F66; font-size: 11pt; margin-bottom: 14pt; }
h2 { font-family: Cambria, Georgia, serif; font-size: 14.5pt; color: #C8102E; margin: 18pt 0 6pt; break-after: avoid; }
h3 { font-size: 11.5pt; margin: 11pt 0 3pt; break-after: avoid; color: #1F2328; }
p { margin: 3pt 0 7pt; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0 10pt; font-size: 9.8pt; break-inside: auto; }
th { background: #1F2328; color: #fff; text-align: left; padding: 4pt 6pt; }
td { border-bottom: 0.6pt solid #D9DBDF; padding: 3.5pt 6pt; vertical-align: top; }
tr { break-inside: avoid; }
.num { text-align: right; white-space: nowrap; }
code, pre { font-family: Consolas, 'Courier New', monospace; font-size: 9.3pt; }
pre { background: #F2F3F5; padding: 6pt 8pt; border-radius: 4pt; white-space: pre-wrap; margin: 4pt 0 8pt; }
.dialogo { background: #F2F3F5; border-radius: 6pt; padding: 7pt 10pt; margin: 4pt 0 6pt; }
.accion { color: #5A5F66; font-style: italic; margin: 2pt 0 2pt; }
.nota { background: #FBE9EB; border-radius: 6pt; padding: 7pt 10pt; margin: 8pt 0; break-inside: avoid; }
.ok { background: #E8F4EC; border-radius: 6pt; padding: 7pt 10pt; margin: 8pt 0; break-inside: avoid; }
.lamina { font-weight: bold; margin: 12pt 0 3pt; break-after: avoid; }
.lamina span { color: #5A5F66; font-weight: normal; }
.qa { break-inside: avoid; }
.cambio { font-size: 9.5pt; color: #5A5F66; }
"""

def documento(titulo, subtitulo, cuerpo):
    return (f"<!doctype html><html lang='es'><head><meta charset='utf-8'><title>{escape(titulo)}</title>"
            f"<style>{CSS}</style></head><body><h1>{escape(titulo)}</h1><div class='sub'>{subtitulo}</div>"
            f"{cuerpo}</body></html>")

def tabla(cab, filas, num_cols=()):
    h = "".join(f"<th>{c}</th>" for c in cab)
    b = "".join("<tr>" + "".join(f"<td class='num'>{v}</td>" if j in num_cols else f"<td>{v}</td>"
                                 for j, v in enumerate(f)) + "</tr>" for f in filas)
    return f"<table><tr>{h}</tr>{b}</table>"

def qa(preg, resp):
    return f"<div class='qa'><h3>{preg}</h3><p>{resp}</p></div>"

def lamina(n, quien, tiempo, texto, titulo=""):
    t = f" · {titulo}" if titulo else ""
    return (f"<div class='lamina'>Lámina {n}{t} <span>· {quien} ({tiempo})</span></div>"
            f"<div class='dialogo'>{texto}</div>")

# ================================================================== GUION
def guion():
    c = []
    c.append("<p class='cambio'><b>Versión corregida (04-10-2026).</b> Actualiza cifras y textos tras la revisión "
             "cruzada del equipo: período, exclusión por año de ingreso 1900, 69,8 %, sensibilidad de la modalidad, "
             "tarjetas del dashboard y limitaciones. Las cifras salen de las tablas generadas por R.</p>")
    c.append("<h2>Reparto</h2><p>Cada persona expone dos bloques seguidos, con una transición entre una y otra. "
             "Total: unos 9 minutos. Ignacio hace la demo porque es quien mejor conoce el dashboard y puede resolver "
             "cualquier problema en el momento.</p>")
    c.append(tabla(["Integrante", "Láminas", "Tiempo aprox."],
                   [["Ignacio", "1, 2, 7 (demo), 10", "3:30"], ["Miguel", "3, 4, 8", "3:00"], ["Johan", "5, 6, 9", "2:30"]]))
    c.append("<h2>Diálogos</h2>")
    c.append(lamina(1, "Ignacio", "0:15",
        f"“Buenas tardes. Somos Miguel Jorquera, Johan Matos e Ignacio Larama. Analizamos los casi 329 mil registros "
        f"de titulados 2025 del SIES para responder una pregunta concreta: quién se titula a tiempo y dónde se "
        f"concentra el atraso. Adelantamos el resultado principal: el {num(kg['pct'])} % de las titulaciones de "
        f"pregrado fue oportuna.”"))
    c.append(lamina(2, "Ignacio", "1:00",
        f"“Dicho al revés, casi 3 de cada 10 titulados terminan más de un año después de lo que dura su carrera. Eso "
        f"significa más arancel, una inserción laboral más tardía y, por lo general, una señal de problemas en la "
        f"práctica, la tesis o el examen de grado.<br><br>Definimos titulación oportuna como titularse dentro de la "
        f"duración teórica más un año. Usamos ese año de holgura porque muchas carreras exigen práctica o tesis "
        f"después de aprobar las asignaturas. Trabajamos el año académico 2025, que va de marzo de 2025 a febrero "
        f"de 2026.<br><br>La decisión que queremos apoyar es dónde focalizar recursos limitados de apoyo a la "
        f"titulación, y por eso la audiencia son las direcciones académicas. Definimos cuatro KPI: titulación "
        f"oportuna con una meta referencial del 75 %, la brecha entre tipos de institución, el atraso mediano y el "
        f"porcentaje que tarda más del doble.<br><br>Miguel va a explicar cómo preparamos los datos.”"))
    c.append(lamina(3, "Miguel", "1:15",
        f"“Partimos con {ent(chq['Registros totales'])} filas y 41 columnas, y terminamos con {ent(kg['n'])} "
        f"titulaciones válidas y 54 columnas. No todo lo que eliminamos era dato sucio: {ent(B['R1']['eliminadas'])} "
        f"filas salieron por alcance, porque eran de posgrado y postítulo; {ent(B['R2']['eliminadas'])} ingresaron "
        f"desde otra institución, por eso su año de ingreso viene con el código 1900 y no se puede medir cuánto "
        f"tardaron —eso lo declaramos como limitación—; y {ent(B['R7']['eliminadas'])} eran planes de continuidad, "
        f"donde el año de ingreso corresponde a otra carrera.<br><br>El hallazgo más importante de esta etapa fue un "
        f"error que casi cometimos. Una primera regla eliminaba el 18 % de la base. Al revisarla vimos que eran "
        f"titulaciones de enero y febrero de 2026, que corresponden al cierre del año académico 2025. Si las "
        f"hubiéramos excluido, el KPI habría bajado de {num(kg['pct'])} % a "
        f"{num(V['pct_oportuna_sin_ene_feb_2026'])} %.<br><br>Por privacidad eliminamos el MRUN y la fecha de "
        f"nacimiento, y todo el proceso queda registrado por código en una bitácora.”"))
    c.append(lamina(4, "Miguel", "1:00",
        f"“Como la respuesta es binaria, fuera de plazo o no, usamos regresión logística. Permite ver el efecto de "
        f"cada factor manteniendo constantes los demás. Tomamos cuatro decisiones para proteger la validez:<ul>"
        f"<li>Primero, usamos la edad al ingreso y no la edad al titularse, porque quien se atrasa llega con más edad "
        f"y eso invertiría la causalidad.</li><li>Segundo, agrupamos los errores por institución, porque los "
        f"estudiantes de una misma institución no son independientes.</li><li>Tercero, dejamos la duración teórica "
        f"fuera del modelo principal por colinealidad y la probamos aparte como análisis de sensibilidad.</li>"
        f"<li>Cuarto, validamos el modelo con datos que no vio: obtuvo un AUC de {num(met['AUC'], 2)} y una buena "
        f"calibración.</li></ul>Ese AUC indica que el modelo sirve para identificar factores asociados, no para "
        f"predecir qué estudiante se va a atrasar. Johan va a presentar los resultados.”"))
    c.append(lamina(5, "Johan", "0:45",
        f"“El {num(kg['pct'])} % se titula de forma oportuna, {num(abs(float(kg['brecha_meta_pp'])))} puntos bajo "
        f"la meta. Pero el promedio esconde brechas: en las carreras profesionales universitarias la cifra baja a "
        f"{num(peor_g['pct'])} %, casi 20 puntos menos que en las técnicas de IP. Y en Derecho solo el "
        f"{num(derecho['pct'])} % se titula a tiempo.<br><br>El color sigue la misma regla que el dashboard: naranja "
        f"solo cuando todo el intervalo de confianza está bajo la meta.”"))
    c.append(lamina(6, "Johan", "1:00",
        f"“Esta lámina muestra el efecto de cada factor manteniendo constantes los demás. Cada barra es el cambio en "
        f"la probabilidad de titularse fuera de plazo frente a una categoría de referencia.<br><br>Derecho tiene "
        f"{num(e('area_conocimiento', 'Derecho'), 0)} puntos más de probabilidad de atraso que Tecnología, y es el "
        f"efecto más grande y robusto. Las carreras de IP y las técnicas universitarias tienen entre "
        f"{num(abs(float(e('grupo_inst', 'IP · técnica'))), 0)} y "
        f"{num(abs(float(e('grupo_inst', 'Universidad · técnica'))), 0)} puntos menos de atraso que las profesionales "
        f"universitarias. La macrozona Norte tiene {num(e('macrozona', 'Norte'), 0)} puntos más, y las mujeres, "
        f"{num(abs(float(e('genero', 'Mujer'))), 0)} puntos menos.<br><br>Igual de importante es lo que no resultó "
        f"concluyente: la modalidad. En la comparación simple, la educación a distancia parecía mejor, pero al "
        f"controlar el perfil de sus estudiantes la diferencia desaparece. La categoría semipresencial queda en el "
        f"límite, con p = {num(semi['p_modelo_principal'], 3)}, así que no la tratamos como resultado. Insistimos en "
        f"que todo esto es asociación, no causalidad.<br><br>Ignacio va a mostrar el dashboard.”",
        "Derecho es el foco más claro; la modalidad no es concluyente"))
    c.append("<div class='lamina'>Lámina 7 · Demo <span>· Ignacio (2:00)</span></div>")
    c.append("<div class='dialogo'><b>Resumen:</b> “Arriba está la fila de tarjetas. Las cuatro métricas que definimos "
             "como KPI tienen su meta, unidad, período, fuente y fecha de actualización; las dos tarjetas marcadas "
             "«Contexto» —Derecho y el total analizado— ayudan a dimensionar, pero no son KPI. Los títulos de los "
             "gráficos dicen el hallazgo, no solo el tema: por ejemplo, ‘las carreras profesionales universitarias "
             "concentran el atraso’, o en el regional, que 4 de las 5 regiones más bajas son del norte.”"
             "<p class='accion'>(Ir a Factores asociados y pasar el mouse sobre la barra de Derecho)</p>"
             "<b>Factores asociados:</b> “Al pasar el cursor se ven el odds ratio y su intervalo. En gris aparece lo "
             "que no tiene diferencia significativa.”"
             "<p class='accion'>(Ir a Explorar: filtrar Área = Derecho y marcar Bajo la meta)</p>"
             "<b>Explorar instituciones:</b> “Aquí se baja a nivel de institución. En la esquina inferior derecha "
             "quedan las combinaciones con más titulados y menor porcentaje oportuno, que es donde una mejora tendría "
             "más impacto. La tabla se filtra junto con el gráfico, está ordenada por titulados fuera de plazo y se "
             "puede descargar en CSV.”"
             "<p class='accion'>(Ir a Datos y método)</p>"
             "<b>Datos y método:</b> “Por último, la trazabilidad: la definición de cada KPI, la bitácora de limpieza "
             "y las limitaciones. Miguel va a explicar qué no permiten afirmar estos datos.”</div>")
    c.append(lamina(8, "Miguel", "0:45",
        f"“Hay cuatro limitaciones. La más importante es el sesgo de supervivencia: la base solo tiene titulados, y "
        f"quien desertó no aparece, así que esto no es una tasa de titulación del sistema. Por eso el resultado de "
        f"la edad hay que leerlo con cautela: que los mayores de 30 se titulen más a tiempo probablemente se debe a "
        f"que los que se atrasan abandonan.<br><br>Además, el diseño es observacional y no incluye rendimiento, "
        f"trabajo ni financiamiento. Excluimos al {num(V['pct_r2_del_pregrado'])} % que ingresó desde otra "
        f"institución, porque no tenemos su año de ingreso real, y cada institución declara la duración a su "
        f"manera. Y trabajamos con un solo año, así que no se pueden ver tendencias.”"))
    c.append(lamina(9, "Johan", "0:45",
        "“Por eso las recomendaciones son proporcionales a la evidencia. Proponemos actuar donde el efecto es grande y "
        "robusto: diagnosticar el proceso de titulación en Derecho y hacer un piloto de acompañamiento en las "
        "carreras profesionales universitarias con más estudiantes. Proponemos investigar donde el efecto es "
        "moderado, como la macrozona Norte. Y no actuar aún donde la evidencia no es concluyente, como en la "
        "modalidad y en los CFT.<br><br>Para el monitoreo, todo el análisis se regenera con un solo script cuando "
        "salga la base del próximo año.”"))
    c.append(lamina(10, "Ignacio", "0:15",
        "“En resumen, el atraso no es parejo: se concentra en Derecho y en las carreras profesionales universitarias, "
        "y ahí conviene empezar. Quedamos atentos a sus preguntas.”"))

    c.append("<h2>Preguntas: quién responde</h2><p>Las respuestas están en las notas del PPT y en la guía de defensa. "
             "Cada tema lo responde quien lo expuso:</p><ul>"
             "<li><b>Miguel:</b> limpieza de datos, MRUN repetidos, exclusión del año 1900, por qué regresión "
             "logística y no un árbol, supuestos del modelo (anexos 11 y 12).</li>"
             "<li><b>Johan:</b> causalidad en Derecho, edad 30+, comparación entre carreras técnicas y profesionales, "
             "CFT y semipresencial (anexo 13).</li>"
             "<li><b>Ignacio:</b> holgura de un año, meta del 75 %, flexdashboard vs. Shiny, celdas ocultas, KPI vs. "
             "tarjetas de contexto.</li></ul>")
    c.append("<h3>Preguntas adicionales (no están en las notas)</h3>")
    c.append(qa("¿Qué sentido tiene un intervalo de confianza si tienen a todos los titulados?",
        "“La base es un censo de 2025, pero nos interesa el proceso que genera las titulaciones, no solo ese año. El "
        "intervalo refleja la variabilidad esperable de un año a otro, que es lo relevante para decidir.”"))
    c.append(qa("¿Excluir a quienes ingresaron desde otra institución no sesga el resultado?",
        f"“Puede sesgarlo, y por eso lo declaramos como limitación. Son {ent(V['n_r2_codigo_1900'])} titulaciones, el "
        f"{num(V['pct_r2_del_pregrado'])} % del pregrado. Su año de ingreso viene como 1900, así que no podemos "
        f"calcular cuánto tardaron. Si se atrasan más que el resto, nuestro KPI estaría algo sobreestimado. Una "
        f"mejora sería usar el año de ingreso a la carrera actual, que sí viene en la base.”"))
    c.append("<div class='ok'><b>Resuelto: la nota de la lámina 5.</b> La versión anterior de este guion advertía "
             "que no se había verificado si la conclusión sobre las universidades profesionales se mantiene al agregar "
             "la duración teórica. <b>Ya está verificado en modelo_sensibilidad.csv:</b> con la duración incluida, "
             f"IP profesional (OR {num(ipp['OR_con_duracion'], 2)}), IP técnica (OR {num(ipt['OR_con_duracion'], 2)}) "
             f"y Universidad técnica (OR {num(ut['OR_con_duracion'], 2)}) siguen siendo significativas frente a la "
             "universidad profesional, e incluso se alejan más de 1. Se puede decir con confianza.</div>")
    return documento("Guion de presentación",
                     "Titulación oportuna en pregrado · Chile 2025 · Minería de Datos TI3V61", "".join(c))

# ================================================================== GUÍA DE DEFENSA
def guia():
    c = []
    c.append("<p><b>Cómo usar esta guía.</b> Las respuestas están escritas para decirlas en voz alta, no para leerlas. "
             "Primero memoricen las cifras de la sección 1; casi todas las preguntas de limpieza se responden con "
             "ellas. Si no saben algo, digan qué harían para averiguarlo; es mejor que inventar.</p>")
    c.append("<p class='cambio'><b>Versión corregida (04-10-2026).</b> Cambios: período mar-2025–feb-2026; la regla "
             "R2 solo excluye el código 1900 (ingreso desde otra institución) y se declara como limitación; 69,8 % "
             "(antes 67,7 %); 13 semestres en planes de continuidad; sensibilidad con semipresencial; tarjetas KPI y "
             "de contexto del dashboard. Las cifras salen de las tablas generadas por R.</p>")

    c.append("<h2>1. Cifras que deben saber de memoria</h2>")
    c.append(tabla(["Dato", "Valor", "Para qué sirve"], [
        ["Período", f"Año académico 2025: titulaciones del {V['primera_fecha']} al {V['ultima_fecha']}",
         "Marzo a febrero, como el calendario académico chileno"],
        ["Filas originales", f"{ent(chq['Registros totales'])} × 41 columnas", "Tamaño del CSV del SIES"],
        ["Filas finales", f"{ent(kg['n'])} × 54 columnas", "Base de pregrado limpia"],
        ["Total eliminado", f"{ent(total_elim)} filas ({num(pct_elim)} %)", "Suma de R1 + R2 + R7"],
        ["…por alcance (R1)", f"{ent(B['R1']['eliminadas'])} (posgrado y postítulo)", "No son errores: quedan fuera de la pregunta"],
        ["…por ingreso desde otra institución (R2)",
         f"{ent(B['R2']['eliminadas'])} (año de ingreso 1900; {num(V['pct_r2_del_pregrado'])} % del pregrado)",
         "Sin año real no se mide la duración. Exclusión no aleatoria: limitación declarada"],
        ["…por planes de continuidad (R7)", ent(B["R7"]["eliminadas"]),
         f"Ingreso de otra carrera: mediana {V['mediana_sem_continuidad']} semestres vs {V['mediana_teorica_continuidad']} teóricos"],
        ["Columnas", "−4 (mrun, fec_nac_alu, nombre_titulo, nombre_grado) y +17 derivadas", "41 − 4 + 17 = 54"],
        ["Error que casi cometimos", "40.522 filas (18 %) de ene–feb 2026",
         f"Sin ellas el KPI sería {num(V['pct_oportuna_sin_ene_feb_2026'])} %"],
        ["MRUN repetidos", f"{ent(chq['MRUN con más de un título (registros adicionales)'])} (personas con más de un título)",
         "No se eliminan: la unidad es la titulación"],
        ["MRUN vacíos", ent(chq["Registros con MRUN vacío"]), "Se informan, no se eliminan"],
        ["Titulación oportuna", f"{num(kg['pct'])} % (IC 95 %: {num(kg['ic_inf'])}–{num(kg['ic_sup'])})", "KPI principal; meta 75 %"],
        ["Criterio estricto (sin holgura)", f"{num(kg['pct_estricto'])} %", "Por eso usamos +2 semestres"],
        ["Fuera de plazo", f"{num(prev_fuera)} %", "Prevalencia de la variable respuesta"],
        ["Brecha", f"{pp(float(peor_g['pct']) - float(mejor_g['pct']))} (Univ. profesional {num(peor_g['pct'])} % vs IP técnica {num(mejor_g['pct'])} %)", "KPI 2"],
        ["Mediana de atraso / más del doble", f"{ent(kg['mediana_sobreduracion'])} semestre / {num(kg['pct_mas_doble'])} %", "KPI 3 y 4"],
        ["Derecho", f"{num(derecho['pct'])} % oportuna; {pp(e('area_conocimiento', 'Derecho'))} en el modelo; OR {num(oD['OR'], 2)}", "Hallazgo más fuerte"],
        ["Modelo", f"{ent(n_mod)} registros (1 excluido por NA de edad)", "Regresión logística"],
        ["AUC / Brier", f"{num(met['AUC'], 3)} / {num(met['Brier'], 3)} vs {num(met['Brier_referencia'], 3)} (mejora {num(met['mejora_Brier_pct'])} %)", "Validación en 30 % de prueba"],
        ["VIF máx. / dispersión / pseudo R²", f"{num(vif_max, 2)} / {num(aj['ratio_dispersion'], 2)} / {num(aj['pseudo_R2_McFadden'], 3)}", "Diagnósticos"],
        ["Celda mínima del dashboard", "30 titulados", "Estabilidad y privacidad"],
    ]))

    c.append("<h2>2. Pipeline y reproducibilidad</h2>")
    c.append(qa("¿Qué es un pipeline?", "Es una cadena de pasos automatizados donde la salida de uno es la entrada del "
        "siguiente. En nuestro caso, <code>run_all.R</code> ejecuta seis scripts en orden: carga → calidad → descriptivo "
        "→ modelo → datos del dashboard → render. Si llega la base 2026, se ejecuta el mismo script y se regenera todo: "
        "tablas, figuras, modelo y dashboard."))
    c.append(tabla(["Script", "Entrada", "Qué hace", "Salida"], [
        ["01_carga.R", "CSV original", "Lee con tipos explícitos y verifica el hash SHA-256", "00_titulados_raw.rds"],
        ["02_calidad.R", "00_…raw.rds", "Perfilado, reglas R1–R8, variables derivadas, privacidad", "01_titulados_pregrado.rds + bitácora"],
        ["03_descriptivo.R", "01_…pregrado.rds", "KPI con IC de Wilson y figuras", "kpi_*.csv, fig_*.png"],
        ["04_modelo.R", "01_…pregrado.rds", "Regresión logística, diagnósticos, validación, sensibilidad", "modelo_*.csv, 02_modelo_resumen.rds"],
        ["05_datos_dashboard.R", "tablas y modelo", "Agrega datos (celdas ≥ 30)", "datos_dashboard.rds"],
        ["06_render_dashboard.R", "datos_dashboard.rds", "Genera el HTML", "dashboard_titulacion.html"],
    ]))
    c.append(qa("¿Qué significa que sea reproducible?", "Que cualquier persona, con el CSV original y el código, obtiene "
        "exactamente los mismos números. Para eso: el archivo original no se modifica, todo cambio se hace por código, la "
        "partición aleatoria usa semilla fija (<code>set.seed(2025)</code>) y se guarda <code>sessionInfo()</code> con las "
        "versiones de R y paquetes."))
    c.append(qa("¿Qué es el hash SHA-256 y para qué lo usan?", "Es una “huella digital” del archivo: si cambia un solo "
        "carácter, el hash cambia completo. Lo calculamos con <code>digest::digest()</code> y lo comparamos con el "
        "registrado; así garantizamos que todos trabajamos con la misma versión del CSV."))
    c.append(qa("¿Por qué guardan archivos .rds intermedios?", "RDS es el formato nativo de R: guarda el objeto con sus "
        "tipos (factores, fechas) y se lee mucho más rápido que el CSV de 188 MB. Además, cada etapa puede ejecutarse por "
        "separado sin repetir todo lo anterior."))
    c.append(qa("¿Por qué los datos originales no están en GitHub?", "Por tamaño (188 MB) y porque contienen datos "
        "personales (MRUN y fecha de nacimiento). El README explica cómo obtenerlos y verificar el hash."))

    c.append("<h2>3. Carga de datos</h2>")
    c.append(qa("¿Con qué función leyeron el archivo y por qué así?", "Con <code>read_delim()</code> de readr, con "
        "separador punto y coma, codificación UTF-8 y tipos de columna explícitos. Los códigos se leen como texto para no "
        "perder ceros a la izquierda ni convertir valores especiales en números “válidos”."))
    c.append("<pre>read_delim(ruta_raw, delim = \";\",\n           col_types = tipos,\n           locale = locale(encoding = \"UTF-8\"),\n           na = c(\"\", \"NA\"))</pre>")
    c.append(qa("¿Qué es el encoding y por qué el texto se veía como “Ã±”?", "El encoding es la tabla que traduce bytes a "
        "caracteres. El archivo está en UTF-8; si se abre como Latin-1 (por ejemplo, en Excel sin indicarlo), la “ñ” "
        "aparece como “Ã±”. En R lo leímos declarando UTF-8, por eso se ve bien."))
    c.append(qa("¿Qué es el perfilado de datos?", "Revisar cada variable antes de limpiar: tipo, cantidad de vacíos, "
        "porcentaje de vacíos, valores distintos y un ejemplo (salvo en MRUN y fecha de nacimiento, donde el ejemplo se "
        "omite por privacidad). Se guarda en <code>perfil_variables.csv</code>. Sirve para decidir qué reglas aplicar."))

    c.append("<h2>4. Limpieza: qué eliminamos, cómo y por qué</h2>")
    c.append(qa("¿Cuántas filas eliminaron y por qué?", f"{ent(total_elim)} de {ent(chq['Registros totales'])} "
        f"({num(pct_elim)} %). Ninguna por ser un error de digitación. {ent(B['R1']['eliminadas'])} salieron por "
        f"alcance, porque la pregunta es sobre pregrado; {ent(B['R2']['eliminadas'])} porque ingresaron desde otra "
        f"institución y su año de ingreso viene como 1900, lo que impide medir la duración; y "
        f"{ent(B['R7']['eliminadas'])} por validez de medición, porque en los planes de continuidad el año de ingreso es "
        f"de otra carrera."))
    c.append(qa("¿Cómo filtraron? ¿Qué función usaron?", "Con <code>filter()</code> de dplyr, dentro de una función "
        "propia, <code>aplicar_regla()</code>, que cuenta las filas antes y después y registra cada regla en una bitácora. "
        "Para las condiciones usamos <code>between()</code> (rango), <code>%in%</code> (pertenece a un conjunto) y "
        "<code>grepl()</code> (patrón de texto)."))
    c.append("<pre>aplicar_regla(\"R2\", \"Validez\",\n  \"Año de ingreso entre 1950 y 2025 (en pregrado solo aparece el código 1900)\",\n  between(anio_ing_carr_ori, 1950L, 2025L))</pre>")
    cond = {"R1": 'nivel_global == "Pregrado"', "R2": "between(anio_ing_carr_ori, 1950, 2025)",
            "R3": "sem_ing_carr_ori %in% c(1, 2)", "R4": "Fecha AAAAMMDD entre 20250301 y 20260228",
            "R5": "dur_total_carr > 0", "R6": "sem_transcurridos >= 1",
            "R7": 'tipo_plan_carr != "Plan Regular de Continuidad"',
            "R8": "select(-mrun, -fec_nac_alu, -nombre_titulo, -nombre_grado)"}
    c.append(tabla(["Regla", "Dimensión", "Condición", "Eliminadas"],
                   [[b["paso"], b["dimension"], f"<code>{escape(cond[b['paso']])}</code>",
                     ent(b["eliminadas"]) + (" (columnas)" if b["paso"] == "R8" else "")] for b in bit], (3,)))
    c.append(qa("Si R3 a R6 eliminaron cero filas, ¿para qué están?", "Son verificaciones. Demuestran que el dato cumple "
        "la regla; si una base futura trae errores, la regla los detecta sola."))
    c.append(qa("¿Qué significa el año de ingreso 1900?", f"Según el diccionario del SIES, 1900 (o 9999) indica “otro "
        f"programa desde otra institución”: la persona ingresó a su carrera actual viniendo de otra institución. En "
        f"nuestra base de pregrado es el <b>único</b> código especial que aparece ({ent(V['n_r2_codigo_1900'])} "
        f"registros). No es un año real, así que no permite calcular cuánto tardó la persona, y por eso se excluye. Como "
        f"la exclusión no es al azar, la declaramos como limitación."))
    c.append(qa("¿Excluir ese grupo no sesga el KPI?", f"Puede. Son el {num(V['pct_r2_del_pregrado'])} % del pregrado. "
        "Si quienes se cambian de institución se atrasan más que el resto, el KPI estaría algo sobreestimado; si se "
        "atrasan menos, subestimado. Como mejora, se podría usar el año de ingreso a la carrera actual "
        "(<code>anio_ing_carr_act</code>), que sí viene en la base."))
    c.append(qa("¿Por qué no eliminaron los MRUN repetidos? ¿No son duplicados?", f"No. Son "
        f"{ent(chq['MRUN con más de un título (registros adicionales)'])} personas con más de un título (por ejemplo, "
        "técnico y luego ingeniería). La unidad de análisis es la titulación, no la persona."))
    c.append(qa("¿Qué pasó con las fechas de 2026?", "La primera versión de R4 aceptaba solo fechas de 2025 y eliminaba "
        "40.522 filas. Al explorarlas (script x01) vimos que todas eran de enero y febrero de 2026, que en Chile es el "
        f"cierre del año académico 2025. Corregimos la regla. Sin esa corrección, el KPI habría bajado a "
        f"{num(V['pct_oportuna_sin_ene_feb_2026'])} %. Además, en la base no hay titulaciones de enero ni febrero de "
        f"2025: el año académico va de marzo de 2025 a febrero de 2026."))
    c.append(qa("¿Eliminaron valores atípicos (outliers)?", "No. Se marcan con la variable <code>atipico_duracion</code> "
        "(tarda más del triple de lo teórico) pero se conservan. La respuesta del modelo es binaria, así que un caso "
        "extremo cuenta igual que uno de 3 semestres de atraso y no distorsiona los coeficientes."))
    c.append(qa("¿Cómo protegieron los datos personales?", "Minimización: eliminamos MRUN y fecha de nacimiento antes de "
        "guardar la base procesada; la edad solo queda en tramos. El dashboard muestra solo datos agregados y oculta "
        "combinaciones con menos de 30 titulados."))
    c.append(qa("¿Qué norma usaron para las reglas de calidad?", "ISO/IEC 25012, con sus dimensiones de completitud (¿falta "
        "el dato?), validez (¿está en el rango o formato permitido?), consistencia (¿es coherente con otros datos?, por "
        "ejemplo titularse después de ingresar) y trazabilidad (¿se puede reconstruir qué se hizo?)."))

    c.append("<h2>5. Valores faltantes: NA, NaN y vacíos</h2>")
    c.append(qa("¿Qué es un NA?", "En R, NA (Not Available) significa “dato faltante”: el valor existe en la realidad pero "
        "no lo tenemos. Cualquier operación con NA da NA, por eso se usa <code>na.rm = TRUE</code> en funciones como "
        "<code>sum()</code> o <code>mean()</code>."))
    c.append(qa("¿Qué es un NaN? ¿Es lo mismo?", "NaN (Not a Number) es el resultado de una operación matemática "
        "indefinida, como 0/0. No es un dato faltante, es un cálculo imposible. <code>is.na()</code> devuelve TRUE para "
        "ambos; <code>is.nan()</code> solo para NaN. En Python/pandas, en cambio, NaN se usa también como faltante."))
    c.append(tabla(["Valor", "Significado", "Ejemplo", "Cómo se detecta"], [
        ["NA", "Dato faltante", "Rango de edad desconocido", "<code>is.na(x)</code>"],
        ["NaN", "Operación indefinida", "0 / 0", "<code>is.nan(x)</code>"],
        ["NULL", "Objeto vacío, no existe", "Una lista sin elementos", "<code>is.null(x)</code>"],
        ['""', "Texto vacío", "nombre_titulo sin texto en el CSV", '<code>x == ""</code>'],
        ["Código especial", "Faltante disfrazado de número", "1900 en año de ingreso", "Regla de rango (R2)"],
    ]))
    c.append(qa("¿Qué hicieron con los faltantes en su base?", f"Depende de la variable. Al leer, los textos vacíos se "
        f"convierten en NA (<code>na = c(\"\", \"NA\")</code>). Los {ent(chq[chr(82) + 'ango de edad ' + chr(39) + 'Sin Información' + chr(39)])} "
        f"“Sin Información” de rango de edad se convierten en NA con <code>na_if()</code>. El código 1900 del año de "
        f"ingreso se excluye con R2. Para el modelo, <code>drop_na()</code> excluyó 1 registro sin edad de ingreso. No "
        f"imputamos (no inventamos valores) porque el volumen afectado en el modelo es mínimo."))
    c.append(qa("¿Qué es imputar y por qué no lo hicieron?", "Imputar es rellenar faltantes con un valor estimado (media, "
        "mediana, modelo). Solo conviene cuando hay muchos faltantes; en el modelo era 1 registro de 216 mil, así que "
        "eliminarlo no cambia nada. El caso del año 1900 es distinto: no es un faltante al azar sino otro tipo de "
        "trayectoria, por eso no se imputa y se declara como limitación."))

    c.append("<h2>6. Variables derivadas</h2>")
    c.append(qa("¿Cómo calcularon si alguien se tituló a tiempo?", "La base no trae esa variable. Convertimos ingreso y "
        "titulación a “semestres académicos” y contamos los transcurridos, ambos inclusive. Marzo a julio es primer "
        "semestre; agosto a febrero, segundo. Oportuna = semestres transcurridos ≤ duración teórica + 2."))
    c.append("<pre>sem_transcurridos = (anio_tit*2 + sem_tit) - (anio_ing*2 + sem_ing) + 1\ntitulacion_oportuna = sem_transcurridos <= dur_total_carr + 2</pre>")
    c.append(qa("Den un ejemplo.", "Ingreso en el primer semestre de 2021 y titulación en enero de 2026, que cuenta como "
        "segundo semestre de 2025: son 10 semestres. Si la carrera dura 10 semestres teóricos, es oportuna incluso sin "
        "holgura."))
    c.append(qa("¿Qué funciones usaron para crear variables?", "<code>mutate()</code> para crear columnas; "
        "<code>if_else()</code> para condiciones simples; <code>case_when()</code> para varias condiciones (macrozona, "
        "modalidad); <code>cut()</code> para crear tramos de edad; <code>recode()</code> para renombrar categorías; "
        "<code>as.Date()</code> para convertir la fecha."))
    c.append(qa("¿Por qué combinaron jornada y modalidad?", "Porque “A Distancia” (jornada) y “No Presencial” (modalidad) "
        "son exactamente los mismos registros. Si se usan las dos, el modelo tiene colinealidad perfecta y no puede "
        "estimarse."))
    c.append(qa("¿Por qué la edad al ingreso y no la edad al titularse?", "Porque quien se atrasa llega más viejo a "
        "titularse: la edad al titularse sería consecuencia del atraso, no causa (causalidad inversa). La calculamos antes "
        "de borrar la fecha de nacimiento."))

    c.append("<h2>7. Análisis descriptivo e intervalos de confianza</h2>")
    c.append(qa("¿Qué es un intervalo de confianza?", f"El rango donde esperamos que esté el valor real con 95 % de "
        f"confianza. {num(kg['pct'])} % con IC {num(kg['ic_inf'])}–{num(kg['ic_sup'])} % significa que la estimación es "
        f"muy precisa."))
    c.append(qa("¿Por qué el método de Wilson?", "Para proporciones es más exacto que la fórmula normal clásica, sobre "
        "todo con grupos pequeños o porcentajes cercanos a 0 o 100 %, donde la fórmula clásica puede dar límites fuera "
        "de rango."))
    c.append(qa("¿Qué sentido tiene un IC si tienen a todos los titulados?", "La base es un censo de 2025, pero nos "
        "interesa el proceso que genera las titulaciones, no solo ese año. El intervalo refleja la variabilidad esperable "
        "de un año a otro."))
    c.append(qa("¿Por qué la mediana y no el promedio del atraso?", "Porque la distribución es asimétrica: unos pocos "
        "casos tardan muchísimo y subirían el promedio. La mediana representa mejor el caso típico."))
    c.append(qa("¿Cuál es la diferencia entre % y pp?", f"pp (puntos porcentuales) es la resta entre dos porcentajes: de "
        f"{num(peor_g['pct'])} % a {num(mejor_g['pct'])} % hay {num(float(mejor_g['pct']) - float(peor_g['pct']))} pp. "
        f"Decir “{num(float(mejor_g['pct']) - float(peor_g['pct']))} %” sería un error, porque eso es un cambio relativo."))
    c.append(qa("¿Por qué la meta es 75 %?", "Es referencial, definida por el equipo, porque no existe un estándar oficial "
        "único. Lo declaramos explícitamente en el informe y en el dashboard."))

    c.append("<h2>8. El modelo: regresión logística</h2>")
    c.append(qa("¿Por qué regresión logística y no lineal?", "Porque la respuesta es binaria (fuera de plazo: sí o no). "
        "Una regresión lineal puede predecir probabilidades menores que 0 o mayores que 1; la logística las mantiene "
        "entre 0 y 1."))
    c.append("<pre>glm(fuera_de_plazo ~ grupo_inst + area_conocimiento + modalidad_jornada +\n    macrozona + tramo_edad_ingreso + genero + tipo_plan_carr +\n    declara_proceso_tit, family = binomial())</pre>")
    c.append(qa("¿Qué es un odds y un odds ratio?", f"El odds es la probabilidad de que ocurra dividida por la de que no "
        f"ocurra: con {num(prev_fuera)} % de atraso, el odds es {num(prev_fuera / 100, 2)}/{num(1 - prev_fuera / 100, 2)} "
        f"≈ {num(odds_atraso, 2)}. El odds ratio compara dos grupos: OR {num(oD['OR'], 2)} en Derecho significa que el "
        f"odds de atrasarse es {num(oD['OR'], 1)} veces el de Tecnología. OR = 1: sin diferencia; mayor que 1: más "
        f"riesgo; menor que 1: menos riesgo."))
    c.append(qa("¿Qué es la categoría de referencia?", "El grupo contra el que se compara cada categoría. Elegimos el más "
        "numeroso (Universidad profesional, Tecnología, Presencial diurna, Metropolitana…) con <code>relevel()</code>."))
    c.append(qa("¿Qué es el efecto marginal en pp?", f"Es traducir el OR a algo entendible: la probabilidad media predicha "
        f"si todos fueran de una categoría menos la de la referencia, manteniendo lo demás. Derecho: "
        f"{pp(e('area_conocimiento', 'Derecho'))}."))
    c.append(qa("¿Qué es el p-valor? ¿Qué significa “significativo”?", f"Es la probabilidad de observar una diferencia así "
        f"si en realidad no hubiera ninguna. Si es menor que 0,05, decimos que es significativo. Con 216 mil registros "
        f"casi todo resulta significativo, por eso miramos la magnitud. Un p-valor como el de semipresencial "
        f"({num(semi['p_modelo_principal'], 3)}) está en el límite: no conviene sacar conclusiones de él."))
    c.append(qa("¿Qué son los errores agrupados por institución?", "Los estudiantes de una misma institución se parecen "
        "entre sí (mismos procesos y reglamentos), así que no son independientes. Ignorarlo haría los intervalos "
        "artificialmente estrechos. Usamos <code>vcovCL()</code> de sandwich y <code>coeftest()</code> de lmtest."))
    c.append(qa("¿Qué es la multicolinealidad y cómo la revisaron?", f"Ocurre cuando dos predictores dicen casi lo mismo y "
        f"el modelo no puede separar sus efectos. Se mide con el VIF (<code>car::vif()</code>). Nuestro máximo ajustado "
        f"fue {num(vif_max, 2)}, muy bajo. La duración teórica tenía VIF 8,7, por eso quedó fuera del modelo principal."))
    c.append(qa("¿Qué es la sobredispersión?", f"Cuando la variabilidad real es mayor que la que supone el modelo. Se mide "
        f"con chi-cuadrado de Pearson dividido por los grados de libertad; nos dio {num(aj['ratio_dispersion'], 2)}, que "
        f"es lo esperado (≈ 1)."))
    c.append(qa("¿Qué es una variable de confusión?", "Una variable que influye en el factor y en el resultado a la vez. "
        "Ejemplo: la modalidad a distancia parecía mejor, pero al controlar el perfil de los estudiantes la diferencia "
        "desapareció."))
    c.append(qa("¿Por qué no usaron un árbol de decisión u otro modelo de machine learning?", "Porque el objetivo es "
        "explicar, no predecir: necesitamos cuantificar el efecto de cada factor con su incertidumbre, y la logística "
        "entrega odds ratio e intervalos interpretables."))

    c.append("<h2>9. Validación del modelo</h2>")
    c.append(qa("¿Qué es la partición 70/30 y para qué sirve?", "Entrenamos con 70 % de los datos y evaluamos en el 30 % "
        "que el modelo no vio. Así detectamos sobreajuste (overfitting): un modelo que memoriza en vez de generalizar."))
    c.append(qa("¿Qué es la semilla (set.seed)?", "Fija el generador de números aleatorios para que la partición sea "
        "siempre la misma y los resultados se puedan reproducir."))
    c.append(qa("¿Qué es el AUC?", f"El área bajo la curva ROC. Es la probabilidad de que el modelo asigne más riesgo a un "
        f"atrasado que a uno a tiempo, ambos elegidos al azar. 0,5 = azar; 1 = perfecto. Nuestro {num(met['AUC'], 2)} es "
        f"moderado: sirve para identificar factores, no para predecir casos individuales."))
    c.append(qa("¿Qué es el puntaje de Brier?", f"El error cuadrático medio entre la probabilidad predicha y lo que ocurrió "
        f"(0 o 1). Más bajo es mejor. Nos dio {num(met['Brier'], 3)} frente a {num(met['Brier_referencia'], 3)} de un "
        f"modelo sin predictores: {num(met['mejora_Brier_pct'])} % de mejora."))
    c.append(qa("¿Qué es la calibración?", "Si el modelo dice 30 % de riesgo, ¿se atrasa realmente cerca del 30 %? Lo "
        "revisamos por deciles: los puntos quedaron cerca de la diagonal."))
    c.append(qa(f"¿Qué es el pseudo R² de McFadden y por qué es tan bajo ({num(aj['pseudo_R2_McFadden'], 3)})?",
        "Mide cuánto mejora el modelo frente a uno sin predictores. En datos individuales con respuesta binaria siempre "
        "es bajo, porque mucho del atraso depende de factores que la base no tiene (rendimiento, trabajo)."))
    c.append(qa("¿Qué es el análisis de sensibilidad y qué encontraron?", f"Repetir el modelo con otra especificación "
        f"para ver si las conclusiones se mantienen. Al agregar la duración teórica: área, género, edad, macrozona y la "
        f"ventaja de IP y técnicas universitarias frente a la universidad profesional <b>no cambian</b> (siguen "
        f"significativas, con OR de {num(ipp['OR_con_duracion'], 2)} a {num(ut['OR_con_duracion'], 2)}). Sí cambian dos "
        f"cosas: <b>CFT</b> pasa de no significativo (OR {num(cft['OR_modelo_principal'], 2)}) a significativo "
        f"(OR {num(cft['OR_con_duracion'], 2)}), y <b>semipresencial u otra</b> pasa de p = "
        f"{num(semi['p_modelo_principal'], 3)} a {num(semi['p_con_duracion'], 3)}. El plan especial cambia de "
        f"dirección, pero no es significativo en ninguno. Por eso no recomendamos actuar sobre esos resultados."))

    c.append("<h2>10. Interpretación y limitaciones</h2>")
    c.append(qa("¿Estudiar Derecho causa el atraso?", "No podemos afirmarlo. Es una asociación en datos observacionales. "
        "Es coherente con un proceso de titulación largo (memoria y examen de grado), pero hace falta un diagnóstico."))
    c.append(qa("¿Qué es el sesgo de supervivencia?", "La base solo tiene a quienes se titularon; los que desertaron no "
        "aparecen. Por eso el KPI no es una tasa de titulación del sistema. Explica también por qué quienes ingresan con "
        "30+ parecen más puntuales: los que se atrasan tienden a abandonar."))
    c.append(qa("¿Cómo resolverían esa limitación?", "Cruzando con las bases de matrícula del SIES para seguir cohortes "
        "completas, incluyendo a quienes desertan."))
    c.append(qa("¿Cuáles son todas las limitaciones?", f"Sesgo de supervivencia; asociación y no causalidad; exclusión del "
        f"{num(V['pct_r2_del_pregrado'])} % que ingresó desde otra institución; duración teórica declarada de forma "
        f"distinta entre instituciones; un solo año; variables omitidas (rendimiento, trabajo, financiamiento); y los "
        f"resultados no se extrapolan a posgrado ni a otros países."))
    c.append(qa("¿Por qué excluyeron la duración teórica del modelo?", "VIF de 8,7 y, al estar ligada al tipo de carrera, "
        "obliga a comparar técnicas y profesionales de igual duración, una combinación que no existe en los datos "
        "(extrapolación)."))
    c.append(qa("¿Qué significa “recomendaciones proporcionales a la evidencia”?", "Actuar donde el efecto es grande y "
        "robusto (Derecho, profesionales universitarias), investigar donde es moderado (Norte) y no actuar donde la "
        "evidencia no es concluyente (modalidad, CFT), considerando el costo de equivocarse."))

    c.append("<h2>11. Dashboard</h2>")
    c.append(qa("¿Por qué flexdashboard y no Shiny?", "Genera un solo archivo HTML que se abre sin R ni servidor; los "
        "filtros funcionan en el navegador con crosstalk. No necesitamos recalcular el modelo en vivo."))
    c.append(qa("¿Qué paquetes usaron y para qué?", "flexdashboard: estructura de páginas y tarjetas. plotly: gráficos "
        "interactivos. crosstalk: filtros que conectan gráfico y tabla. DT: tablas con búsqueda y descarga CSV. "
        "rmarkdown: genera el HTML. dplyr y knitr: preparar datos y la tabla de la bitácora."))
    c.append(qa("¿Por qué hay cinco tarjetas si definieron cuatro KPI?", "Porque dos tarjetas son de contexto y están "
        "marcadas como «Contexto»: el área más crítica (Derecho) y el volumen de titulaciones analizadas. Ayudan a "
        "dimensionar el problema, pero no son KPI. Los KPI son titulación oportuna, brecha, mediana de atraso y % que "
        "tarda más del doble (este último aparece dentro de la tarjeta de la mediana)."))
    c.append(qa("¿Por qué no usaron un velocímetro (gauge) para el KPI?", "Lo probamos, pero el componente de "
        "flexdashboard muestra los decimales con punto (71.8 %) y el resto del panel usa coma. Lo reemplazamos por una "
        "tarjeta con la meta y el intervalo de confianza, para mantener un formato coherente."))
    c.append(qa("¿Qué dice el gráfico por región?", "Que 4 de las 5 regiones más bajas son del norte; la más baja es Los "
        f"Ríos. Es coherente con el modelo, donde la macrozona Norte tiene {pp(e('macrozona', 'Norte'))} de atraso "
        f"ajustado ({'OR ' + num(oN['OR'], 2)})."))
    c.append(qa("¿Por qué hay celdas ocultas?", "Las combinaciones con menos de 30 titulados tienen porcentajes "
        "inestables y aumentan el riesgo de reidentificar personas."))
    c.append(qa("¿Qué significan los colores?", "Naranja: todo el IC 95 % está bajo la meta. Azul: en o sobre la meta. "
        "Gris: el intervalo cruza la meta (no concluyente). La misma regla en todas las páginas."))
    c.append(qa("¿Cómo es accesible?", "Paleta validada para daltonismo, el color nunca es la única señal (hay etiquetas "
        "y leyendas), contraste suficiente y valores disponibles en tablas."))

    c.append("<h2>12. Funciones de R que usaron</h2>")
    c.append(tabla(["Función", "Paquete", "Para qué"], [
        ["<code>read_delim()</code>", "readr", "Leer el CSV con separador ;"],
        ["<code>digest()</code>", "digest", "Calcular el hash SHA-256"],
        ["<code>filter()</code>", "dplyr", "Quedarse con filas que cumplen una condición"],
        ["<code>select()</code>", "dplyr", "Elegir o eliminar columnas"],
        ["<code>mutate()</code>", "dplyr", "Crear o modificar columnas"],
        ["<code>if_else()</code> / <code>case_when()</code>", "dplyr", "Condiciones simples / múltiples"],
        ["<code>between()</code> / <code>%in%</code>", "dplyr / base", "Rango / pertenencia a un conjunto"],
        ["<code>grepl()</code>", "base", "Buscar un patrón de texto (formato de fecha)"],
        ["<code>na_if()</code> / <code>drop_na()</code>", "dplyr / tidyr", "Convertir un valor en NA / eliminar filas con NA"],
        ["<code>group_by()</code> + <code>summarise()</code>", "dplyr", "Calcular KPI por grupo"],
        ["<code>n()</code> / <code>n_distinct()</code>", "dplyr", "Contar filas / valores distintos"],
        ["<code>cut()</code>", "base", "Crear tramos (edad)"],
        ["<code>relevel()</code> / <code>factor()</code>", "base", "Fijar la categoría de referencia"],
        ["<code>glm(family = binomial())</code>", "stats", "Regresión logística"],
        ["<code>vcovCL()</code> / <code>coeftest()</code>", "sandwich / lmtest", "Errores agrupados y pruebas"],
        ["<code>vif()</code>", "car", "Multicolinealidad"],
        ["<code>roc()</code> / <code>ci.auc()</code>", "pROC", "AUC y su intervalo"],
        ["<code>predict(type = \"response\")</code>", "stats", "Probabilidades predichas"],
        ["<code>set.seed()</code> / <code>sample()</code>", "base", "Partición aleatoria reproducible"],
        ["<code>ggplot()</code> / <code>ggsave()</code>", "ggplot2", "Gráficos y guardarlos en PNG"],
        ["<code>saveRDS()</code> / <code>readRDS()</code>", "base", "Guardar y leer objetos de R"],
        ["<code>write_csv()</code>", "readr", "Exportar tablas"],
        ["<code>rmarkdown::render()</code>", "rmarkdown", "Generar el dashboard HTML"],
        ["<code>|&gt;</code>", "base", "Pipe: pasa el resultado al paso siguiente"],
    ]))

    c.append("<h2>13. Glosario rápido</h2>")
    c.append(tabla(["Concepto", "Definición corta"], [
        ["Dataset / base", "Conjunto de datos; aquí, una fila por titulación"],
        ["Observación / registro", "Una fila"], ["Variable", "Una columna (característica medida)"],
        ["Unidad de análisis", "Qué representa cada fila: la titulación"],
        ["Variable respuesta", "Lo que se quiere explicar: fuera de plazo (0/1)"],
        ["Variable explicativa", "Factores que se asocian a la respuesta"],
        ["Variable categórica / factor", "Toma categorías (área, región), no números"],
        ["KPI", "Indicador clave con meta, unidad, período y fuente"],
        ["Indicador de contexto", "Dato que ayuda a dimensionar, sin meta propia (no es KPI)"],
        ["Censo vs muestra", "Toda la población vs una parte"],
        ["Prevalencia", f"% de casos con el evento ({num(prev_fuera)} % fuera de plazo)"],
        ["Outlier / atípico", "Valor muy alejado del resto"],
        ["Overfitting", "Modelo que memoriza los datos de entrenamiento"],
        ["Causalidad inversa", "Creer que A causa B cuando B causa A"],
        ["Extrapolación", "Concluir sobre combinaciones que no existen en los datos"],
        ["Exclusión no aleatoria", "Sacar un grupo que puede ser distinto del resto (ej.: año de ingreso 1900)"],
        ["Bitácora", "Registro de cada regla aplicada y cuántas filas eliminó"],
        ["Trazabilidad", "Poder reconstruir el origen y cada cambio del dato"],
        ["Minimización", "Conservar solo los datos personales estrictamente necesarios"],
        ["Encoding (UTF-8)", "Cómo se traducen bytes a caracteres"],
        ["Tidyverse", "Conjunto de paquetes de R (dplyr, readr, ggplot2, tidyr…)"],
    ]))

    c.append("<h2>14. Preguntas trampa</h2>")
    trampa = [
        (f"“¿Entonces el {num(prev_fuera, 0)} % de los estudiantes se atrasa?”",
         f"No: el {num(prev_fuera)} % de los <b>titulados</b>. Los desertores no están en la base."),
        ("“¿Eliminaron un tercio de los datos?”",
         f"Sí, pero ninguno por error de digitación. {ent(B['R1']['eliminadas'])} por alcance (posgrado), "
         f"{ent(B['R2']['eliminadas'])} ({num(V['pct_r2_del_total'])} % del total) porque ingresaron desde otra "
         f"institución y no tienen año de ingreso real, y {ent(B['R7']['eliminadas'])} por validez de medición "
         f"(continuidad)."),
        ("“¿La educación a distancia funciona mejor?”",
         f"En lo descriptivo parece ({num(kv('modalidad_jornada', 'A distancia')['pct'])} %), pero en el modelo no hay "
         "diferencia significativa: es efecto de composición. Semipresencial está en el límite y no es concluyente."),
        ("“¿El modelo predice quién se va a atrasar?”",
         f"No. AUC {num(met['AUC'], 2)}: identifica factores asociados, no casos individuales."),
        ("“¿Por qué los mayores de 30 se titulan más a tiempo?”",
         "Probablemente sesgo de supervivencia, no un efecto real de la edad."),
        (f"“Bajó de {num(mejor_g['pct'])} % a {num(peor_g['pct'])} %, ¿eso es "
         f"{num(float(mejor_g['pct']) - float(peor_g['pct']))} %?”",
         f"No: {num(float(mejor_g['pct']) - float(peor_g['pct']))} puntos porcentuales."),
        ("“¿El norte es la zona con peor titulación?”",
         "Como macrozona sí, y el modelo lo confirma; pero la región más baja es Los Ríos, que está en el sur."),
        ("“¿Su período incluye enero de 2025?”",
         "No. El año académico 2025 va de marzo de 2025 a febrero de 2026; en la base no hay titulaciones de enero ni "
         "febrero de 2025."),
    ]
    c.append("".join(f"<div class='qa'><p><b>{q}</b> {r}</p></div>" for q, r in trampa))
    return documento("Guía para la defensa", "Preguntas probables y conceptos · Titulación oportuna en pregrado, Chile "
                     "2025 · Minería de Datos TI3V61", "".join(c))

# ------------------------------------------------------------------ salida
def a_pdf(html, nombre):
    ruta_html = os.path.join(SALIDA, nombre + ".html")
    ruta_pdf = os.path.join(SALIDA, nombre + ".pdf")
    with open(ruta_html, "w", encoding="utf-8") as fh:
        fh.write(html)
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--print-to-pdf-no-header", f"--print-to-pdf={ruta_pdf}",
                    "file:///" + ruta_html.replace("\\", "/")], check=True, timeout=120,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Generado:", ruta_pdf)

if __name__ == "__main__":
    a_pdf(guion(), "Guion_Presentacion_Titulacion_2025")
    a_pdf(guia(), "Guia_Defensa_Titulacion_2025")
