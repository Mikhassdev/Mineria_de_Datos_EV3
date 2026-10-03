# =============================================================================
# 01_carga.R
# Lectura del CSV original de Titulados de Educación Superior 2025 (SIES-Mineduc)
# con tipos de columna explícitos. No modifica el archivo original.
# Ejecutar desde la raíz del proyecto (abrir Mineria_de_Datos_EV3.Rproj).
# =============================================================================

suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
})

ruta_raw <- "data/raw/20260817_Titulados_Ed_Superior_2025_WEB.csv"
dir.create("data/processed", showWarnings = FALSE, recursive = TRUE)
dir.create("output/tablas", showWarnings = FALSE, recursive = TRUE)

# Trazabilidad: el hash debe coincidir con data/raw/SHA256.txt
hash_esperado <- "43ed84f62411f2ddfe85c12401afbb9148e30603b200b0629ea5c4bfdfa37676"
hash_actual   <- digest::digest(file = ruta_raw, algo = "sha256")
if (hash_actual != hash_esperado) {
  warning("El CSV original no coincide con el hash registrado: revisar versión del archivo.")
}

# Tipos explícitos: los códigos se leen como texto para no perder ceros ni
# convertir valores especiales (9995, 9998, 9999, 1900) en números "válidos".
tipos <- cols(
  .default               = col_character(),
  gen_alu                = col_integer(),
  anio_ing_carr_ori      = col_integer(),
  sem_ing_carr_ori       = col_integer(),
  anio_ing_carr_act      = col_integer(),
  sem_ing_carr_act       = col_integer(),
  dur_estudio_carr       = col_integer(),
  dur_proceso_tit        = col_integer(),
  dur_total_carr         = col_integer()
)

titulados_raw <- read_delim(
  ruta_raw,
  delim = ";",
  col_types = tipos,
  locale = locale(encoding = "UTF-8"),
  na = c("", "NA"),
  progress = FALSE
)

problemas <- problems(titulados_raw)
cat("Filas leídas:   ", format(nrow(titulados_raw), big.mark = ".", decimal.mark = ","), "\n")
cat("Columnas:       ", ncol(titulados_raw), "\n")
cat("Problemas de parseo:", nrow(problemas), "\n")
cat("SHA-256 coincide:", hash_actual == hash_esperado, "\n")

saveRDS(titulados_raw, "data/processed/00_titulados_raw.rds")
