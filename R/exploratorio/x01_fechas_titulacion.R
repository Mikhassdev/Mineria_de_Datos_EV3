# Exploración: ¿por qué la regla R4 excluye ~40 mil registros?
suppressPackageStartupMessages(library(dplyr))
r <- readRDS("data/processed/00_titulados_raw.rds") |>
  filter(nivel_global == "Pregrado", between(anio_ing_carr_ori, 1950L, 2025L)) |>
  mutate(anio_tit = substr(fecha_obtencion_titulo, 1, 4))
print(count(r, anio_tit) |> mutate(pct = round(100 * n / sum(n), 1)), n = Inf)
cat("\nFormato inválido:", sum(!grepl("^[0-9]{8}$", r$fecha_obtencion_titulo)), "\n")
print(count(filter(r, anio_tit == "2024"), mes = substr(fecha_obtencion_titulo, 5, 6)), n = Inf)
print(count(filter(r, anio_tit < "2025"), tipo_inst_1))

# Hallazgo: los registros excluidos tienen fecha 2026. Distribución por mes:
print(count(filter(r, anio_tit == "2026"), mes = substr(fecha_obtencion_titulo, 5, 6)), n = Inf)
print(count(filter(r, anio_tit == "2026"), tipo_inst_1, nivel_carrera_2))
