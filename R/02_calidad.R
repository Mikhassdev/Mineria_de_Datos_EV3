# =============================================================================
# 02_calidad.R
# Perfilado inicial, reglas de calidad (ISO/IEC 25012: completitud, validez,
# consistencia, trazabilidad), construcción de la variable respuesta y
# minimización de datos personales.
# Entrada:  data/processed/00_titulados_raw.rds  (generado por 01_carga.R)
# Salidas:  data/processed/01_titulados_pregrado.rds
#           output/tablas/perfil_variables.csv
#           output/tablas/bitacora_calidad.csv
#           output/tablas/chequeos_calidad.csv
# =============================================================================

suppressPackageStartupMessages({
  library(dplyr)
  library(tidyr)
  library(readr)
})

if (!file.exists("data/processed/00_titulados_raw.rds")) source("R/01_carga.R")
raw <- readRDS("data/processed/00_titulados_raw.rds")

# -----------------------------------------------------------------------------
# 1. Perfilado inicial (sobre el dataset completo, antes de cualquier filtro)
# -----------------------------------------------------------------------------
perfil <- tibble(
  variable   = names(raw),
  tipo       = vapply(raw, function(x) class(x)[1], character(1)),
  n_vacios   = vapply(raw, function(x) sum(is.na(x)), integer(1)),
  pct_vacios = round(100 * n_vacios / nrow(raw), 2),
  n_distintos = vapply(raw, function(x) n_distinct(x, na.rm = TRUE), integer(1)),
  ejemplo    = vapply(raw, function(x) as.character(x[!is.na(x)][1]), character(1))
) |>
  # No exponer valores reales de identificadores o cuasi-identificadores
  mutate(ejemplo = if_else(variable %in% c("mrun", "fec_nac_alu"), "[omitido]", ejemplo))
write_csv(perfil, "output/tablas/perfil_variables.csv")

# Chequeos que se informan pero NO excluyen registros
chequeos <- tibble(
  chequeo = c(
    "Registros totales",
    "Registros con MRUN vacío",
    "MRUN con más de un título (registros adicionales)",
    "Año de ingreso original con código especial (<1950 o >2025)",
    "Fecha de titulación con valor por defecto 19000101",
    "Género fuera de {1,2}",
    "Rango de edad 'Sin Información'"
  ),
  n = c(
    nrow(raw),
    sum(is.na(raw$mrun)),
    sum(!is.na(raw$mrun)) - n_distinct(raw$mrun, na.rm = TRUE),
    sum(raw$anio_ing_carr_ori < 1950 | raw$anio_ing_carr_ori > 2025, na.rm = TRUE),
    sum(raw$fecha_obtencion_titulo == "19000101", na.rm = TRUE),
    sum(!raw$gen_alu %in% c(1L, 2L)),
    sum(grepl("^Sin", raw$rango_edad))
  )
)
write_csv(chequeos, "output/tablas/chequeos_calidad.csv")

# -----------------------------------------------------------------------------
# 2. Reglas de calidad. Cada regla registra cuántas filas elimina (bitácora).
#    Unidad de análisis: la TITULACIÓN (un registro), no la persona; por eso
#    los MRUN repetidos (personas con más de un título) se conservan.
# -----------------------------------------------------------------------------
bitacora <- tibble(paso = character(), dimension = character(),
                   regla = character(), filas_antes = integer(),
                   filas_despues = integer(), eliminadas = integer())

aplicar_regla <- function(datos, paso, dimension, regla, condicion) {
  antes   <- nrow(datos)
  datos   <- filter(datos, {{ condicion }})
  despues <- nrow(datos)
  bitacora <<- add_row(bitacora, paso = paso, dimension = dimension,
                       regla = regla, filas_antes = antes,
                       filas_despues = despues, eliminadas = antes - despues)
  datos
}

