# =============================================================================
# 00_funciones.R
# Funciones y parámetros compartidos por los scripts de análisis y el dashboard.
# =============================================================================

suppressPackageStartupMessages({
  library(dplyr)
  library(ggplot2)
})

# Parámetros del KPI (centralizados para que cualquier cambio sea trazable)
HOLGURA_SEM     <- 2L      # semestres de holgura sobre la duración teórica
META_OPORTUNA   <- 75      # meta referencial (%), definida por el equipo
FUENTE          <- "SIES-Mineduc, Titulados Educación Superior 2025 (base WEB, ago-2026)"

# Proporción con intervalo de confianza de Wilson al 95 %
prop_ic <- function(x, n, conf = 0.95) {
  z <- qnorm(1 - (1 - conf) / 2)
  p <- x / n
  centro <- (p + z^2 / (2 * n)) / (1 + z^2 / n)
  margen <- z * sqrt(p * (1 - p) / n + z^2 / (4 * n^2)) / (1 + z^2 / n)
  tibble(pct = 100 * p, ic_inf = 100 * (centro - margen), ic_sup = 100 * (centro + margen))
}

# Resumen de KPI para cualquier agrupación
resumir_kpi <- function(datos, ...) {
  datos |>
    group_by(...) |>
    summarise(n = n(),
              n_oportuna = sum(titulacion_oportuna),
              mediana_sobreduracion = median(sobreduracion_sem),
              pct_mas_doble = 100 * mean(ratio_duracion > 2),
              .groups = "drop") |>
    (\(r) bind_cols(r, prop_ic(r$n_oportuna, r$n)))() |>
    mutate(brecha_meta_pp = pct - META_OPORTUNA)
}

# Paleta (validada: ver skill dataviz, palette.md) y tema gráfico
COL_PRINCIPAL <- "#2a78d6"
COL_ALERTA    <- "#eb6834"
COL_TEXTO_2   <- "#52514e"
COL_GRILLA    <- "#e1e0d9"

tema_ev3 <- function() {
  theme_minimal(base_size = 11) +
    theme(
      plot.title       = element_text(face = "bold", size = 13),
      plot.subtitle    = element_text(color = COL_TEXTO_2),
      plot.caption     = element_text(color = "#898781", size = 8, hjust = 0),
      panel.grid.major = element_line(color = COL_GRILLA, linewidth = 0.3),
      panel.grid.minor = element_blank(),
      axis.text        = element_text(color = COL_TEXTO_2)
    )
}
