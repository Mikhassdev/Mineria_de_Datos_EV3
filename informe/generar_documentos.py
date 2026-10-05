# -*- coding: utf-8 -*-
"""
Genera, sobre la plantilla institucional:
  informe/Informe_Titulacion_Oportuna_2025.docx   (informe técnico)
  informe/Resumen_Problematica_y_Avance.docx     (resumen de la problemática y lo realizado)
Todas las cifras se leen de output/tablas/*.csv (generadas por R/run_all.R).
Uso (desde la raíz del proyecto):  python informe/generar_documentos.py
"""
import csv, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from docx_plantilla import Documento, h1, h2, h3, p, vineta, referencia, tabla, salto_pagina

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = lambda f: os.path.join(RAIZ, "output", "tablas", f)
FIG = lambda f: os.path.join(RAIZ, "output", "figuras", f)
URL_DASH = "https://mikhassdev.github.io/Mineria_de_Datos_EV3/"
URL_REPO = "https://github.com/Mikhassdev/Mineria_de_Datos_EV3"

# ---------------------------------------------------------------- datos
def leer(f):
    with open(T(f), encoding="utf-8") as fh:
        return list(csv.DictReader(fh))

def num(v, d=1):
    """Formato chileno: miles con punto, decimales con coma."""
    v = float(v)
    s = f"{v:,.{d}f}" if d else f"{round(v):,}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")

def ent(v):
    return num(v, 0)

def pp(v):
    v = float(v)
    return ("+" if v > 0 else "") + num(v) + " pp"

kg = leer("kpi_global.csv")[0]
kd = leer("kpi_por_dimension.csv")
bit = leer("bitacora_calidad.csv")
chq = {r["chequeo"]: r["n"] for r in leer("chequeos_calidad.csv")}
orx = {r["termino"]: r for r in leer("modelo_odds_ratio.csv")}
ef = leer("modelo_efectos_marginales.csv")
aj = leer("modelo_ajuste.csv")[0]
met = leer("modelo_metricas_test.csv")[0]
vif = leer("modelo_vif.csv")
sens = {r["termino"]: r for r in leer("modelo_sensibilidad.csv")}

def dim(d):
    return sorted([r for r in kd if r["dimension"] == d and r["valor"] not in ("", "NA")],
                  key=lambda r: -float(r["pct"]))

def kv(d, v):
    return next(r for r in kd if r["dimension"] == d and r["valor"] == v)

def efecto(var, niv):
    return next(r for r in ef if r["variable"] == var and r["nivel"] == niv)

def OR(term):
    r = orx[term]
    return f"OR {num(r['OR'], 2)} (IC 95 %: {num(r['OR_inf'], 2)}–{num(r['OR_sup'], 2)})"

g_inst = dim("grupo_inst"); area = dim("area_conocimiento")
peor_g, mejor_g = g_inst[-1], g_inst[0]
derecho = kv("area_conocimiento", "Derecho")
n_mod = int(aj["n"])
prev_fuera = 100 - float(kg["pct"])

# ---------------------------------------------------------------- portada
def portada(titulo, subtitulo):
    rpr = '<w:color w:val="404040" w:themeColor="text1" w:themeTint="BF"/><w:lang w:eastAsia="es-CL"/>'
    amarillo = '<w:b/><w:highlight w:val="yellow"/>' + rpr
    run = lambda t, extra=rpr: '<w:r><w:rPr>%s</w:rPr><w:t xml:space="preserve">%s</w:t></w:r>' % (extra, t)
    # Datos de portada tal como el equipo los completó en Word (03-10-2026)
    return [
        ('<w:t xml:space="preserve">Asignatura: </w:t></w:r>',
         '<w:t xml:space="preserve">Asignatura: </w:t></w:r>' + run("Minería de Datos")),
        ('<w:t xml:space="preserve">Sección: </w:t></w:r>',
         '<w:t xml:space="preserve">Sección: </w:t></w:r>' + run("2026/P TI3V61/V-IEI-N6-P3-C1/V")),
        ('<w:t xml:space="preserve"> Nombre y apellidos</w:t></w:r>',
         '<w:t xml:space="preserve"> </w:t></w:r>' + run("Igor Cáceres Padilla")),
        ('<w:t>Nombre de los integrantes del grupo:</w:t></w:r>',
         '<w:t xml:space="preserve">Nombre de los integrantes del grupo: </w:t></w:r>'
         + run("Ignacio Larama Paycho, Miguel Jorquera Marín y Johan Matos Chauca")),
        ('<w:t>Fecha de entrega</w:t></w:r>',
         '<w:t xml:space="preserve">Fecha de entrega: </w:t></w:r>' + run("05/10/2026")),
        ("<w:t>Informe Nombre del trabajo</w:t>", "<w:t>%s</w:t>" % titulo),
        ("<w:t>Nombre de la unidad de aprendizaje</w:t>", "<w:t>%s</w:t>" % subtitulo),
    ]