d <- raw |>
  aplicar_regla("R1", "Alcance",
                "Solo nivel_global = 'Pregrado' (la pregunta es sobre pregrado)",
                nivel_global == "Pregrado") |>
  aplicar_regla("R2", "Validez",
                "Año de ingreso original entre 1950 y 2025 (en pregrado solo aparece el código 1900 = ingreso desde otra institución)",
                between(anio_ing_carr_ori, 1950L, 2025L)) |>
  aplicar_regla("R3", "Validez",
                "Semestre de ingreso original en {1, 2}",
                sem_ing_carr_ori %in% c(1L, 2L)) |>
  # El proceso 2025 incluye titulaciones de ene-feb 2026 (cierre del año
  # académico 2025); ver R/exploratorio/x01_fechas_titulacion.R
  aplicar_regla("R4", "Validez",
                "Fecha de titulación válida (AAAAMMDD) dentro del año académico 2025 (2025-03-01 a 2026-02-28)",
                grepl("^[0-9]{8}$", fecha_obtencion_titulo) &
                  between(fecha_obtencion_titulo, "20250301", "20260228")) |>
  aplicar_regla("R5", "Validez",
                "Duración teórica total de la carrera > 0 semestres",
                !is.na(dur_total_carr) & dur_total_carr > 0)

# -----------------------------------------------------------------------------
# 3. Variables derivadas
#    Semestre académico chileno de la titulación:
#      marzo-julio -> S1; agosto-diciembre -> S2; enero-febrero -> S2 del año anterior.
#    sem_transcurridos: semestres académicos desde el ingreso hasta la
#    titulación, ambos inclusive.
#    Ej.: ingreso 2021-S1, titulación ene-2026 (S2 2025) -> 10 semestres.
# -----------------------------------------------------------------------------
d <- d |>
  mutate(
    fecha_titulo      = as.Date(fecha_obtencion_titulo, format = "%Y%m%d"),
    mes_titulo        = as.integer(format(fecha_titulo, "%m")),
    anio_acad_titulo  = as.integer(format(fecha_titulo, "%Y")) - as.integer(mes_titulo <= 2),
    sem_titulo        = if_else(between(mes_titulo, 3L, 7L), 1L, 2L),
    sem_transcurridos = (anio_acad_titulo * 2L + sem_titulo) -
                        (anio_ing_carr_ori * 2L + sem_ing_carr_ori) + 1L,
    sobreduracion_sem = sem_transcurridos - dur_total_carr,
    ratio_duracion    = sem_transcurridos / dur_total_carr
  )

d <- d |>
  aplicar_regla("R6", "Consistencia",
                "Semestres transcurridos >= 1 (titulación no anterior al ingreso)",
                sem_transcurridos >= 1L) |>
  # En planes de continuidad, anio_ing_carr_ori corresponde al ingreso a la
  # carrera de origen: la duración real no es comparable con dur_total_carr
  # (mediana 13 semestres transcurridos vs 6 teóricos). Validez de medición.
  aplicar_regla("R7", "Validez de medición",
                "Excluye 'Plan Regular de Continuidad' (ingreso de origen no comparable con duración teórica)",
                tipo_plan_carr != "Plan Regular de Continuidad")

