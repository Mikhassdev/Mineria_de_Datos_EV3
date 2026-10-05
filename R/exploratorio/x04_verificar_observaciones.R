# Verificación de observaciones del equipo (revisión cruzada antes de la entrega)
suppressPackageStartupMessages({ library(dplyr); library(readr) })
raw <- readRDS("data/processed/00_titulados_raw.rds")
d   <- readRDS("data/processed/01_titulados_pregrado.rds")

cat("== 1. Rango real de fechas de titulación (pregrado limpio) ==\n")
print(range(d$fecha_titulo))
print(count(d, anio_mes = format(fecha_titulo, "%Y-%m")) |> arrange(anio_mes), n = 30)

pre <- raw |> filter(nivel_global == "Pregrado")
cat("\n== 2a. KPI si se excluyeran las titulaciones de 2026 (cifra '67,7 %') ==\n")
d |> filter(format(fecha_titulo, "%Y") == "2025") |>
  summarise(n = n(), pct_oportuna = round(100 * mean(titulacion_oportuna), 1)) |> print()

cat("\n== 2b. Planes de continuidad con el cálculo actual de semestres ==\n")
cont <- pre |>
  filter(between(anio_ing_carr_ori, 1950L, 2025L), sem_ing_carr_ori %in% 1:2,
         tipo_plan_carr == "Plan Regular de Continuidad") |>
  mutate(f = as.Date(fecha_obtencion_titulo, "%Y%m%d"), m = as.integer(format(f, "%m")),
         aa = as.integer(format(f, "%Y")) - as.integer(m <= 2), st = if_else(between(m, 3L, 7L), 1L, 2L),
         sem = (aa * 2L + st) - (anio_ing_carr_ori * 2L + sem_ing_carr_ori) + 1L)
cat("n:", nrow(cont), " mediana semestres transcurridos:", median(cont$sem),
    " mediana duración teórica:", median(cont$dur_total_carr), "\n")

cat("\n== 3. Valores de año de ingreso excluidos por R2 (pregrado) ==\n")
pre |> filter(!between(anio_ing_carr_ori, 1950L, 2025L)) |> count(anio_ing_carr_ori) |> print()
cat("% del pregrado:", round(100 * sum(!between(pre$anio_ing_carr_ori, 1950L, 2025L)) / nrow(pre), 1), "\n")
cat("Todo el archivo (todos los niveles):\n")
raw |> filter(!between(anio_ing_carr_ori, 1950L, 2025L)) |> count(anio_ing_carr_ori) |> print()

cat("\n== 4. Sensibilidad: modalidad ==\n")
read_csv("output/tablas/modelo_sensibilidad.csv", show_col_types = FALSE) |>
  filter(grepl("modalidad|macrozona", termino)) |>
  mutate(across(where(is.numeric), \(x) signif(x, 3))) |> print(width = Inf)

cat("\n== 5. Regiones ordenadas por % oportuna ==\n")
read_csv("output/tablas/kpi_por_dimension.csv", show_col_types = FALSE) |>
  filter(dimension %in% c("region_sede", "macrozona")) |>
  select(dimension, valor, n, pct, ic_inf, ic_sup) |> arrange(dimension, pct) |>
  mutate(across(where(is.numeric), \(x) round(x, 1))) |> print(n = Inf)

# Guardar las cifras verificadas para que los documentos las lean (no escribirlas a mano)
pre_val <- pre |> filter(between(anio_ing_carr_ori, 1950L, 2025L))
verif <- tibble(
  indicador = c("pct_oportuna_sin_ene_feb_2026", "mediana_sem_continuidad", "mediana_teorica_continuidad",
                "n_r2_codigo_1900", "pct_r2_del_pregrado", "pct_r2_del_total", "primera_fecha", "ultima_fecha"),
  valor = c(round(100 * mean(d$titulacion_oportuna[format(d$fecha_titulo, "%Y") == "2025"]), 1),
            median(cont$sem), median(cont$dur_total_carr),
            sum(pre$anio_ing_carr_ori == 1900L), round(100 * mean(pre$anio_ing_carr_ori == 1900L), 1),
            round(100 * sum(raw$anio_ing_carr_ori == 1900L & raw$nivel_global == "Pregrado") / nrow(raw), 1),
            format(min(d$fecha_titulo), "%d-%m-%Y"), format(max(d$fecha_titulo), "%d-%m-%Y")))
write_csv(verif, "output/tablas/verificaciones.csv")
print(verif)
