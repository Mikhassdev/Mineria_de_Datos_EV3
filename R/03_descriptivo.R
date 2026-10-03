# =============================================================================
# 03_descriptivo.R
# KPI y análisis descriptivo con intervalos de confianza (Wilson 95 %).
# Entrada:  data/processed/01_titulados_pregrado.rds
# Salidas:  output/tablas/kpi_*.csv, output/figuras/fig_*.png
# =============================================================================

source("R/00_funciones.R")
suppressPackageStartupMessages(library(readr))
dir.create("output/figuras", showWarnings = FALSE, recursive = TRUE)

d <- readRDS("data/processed/01_titulados_pregrado.rds")
pie <- paste0("Fuente: ", FUENTE, ".\nOportuna = duración teórica + ",
              HOLGURA_SEM, " semestres. Barras: IC 95 % (Wilson).")

# -----------------------------------------------------------------------------
# 1. KPI globales
# -----------------------------------------------------------------------------
kpi_global <- resumir_kpi(d)
kpi_global$pct_estricto <- 100 * mean(d$a_tiempo_estricto)
write_csv(kpi_global, "output/tablas/kpi_global.csv")

# -----------------------------------------------------------------------------
# 2. KPI por dimensión
# -----------------------------------------------------------------------------
dims <- c("grupo_inst", "area_conocimiento", "modalidad_jornada", "macrozona",
          "region_sede", "tramo_edad_ingreso", "genero", "tipo_plan_carr")
kpi_dim <- purrr::map(dims, \(v) resumir_kpi(d, valor = .data[[v]]) |>
                        mutate(dimension = v, valor = as.character(valor), .before = 1)) |>
  purrr::list_rbind()
write_csv(kpi_dim, "output/tablas/kpi_por_dimension.csv")

# Detalle por institución (mínimo 100 titulados para estabilidad)
kpi_inst <- resumir_kpi(d, tipo_inst_1, nomb_inst) |>
  filter(n >= 100) |> arrange(pct)
write_csv(kpi_inst, "output/tablas/kpi_por_institucion.csv")

# -----------------------------------------------------------------------------
# 3. Figuras
# -----------------------------------------------------------------------------
graficar_dim <- function(dim, titulo, archivo) {
  t <- kpi_dim |> filter(dimension == dim, !is.na(valor), valor != "NA") |> mutate(valor = reorder(valor, pct))
  g <- ggplot(t, aes(x = pct, y = valor)) +
    geom_vline(xintercept = META_OPORTUNA, linetype = "dashed", color = COL_ALERTA) +
    annotate("text", x = META_OPORTUNA, y = Inf, label = paste0("Meta ", META_OPORTUNA, " %"),
             vjust = 1.5, hjust = -0.05, size = 3, color = COL_ALERTA) +
    geom_errorbar(aes(xmin = ic_inf, xmax = ic_sup), width = 0.25, orientation = "y", color = COL_TEXTO_2) +
    geom_point(size = 2.8, color = COL_PRINCIPAL) +
    geom_text(aes(label = sprintf("%s %%  (n = %s)", format(round(pct, 1), nsmall = 1, decimal.mark = ","), format(n, big.mark = ".", decimal.mark = ","))),
              hjust = -0.15, vjust = -0.8, size = 3, color = COL_TEXTO_2) +
    scale_x_continuous(limits = c(min(20, floor(min(t$ic_inf) / 10) * 10), 100), labels = \(x) paste0(x, " %")) +
    labs(title = titulo, x = "% titulación oportuna", y = NULL, caption = pie) +
    tema_ev3()
  ggsave(file.path("output/figuras", archivo), g, width = 8, height = 4.5, dpi = 150, bg = "white")
}

graficar_dim("grupo_inst", "Las carreras profesionales universitarias tienen la menor titulación oportuna",
             "fig_01_grupo_inst.png")
graficar_dim("area_conocimiento", "Titulación oportuna por área del conocimiento", "fig_02_area.png")
graficar_dim("modalidad_jornada", "Titulación oportuna por modalidad y jornada", "fig_03_modalidad.png")
graficar_dim("tramo_edad_ingreso", "Titulación oportuna según edad al ingresar a la carrera",
             "fig_04_edad_ingreso.png")
graficar_dim("macrozona", "Titulación oportuna por macrozona de la sede", "fig_05_macrozona.png")

# Distribución de la sobreduración (semestres sobre la duración teórica)
g_hist <- d |>
  mutate(sobre = pmin(pmax(sobreduracion_sem, -4), 12)) |>
  ggplot(aes(x = sobre)) +
  geom_histogram(binwidth = 1, fill = COL_PRINCIPAL, color = "white", linewidth = 0.4) +
  geom_vline(xintercept = HOLGURA_SEM + 0.5, linetype = "dashed", color = COL_ALERTA) +
  annotate("text", x = HOLGURA_SEM + 0.7, y = Inf, vjust = 1.5, hjust = 0, size = 3,
           color = COL_ALERTA, label = "Límite de titulación oportuna") +
  scale_x_continuous(breaks = seq(-4, 12, 2),
                     labels = \(x) ifelse(x == 12, "12+", ifelse(x == -4, "-4 o menos", x))) +
  scale_y_continuous(labels = \(x) format(x, big.mark = ".", decimal.mark = ",")) +
  labs(title = "La mayoría se titula 0 a 2 semestres después de la duración teórica",
       x = "Semestres sobre la duración teórica", y = "Titulados", caption = paste0("Fuente: ", FUENTE)) +
  tema_ev3()
ggsave("output/figuras/fig_06_sobreduracion.png", g_hist, width = 8, height = 4.5, dpi = 150, bg = "white")

# -----------------------------------------------------------------------------
# 4. Consola
# -----------------------------------------------------------------------------
cat("== KPI global ==\n"); print(kpi_global, width = Inf)
cat("\n== KPI por dimensión ==\n")
kpi_dim |> select(dimension, valor, n, pct, ic_inf, ic_sup, mediana_sobreduracion) |>
  mutate(across(c(pct, ic_inf, ic_sup), \(x) round(x, 1))) |> print(n = Inf, width = Inf)
