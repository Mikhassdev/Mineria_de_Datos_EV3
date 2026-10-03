# =============================================================================
# 04_modelo.R
# Regresión logística: factores asociados a titularse FUERA DE PLAZO
# (más de duración teórica + HOLGURA_SEM semestres) en pregrado 2025.
#
# Decisiones metodológicas:
#  - Respuesta binaria -> regresión logística (glm, enlace logit).
#  - Inferencia con errores estándar agrupados por institución (vcovCL):
#    los titulados de una misma institución no son observaciones independientes.
#  - Edad AL INGRESO (no al titularse) para evitar causalidad inversa.
#  - Validación predictiva en partición 70/30 (AUC, Brier, calibración).
#  - Efectos traducidos a puntos porcentuales (efecto marginal promedio por
#    estandarización) para la audiencia no técnica.
#
# Entrada:  data/processed/01_titulados_pregrado.rds
# Salidas:  output/tablas/modelo_*.csv, output/figuras/fig_1*_*.png,
#           data/processed/02_modelo_resumen.rds
# =============================================================================

source("R/00_funciones.R")
suppressPackageStartupMessages({
  library(readr)
  library(tidyr)
  library(broom)
  library(sandwich)
  library(lmtest)
  library(car)
  library(pROC)
})

d <- readRDS("data/processed/01_titulados_pregrado.rds")

# -----------------------------------------------------------------------------
# 1. Datos del modelo: categorías de referencia = grupo más numeroso
# -----------------------------------------------------------------------------
dm <- d |>
  transmute(
    fuera_de_plazo,
    cod_inst,
    grupo_inst         = relevel(factor(grupo_inst), ref = "Universidad · profesional"),
    area_conocimiento  = relevel(factor(area_conocimiento), ref = "Tecnología"),
    modalidad_jornada  = relevel(factor(modalidad_jornada), ref = "Presencial diurna"),
    macrozona          = relevel(factor(macrozona), ref = "Metropolitana"),
    tramo_edad_ingreso = tramo_edad_ingreso,
    genero             = genero,
    tipo_plan_carr     = relevel(factor(tipo_plan_carr), ref = "Plan Regular"),
    declara_proceso_tit,
    dur_total_carr
  ) |>
  drop_na()

cat("Registros para el modelo:", nrow(dm), "(excluidos por NA:", nrow(d) - nrow(dm), ")\n")
cat("Prevalencia fuera de plazo:", round(100 * mean(dm$fuera_de_plazo), 1), "%\n")

formula_modelo <- fuera_de_plazo ~ grupo_inst + area_conocimiento + modalidad_jornada +
  macrozona + tramo_edad_ingreso + genero + tipo_plan_carr +
  declara_proceso_tit
# dur_total_carr NO se incluye en el modelo principal: es colineal con
# grupo_inst (VIF ~8,7) y condicionar en ella obliga a comparar carreras
# técnicas y profesionales "a igual duración", combinación que no existe en
# los datos (extrapolación). Se evalúa como análisis de sensibilidad (6b).

# -----------------------------------------------------------------------------
# 2. Modelo de inferencia (todos los datos) con errores agrupados
# -----------------------------------------------------------------------------
m <- glm(formula_modelo, data = dm, family = binomial())
vc <- vcovCL(m, cluster = ~ cod_inst)
ct <- coeftest(m, vcov. = vc)

tabla_or <- tibble(
  termino  = rownames(ct),
  log_odds = ct[, 1],
  ee_cluster = ct[, 2],
  z        = ct[, 3],
  p_valor  = ct[, 4]
) |>
  mutate(OR     = exp(log_odds),
         OR_inf = exp(log_odds - qnorm(0.975) * ee_cluster),
         OR_sup = exp(log_odds + qnorm(0.975) * ee_cluster),
         significativo_5pct = p_valor < 0.05) |>
  filter(termino != "(Intercept)")
write_csv(tabla_or, "output/tablas/modelo_odds_ratio.csv")

# -----------------------------------------------------------------------------
# 3. Diagnósticos
# -----------------------------------------------------------------------------
# 3a. Multicolinealidad (GVIF ajustado: GVIF^(1/(2*gl)); umbral habitual < 2.24 ~ VIF 5)
vif_tab <- as_tibble(car::vif(m), rownames = "variable") |>
  rename(GVIF = 2, gl = 3, GVIF_ajustado = 4)
write_csv(vif_tab, "output/tablas/modelo_vif.csv")

# 3b. Ajuste global
ajuste <- tibble(
  n            = nobs(m),
  AIC          = AIC(m),
  devianza_nula = m$null.deviance,
  devianza_res = m$deviance,
  pseudo_R2_McFadden = 1 - m$deviance / m$null.deviance,
  # Sobredispersión: en logit binaria individual debería ser ~1
  ratio_dispersion = sum(residuals(m, type = "pearson")^2) / m$df.residual
)
write_csv(ajuste, "output/tablas/modelo_ajuste.csv")

