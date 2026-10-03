# =============================================================================
# 05_datos_dashboard.R
# Prepara los insumos AGREGADOS del dashboard (no contiene registros
# individuales). Celdas con menos de N_MIN_CELDA titulados se excluyen para
# evitar porcentajes inestables y reducir el riesgo de reidentificación.
# Entrada:  data/processed/01_titulados_pregrado.rds, 02_modelo_resumen.rds,
#           output/tablas/*.csv
# Salida:   dashboard/datos_dashboard.rds
# =============================================================================

source("R/00_funciones.R")
suppressPackageStartupMessages(library(readr))

N_MIN_CELDA <- 30

d      <- readRDS("data/processed/01_titulados_pregrado.rds")
modelo <- readRDS("data/processed/02_modelo_resumen.rds")

# Celdas institución × grupo × área: unidad de la vista "Explorar"
celdas <- resumir_kpi(d, nomb_inst, tipo_inst_1, grupo_inst, area_conocimiento, macrozona) |>
  filter(n >= N_MIN_CELDA) |>
  mutate(bajo_meta = pct < META_OPORTUNA)

# Efectos marginales + significancia del OR correspondiente
efectos <- modelo$efectos |>
  mutate(termino = paste0(variable, nivel)) |>
  left_join(select(modelo$tabla_or, termino, OR, OR_inf, OR_sup, p_valor), by = "termino") |>
  mutate(es_referencia = dif_vs_ref_pp == 0 & is.na(OR),
         significativo = !is.na(p_valor) & p_valor < 0.05)

insumos <- list(
  generado        = Sys.Date(),
  fecha_datos     = as.Date("2026-08-17"),   # fecha del archivo SIES
  fuente          = FUENTE,
  meta            = META_OPORTUNA,
  holgura         = HOLGURA_SEM,
  n_min_celda     = N_MIN_CELDA,
  kpi_global      = read_csv("output/tablas/kpi_global.csv", show_col_types = FALSE),
  kpi_dim         = read_csv("output/tablas/kpi_por_dimension.csv", show_col_types = FALSE),
  bitacora        = read_csv("output/tablas/bitacora_calidad.csv", show_col_types = FALSE),
  celdas          = celdas,
  n_celdas_excl   = nrow(resumir_kpi(d, nomb_inst, grupo_inst, area_conocimiento, macrozona)) - nrow(celdas),
  efectos         = efectos,
  metricas        = modelo$metricas,
  calibracion     = modelo$calibracion,
  sensibilidad    = modelo$sensibilidad
)
saveRDS(insumos, "dashboard/datos_dashboard.rds")
cat("Celdas en dashboard:", nrow(celdas), "| excluidas (n <", N_MIN_CELDA, "):", insumos$n_celdas_excl, "\n")