# Variable respuesta (dos criterios, declarados explícitamente)
#  - estricto: titulación dentro de la duración teórica total
#  - oportuna: duración teórica + 2 semestres (1 año de holgura, criterio
#    habitual de "titulación oportuna"; confirmar con el docente)
d <- d |>
  mutate(
    a_tiempo_estricto = as.integer(sem_transcurridos <= dur_total_carr),
    titulacion_oportuna = as.integer(sem_transcurridos <= dur_total_carr + 2L),
    fuera_de_plazo      = 1L - titulacion_oportuna,
    genero = factor(gen_alu, levels = c(1L, 2L), labels = c("Hombre", "Mujer")),
    rango_edad = na_if(rango_edad, "Sin Información"),
    # rango_edad es la edad AL TITULARSE: quien se atrasa llega más viejo, por
    # lo que usarla como predictor genera causalidad inversa. Se deriva la edad
    # AL INGRESO (antes de eliminar fec_nac_alu) y se guarda solo en tramos.
    anio_nac    = as.integer(substr(fec_nac_alu, 1, 4)),
    edad_ingreso = if_else(between(anio_nac, 1930L, 2010L),
                           anio_ing_carr_ori - anio_nac, NA_integer_),
    tramo_edad_ingreso = cut(edad_ingreso, breaks = c(-Inf, 19, 24, 29, Inf),
                             labels = c("19 o menos", "20 a 24", "25 a 29", "30 o más")),
    # Algunas instituciones declaran proceso de titulación sin sumarlo a la
    # duración total (ver R/exploratorio/x02_duracion_teorica.R). Se registra
    # para controlar esta heterogeneidad de reporte en el modelo.
    declara_proceso_tit = dur_proceso_tit > 0,
    # jornada y modalidad son redundantes ("A Distancia" = "No Presencial"):
    # se combinan en una sola variable para evitar colinealidad perfecta.
    modalidad_jornada = case_when(
      modalidad == "No Presencial"                       ~ "A distancia",
      modalidad == "Semipresencial" |
        jornada %in% c("Semipresencial", "Otra")         ~ "Semipresencial u otra",
      jornada == "Vespertina"                            ~ "Presencial vespertina",
      TRUE                                               ~ "Presencial diurna"),
    grupo_inst = paste(
      recode(tipo_inst_1, "Universidades" = "Universidad",
             "Institutos Profesionales" = "IP",
             "Centros de Formación Técnica" = "CFT"),
      if_else(nivel_carrera_2 == "Carreras Técnicas", "técnica", "profesional"),
      sep = " · "),
    macrozona = case_when(
      region_sede == "Metropolitana" ~ "Metropolitana",
      region_sede %in% c("Arica y Parinacota", "Tarapacá", "Antofagasta",
                         "Atacama", "Coquimbo") ~ "Norte",
      region_sede %in% c("Valparaíso", "Lib. Gral. B. O'Higgins", "Maule") ~ "Centro",
      region_sede %in% c("Aysén", "Magallanes") ~ "Austral",
      TRUE ~ "Sur")
  ) |>
  select(-anio_nac, -edad_ingreso)

# Atipicidad: se marca, no se elimina (el modelo usa una respuesta binaria,
# por lo que valores extremos de duración no distorsionan coeficientes)
d <- d |> mutate(atipico_duracion = ratio_duracion > 3)

# -----------------------------------------------------------------------------
# 4. Minimización de datos personales
#    Se eliminan identificador (mrun) y fecha de nacimiento (cuasi-identificador).
#    La edad se conserva solo como rango.
# -----------------------------------------------------------------------------
d <- d |> select(-mrun, -fec_nac_alu, -nombre_titulo, -nombre_grado)

bitacora <- add_row(bitacora, paso = "R8", dimension = "Privacidad",
                    regla = "Eliminación de mrun, fec_nac_alu, nombre_titulo y nombre_grado (minimización)",
                    filas_antes = nrow(d), filas_despues = nrow(d), eliminadas = 0L)

write_csv(bitacora, "output/tablas/bitacora_calidad.csv")
saveRDS(d, "data/processed/01_titulados_pregrado.rds")

# -----------------------------------------------------------------------------
# 5. Resumen en consola
# -----------------------------------------------------------------------------
cat("\n== Chequeos informativos ==\n");  print(chequeos, n = Inf)
cat("\n== Bitácora de reglas ==\n");     print(bitacora |> select(-dimension), n = Inf, width = Inf)
cat("\n== Variable respuesta (pregrado limpio) ==\n")
d |>
  summarise(
    n = n(),
    pct_a_tiempo_estricto = round(100 * mean(a_tiempo_estricto), 1),
    pct_titulacion_oportuna = round(100 * mean(titulacion_oportuna), 1),
    mediana_sobreduracion_sem = median(sobreduracion_sem),
    pct_atipicos = round(100 * mean(atipico_duracion), 2)
  ) |> print(width = Inf)

cat("\n== Por tipo de institución y nivel ==\n")
d |>
  group_by(tipo_inst_1, nivel_carrera_2) |>
  summarise(n = n(),
            pct_oportuna = round(100 * mean(titulacion_oportuna), 1),
            mediana_sobreduracion = median(sobreduracion_sem), .groups = "drop") |>
  print(n = Inf, width = Inf)

cat("\n== Por tipo de plan (revisar comportamiento de planes de continuidad) ==\n")
d |>
  group_by(tipo_plan_carr) |>
  summarise(n = n(),
            pct_oportuna = round(100 * mean(titulacion_oportuna), 1),
            mediana_dur_teorica = median(dur_total_carr),
            mediana_sem_transc = median(sem_transcurridos), .groups = "drop") |>
  print(n = Inf, width = Inf)