# ================================================================ INFORME
def informe():
    d = Documento()
    A = d.add

    # I. Introducción --------------------------------------------------------
    A(h1("Introducción"),
      p("Las instituciones de educación superior y los organismos que las supervisan necesitan saber **cuánto tardan "
        "sus estudiantes en titularse respecto de lo que promete el plan de estudios**. Un atraso sistemático aumenta el "
        "costo para las familias y el Estado, retrasa la inserción laboral y suele ser síntoma de problemas en el avance "
        "curricular o en el proceso de titulación (práctica, tesis, examen de grado)."),
      p(f"Este informe analiza la base pública de **Titulados de Educación Superior 2025** del Servicio de Información de "
        f"Educación Superior (SIES, 2026), con {ent(chq['Registros totales'])} registros. Tras aplicar reglas de calidad "
        f"documentadas se trabajó con **{ent(kg['n'])} titulaciones de pregrado**. Se formuló una pregunta analítica "
        "vinculada a una decisión, se evaluó la aptitud de los datos, se ajustó un modelo de regresión logística en R y "
        "los resultados se sistematizaron en un dashboard interactivo publicado en la web."),
      p(f"El hallazgo central es que el **{num(kg['pct'])} %** de las titulaciones fue oportuna (dentro de la duración "
        f"teórica más un año), pero con brechas importantes: en las carreras profesionales universitarias la cifra baja a "
        f"{num(peor_g['pct'])} % y en Derecho a {num(derecho['pct'])} %. El informe describe el procedimiento completo, "
        "interpreta la magnitud y la incertidumbre de los resultados, declara sus limitaciones y propone acciones "
        "proporcionales a la evidencia."))

    # II. Objetivo -----------------------------------------------------------
    A(h1("Objetivo"),
      h3("Objetivo general"),
      p("Identificar qué características de la carrera, la institución y el estudiante se asocian con titularse fuera "
        "de plazo en pregrado en Chile (año académico 2025), y sistematizar la evidencia en un dashboard que apoye la "
        "focalización de acciones de apoyo a la titulación."),
      h3("Objetivos específicos"),
      vineta("Definir el problema, la decisión, la audiencia y los KPI vinculados a la titulación oportuna."),
      vineta("Evaluar y documentar la calidad de los datos (completitud, validez, consistencia y trazabilidad) y "
             "aplicar minimización de datos personales."),
      vineta("Estimar en R un modelo de regresión logística con revisión de supuestos, diagnósticos y validación."),
      vineta("Interpretar los resultados considerando magnitud, incertidumbre y limitaciones, y formular recomendaciones."),
      vineta("Construir un dashboard funcional, accesible y trazable que permita identificar qué ocurre, dónde se "
             "concentra el problema y qué acción tomar."))

    # III. Desarrollo --------------------------------------------------------
    A(h1("Desarrollo"))

    # 1. Problema
    A(h2("Definición del problema, la decisión y la audiencia"),
      p("**Contexto y necesidad.** Una dirección académica o una unidad de análisis institucional debe decidir **dónde "
        "focalizar recursos limitados** (tutorías, acompañamiento de tesis, revisión de procesos de titulación) para "
        "reducir el atraso en la titulación. Para ello necesita saber en qué tipos de carrera, áreas y territorios se "
        "concentra el problema."),
      p("**Pregunta analítica.** ¿Qué características de la carrera, la institución y el estudiante se asocian con "
        "titularse fuera de plazo en pregrado?"),
      tabla(["Elemento", "Definición"], [
          ["Decisión que apoya", "Priorizar carreras, áreas e instituciones para intervenciones de apoyo a la titulación"],
          ["Audiencia", "Direcciones académicas y de análisis institucional; equipos de aseguramiento de la calidad"],
          ["Unidad de análisis", "La titulación (un registro). Una persona con dos títulos aporta dos registros"],
          ["Período", "Año académico 2025 (titulaciones entre marzo de 2025 y febrero de 2026)"],
          ["Variable respuesta", "Titulación fuera de plazo: semestres transcurridos > duración teórica + 2 semestres"],
      ], [1, 3]),
      p("**KPI definidos.** Se seleccionaron cuatro indicadores directamente relacionados con la decisión. La meta del "
        "75 % es **referencial y fue definida por el equipo**, ya que no existe un estándar oficial único para este "
        "indicador; se presenta explícitamente como tal en el dashboard."),
      tabla(["KPI", "Definición", "Unidad", "Meta", "Valor 2025"], [
          ["Titulación oportuna", "Titulaciones con semestres transcurridos ≤ duración teórica + 2", "% de titulaciones",
           "75 % (referencial)", f"{num(kg['pct'])} %"],
          ["Brecha entre tipos de institución", "Diferencia entre el grupo con menor y mayor % oportuna", "pp",
           "Reducir", pp(float(peor_g['pct']) - float(mejor_g['pct']))],
          ["Mediana de atraso", "Mediana de (semestres transcurridos − duración teórica)", "semestres", "≤ 1",
           ent(kg["mediana_sobreduracion"])],
          ["% que tarda más del doble", "Titulaciones con más del doble de la duración teórica", "%", "Monitoreo",
           f"{num(kg['pct_mas_doble'])} %"],
      ], [1.4, 2.6, 1.1, 1.1, 1], ["left", "left", "center", "center", "center"]),
      p("**Por qué una holgura de dos semestres.** Muchas carreras exigen práctica profesional, tesis o examen de grado "
        "después de aprobar las asignaturas, lo que agrega alrededor de un semestre. Además, el análisis exploratorio "
        "mostró que las instituciones declaran la duración teórica de forma heterogénea: en el "
        "caso más frecuente de carreras técnicas se informa un semestre de proceso de titulación que no se suma a la "
        "duración total. Por ello se usa un año de holgura y se reporta también el criterio estricto (sin holgura), "
        f"con el cual la titulación a tiempo es de solo {num(kg['pct_estricto'])} %."))

    # 2. Datos
    A(h2("Descripción de los datos"),
      tabla(["Atributo", "Detalle"], [
          ["Fuente", "SIES – Ministerio de Educación de Chile. Base “Titulados de Educación Superior 2025” (base WEB con MRUN)"],
          ["Archivo", "20260817_Titulados_Ed_Superior_2025_WEB.csv (188 MB, UTF-8, separador “;”)"],
          ["Tamaño", f"{ent(chq['Registros totales'])} filas × 41 columnas; una fila por titulación"],
          ["Variables utilizadas", "Tipo de institución, nivel de carrera, área del conocimiento, modalidad, jornada, "
                                   "región de la sede, género, año y semestre de ingreso, fecha de titulación, duración "
                                   "teórica (estudio, proceso de titulación y total), tipo de plan"],
          ["Diccionario", "“Esquema de registro Titulados de Educación Superior 2007–2025” (SIES)"],
          ["Restricciones de uso", "Dataset entregado por el docente para fines académicos. Contiene un identificador "
                                   "enmascarado (MRUN) y la fecha de nacimiento, que son datos personales"],
          ["Integridad", "Se registró el hash SHA-256 del archivo original y se verifica en cada ejecución"],
      ], [1, 3.2]),
      p("El archivo original se conserva sin modificaciones en *data/raw/* y nunca se publica. Todas las transformaciones "
        "se realizan por código, por lo que cualquier tabla o gráfico puede reproducirse desde el archivo original."))

    # 3. Calidad
    A(h2("Preparación y control de calidad de los datos"),
      p("Se aplicó un perfilado inicial (tipo, vacíos y valores distintos de cada variable) y reglas de calidad basadas "
        "en las dimensiones de la norma ISO/IEC 25012 (ISO/IEC, 2008) y en las buenas prácticas de DAMA International "
        "(2017): completitud, validez, consistencia y trazabilidad. Cada regla registra cuántas filas elimina en una "
        "bitácora automática."),
      h3("Chequeos informativos (no excluyen registros)"),
      tabla(["Chequeo", "Registros"], [[r, ent(chq[r])] for r in chq], [4, 1], ["left", "right"]),
      p(f"Los {ent(chq['MRUN con más de un título (registros adicionales)'])} MRUN repetidos corresponden a personas con "
        "más de un título; se conservan porque la unidad de análisis es la titulación y no la persona."),
      h3("Reglas aplicadas (bitácora)"),
      tabla(["Paso", "Dimensión", "Regla", "Antes", "Después", "Eliminadas"],
            [[b["paso"], b["dimension"], b["regla"], ent(b["filas_antes"]), ent(b["filas_despues"]), ent(b["eliminadas"])]
             for b in bit], [0.5, 1.1, 3.6, 0.9, 0.9, 0.9],
            ["center", "left", "left", "right", "right", "right"], tam=16),
      h3("Decisiones de tratamiento justificadas"),
      vineta("**Año académico 2025 incluye enero y febrero de 2026.** Una primera versión de la regla R4 aceptaba solo "
             "fechas de 2025 y excluía 40.522 registros (18 %). La exploración mostró que todos tenían fecha de enero o "
             "febrero de 2026, que en Chile corresponde al cierre del año académico 2025. Excluirlos habría eliminado a "
             "quienes se titulan inmediatamente después de egresar y habría sesgado el KPI a la baja (69,8 % en lugar de "
             f"{num(kg['pct'])} %)."),
      vineta(f"**Año de ingreso con código 1900 (R2).** En pregrado, los {ent(bit[1]['eliminadas'])} registros excluidos "
             "por esta regla tienen todos el código 1900, que según el diccionario significa “otro programa desde otra "
             "institución”: son estudiantes que ingresaron a su carrera desde otra institución. Sin un año de ingreso real "
             "no se puede medir su duración, por lo que se excluyen. Es una exclusión no aleatoria y se declara como "
             "limitación."),
      vineta("**Planes regulares de continuidad excluidos (R7).** En ellos el año de ingreso corresponde a la carrera de "
             "origen, por lo que la duración real no es comparable con la teórica (mediana de 13 semestres transcurridos "
             "frente a 6 teóricos). Es un problema de validez de medición, no de calidad del registro."),
      vineta("**Semestre académico de titulación.** Marzo a julio = primer semestre; agosto a febrero = segundo "
             "semestre. Los semestres transcurridos se cuentan desde el semestre de ingreso hasta el de titulación, "
             "ambos inclusive."),
      vineta("**Minimización de datos personales (R8).** Se eliminan MRUN y fecha de nacimiento antes de guardar los datos "
             "procesados. La edad se conserva solo en tramos y el dashboard muestra únicamente datos agregados "
             "(celdas con al menos 30 titulados)."))

    # 4. Método
    A(h2("Método: técnica analítica y ejecución en R"),
      p("**Técnica.** La variable respuesta es binaria (fuera de plazo: sí/no), por lo que se utilizó **regresión "
        "logística** (Hosmer, Lemeshow y Sturdivant, 2013). Permite estimar la asociación de cada factor manteniendo "
        "constantes los demás y expresarla como odds ratio (OR) con intervalo de confianza, y traducirla a puntos "
        "porcentuales para la audiencia no técnica."),
      p("**Variables explicativas.** Tipo de institución × nivel de carrera (5 grupos), área del conocimiento (10), "
        "modalidad y jornada (4), macrozona de la sede (5), tramo de edad al ingreso (4), género, tipo de plan y si la "
        "carrera declara un proceso de titulación. La categoría de referencia de cada variable es su grupo más numeroso."),
      h3("Decisiones metodológicas"),
      vineta("**Edad al ingreso y no edad al titularse.** La variable *rango_edad* del dataset mide la edad al titularse; "
             "quien se atrasa llega con más edad, de modo que usarla generaría causalidad inversa. La edad al ingreso se "
             "calculó antes de eliminar la fecha de nacimiento."),
      vineta("**Jornada y modalidad combinadas.** “A distancia” y “No presencial” identifican exactamente los mismos "
             "registros; se unieron en una sola variable para evitar colinealidad perfecta."),
      vineta("**Errores estándar agrupados por institución** (Zeileis, Köll y Graham, 2020; Cameron y Miller, 2015). "
             "Los titulados de una misma institución no son independientes; ignorarlo subestimaría la incertidumbre."),
      vineta("**Duración teórica fuera del modelo principal.** Su VIF era 8,7 y, al estar ligada al tipo de carrera, obligaba "
             "a comparar carreras técnicas y profesionales “a igual duración”, combinación que no existe en los datos "
             "(extrapolación). Se evaluó como análisis de sensibilidad."),
      vineta("**Validación predictiva.** Partición aleatoria 70/30 con semilla fija; se reportan AUC (Robin et al., 2011), "
             "puntaje de Brier y calibración por deciles."),
      vineta("**Efectos marginales promedio.** Para cada categoría se calculó la probabilidad media predicha si todos "
             "pertenecieran a ella, manteniendo sus demás características; la diferencia con la referencia se expresa "
             "en puntos porcentuales (pp)."),
      p("**Herramientas.** R 4.6.1 (R Core Team, 2026) con tidyverse (Wickham et al., 2019), sandwich, lmtest, car (Fox y "
        "Weisberg, 2019) y pROC. Los intervalos de las proporciones descriptivas usan el método de Wilson (1927). Todo el "
        "análisis se ejecuta con un único script (*R/run_all.R*)."))

    # 5. Resultados
    A(h2("Resultados"),
      h3("Resultados descriptivos"),
      p(f"De {ent(kg['n'])} titulaciones de pregrado, **{ent(kg['n_oportuna'])} fueron oportunas ({num(kg['pct'])} %; "
        f"IC 95 %: {num(kg['ic_inf'])}–{num(kg['ic_sup'])} %)**, es decir, {num(float(kg['brecha_meta_pp']))} pp respecto "
        "de la meta referencial. La mediana de atraso es de 1 semestre sobre la duración teórica y "
        f"{num(kg['pct_mas_doble'])} % de los titulados tardó más del doble."),
      tabla(["Institución · nivel", "Titulados", "% oportuna", "IC 95 %", "Atraso mediano (sem.)"],
            [[r["valor"], ent(r["n"]), num(r["pct"]), f"{num(r['ic_inf'])}–{num(r['ic_sup'])}",
              ent(r["mediana_sobreduracion"])] for r in g_inst],
            [2, 1, 1, 1.3, 1.3], ["left", "right", "right", "center", "center"]))
    d.figura(FIG("fig_01_grupo_inst.png"), "Figura 1. Titulación oportuna por tipo de institución y nivel de carrera "
             "(IC 95 % de Wilson). Fuente: elaboración propia con datos SIES.", 6.0)
    d.figura(FIG("fig_02_area.png"), "Figura 2. Titulación oportuna por área del conocimiento. Derecho y Ciencias "
             "Básicas se ubican muy por debajo del resto.", 6.0)
    d.figura(FIG("fig_06_sobreduracion.png"), "Figura 3. Distribución de semestres sobre la duración teórica. "
             "La línea marca el límite de titulación oportuna.", 6.0)

    filas_ef = []
    nombres = {"grupo_inst": "Institución · nivel", "area_conocimiento": "Área", "modalidad_jornada": "Modalidad",
               "macrozona": "Macrozona", "tramo_edad_ingreso": "Edad al ingreso", "genero": "Género"}
    for r in ef:
        term = r["variable"] + r["nivel"]
        if term in orx:
            o = orx[term]
            sig = "Sí" if float(o["p_valor"]) < 0.05 else "No"
            filas_ef.append([nombres[r["variable"]], r["nivel"], pp(r["dif_vs_ref_pp"]),
                             f"{num(o['OR'], 2)} ({num(o['OR_inf'], 2)}–{num(o['OR_sup'], 2)})", sig])
        else:
            filas_ef.append([nombres[r["variable"]], r["nivel"] + " (ref.)", "—", "1", "—"])
    A(h3("Modelo de regresión logística"),
      p(f"El modelo se estimó con {ent(n_mod)} titulaciones (se excluyó 1 registro sin edad de ingreso); el "
        f"{num(prev_fuera)} % se tituló fuera de plazo. La Tabla siguiente muestra, para cada categoría, el cambio en la "
        "probabilidad de titularse fuera de plazo respecto de la referencia, junto con el odds ratio y su intervalo de "
        "confianza (errores agrupados por institución)."),
      tabla(["Variable", "Categoría", "Efecto (pp)", "OR (IC 95 %)", "Signif."], filas_ef,
            [1.3, 2.2, 1, 1.6, 0.7], ["left", "left", "right", "center", "center"], tam=16))
    d.figura(FIG("fig_10_odds_ratio.png"), "Figura 4. Odds ratio de titularse fuera de plazo con IC 95 % (escala "
             "logarítmica). Gris: sin diferencia significativa.", 6.3)

    A(h3("Diagnósticos y validación"),
      tabla(["Diagnóstico", "Resultado", "Lectura"], [
          ["Multicolinealidad (GVIF ajustado)", f"máximo {num(max(float(v['GVIF_ajustado']) for v in vif), 2)}",
           "Muy por debajo del umbral habitual (≈2,24, equivalente a VIF 5)"],
          ["Dispersión (Pearson χ² / gl)", num(aj["ratio_dispersion"], 2), "≈1: sin sobredispersión"],
          ["Pseudo R² de McFadden", num(aj["pseudo_R2_McFadden"], 3), "Bajo, esperable en datos individuales"],
          ["AUC en prueba (30 %)", f"{num(met['AUC'], 3)} ({num(met['AUC_inf'], 3)}–{num(met['AUC_sup'], 3)})",
           "Discriminación moderada"],
          ["Brier en prueba", f"{num(met['Brier'], 3)} vs {num(met['Brier_referencia'], 3)} sin predictores",
           f"Mejora de {num(met['mejora_Brier_pct'])} %"],
          ["Calibración por deciles", "Puntos cercanos a la diagonal", "Probabilidades confiables en promedio"],
      ], [1.6, 1.5, 2.2]))
    d.figura(FIG("fig_11_calibracion.png"), "Figura 5. Calibración del modelo en datos de prueba: probabilidad "
             "predicha vs. observada por decil.", 4.2)
    cft = sens["grupo_instCFT · técnica"]
    semi = sens["modalidad_jornadaSemipresencial u otra"]
    A(p(f"**Análisis de sensibilidad.** Al agregar la duración teórica al modelo, las conclusiones sobre área, género, "
        f"edad al ingreso y macrozona no cambian. Dos resultados sí dependen de la especificación: el de los CFT, cuyo "
        f"OR pasa de {num(cft['OR_modelo_principal'], 2)} (no significativo) a {num(cft['OR_con_duracion'], 2)} "
        f"(significativo), y el de la modalidad semipresencial u otra, que está en el límite de la significancia "
        f"(p = {num(semi['p_modelo_principal'], 3)} en el modelo principal y {num(semi['p_con_duracion'], 3)} con la "
        "duración). El plan especial cambia de dirección, pero no es significativo en ninguno de los dos modelos. Por "
        "eso no se recomienda actuar sobre estos resultados sin más análisis."))

    # 6. Interpretación
    A(h2("Interpretación de los resultados"),
      vineta(f"**Derecho es el foco más claro.** A igualdad de las demás características, estudiar Derecho se asocia con "
             f"{pp(efecto('area_conocimiento', 'Derecho')['dif_vs_ref_pp'])} de probabilidad de titularse fuera de plazo "
             f"respecto de Tecnología ({OR('area_conocimientoDerecho')}). Es consistente con un proceso de titulación "
             "largo (examen de grado y memoria), aunque los datos no permiten confirmarlo."),
      vineta(f"**Las carreras profesionales universitarias concentran el atraso.** Frente a ellas, las carreras de IP y "
             f"las técnicas universitarias tienen entre {num(abs(float(efecto('grupo_inst', 'IP · técnica')['dif_vs_ref_pp'])))} "
             f"y {num(abs(float(efecto('grupo_inst', 'Universidad · técnica')['dif_vs_ref_pp'])))} pp menos de probabilidad "
             "de atraso. En términos absolutos es también el grupo con más titulados, por lo que concentra el mayor "
             "volumen de casos fuera de plazo."),
      vineta(f"**Ciencias Sociales, Educación y Salud** muestran los mejores resultados ({pp(efecto('area_conocimiento', 'Ciencias Sociales')['dif_vs_ref_pp'])}, "
             f"{pp(efecto('area_conocimiento', 'Educación')['dif_vs_ref_pp'])} y {pp(efecto('area_conocimiento', 'Salud')['dif_vs_ref_pp'])}), "
             "lo que puede servir para identificar prácticas transferibles."),
      vineta(f"**Macrozona Norte** presenta {pp(efecto('macrozona', 'Norte')['dif_vs_ref_pp'])} respecto de la "
             f"Metropolitana ({OR('macrozonaNorte')}); el resto de las macrozonas no difiere significativamente."),
      vineta(f"**Mujeres** tienen {pp(efecto('genero', 'Mujer')['dif_vs_ref_pp'])} de probabilidad de atraso "
             f"({OR('generoMujer')}). La diferencia es estadísticamente clara pero de magnitud moderada."),
      vineta("**Modalidad no muestra diferencias significativas en el modelo principal** una vez controladas las demás "
             "variables, aunque en la comparación simple los programas a distancia parecían mejores (80,7 % oportuna). "
             "La diferencia descriptiva se explica por la composición de sus estudiantes y carreras, no por la modalidad. "
             "La categoría semipresencial u otra (2.381 titulaciones) está en el límite: pasa a ser significativa al "
             "agregar la duración teórica, por lo que su resultado no es concluyente."),
      vineta(f"**Edad al ingreso:** quienes ingresan con 30 años o más tienen {pp(efecto('tramo_edad_ingreso', '30 o más')['dif_vs_ref_pp'])}. "
             "Este resultado debe leerse con cautela: probablemente refleja un sesgo de supervivencia, porque los "
             "estudiantes mayores que se atrasan tienden a abandonar y no aparecen en una base de titulados."),
      p("**Incertidumbre y relevancia práctica.** Con más de 200 mil registros casi cualquier diferencia resulta "
        "significativa, por lo que el foco está en la **magnitud**. Los errores agrupados por institución amplían los "
        "intervalos de forma realista; los efectos de Derecho, tipo de institución y área superan los 8 pp, una "
        "diferencia relevante para la gestión. El AUC de 0,69 indica que el modelo sirve para identificar factores "
        "asociados, **no para predecir qué estudiante específico se atrasará**."),
      p("**Asociación, no causalidad.** El diseño es observacional y no incluye variables de rendimiento académico, "
        "situación laboral ni financiamiento. Por ello los resultados describen dónde se concentra el atraso, pero no "
        "permiten afirmar que estudiar Derecho o en una universidad *cause* el atraso."))

    # 7. Limitaciones
    A(h2("Limitaciones"),
      vineta("**Sesgo de supervivencia (diseño):** la base contiene solo titulados; no se observa a quienes desertaron ni a "
             "quienes siguen estudiando. El KPI no es una tasa de titulación del sistema."),
      vineta("**Medición:** la duración teórica se declara de forma heterogénea entre instituciones. Se controla con una "
             "variable indicadora, pero puede quedar sesgo residual."),
      vineta("**Muestra y período:** un solo año (2025), sin posibilidad de analizar tendencias. Se excluyeron 4.526 "
             "titulaciones de planes de continuidad."),
      vineta(f"**Exclusión de ingresos desde otra institución:** {ent(bit[1]['eliminadas'])} titulaciones (7,4 % del "
             "pregrado) tienen año de ingreso 1900, es decir, ingresaron desde otra institución, y se excluyeron porque no "
             "permiten medir la duración. Si este grupo se atrasa más (o menos) que el resto, el KPI podría estar sobre o "
             "subestimado. Una mejora futura es usar el año de ingreso a la carrera actual para estimar su duración."),
      vineta("**Variables omitidas:** rendimiento previo, nivel socioeconómico, trabajo y financiamiento no están en la base."),
      vineta("**Extrapolación:** los resultados aplican a pregrado en Chile en 2025; no deben extenderse a posgrado ni a "
             "otros países."))

    # 8. Recomendaciones
    A(h2("Recomendaciones y monitoreo"),
      p("Las recomendaciones se formulan en proporción a la evidencia y consideran el costo de equivocarse: intervenir "
        "donde el atraso responde al diseño curricular (por ejemplo, una duración teórica subdeclarada) gastaría recursos "
        "sin mejorar la experiencia estudiantil."),
      tabla(["Recomendación", "Evidencia que la respalda", "Alcance sugerido"], [
          ["Diagnosticar el proceso de titulación en Derecho (plazos de memoria y examen de grado)",
           "Efecto más grande y robusto (+20,9 pp)", "Estudio focalizado antes de intervenir"],
          ["Programa piloto de acompañamiento de titulación en carreras profesionales universitarias de mayor volumen",
           "Grupo con menor % oportuna y mayor número de casos", "Piloto en instituciones priorizadas en el dashboard"],
          ["Investigar causas del atraso en la macrozona Norte", "Efecto moderado (+6 pp) y significativo",
           "Análisis exploratorio con datos regionales"],
          ["No intervenir por modalidad ni por tipo CFT con esta evidencia", "Sin diferencias significativas / no robusto",
           "Sin acción; seguir monitoreando"],
          ["Estandarizar la declaración de duración teórica y proceso de titulación", "Heterogeneidad detectada en x02",
           "Recomendación al proveedor de datos"],
      ], [2.4, 1.8, 1.6]),
      p("**Monitoreo del impacto.** El pipeline es reproducible: con cada nueva base anual del SIES basta ejecutar "
        "*R/run_all.R* para actualizar los KPI y el dashboard. Se propone seguir anualmente el % de titulación oportuna y "
        "la brecha entre grupos en las carreras intervenidas frente a carreras similares no intervenidas, e incorporar en "
        "una segunda etapa las bases de matrícula del SIES para medir cohortes completas (incluyendo deserción)."))

    # 9. Dashboard
    A(h2("Dashboard: diseño y decisiones"),
      p(f"El dashboard se construyó con flexdashboard (Aden-Buie et al., 2026), plotly (Sievert, 2020), crosstalk (Cheng y "
        f"Sievert, 2025) y DT (Xie et al., 2025). Está publicado en **{URL_DASH}** y se genera con el mismo pipeline que el "
        "análisis."),
      tabla(["Página", "Nivel", "Contenido"], [
          ["Resumen", "Qué ocurre", "KPI con meta, unidad, período, fuente y fecha; gráficos por institución, área y región; lectura para la decisión"],
          ["Factores asociados", "Por qué", "Efecto ajustado de cada factor en pp, calibración, robustez y advertencias"],
          ["Explorar instituciones", "Dónde actuar", "Filtros (institución, área, macrozona, estado, volumen); gráfico y tabla enlazados; descarga CSV"],
          ["Datos y método", "Trazabilidad", "Definición de KPI, bitácora de calidad, limitaciones y reproducibilidad"],
      ], [1.2, 0.9, 3.3]))
    d.figura(FIG("dash_resumen.png"), "Figura 6. Página Resumen del dashboard.", 6.3)
    d.figura(FIG("dash_explorar-instituciones.png"), "Figura 7. Página Explorar instituciones: cada punto es una "
             "combinación institución × nivel × área × macrozona.", 6.3)
    A(h3("Decisiones de diseño"),
      vineta("**Herramienta:** flexdashboard genera un único archivo HTML que se abre sin instalar R ni levantar un servidor "
             "(a diferencia de Shiny), lo que reduce el riesgo en la demostración y facilita la entrega."),
      vineta("**Jerarquía:** resumen → análisis → detalle, con títulos que enuncian el hallazgo (“las carreras profesionales "
             "universitarias concentran el atraso”) en lugar de describir el gráfico."),
      vineta("**Gráficos:** puntos con intervalo de confianza para comparar proporciones, barras horizontales para efectos y "
             "dispersión volumen vs. % para priorizar. No se usan gráficos circulares ni dobles ejes."),
      vineta("**Estado frente a la meta con incertidumbre:** naranja solo si todo el IC 95 % está bajo la meta; gris si el "
             "intervalo la cruza (no concluyente). La misma regla se aplica en todas las páginas."),
      vineta("**Accesibilidad:** paleta validada para daltonismo, el color nunca es la única señal (etiquetas, leyendas y "
             "textos), contraste suficiente y valores disponibles en tablas."),
      vineta("**Privacidad y trazabilidad:** solo datos agregados con celdas de 30 o más titulados; cada KPI muestra fuente y "
             "fecha de actualización, y la página de método incluye la bitácora de calidad."),
      vineta("**KPI e indicadores de contexto:** la fila superior del Resumen muestra los KPI definidos en este informe "
             "(titulación oportuna, brecha entre instituciones y mediana de atraso, con el % que tarda más del doble) y "
             "dos tarjetas marcadas como «Contexto»: el área más crítica (Derecho) y el volumen de titulaciones analizadas, "
             "que ayudan a dimensionar el problema pero no son KPI."))

    # 10. Reproducibilidad
    A(h2("Reproducibilidad y organización del trabajo"),
      tabla(["Archivo o carpeta", "Función"], [
          ["R/01_carga.R", "Lectura con tipos explícitos y verificación del hash SHA-256"],
          ["R/02_calidad.R", "Perfilado, reglas de calidad, variables derivadas y minimización"],
          ["R/03_descriptivo.R", "KPI con IC de Wilson y figuras descriptivas"],
          ["R/04_modelo.R", "Regresión logística, diagnósticos, validación y sensibilidad"],
          ["R/05_datos_dashboard.R y 06_render_dashboard.R", "Insumos agregados y generación del dashboard"],
          ["R/run_all.R", "Ejecuta todo el pipeline en orden (≈45 segundos)"],
          ["R/exploratorio/", "Exploraciones que justifican reglas de calidad"],
          ["output/", "Tablas, figuras y registros de ejecución generados por código"],
      ], [2, 3]),
      p(f"El código está disponible en {URL_REPO}. Los datos originales no se publican por su tamaño y por contener datos "
        "personales; el README indica cómo obtenerlos y verificar su integridad."))

    # IV. Conclusiones -------------------------------------------------------
    A(h1("Conclusiones"),
      p(f"Cerca de **3 de cada 10 titulados de pregrado 2025** terminó más de un año después de la duración teórica de su "
        "carrera. El atraso no se distribuye de forma homogénea: se concentra en las carreras profesionales universitarias, "
        "en Derecho y, en menor medida, en la macrozona Norte. Estos resultados permiten a una dirección académica "
        "focalizar el diagnóstico y los pilotos de apoyo donde el problema es mayor y más robusto."),
      p("Desde el punto de vista metodológico, el trabajo mostró que las decisiones sobre los datos pesan tanto como la "
        "técnica: revisar una regla de fechas evitó excluir al 18 % de la base, usar la edad al ingreso evitó una "
        "causalidad inversa y el análisis de sensibilidad evitó recomendar una acción sobre un resultado frágil (CFT)."),
      p("Como proyección, se propone incorporar las bases de matrícula del SIES para seguir cohortes completas y medir "
        "también la deserción, ampliar el análisis a varios años para observar tendencias y explorar modelos multinivel "
        "que separen la variación entre instituciones de la variación entre estudiantes."))

    # V. Referencias ---------------------------------------------------------
    A(h1("Referencias bibliográficas"))
    refs = [
        "Aden-Buie, G., Sievert, C., Iannone, R., Allaire, J. J. y Borges, B. (2026). *flexdashboard: R Markdown format for flexible dashboards* (Versión 0.6.3) [Paquete de R]. https://CRAN.R-project.org/package=flexdashboard",
        "Cameron, A. C. y Miller, D. L. (2015). A practitioner’s guide to cluster-robust inference. *Journal of Human Resources, 50*(2), 317–372.",
        "Cheng, J. y Sievert, C. (2025). *crosstalk: Inter-widget interactivity for HTML widgets* (Versión 1.2.2) [Paquete de R]. https://CRAN.R-project.org/package=crosstalk",
        "DAMA International. (2017). *DAMA-DMBOK: Data management body of knowledge* (2.ª ed.). Basking Ridge, NJ: Technics Publications.",
        "Fox, J. y Weisberg, S. (2019). *An R companion to applied regression* (3.ª ed.). Thousand Oaks, CA: Sage.",
        "Hosmer, D. W., Lemeshow, S. y Sturdivant, R. X. (2013). *Applied logistic regression* (3.ª ed.). Hoboken, NJ: Wiley.",
        "ISO/IEC. (2008). *ISO/IEC 25012:2008. Software engineering — Software product Quality Requirements and Evaluation (SQuaRE) — Data quality model*. Ginebra: International Organization for Standardization.",
        "R Core Team. (2026). *R: A language and environment for statistical computing* (Versión 4.6.1). Viena: R Foundation for Statistical Computing. https://www.R-project.org/",
        "Robin, X., Turck, N., Hainard, A., Tiberti, N., Lisacek, F., Sanchez, J. y Müller, M. (2011). pROC: An open-source package for R and S+ to analyze and compare ROC curves. *BMC Bioinformatics, 12*, 77.",
        "Servicio de Información de Educación Superior. (2026). *Titulados de Educación Superior 2025* [Base de datos y esquema de registro]. Santiago: Ministerio de Educación de Chile. Recuperado de https://www.mifuturo.cl",
        "Sievert, C. (2020). *Interactive web-based data visualization with R, plotly, and shiny*. Boca Ratón, FL: Chapman and Hall/CRC.",
        "Wickham, H., Averick, M., Bryan, J., Chang, W., McGowan, L. D., François, R., … Yutani, H. (2019). Welcome to the tidyverse. *Journal of Open Source Software, 4*(43), 1686.",
        "Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. *Journal of the American Statistical Association, 22*(158), 209–212.",
        "Xie, Y., Cheng, J., Tan, X. y Aden-Buie, G. (2025). *DT: A wrapper of the JavaScript library “DataTables”* (Versión 0.34.0) [Paquete de R]. https://CRAN.R-project.org/package=DT",
        "Zeileis, A., Köll, S. y Graham, N. (2020). Various versatile variances: An object-oriented implementation of clustered covariances in R. *Journal of Statistical Software, 95*(1), 1–36.",
    ]
    A(*[referencia(r) for r in refs])

    d.guardar(os.path.join(RAIZ, "informe", "Informe_Titulacion_Oportuna_2025.docx"),
              portada("Informe: Titulación oportuna en pregrado, Chile 2025",
                      "Análisis estadístico en R y dashboard para la toma de decisiones"),
              "Titulación oportuna en pregrado · Chile 2025")