# -----------------------------------------------------------------------------
# 4. Validación predictiva (partición 70/30, semilla fija)
# -----------------------------------------------------------------------------
set.seed(2025)
idx_train <- sample(nrow(dm), size = floor(0.7 * nrow(dm)))
train <- dm[idx_train, ]
test  <- dm[-idx_train, ]
m_train <- glm(formula_modelo, data = train, family = binomial())
test$prob <- predict(m_train, newdata = test, type = "response")

roc_obj <- roc(test$fuera_de_plazo, test$prob, quiet = TRUE)
auc_ic  <- ci.auc(roc_obj)
brier   <- mean((test$prob - test$fuera_de_plazo)^2)
brier_ref <- mean((mean(train$fuera_de_plazo) - test$fuera_de_plazo)^2)  # modelo sin predictores

metricas <- tibble(
  n_test = nrow(test),
  AUC = as.numeric(auc_ic[2]), AUC_inf = as.numeric(auc_ic[1]), AUC_sup = as.numeric(auc_ic[3]),
  Brier = brier, Brier_referencia = brier_ref,
  mejora_Brier_pct = 100 * (1 - brier / brier_ref)
)
write_csv(metricas, "output/tablas/modelo_metricas_test.csv")

# Calibración por deciles de probabilidad predicha
calib <- test |>
  mutate(decil = ntile(prob, 10)) |>
  group_by(decil) |>
  summarise(n = n(), prob_predicha = mean(prob), tasa_observada = mean(fuera_de_plazo),
            .groups = "drop")
write_csv(calib, "output/tablas/modelo_calibracion.csv")

# -----------------------------------------------------------------------------
# 5. Efectos marginales promedio (puntos porcentuales) por estandarización:
#    probabilidad media predicha si TODOS pertenecieran a cada categoría,
#    manteniendo el resto de las características observadas.
# -----------------------------------------------------------------------------
efecto_marginal <- function(variable) {
  niveles <- levels(dm[[variable]])
  purrr::map(niveles, \(nv) {
    tmp <- dm
    tmp[[variable]] <- factor(nv, levels = niveles)
    tibble(variable = variable, nivel = nv,
           prob_fuera_plazo = mean(predict(m, newdata = tmp, type = "response")))
  }) |>
    purrr::list_rbind() |>
    mutate(dif_vs_ref_pp = 100 * (prob_fuera_plazo - prob_fuera_plazo[nivel == niveles[1]]),
           prob_fuera_plazo = 100 * prob_fuera_plazo)
}
efectos <- purrr::map(c("grupo_inst", "area_conocimiento", "modalidad_jornada",
                        "macrozona", "tramo_edad_ingreso", "genero"), efecto_marginal) |>
  purrr::list_rbind()
write_csv(efectos, "output/tablas/modelo_efectos_marginales.csv")

# -----------------------------------------------------------------------------
# 6. Figuras
# -----------------------------------------------------------------------------
etiquetar <- function(t) {
  t |>
    mutate(variable = case_when(
      startsWith(termino, "grupo_inst") ~ "Institución · nivel",
      startsWith(termino, "area_conocimiento") ~ "Área",
      startsWith(termino, "modalidad_jornada") ~ "Modalidad",
      startsWith(termino, "macrozona") ~ "Macrozona",
      startsWith(termino, "tramo_edad_ingreso") ~ "Edad al ingreso",
      startsWith(termino, "genero") ~ "Género",
      startsWith(termino, "tipo_plan") ~ "Tipo de plan",
      startsWith(termino, "declara") ~ "Declara proceso tit.",
      TRUE ~ "Duración teórica (por semestre)"),
      nivel = sub("^(grupo_inst|area_conocimiento|modalidad_jornada|macrozona|tramo_edad_ingreso|genero|tipo_plan_carr|declara_proceso_tit)", "", termino),
      nivel = ifelse(nivel == "TRUE", "Sí", nivel),
      nivel = ifelse(nivel == "dur_total_carr", "+1 semestre teórico", nivel))
}

