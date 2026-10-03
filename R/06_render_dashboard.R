# =============================================================================
# 06_render_dashboard.R - Genera dashboard/dashboard_titulacion.html
# (desde RStudio basta con "Knit"; fuera de RStudio se usa el Pandoc incluido)
# =============================================================================
if (!rmarkdown::pandoc_available()) {
  Sys.setenv(RSTUDIO_PANDOC = file.path(Sys.getenv("LOCALAPPDATA"),
    "Programs/RStudio/resources/app/bin/quarto/bin/tools"))
}
rmarkdown::render("dashboard/dashboard_titulacion.Rmd", quiet = TRUE,
                  output_file = "dashboard_titulacion.html")
cat("Dashboard generado:", normalizePath("dashboard/dashboard_titulacion.html"), "\n")

# Copia para GitHub Pages (rama main, carpeta /docs)
dir.create("docs", showWarnings = FALSE)
file.copy("dashboard/dashboard_titulacion.html", "docs/index.html", overwrite = TRUE)
file.create("docs/.nojekyll")
