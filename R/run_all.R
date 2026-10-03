# =============================================================================
# run_all.R  -  Reproduce todo el análisis desde el CSV original.
# Uso: abrir Mineria_de_Datos_EV3.Rproj en RStudio y ejecutar source("R/run_all.R")
# =============================================================================
pasos <- c("R/01_carga.R", "R/02_calidad.R", "R/03_descriptivo.R", "R/04_modelo.R",
           "R/05_datos_dashboard.R", "R/06_render_dashboard.R")
for (p in pasos) {
  cat("\n>>> Ejecutando", p, "\n")
  t0 <- Sys.time()
  source(p, local = new.env(), encoding = "UTF-8")
  cat(">>> OK", p, "en", round(difftime(Sys.time(), t0, units = "secs")), "s\n")
}
writeLines(capture.output(sessionInfo()), "output/logs/sessionInfo.txt")
