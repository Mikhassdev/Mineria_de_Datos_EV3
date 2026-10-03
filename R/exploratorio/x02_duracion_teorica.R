# Exploración: ¿dur_total_carr ya incluye el proceso de titulación (práctica/tesis)?
suppressPackageStartupMessages(library(dplyr))
d <- readRDS("data/processed/01_titulados_pregrado.rds")
d |>
  mutate(relacion = case_when(
    dur_total_carr == dur_estudio_carr + dur_proceso_tit ~ "total = estudio + proceso",
    dur_total_carr == dur_estudio_carr                   ~ "total = estudio",
    TRUE                                                 ~ "otra")) |>
  count(nivel_carrera_2, relacion) |> group_by(nivel_carrera_2) |>
  mutate(pct = round(100 * n / sum(n), 1)) |> print(n = Inf)
cat("\nCombinaciones más frecuentes (estudio, proceso, total):\n")
d |> count(nivel_carrera_2, dur_estudio_carr, dur_proceso_tit, dur_total_carr, sort = TRUE) |>
  group_by(nivel_carrera_2) |> slice_head(n = 5) |> print(n = Inf)
cat("\n% oportuna según si la carrera declara proceso de titulación > 0:\n")
d |> group_by(nivel_carrera_2, con_proceso = dur_proceso_tit > 0) |>
  summarise(n = n(), pct_estricto = round(100 * mean(a_tiempo_estricto), 1),
            pct_oportuna = round(100 * mean(titulacion_oportuna), 1),
            mediana_sobreduracion = median(sobreduracion_sem), .groups = "drop") |> print()