# ================================================================ RESUMEN
def resumen():
    d = Documento()
    A = d.add
    A(h1("La problemática"),
      p("En Chile, una parte importante de los estudiantes de educación superior se titula bastante después de la "
        "duración que declara su plan de estudios. Ese atraso tiene costos para los estudiantes (más aranceles, ingreso "
        "tardío al trabajo), para las instituciones y para el financiamiento público."),
      p("**Pregunta que guía el trabajo:** ¿qué características de la carrera, la institución y el estudiante se asocian "
        "con titularse fuera de plazo en pregrado?"),
      p("**Decisión que se busca apoyar:** que una dirección académica pueda priorizar dónde focalizar apoyo al avance "
        "curricular y al proceso de titulación (práctica, tesis, examen de grado)."),
      p("**Datos:** base pública de Titulados de Educación Superior 2025 del SIES-Mineduc, entregada por el docente "
        f"({ent(chq['Registros totales'])} registros)."),
      p("**Definición clave:** una titulación es *oportuna* si ocurre dentro de la duración teórica de la carrera más un "
        "año (2 semestres) de holgura para práctica, tesis o examen de grado."))

    A(h1("Lo que se ha realizado"),
      tabla(["Etapa", "Qué se hizo", "Estado"], [
          ["1. Problema y KPI", "Pregunta, decisión, audiencia, unidad de análisis y 4 KPI con meta referencial (75 %)", "Listo"],
          ["2. Calidad de datos", f"Perfilado y 8 reglas documentadas en bitácora; {ent(kg['n'])} titulaciones de pregrado "
                                  "válidas; eliminación de MRUN y fecha de nacimiento", "Listo"],
          ["3. Análisis en R", "Regresión logística con errores agrupados por institución, diagnósticos (VIF, "
                               "calibración, AUC) y análisis de sensibilidad", "Listo"],
          ["4. Interpretación", "Efectos en puntos porcentuales, limitaciones y recomendaciones proporcionales", "Listo"],
          ["5. Dashboard", "4 páginas interactivas publicadas en la web, con filtros y solo datos agregados", "Listo"],
          ["6. Informe técnico", "Documento en plantilla institucional", "Listo"],
          ["7. Presentación oral", "10 láminas + anexo con notas del orador; demostración en vivo del dashboard", "Lista (falta ensayar)"],
      ], [1.2, 3.6, 1]),
      h3("Principales resultados"),
      vineta(f"**{num(kg['pct'])} %** de las titulaciones fue oportuna (meta referencial: 75 %)."),
      vineta(f"Las **carreras profesionales universitarias** tienen la cifra más baja ({num(peor_g['pct'])} %), frente a "
             f"{num(mejor_g['pct'])} % en {mejor_g['valor']}."),
      vineta(f"**Derecho** es el área más crítica: {num(derecho['pct'])} % de titulación oportuna; a igualdad de otras "
             f"características, {pp(efecto('area_conocimiento', 'Derecho')['dif_vs_ref_pp'])} de probabilidad de atraso."),
      vineta(f"La **macrozona Norte** tiene {pp(efecto('macrozona', 'Norte')['dif_vs_ref_pp'])} de probabilidad de atraso "
             "respecto de la Metropolitana."),
      vineta("La modalidad (presencial, a distancia) no muestra diferencias significativas una vez controlados los demás factores."),
      h3("Decisiones importantes que el equipo debe poder defender"),
      vineta("Se incluyeron las titulaciones de enero y febrero de 2026 porque pertenecen al año académico 2025; excluirlas "
             "habría eliminado el 18 % de la base y sesgado el resultado."),
      vineta("Se usó la edad al ingreso, no la edad al titularse, para evitar causalidad inversa."),
      vineta("Se excluyeron los planes de continuidad porque su año de ingreso corresponde a otra carrera."),
      vineta("Se excluyó al 7,4 % que ingresó desde otra institución (año de ingreso 1900), porque no permite medir la "
             "duración; es una limitación declarada."),
      vineta("Los resultados son asociaciones, no causas, y la base solo incluye a quienes se titularon (sesgo de "
             "supervivencia)."),
      h3("Productos y acceso"),
      vineta(f"Dashboard: {URL_DASH}"),
      vineta(f"Código reproducible: {URL_REPO} (ejecutar *R/run_all.R*)"),
      vineta("Informe técnico: *informe/Informe_Titulacion_Oportuna_2025.docx*"),
      h3("Pendientes"),
      vineta("Validar con el docente la meta referencial del 75 % y el criterio de holgura de 2 semestres."),
      vineta("Distribuir la participación entre los integrantes y ensayar la presentación con cronómetro."))

    # ---------------------------------------------------------- limpieza de datos
    elim = {b["paso"]: int(b["eliminadas"]) for b in bit}
    sin_info = chq["Rango de edad 'Sin Información'"]
    ini_f, fin_f = int(chq["Registros totales"]), int(kg["n"])
    criterio = {
        "R1": "La pregunta es sobre pregrado; se excluyen posgrado y postítulo (no es un error del dato, es alcance)",
        "R2": "Año de ingreso 1900 = ingresó desde otra institución (único código presente en pregrado): no permite calcular la duración",
        "R3": "Valor fuera de dominio",
        "R4": "Fecha con formato inválido o fuera del año académico 2025 (mar-2025 a feb-2026)",
        "R5": "Sin duración teórica no se puede medir el atraso",
        "R6": "La titulación no puede ser anterior al ingreso",
        "R7": "El año de ingreso corresponde a la carrera de origen: el atraso queda mal medido",
        "R8": "Minimización de datos personales (solo elimina columnas)",
    }
    A(h1("Limpieza de datos"),
      p("**Sí, hubo limpieza de datos.** Se hizo completamente por código en R (scripts *R/01_carga.R* y "
        "*R/02_calidad.R*), sin modificar el archivo original, y cada regla quedó registrada en una bitácora automática "
        "(*output/tablas/bitacora_calidad.csv*) con las filas antes y después."),
      h3("Dimensiones del dataset: inicio y fin"),
      tabla(["Etapa", "Filas", "Columnas", "Detalle"], [
          ["Dataset original (CSV SIES)", ent(ini_f), "41", "Archivo sin modificar, verificado con hash SHA-256"],
          ["Dataset limpio (análisis)", ent(fin_f), "54",
           "41 originales − 4 eliminadas + 17 variables derivadas"],
          ["Datos del modelo", ent(n_mod), "11", "Respuesta + 8 predictores + institución (errores agrupados) + duración "
                                                 "teórica (sensibilidad). Se excluye 1 registro sin edad de ingreso"],
          ["Datos del dashboard", "861 celdas", "14",
           "Agregados institución × nivel × área × macrozona (n ≥ 30); sin registros individuales"],
      ], [1.7, 1, 0.8, 2.8], ["left", "right", "center", "left"]),
      p(f"En total se eliminaron **{ent(ini_f - fin_f)} filas ({num(100 * (ini_f - fin_f) / ini_f)} %)**. Conviene "
        f"distinguir el motivo: {ent(elim['R1'])} filas salieron por **alcance** (no son pregrado), "
        f"{ent(elim['R2'])} porque **ingresaron desde otra institución** (año de ingreso 1900, sin año real) y "
        f"{ent(elim['R7'])} por **validez de medición**. La exclusión de quienes ingresaron desde otra institución "
        "no es aleatoria y se declara como limitación."),
      h3("Filas eliminadas: regla, criterio y cantidad"),
      tabla(["Paso", "Regla", "Criterio", "Filas antes", "Eliminadas", "Filas después"],
            [[b["paso"], b["regla"], criterio[b["paso"]], ent(b["filas_antes"]), ent(b["eliminadas"]),
              ent(b["filas_despues"])] for b in bit],
            [0.45, 2.1, 2.3, 0.85, 0.85, 0.85], ["center", "left", "left", "right", "right", "right"], tam=15),
      p("Las reglas R3 a R6 no eliminaron filas: funcionaron como **verificaciones** que confirman que los datos "
        "cumplen esas condiciones."),
      h3("Columnas eliminadas"),
      tabla(["Columna", "Criterio"], [
          ["mrun", "Identificador de la persona (dato personal). No se necesita para el análisis"],
          ["fec_nac_alu", "Fecha de nacimiento (cuasi-identificador). Antes de eliminarla se calculó la edad al ingreso en tramos"],
          ["nombre_titulo", "Texto libre del título; no se usa y ayuda a reidentificar"],
          ["nombre_grado", "Texto libre del grado; vacío en 201.664 filas y no se usa"],
      ], [1.2, 4]),
      h3("Columnas agregadas (17 variables derivadas)"),
      tabla(["Grupo", "Columnas", "Para qué"], [
          ["Tiempo de titulación", "fecha_titulo, mes_titulo, anio_acad_titulo, sem_titulo, sem_transcurridos, "
                                   "sobreduracion_sem, ratio_duracion", "Medir cuánto tardó cada titulación"],
          ["Variable respuesta", "a_tiempo_estricto, titulacion_oportuna, fuera_de_plazo", "KPI y variable del modelo"],
          ["Recodificaciones", "genero, tramo_edad_ingreso, modalidad_jornada, grupo_inst, macrozona",
           "Categorías legibles y sin redundancia (jornada y modalidad repetían información)"],
          ["Controles de calidad", "declara_proceso_tit, atipico_duracion",
           "Marcar heterogeneidad de reporte y casos extremos (se marcan, no se eliminan)"],
      ], [1.2, 2.8, 1.8], tam=16),
      h3("Problemas detectados que NO se eliminaron (y por qué)"),
      vineta(f"**{ent(chq['MRUN con más de un título (registros adicionales)'])} MRUN repetidos:** son personas con más de "
             "un título, no duplicados. La unidad de análisis es la titulación, así que se conservan."),
      vineta(f"**{ent(chq['Registros con MRUN vacío'])} filas sin MRUN:** el MRUN no se usa en el análisis; eliminarlas "
             "habría perdido información válida."),
      vineta(f"**{ent(sin_info)} filas con edad "
             "“Sin Información”:** se convirtieron en valor faltante (NA), no se eliminaron."),
      vineta(f"**{num(kg['pct_mas_doble'])} % tarda más del doble de lo teórico:** son valores extremos pero plausibles "
             "(personas que retoman sus estudios); se marcan con *atipico_duracion* y se conservan."),
      vineta("**Corrección clave:** una primera versión de la regla R4 eliminaba 40.522 filas (18 %) con fecha en enero y "
             "febrero de 2026. Se revisó y se corrigió, porque esas fechas pertenecen al cierre del año académico 2025."))

    # ---------------------------------------------------------- herramientas
    A(h1("Herramientas utilizadas"),
      h3("Funciones y comandos para la limpieza del dataset"),
      tabla(["Función o comando", "Paquete", "Uso en la limpieza"], [
          ["read_delim() con cols()", "readr", "Leer el CSV (separador “;”, UTF-8) con tipos de columna explícitos"],
          ["problems()", "readr", "Verificar que no hubo errores de lectura (resultado: 0)"],
          ["digest()", "digest", "Calcular el hash SHA-256 y comprobar que el archivo original no cambió"],
          ["is.na(), n_distinct(), vapply()", "base / dplyr", "Perfilado: vacíos y valores distintos por columna"],
          ["filter() con between(), %in% y grepl()", "dplyr / base", "Aplicar las reglas de validez (rangos, dominios y formato de fecha con expresión regular)"],
          ["nrow() + add_row()", "base / tibble", "Registrar en la bitácora las filas antes y después de cada regla"],
          ["mutate(), case_when(), if_else()", "dplyr", "Crear variables derivadas y recodificar categorías"],
          ["as.Date(), format()", "base", "Convertir la fecha AAAAMMDD y obtener mes y año académico"],
          ["na_if()", "dplyr", "Convertir “Sin Información” en valor faltante"],
          ["cut()", "base", "Agrupar la edad al ingreso en tramos"],
          ["select(-columna)", "dplyr", "Eliminar columnas con datos personales"],
          ["drop_na()", "tidyr", "Excluir el registro sin edad de ingreso antes del modelo"],
          ["write_csv(), saveRDS()", "readr / base", "Guardar la bitácora, el perfil y los datos limpios"],
      ], [1.8, 1, 2.8], tam=16),
      h3("Librerías utilizadas para el dashboard"),
      tabla(["Librería", "Función en el dashboard"], [
          ["flexdashboard", "Estructura del panel: páginas, filas, barra lateral, gauge y cajas de KPI"],
          ["rmarkdown", "Generar el HTML a partir del archivo .Rmd"],
          ["plotly", "Gráficos interactivos (puntos con IC, barras de efectos, calibración, dispersión)"],
          ["crosstalk", "Filtros enlazados entre el gráfico y la tabla sin necesidad de servidor"],
          ["DT", "Tabla interactiva con búsqueda, orden, paginación y descarga CSV"],
          ["dplyr", "Preparar los datos agregados que muestra el panel"],
          ["knitr", "Tabla de la bitácora de calidad en la página “Datos y método”"],
      ], [1.3, 4]),
      p("**Para el análisis estadístico** (no para el dashboard) se usaron además broom, sandwich, lmtest, car y pROC, y "
        "ggplot2 para las figuras del informe."))

    d.guardar(os.path.join(RAIZ, "informe", "Resumen_Problematica_y_Avance.docx"),
              portada("Resumen: problemática y trabajo realizado",
                      "Titulación oportuna en pregrado, Chile 2025"),
              "Resumen · Titulación oportuna en pregrado 2025", con_indice=False)

if __name__ == "__main__":
    # Uso: python informe/generar_documentos.py [informe] [resumen]   (sin argumentos: ambos)
    # Ojo: regenerar sobrescribe el .docx, incluidos los datos de portada completados a mano.
    pedidos = sys.argv[1:] or ["informe", "resumen"]
    if "informe" in pedidos:
        informe()
    if "resumen" in pedidos:
        resumen()
    print("Generado:", ", ".join(pedidos))