g_or <- tabla_or |>
  etiquetar() |>
  mutate(nivel = reorder(paste0(nivel, "  "), OR)) |>
  ggplot(aes(x = OR, y = nivel)) +
  geom_vline(xintercept = 1, color = COL_TEXTO_2, linewidth = 0.4) +
  geom_errorbar(aes(xmin = OR_inf, xmax = OR_sup), width = 0.3, orientation = "y",
                color = COL_TEXTO_2) +
  # El color solo indica dirección cuando el IC 95 % excluye 1; si no, gris
  geom_point(aes(color = case_when(p_valor >= 0.05 ~ "Sin diferencia significativa",
                                   OR > 1 ~ "Más riesgo de atraso",
                                   TRUE ~ "Menos riesgo de atraso")), size = 2.4) +
  scale_color_manual(values = c("Más riesgo de atraso" = COL_ALERTA,
                                "Menos riesgo de atraso" = COL_PRINCIPAL,
                                "Sin diferencia significativa" = "#898781"),
                     name = NULL) +
  scale_x_log10() +
  facet_grid(variable ~ ., scales = "free_y", space = "free_y", switch = "y") +
  labs(title = "Factores asociados a titularse fuera de plazo",
       subtitle = "Odds ratio con IC 95 % (errores agrupados por institución).\nEscala logarítmica; 1 = sin diferencia respecto de la referencia.",
       x = "Odds ratio vs. categoría de referencia", y = NULL,
       caption = paste0("Referencias: Universidad · profesional, Tecnología, Presencial diurna, Metropolitana, ",
                        "19 o menos, Hombre, Plan Regular.\nFuente: ", FUENTE)) +
  tema_ev3() +
  theme(strip.placement = "outside", strip.text.y.left = element_text(angle = 0, face = "bold"),
        legend.position = "top")
ggsave("output/figuras/fig_10_odds_ratio.png", g_or, width = 9, height = 10, dpi = 150, bg = "white")

g_cal <- ggplot(calib, aes(x = 100 * prob_predicha, y = 100 * tasa_observada)) +
  geom_abline(slope = 1, intercept = 0, linetype = "dashed", color = COL_TEXTO_2) +
  geom_line(color = COL_PRINCIPAL, linewidth = 0.6) +
  geom_point(color = COL_PRINCIPAL, size = 2.5) +
  coord_equal(xlim = c(0, 80), ylim = c(0, 80)) +
  labs(title = "Calibración en datos de prueba (30 %)",
       subtitle = "Cada punto es un decil de probabilidad predicha; la diagonal es calibración perfecta",
       x = "% predicho fuera de plazo", y = "% observado fuera de plazo",
       caption = sprintf("AUC = %.3f (IC 95 %%: %.3f–%.3f).\nFuente: %s",
                         metricas$AUC, metricas$AUC_inf, metricas$AUC_sup, FUENTE)) +
  tema_ev3()
ggsave("output/figuras/fig_11_calibracion.png", g_cal, width = 7, height = 6, dpi = 150, bg = "white")

# -----------------------------------------------------------------------------
# 6b. Sensibilidad: se agrega dur_total_carr al modelo principal y se
#     comparan los OR de las variables comunes.
# -----------------------------------------------------------------------------
m_sens  <- glm(update(formula_modelo, . ~ . + dur_total_carr), data = dm, family = binomial())
ct_sens <- coeftest(m_sens, vcov. = vcovCL(m_sens, cluster = ~ cod_inst))
sensibilidad <- tibble(termino = rownames(ct_sens), OR_con_duracion = exp(ct_sens[, 1]),
                       p_con_duracion = ct_sens[, 4]) |>
  inner_join(select(tabla_or, termino, OR_modelo_principal = OR, p_modelo_principal = p_valor),
             by = "termino") |>
  mutate(cambio_pct = 100 * (OR_con_duracion / OR_modelo_principal - 1),
         cambia_conclusion = (OR_con_duracion > 1) != (OR_modelo_principal > 1) |
           (p_con_duracion < 0.05) != (p_modelo_principal < 0.05))
write_csv(sensibilidad, "output/tablas/modelo_sensibilidad.csv")
cat("\n== Sensibilidad (agregando dur_total_carr) ==\n")
sensibilidad |> mutate(across(where(is.numeric), \(x) signif(x, 3))) |> print(n = Inf, width = Inf)
cat("GVIF ajustado de dur_total_carr en el modelo de sensibilidad:",
    round(car::vif(m_sens)["dur_total_carr", 3], 2), "\n")

saveRDS(list(tabla_or = tabla_or, efectos = efectos, metricas = metricas,
             ajuste = ajuste, vif = vif_tab, calibracion = calib,
             sensibilidad = sensibilidad),
        "data/processed/02_modelo_resumen.rds")

# -----------------------------------------------------------------------------
# 7. Consola
# -----------------------------------------------------------------------------
cat("\n== Odds ratio (errores agrupados por institución) ==\n")
tabla_or |> select(termino, OR, OR_inf, OR_sup, p_valor) |>
  mutate(across(where(is.numeric), \(x) signif(x, 3))) |> print(n = Inf, width = Inf)
cat("\n== VIF ==\n"); print(vif_tab)
cat("\n== Ajuste ==\n"); print(ajuste, width = Inf)
cat("\n== Métricas en test ==\n"); print(metricas, width = Inf)
cat("\n== Calibración ==\n"); print(calib)
cat("\n== Efectos marginales promedio (pp vs referencia) ==\n")
efectos |> mutate(across(where(is.numeric), \(x) round(x, 1))) |> print(n = Inf)
