# Titulación oportuna en pregrado · Chile 2025

Evaluación sumativa TI3V61 (U3 · S9): análisis estadístico en R y dashboard para apoyar decisiones.

**Dashboard:** https://mikhassdev.github.io/Mineria_de_Datos_EV3/

**Pregunta:** ¿qué características de la carrera, la institución y el estudiante se asocian con titularse fuera de plazo (más de la duración teórica + 2 semestres) en pregrado?

## Estructura
| Carpeta | Contenido |
|---|---|
| `R/` | Scripts numerados en orden de ejecución (`00_funciones` … `06_render_dashboard`) y `run_all.R` |
| `R/exploratorio/` | Exploraciones que justifican reglas de calidad (`x01`, `x02`) |
| `dashboard/` | Dashboard en flexdashboard (`.Rmd`) y su versión HTML |
| `docs/` | Copia del dashboard publicada en GitHub Pages |
| `output/tablas/` | KPI, bitácora de calidad y resultados del modelo (generados por código) |
| `output/figuras/` | Figuras para el informe (generadas por código) |
| `output/logs/` | Salida de consola de cada script y `sessionInfo` |
| `data/` | **No se publica**: CSV original (188 MB, contiene MRUN) y datos procesados |

## Reproducir
1. Descargar la base *Titulados de Educación Superior 2025* del SIES-Mineduc y dejar
   `20260817_Titulados_Ed_Superior_2025_WEB.csv` en `data/raw/`
   (SHA-256: `43ed84f62411f2ddfe85c12401afbb9148e30603b200b0629ea5c4bfdfa37676`).
2. Abrir `Mineria_de_Datos_EV3.Rproj` en RStudio y ejecutar `source("R/run_all.R")` (~45 s).

## Decisiones
| Decisión | Motivo |
|---|---|
| Dataset entregado por el docente (uso autorizado) | Requisito de la evaluación |
| Técnica: regresión logística | Respuesta binaria; OR con IC 95 % y diagnósticos |
| Herramienta: flexdashboard + crosstalk (HTML estático) | Se abre sin servidor; filtros en el navegador; solo datos agregados |
| Titulación oportuna = duración teórica + 2 semestres | Práctica/tesis; las instituciones declaran el proceso de titulación de forma heterogénea (`x02`) |
| Año académico 2025 = mar-2025 a feb-2026 | 40.522 titulaciones de ene-feb 2026 pertenecen al cierre de 2025 (`x01`) |
| Excluir Plan Regular de Continuidad | El año de ingreso corresponde a la carrera de origen: respuesta mal medida |
| Edad al ingreso, no `rango_edad` | `rango_edad` es al titularse: causalidad inversa |
| Modelo principal sin `dur_total_carr` | VIF 8,7 y extrapolación; se reporta como sensibilidad |
| Errores estándar agrupados por institución | Observaciones no independientes dentro de cada institución |
| Meta referencial 75 % | Definida por el equipo (provisoria) |
| Celdas del dashboard con n ≥ 30 | Estabilidad de porcentajes y menor riesgo de reidentificación |

## Privacidad
Se eliminan `mrun` y `fec_nac_alu` en el procesamiento; el dashboard contiene solo datos agregados.

## Entorno
R 4.6.1, RStudio 2026.09.0, Pandoc 3.10. Paquetes: tidyverse, rmarkdown, flexdashboard, plotly, DT,
crosstalk, broom, sandwich, lmtest, car, pROC. Detalle en `output/logs/sessionInfo.txt`.
