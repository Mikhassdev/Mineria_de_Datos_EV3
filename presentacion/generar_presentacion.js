// =============================================================================
// generar_presentacion.js
// Genera presentacion/Presentacion_Titulacion_Oportuna_2025.pptx (≈9 min + anexo).
// Uso (desde la raíz del proyecto):  node presentacion/generar_presentacion.js
// Cifras: provienen de output/tablas/*.csv (generadas por R/run_all.R).
// =============================================================================
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa6");

const RAIZ = path.resolve(__dirname, "..");
const FIG = (f) => path.join(RAIZ, "output", "figuras", f);
const SALIDA = path.join(__dirname, "Presentacion_Titulacion_Oportuna_2025.pptx");
const URL_DASH = "mikhassdev.github.io/Mineria_de_Datos_EV3";
const URL_REPO = "github.com/Mikhassdev/Mineria_de_Datos_EV3";

// ------------------------------------------------------------------ datos
function leerCSV(f) {
  const txt = fs.readFileSync(path.join(RAIZ, "output", "tablas", f), "utf8").trim().split(/\r?\n/);
  const cab = txt[0].split(",");
  return txt.slice(1).map((l) => {
    const v = l.match(/("([^"]|"")*"|[^,]*)(,|$)/g).map((x) => x.replace(/,$/, "").replace(/^"|"$/g, ""));
    return Object.fromEntries(cab.map((c, i) => [c, v[i]]));
  });
}
const num = (v, d = 1) => Number(v).toLocaleString("es-CL", { minimumFractionDigits: d, maximumFractionDigits: d });
const ent = (v) => Math.round(Number(v)).toLocaleString("es-CL");
const pp = (v) => (Number(v) > 0 ? "+" : "") + num(v) + " pp";

const kg = leerCSV("kpi_global.csv")[0];
const kd = leerCSV("kpi_por_dimension.csv");
const bit = leerCSV("bitacora_calidad.csv");
const ef = leerCSV("modelo_efectos_marginales.csv");
const orx = Object.fromEntries(leerCSV("modelo_odds_ratio.csv").map((r) => [r.termino, r]));
const met = leerCSV("modelo_metricas_test.csv")[0];
const aj = leerCSV("modelo_ajuste.csv")[0];
const vif = leerCSV("modelo_vif.csv");
const sens = Object.fromEntries(leerCSV("modelo_sensibilidad.csv").map((r) => [r.termino, r]));
const kv = (d, v) => kd.find((r) => r.dimension === d && r.valor === v);
const efe = (v, n) => ef.find((r) => r.variable === v && r.nivel === n);
const grupos = kd.filter((r) => r.dimension === "grupo_inst");
const peor = grupos.reduce((a, b) => (Number(a.pct) < Number(b.pct) ? a : b));
const mejor = grupos.reduce((a, b) => (Number(a.pct) > Number(b.pct) ? a : b));
const derecho = kv("area_conocimiento", "Derecho");
const filas = Object.fromEntries(bit.map((b) => [b.paso, b]));
const fueraPlazo = 100 - Number(kg.pct);

// ------------------------------------------------------------------ tema
const THEME = {
  name: "Titulacion Oportuna",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1F2328", lt1: "FFFFFF", dk2: "3A3F47", lt2: "F2F3F5",
    accent1: "C8102E", accent2: "2A78D6", accent3: "EB6834",
    accent4: "898781", accent5: "1BAF7A", accent6: "4A3AA7",
    hlink: "2A78D6", folHlink: "4A3AA7",
  },
};
const HEX = THEME.colors;
const ROJO_SUAVE = "FBE9EB";   // tinte del rojo para tarjetas de alerta
const GRIS_TEXTO = "5A5F66";
const GRIS_CLARO_OSCURO = "C9CCD1"; // texto secundario sobre fondo oscuro

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13,33" × 7,5"
pres.title = "Titulación oportuna en pregrado · Chile 2025";
pres.subject = "TI3V61 · Evaluación sumativa · Unidad 3";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;

// ------------------------------------------------------------------ íconos
async function icono(Comp, color = "#FFFFFF") {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color, size: 256 }));
  const png = await sharp(Buffer.from(svg)).resize(256, 256).png().toBuffer();
  return "image/png;base64," + png.toString("base64");
}
// Motivo visual: ícono blanco dentro de un círculo de color
function circuloIcono(slide, data, x, y, d, relleno, nombre) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: relleno }, line: { color: relleno }, objectName: nombre + " círculo" });
  const m = d * 0.24;
  slide.addImage({ data, x: x + m, y: y + m, w: d - 2 * m, h: d - 2 * m, objectName: nombre + " ícono" });
}
const T = (slide, text, opts) => slide.addText(text, Object.assign({ isTextBox: true, margin: 0, fontFace: THEME.bodyFontFace }, opts));

// ------------------------------------------------------------------ layouts
const PIE = "Titulación oportuna en pregrado · Chile 2025";
pres.defineSlideMaster({
  title: "OSCURA",
  background: { color: HEX.dk1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.7, y: 0.45, w: 11.9, h: 1.0, fontFace: THEME.headFontFace,
        fontSize: 32, bold: true, color: C.background1, valign: "top", margin: 0 }, text: "" } },
  ],
  slideNumber: { x: 12.3, y: 6.95, w: 0.6, h: 0.3, fontSize: 10, color: GRIS_CLARO_OSCURO, align: "right" },
});
// Portada y cierre: el título vive en su propia posición (las posiciones de un
// placeholder no se pueden cambiar lámina a lámina)
pres.defineSlideMaster({
  title: "PORTADA",
  background: { color: HEX.dk1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.7, y: 1.85, w: 8.2, h: 1.2, fontFace: THEME.headFontFace,
        fontSize: 48, bold: true, color: C.background1, align: "left", valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CIERRE",
  background: { color: HEX.dk1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.7, y: 1.3, w: 11.9, h: 2.0, fontFace: THEME.headFontFace,
        fontSize: 34, bold: true, color: C.background1, align: "left", valign: "top", margin: 0 }, text: "" } },
  ],
  slideNumber: { x: 12.3, y: 6.95, w: 0.6, h: 0.3, fontSize: 10, color: GRIS_CLARO_OSCURO, align: "right" },
});
pres.defineSlideMaster({
  title: "CONTENIDO",
  background: { color: HEX.lt1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.4, w: 12.1, h: 0.95, fontFace: THEME.headFontFace,
        fontSize: 28, bold: true, color: C.text1, valign: "top", margin: 0 }, text: "" } },
    { text: { text: PIE, options: { x: 0.6, y: 6.95, w: 8, h: 0.3, fontSize: 10, color: HEX.accent4, margin: 0 } } },
  ],
  slideNumber: { x: 12.1, y: 6.95, w: 0.6, h: 0.3, fontSize: 10, color: HEX.accent4, align: "right" },
});

// ------------------------------------------------------------------ gráficos
const EJE = { catAxisLabelColor: GRIS_TEXTO, valAxisLabelColor: GRIS_TEXTO, catAxisLabelFontFace: "+mn-lt",
  valAxisLabelFontFace: "+mn-lt", dataLabelFontFace: "+mn-lt", catAxisLabelFontSize: 13, valAxisLabelFontSize: 11,
  dataLabelFontSize: 13, dataLabelColor: HEX.dk1, valGridLine: { color: "E3E4E8", size: 0.75 },
  catGridLine: { style: "none" }, showLegend: false, catAxisLineShow: false };

async function construir() {
  const I = {
    grad: await icono(fa.FaUserGraduate), pregunta: await icono(fa.FaCircleQuestion), decision: await icono(fa.FaScaleBalanced),
    audiencia: await icono(fa.FaPeopleGroup), alerta: await icono(fa.FaTriangleExclamation), columnas: await icono(fa.FaTableColumns),
    reloj: await icono(fa.FaUserClock), red: await icono(fa.FaBuildingColumns), corte: await icono(fa.FaCodeBranch),
    check: await icono(fa.FaCircleCheck), sobrevive: await icono(fa.FaFilter), causa: await icono(fa.FaArrowsLeftRight),
    regla: await icono(fa.FaRulerHorizontal), calendario: await icono(fa.FaCalendarDay), actuar: await icono(fa.FaBullseye),
    investigar: await icono(fa.FaMagnifyingGlass), pausa: await icono(fa.FaCirclePause), monitor: await icono(fa.FaArrowsRotate),
    link: await icono(fa.FaLink),
  };

  // =============================================================== 1. PORTADA
  pres.addSection({ title: "Inicio" });
  let s = pres.addSlide({ masterName: "PORTADA", sectionTitle: "Inicio" });
  T(s, "TI3V61 · Evaluación sumativa · Unidad 3", { x: 0.7, y: 0.55, w: 8, h: 0.35, fontSize: 14, color: GRIS_CLARO_OSCURO });
  s.addText("¿Quién se titula a tiempo?", { placeholder: "title" });
  T(s, "Titulación oportuna en pregrado · Chile 2025", { x: 0.7, y: 3.1, w: 7.8, h: 0.55, fontSize: 24, color: C.background1 });
  T(s, "Análisis estadístico en R y dashboard para apoyar decisiones académicas", { x: 0.7, y: 3.7, w: 7.6, h: 0.8, fontSize: 17, color: GRIS_CLARO_OSCURO });
  T(s, [{ text: "Integrantes: ", options: { bold: true } }, { text: "[Tu nombre] · Ignacio Larama Paycho · Johan Matos Chauca" }],
    { x: 0.7, y: 5.75, w: 8.2, h: 0.4, fontSize: 14, color: GRIS_CLARO_OSCURO });
  s.addShape(pres.shapes.OVAL, { x: 9.2, y: 1.55, w: 3.4, h: 3.4, fill: { color: C.accent1 }, line: { color: HEX.accent1 }, objectName: "Círculo KPI" });
  T(s, num(kg.pct) + " %", { x: 9.2, y: 2.45, w: 3.4, h: 0.9, fontSize: 48, bold: true, color: C.background1, align: "center", fontFace: THEME.headFontFace });
  T(s, "de las titulaciones fue oportuna", { x: 9.55, y: 3.35, w: 2.7, h: 0.7, fontSize: 15, color: C.background1, align: "center" });
  s.addNotes(
`[0:15] Presentación del equipo y del tema.
Decir: "Analizamos los 328 mil registros de titulados 2025 del SIES para responder una pregunta concreta: quién se titula a tiempo y dónde se concentra el atraso."
El círculo adelanta el resultado principal: 71,8 % de titulación oportuna.`);

  // =============================================================== 2. PROBLEMA
  s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Inicio" });
  s.addText("3 de cada 10 titulados terminan más de un año tarde", { placeholder: "title" });
  T(s, num(fueraPlazo) + " %", { x: 0.6, y: 1.55, w: 4.4, h: 1.3, fontSize: 72, bold: true, color: C.accent1, fontFace: THEME.headFontFace });
  T(s, "de las titulaciones de pregrado 2025 ocurrió más de un año después de la duración teórica de la carrera",
    { x: 0.6, y: 2.9, w: 4.3, h: 1.0, fontSize: 16, color: C.text1 });
  T(s, "Más arancel, inserción laboral tardía y una señal de problemas en práctica, tesis o examen de grado.",
    { x: 0.6, y: 4.0, w: 4.3, h: 0.9, fontSize: 14, color: GRIS_TEXTO, italic: true });
  const filasProb = [
    [I.pregunta, "Pregunta", "¿Qué características de la carrera, la institución y el estudiante se asocian con titularse fuera de plazo?"],
    [I.decision, "Decisión que apoya", "Dónde focalizar apoyo al avance curricular y al proceso de titulación"],
    [I.audiencia, "Audiencia", "Direcciones académicas y unidades de análisis institucional"],
  ];
  filasProb.forEach(([ic, tit, txt], i) => {
    const y = 1.6 + i * 1.1;
    circuloIcono(s, ic, 5.5, y, 0.7, C.text1, tit);
    T(s, tit, { x: 6.45, y: y - 0.02, w: 6.2, h: 0.35, fontSize: 17, bold: true, color: C.text1 });
    T(s, txt, { x: 6.45, y: y + 0.33, w: 6.2, h: 0.6, fontSize: 14, color: GRIS_TEXTO, valign: "top" });
  });
  const kpis = [
    [num(kg.pct) + " %", "Titulación oportuna · meta 75 %"],
    [pp(Number(peor.pct) - Number(mejor.pct)), "Brecha entre tipos de institución"],
    [ent(kg.mediana_sobreduracion) + " semestre", "Atraso mediano sobre lo teórico"],
    [num(kg.pct_mas_doble) + " %", "Tarda más del doble"],
  ];
  kpis.forEach(([v, l], i) => {
    const x = 0.6 + i * 3.08;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 5.15, w: 2.85, h: 1.45, rectRadius: 0.12, fill: { color: C.background2 }, line: { color: HEX.lt2 }, objectName: "KPI " + (i + 1) });
    T(s, v, { x: x + 0.2, y: 5.3, w: 2.5, h: 0.6, fontSize: 26, bold: true, color: C.text1, fontFace: THEME.headFontFace });
    T(s, l, { x: x + 0.2, y: 5.92, w: 2.5, h: 0.55, fontSize: 12, color: GRIS_TEXTO, valign: "top" });
  });
  s.addNotes(
`[1:00] El problema y para qué sirve el análisis.
Decir: "Definimos titulación oportuna como titularse dentro de la duración teórica más un año, porque muchas carreras exigen práctica, tesis o examen de grado después de las asignaturas."
"La decisión que apoyamos es dónde focalizar recursos limitados de apoyo a la titulación; por eso la audiencia son direcciones académicas."
"Definimos cuatro KPI; la meta del 75 % es referencial, definida por el equipo, porque no existe un estándar oficial único."

Pregunta probable: ¿por qué un año de holgura y no la duración exacta?
Respuesta: con la duración exacta solo el 31,4 % se titula a tiempo; además, las instituciones declaran la duración de forma heterogénea (muchas informan un semestre de proceso de titulación sin sumarlo al total). Reportamos ambos criterios.`);

  // =============================================================== 3. DATOS Y LIMPIEZA
  pres.addSection({ title: "Análisis" });
  s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Análisis" });
  s.addText("De " + ent(filas.R1.filas_antes) + " registros a " + ent(kg.n) + " titulaciones válidas", { placeholder: "title" });
  const embudo = [
    [Number(filas.R1.filas_antes), ent(filas.R1.filas_antes) + " × 41 col.", "Base original SIES 2025", HEX.dk1],
    [Number(filas.R1.filas_despues), ent(filas.R1.filas_despues), "− " + ent(filas.R1.eliminadas) + " de posgrado y postítulo (alcance, no error)", HEX.dk2],
    [Number(filas.R2.filas_despues), ent(filas.R2.filas_despues), "− " + ent(filas.R2.eliminadas) + " con año de ingreso inválido (códigos 1900, 9995, 9998, 9999)", HEX.dk2],
    [Number(filas.R7.filas_despues), ent(filas.R7.filas_despues) + " × 54 col.", "− " + ent(filas.R7.eliminadas) + " de planes de continuidad (ingreso de otra carrera)", HEX.accent1],
  ];
  const maxN = embudo[0][0];
  embudo.forEach(([n, etiqueta, motivo, color], i) => {
    const y = 1.65 + i * 1.12, w = 4.2 * n / maxN;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y, w, h: 0.78, rectRadius: 0.08, fill: { color }, line: { color }, objectName: "Embudo " + (i + 1) });
    T(s, etiqueta, { x: 0.8, y, w: w - 0.3, h: 0.78, fontSize: 17, bold: true, color: C.background1, valign: "middle" });
    T(s, motivo, { x: 5.05, y, w: 3.35, h: 0.78, fontSize: 13, color: i === 0 ? C.text1 : GRIS_TEXTO, valign: "middle", bold: i === 0 });
  });
  T(s, "Todo por código en R, con bitácora automática y verificación SHA-256 del archivo original",
    { x: 0.6, y: 6.25, w: 7.8, h: 0.4, fontSize: 12, color: GRIS_TEXTO, italic: true });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.75, y: 1.6, w: 3.98, h: 2.95, rectRadius: 0.12, fill: { color: ROJO_SUAVE }, line: { color: ROJO_SUAVE }, objectName: "Tarjeta corrección" });
  circuloIcono(s, I.alerta, 9.0, 1.82, 0.62, C.accent1, "Alerta");
  T(s, "Casi eliminamos el 18 % por error", { x: 9.75, y: 1.82, w: 2.85, h: 0.65, fontSize: 16, bold: true, color: C.accent1, valign: "middle" });
  T(s, "Una regla descartaba 40.522 titulaciones de enero y febrero de 2026. Son del cierre del año académico 2025: excluirlas habría bajado el KPI de " + num(kg.pct) + " % a 67,7 %.",
    { x: 9.0, y: 2.6, w: 3.5, h: 1.8, fontSize: 13.5, color: C.text1, valign: "top" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.75, y: 4.75, w: 3.98, h: 1.9, rectRadius: 0.12, fill: { color: C.background2 }, line: { color: HEX.lt2 }, objectName: "Tarjeta columnas" });
  circuloIcono(s, I.columnas, 9.0, 4.97, 0.62, C.text1, "Columnas");
  T(s, "Columnas: −4 y +17", { x: 9.75, y: 4.97, w: 2.85, h: 0.62, fontSize: 16, bold: true, color: C.text1, valign: "middle" });
  T(s, "Se eliminan MRUN, fecha de nacimiento y títulos en texto (privacidad). Se crean 17 variables: tiempo de titulación, respuesta y recodificaciones.",
    { x: 9.0, y: 5.7, w: 3.5, h: 0.9, fontSize: 12, color: GRIS_TEXTO, valign: "top" });
  s.addNotes(
`[1:15] Calidad y limpieza de datos.
Decir: "Partimos con 328.998 filas y 41 columnas y terminamos con 216.436 filas y 54 columnas."
"Ojo: no todo lo eliminado era dato sucio. 90 mil filas salieron por alcance (posgrado y postítulo), 17 mil por códigos inválidos en el año de ingreso, y 4.500 de planes de continuidad, donde el año de ingreso corresponde a otra carrera."
"Lo más importante: una primera regla eliminaba el 18 % de la base. Revisamos y eran titulaciones de enero y febrero de 2026, que pertenecen al cierre del año académico 2025. Si no lo detectamos, habríamos subestimado el KPI."
"Por privacidad eliminamos el MRUN y la fecha de nacimiento; el dashboard solo muestra datos agregados."

Pregunta probable: ¿por qué no eliminaron los MRUN repetidos?
Respuesta: no son duplicados, son 11.951 personas con más de un título. La unidad de análisis es la titulación.`);

  // =============================================================== 4. MÉTODO
  s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Análisis" });
  s.addText("Regresión logística con cuatro decisiones que protegen la validez", { placeholder: "title" });
  T(s, [{ text: "Respuesta: ", options: { bold: true } }, { text: "titularse fuera de plazo (sí/no) · " + ent(aj.n) + " titulaciones · 8 factores de carrera, institución y estudiante" }],
    { x: 0.6, y: 1.45, w: 12.1, h: 0.4, fontSize: 15, color: GRIS_TEXTO });
  const decisiones = [
    [I.reloj, "Edad al ingreso, no al titularse", "Quien se atrasa llega con más edad al titularse: usar esa edad invertiría la causalidad."],
    [I.red, "Errores agrupados por institución", "Los titulados de una misma institución no son independientes; así la incertidumbre no se subestima."],
    [I.corte, "Duración teórica fuera del modelo", "VIF de 8,7 y comparaciones que no existen en los datos; se evaluó como análisis de sensibilidad."],
    [I.check, "Validación en datos no vistos", "70 % para entrenar y 30 % para probar: AUC de " + num(met.AUC, 2) + " y buena calibración."],
  ];
  decisiones.forEach(([ic, tit, txt], i) => {
    const x = 0.6 + (i % 2) * 6.15, y = 2.1 + Math.floor(i / 2) * 2.15;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 5.95, h: 1.95, rectRadius: 0.12, fill: { color: C.background2 }, line: { color: HEX.lt2 }, objectName: "Decisión " + (i + 1) });
    circuloIcono(s, ic, x + 0.3, y + 0.32, 0.8, C.accent1, tit);
    T(s, tit, { x: x + 1.35, y: y + 0.3, w: 4.4, h: 0.45, fontSize: 17, bold: true, color: C.text1 });
    T(s, txt, { x: x + 1.35, y: y + 0.8, w: 4.4, h: 1.0, fontSize: 14, color: GRIS_TEXTO, valign: "top" });
  });
  T(s, "R 4.6.1 · tidyverse · sandwich · lmtest · car · pROC", { x: 0.6, y: 6.5, w: 8, h: 0.35, fontSize: 12, color: GRIS_TEXTO, italic: true });
  s.addNotes(
`[1:00] Método.
Decir: "Como la respuesta es binaria, usamos regresión logística. Nos permite ver el efecto de cada factor manteniendo constantes los demás."
"Tomamos cuatro decisiones para que el resultado sea válido:" (recorrer las cuatro tarjetas, una frase cada una).
"El AUC de 0,69 es moderado: el modelo sirve para identificar factores asociados, no para predecir qué estudiante se atrasará."

Pregunta probable: ¿por qué no usaron otra técnica, como un árbol de decisión?
Respuesta: la decisión requiere cuantificar y explicar el efecto de cada factor con su incertidumbre; la regresión logística entrega odds ratio e intervalos de confianza interpretables. Un árbol prioriza predicción, y nuestro objetivo es explicativo.
Pregunta probable: ¿revisaron supuestos?
Respuesta: sí, multicolinealidad (VIF máximo 1,17), dispersión (1,01), calibración por deciles y análisis de sensibilidad (ver anexo).`);

  // =============================================================== 5. QUÉ OCURRE
  s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Análisis" });
  s.addText("Las carreras profesionales universitarias concentran el atraso", { placeholder: "title" });
  const ordenG = [...grupos].sort((a, b) => Number(b.pct) - Number(a.pct)); // mejor abajo -> peor arriba
  s.addChart(pres.charts.BAR, [{ name: "% oportuna", labels: ordenG.map((g) => g.valor), values: ordenG.map((g) => Number(g.pct)) }],
    Object.assign({}, EJE, {
      x: 0.6, y: 1.5, w: 7.6, h: 4.6, barDir: "bar", barGapWidthPct: 55,
      chartColors: ordenG.map((g) => (Number(g.ic_sup) < 75 ? HEX.accent3 : HEX.accent2)),
      valAxisMinVal: 0, valAxisMaxVal: 100, valAxisMajorUnit: 25, valAxisLabelFormatCode: '0" %"',
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '0.0" %"',
      showTitle: true, title: "% de titulación oportuna por tipo de institución y nivel", titleFontSize: 14,
      titleColor: GRIS_TEXTO, titleFontFace: "+mn-lt",
    }));
  T(s, [{ text: "■ ", options: { color: HEX.accent3 } }, { text: "Bajo la meta del 75 % (todo el IC 95 %)   " },
        { text: "■ ", options: { color: HEX.accent2 } }, { text: "En o sobre la meta" }],
    { x: 0.6, y: 6.2, w: 7.6, h: 0.35, fontSize: 12, color: GRIS_TEXTO });
  const stats = [
    [num(kg.pct) + " %", "titulación oportuna global", "IC 95 %: " + num(kg.ic_inf) + "–" + num(kg.ic_sup) + " %", C.text1],
    [pp(Number(peor.pct) - Number(mejor.pct)), "brecha: " + peor.valor + " vs " + mejor.valor, "", C.accent3],
    [num(derecho.pct) + " %", "titulación oportuna en Derecho", "el área más baja (" + ent(derecho.n) + " titulados)", C.accent1],
  ];
  stats.forEach(([v, l, sub], i) => {
    const y = 1.6 + i * 1.6;
    T(s, v, { x: 8.75, y, w: 4.0, h: 0.75, fontSize: 40, bold: true, color: stats[i][3], fontFace: THEME.headFontFace });
    T(s, l, { x: 8.75, y: y + 0.75, w: 4.0, h: 0.4, fontSize: 14, color: C.text1 });
    if (sub) T(s, sub, { x: 8.75, y: y + 1.08, w: 4.0, h: 0.35, fontSize: 12, color: GRIS_TEXTO });
  });
  s.addNotes(
`[0:45] Qué ocurre.
Decir: "El 71,8 % se titula de forma oportuna, 3 puntos bajo la meta referencial."
"Pero el promedio esconde brechas: en las carreras profesionales universitarias la cifra baja a 62,1 %, casi 20 puntos menos que en las carreras técnicas de IP."
"Y en Derecho solo el 34,4 % se titula a tiempo."
"El color sigue la misma regla del dashboard: naranja solo si todo el intervalo de confianza está bajo la meta."

Pregunta probable: ¿no es injusto comparar carreras técnicas de 5 semestres con profesionales de 10?
Respuesta: por eso el modelo de la lámina siguiente controla área, edad, género, región y modalidad, y además probamos incluir la duración teórica (análisis de sensibilidad): la conclusión sobre las universidades profesionales se mantiene.`);

  // =============================================================== 6. FACTORES
  s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Análisis" });
  s.addText("Derecho es el foco más claro; la modalidad no marca diferencia", { placeholder: "title" });
  const factores = [
    ["Derecho (vs Tecnología)", efe("area_conocimiento", "Derecho")],
    ["Macrozona Norte (vs Metropolitana)", efe("macrozona", "Norte")],
    ["Mujer (vs hombre)", efe("genero", "Mujer")],
    ["Ingresa con 30+ años (vs 19 o menos)", efe("tramo_edad_ingreso", "30 o más")],
    ["IP · técnica (vs Univ. profesional)", efe("grupo_inst", "IP · técnica")],
    ["Salud (vs Tecnología)", efe("area_conocimiento", "Salud")],
    ["IP · profesional (vs Univ. profesional)", efe("grupo_inst", "IP · profesional")],
    ["Univ. técnica (vs Univ. profesional)", efe("grupo_inst", "Universidad · técnica")],
    ["Educación (vs Tecnología)", efe("area_conocimiento", "Educación")],
    ["Ciencias Sociales (vs Tecnología)", efe("area_conocimiento", "Ciencias Sociales")],
  ].map(([l, r]) => [l, Number(r.dif_vs_ref_pp)]).sort((a, b) => a[1] - b[1]);
  s.addChart(pres.charts.BAR, [{ name: "Efecto (pp)", labels: factores.map((f) => f[0]), values: factores.map((f) => Number(f[1].toFixed(1))) }],
    Object.assign({}, EJE, {
      x: 0.6, y: 1.45, w: 8.2, h: 5.2, barDir: "bar", barGapWidthPct: 45,
      chartColors: factores.map((f) => (f[1] > 0 ? HEX.accent3 : HEX.accent2)),
      valAxisMinVal: -25, valAxisMaxVal: 25, valAxisMajorUnit: 10, valAxisLabelFormatCode: '+0;-0;0',
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '+0.0" pp";-0.0" pp"',
      catAxisLabelFontSize: 12, catAxisLabelPos: "low",
      showTitle: true, title: "Cambio en la probabilidad de titularse fuera de plazo (puntos porcentuales)",
      titleFontSize: 13, titleColor: GRIS_TEXTO, titleFontFace: "+mn-lt",
    }));
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 9.2, y: 1.55, w: 3.53, h: 2.1, rectRadius: 0.12, fill: { color: C.background2 }, line: { color: HEX.lt2 }, objectName: "Cómo leer" });
  T(s, "Cómo leer", { x: 9.45, y: 1.72, w: 3.1, h: 0.35, fontSize: 15, bold: true, color: C.text1 });
  T(s, "Diferencia frente a la categoría de referencia, manteniendo constantes los demás factores. Solo efectos significativos (IC 95 %). Es asociación, no causalidad.",
    { x: 9.45, y: 2.1, w: 3.1, h: 1.5, fontSize: 12.5, color: GRIS_TEXTO, valign: "top" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 9.2, y: 3.85, w: 3.53, h: 2.8, rectRadius: 0.12, fill: { color: C.background2 }, line: { color: HEX.lt2 }, objectName: "No significativos" });
  T(s, "Sin diferencia significativa", { x: 9.45, y: 4.02, w: 3.1, h: 0.35, fontSize: 15, bold: true, color: C.text1 });
  T(s, [
    { text: "Modalidad: a distancia, vespertina, semipresencial", options: { bullet: true, breakLine: true } },
    { text: "CFT: depende de cómo se especifica el modelo", options: { bullet: true, breakLine: true } },
    { text: "Macrozonas Centro, Sur y Austral", options: { bullet: true, breakLine: true } },
    { text: "Agropecuaria y Ciencias Básicas", options: { bullet: true } },
  ], { x: 9.45, y: 4.45, w: 3.15, h: 2.1, fontSize: 12.5, color: GRIS_TEXTO, valign: "top", paraSpaceAfter: 4 });
  const oD = orx["area_conocimientoDerecho"];
  s.addNotes(
`[1:00] Factores asociados.
Decir: "Cada barra es el cambio en la probabilidad de titularse fuera de plazo frente a una referencia, a igualdad de lo demás."
"Derecho: +20,9 puntos frente a Tecnología (odds ratio ${num(oD.OR, 2)}, IC 95 % ${num(oD.OR_inf, 2)}–${num(oD.OR_sup, 2)}). Es el efecto más grande y robusto."
"Las carreras de IP y las técnicas universitarias tienen entre 14 y 17 puntos menos de atraso que las profesionales universitarias."
"Macrozona Norte: +6 puntos. Mujeres: 5 puntos menos."
"Igual de importante es lo que NO resultó: la modalidad no marca diferencia. En la comparación simple la educación a distancia parecía mejor, pero al controlar el perfil de sus estudiantes la diferencia desaparece."

Pregunta probable: ¿entonces estudiar Derecho causa el atraso?
Respuesta: no. Es una asociación en datos observacionales. Es consistente con un proceso de titulación largo (memoria y examen de grado), pero los datos no permiten confirmarlo; por eso recomendamos un diagnóstico antes de intervenir.
Pregunta probable: ¿por qué ingresar con 30+ años se asocia a menos atraso?
Respuesta: probablemente sesgo de supervivencia: los estudiantes mayores que se atrasan tienden a abandonar y no aparecen en una base de titulados.`);

  // =============================================================== 7. DEMO
  pres.addSection({ title: "Dashboard" });
  s = pres.addSlide({ masterName: "OSCURA", sectionTitle: "Dashboard" });
  s.addText("Demostración en vivo del dashboard", { placeholder: "title" });
  circuloIcono(s, I.link, 0.7, 1.55, 0.55, C.accent1, "Enlace");
  T(s, URL_DASH, { x: 1.4, y: 1.55, w: 5.4, h: 0.55, fontSize: 17, bold: true, color: C.background1, valign: "middle" });
  const pasos = [
    ["Resumen", "Qué ocurre: KPI con meta, fuente y fecha"],
    ["Factores asociados", "Por qué: efectos ajustados y calibración"],
    ["Explorar instituciones", "Dónde actuar: filtrar Derecho y Universidad · profesional"],
    ["Datos y método", "Trazabilidad: KPI, bitácora y limitaciones"],
  ];
  pasos.forEach(([tit, txt], i) => {
    const y = 2.5 + i * 1.08;
    s.addShape(pres.shapes.OVAL, { x: 0.7, y, w: 0.62, h: 0.62, fill: { color: C.background1 }, line: { color: HEX.lt1 }, objectName: "Paso " + (i + 1) });
    T(s, String(i + 1), { x: 0.7, y, w: 0.62, h: 0.62, fontSize: 20, bold: true, color: C.text1, align: "center", valign: "middle", fontFace: THEME.headFontFace });
    T(s, tit, { x: 1.55, y: y - 0.04, w: 5.3, h: 0.36, fontSize: 17, bold: true, color: C.background1 });
    T(s, txt, { x: 1.55, y: y + 0.32, w: 5.3, h: 0.36, fontSize: 13, color: GRIS_CLARO_OSCURO });
  });
  s.addImage({ path: FIG("dash_resumen.png"), x: 7.25, y: 1.55, w: 5.4, h: 5.4 * 1575 / 1950, objectName: "Captura del dashboard",
    altText: "Página Resumen del dashboard de titulación oportuna" });
  T(s, "Respaldo si falla la conexión: dashboard/dashboard_titulacion.html (funciona sin internet)",
    { x: 7.25, y: 6.05 + 0.4, w: 5.4, h: 0.35, fontSize: 11, color: GRIS_CLARO_OSCURO, italic: true });
  s.addNotes(
`[2:00] DEMO EN VIVO. Tener el dashboard abierto en otra pestaña ANTES de empezar. Respaldo sin internet: abrir dashboard/dashboard_titulacion.html con doble clic.

Guion sugerido:
1. Resumen (30 s): "Arriba los KPI con meta, unidad, período, fuente y fecha. El gauge muestra 71,8 % frente a la meta. Los títulos de cada gráfico dicen el hallazgo, no solo el tema."
2. Factores asociados (30 s): pasar el mouse por la barra de Derecho para mostrar el odds ratio y su intervalo. "Gris significa que no hay diferencia significativa."
3. Explorar instituciones (45 s): en el filtro de Área elegir Derecho; marcar "Bajo la meta". "Abajo a la derecha están las celdas con más volumen y menor % oportuna: ahí una mejora tiene más impacto." Mostrar que la tabla se filtra igual y que se puede descargar en CSV.
4. Datos y método (15 s): "Cada KPI tiene definición, fuente y fecha; aquí está la bitácora de limpieza y las limitaciones."

Pregunta probable: ¿por qué flexdashboard y no Shiny?
Respuesta: genera un solo archivo HTML que se abre sin R ni servidor; los filtros funcionan en el navegador con crosstalk. Para lo que pide la decisión no necesitamos recalcular el modelo en vivo.
Pregunta probable: ¿por qué hay celdas ocultas?
Respuesta: se ocultan las combinaciones con menos de 30 titulados, porque sus porcentajes son inestables y aumentan el riesgo de reidentificar personas.`);

  // =============================================================== 8. LIMITACIONES
  pres.addSection({ title: "Cierre" });
  s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Cierre" });
  s.addText("Lo que estos datos no permiten afirmar", { placeholder: "title" });
  const lims = [
    [I.sobrevive, "Sesgo de supervivencia", "Solo hay titulados: quien desertó no aparece. El KPI no es una tasa de titulación del sistema."],
    [I.causa, "Asociación, no causalidad", "Diseño observacional, sin datos de rendimiento, trabajo ni financiamiento."],
    [I.regla, "Duración declarada distinta", "Cada institución informa la duración a su manera; se controla, pero puede quedar sesgo."],
    [I.calendario, "Un solo año", "2025 no muestra tendencias, y un AUC de " + num(met.AUC, 2) + " no sirve para predecir casos individuales."],
  ];
  lims.forEach(([ic, tit, txt], i) => {
    const x = 0.6 + i * 3.08;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.6, w: 2.85, h: 3.7, rectRadius: 0.12, fill: { color: C.background2 }, line: { color: HEX.lt2 }, objectName: "Limitación " + (i + 1) });
    circuloIcono(s, ic, x + 0.3, 1.9, 0.85, C.text1, tit);
    T(s, tit, { x: x + 0.3, y: 2.95, w: 2.3, h: 0.75, fontSize: 17, bold: true, color: C.text1, valign: "top" });
    T(s, txt, { x: x + 0.3, y: 3.7, w: 2.3, h: 1.5, fontSize: 13.5, color: GRIS_TEXTO, valign: "top" });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 5.55, w: 12.13, h: 1.05, rectRadius: 0.12, fill: { color: ROJO_SUAVE }, line: { color: ROJO_SUAVE }, objectName: "Ejemplo limitación" });
  T(s, [{ text: "Ejemplo: ", options: { bold: true, color: HEX.accent1 } },
        { text: "que quienes ingresan con 30 años o más se titulen más a tiempo probablemente refleja que los mayores que se atrasan abandonan, no un efecto real de la edad." }],
    { x: 0.9, y: 5.55, w: 11.6, h: 1.05, fontSize: 14, color: C.text1, valign: "middle" });
  s.addNotes(
`[0:45] Limitaciones.
Decir: "Declaramos cuatro limitaciones que condicionan cómo leer los resultados." (una frase por tarjeta)
"La más importante es el sesgo de supervivencia: la base solo tiene titulados. Por eso no hablamos de tasa de titulación del sistema, y por eso el resultado de la edad hay que leerlo con cautela."

Pregunta probable: ¿cómo se resolvería el sesgo de supervivencia?
Respuesta: cruzando con las bases de matrícula del SIES para seguir cohortes completas, incluyendo a quienes desertan. Es nuestra propuesta de continuidad.`);

  // =============================================================== 9. RECOMENDACIONES
  s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Cierre" });
  s.addText("Actuar donde la evidencia es fuerte, investigar donde es moderada", { placeholder: "title" });
  const recs = [
    [I.actuar, "Actuar", C.accent1, HEX.accent1, ["Diagnosticar el proceso de titulación en Derecho (memoria y examen de grado)", "Piloto de acompañamiento en carreras profesionales universitarias de mayor volumen"]],
    [I.investigar, "Investigar", C.text2, HEX.dk2, ["Causas del atraso en la macrozona Norte (+6 pp)", "Estandarizar cómo se declara la duración teórica"]],
    [I.pausa, "No actuar aún", C.accent4, HEX.accent4, ["Modalidad: sin diferencias significativas", "CFT: resultado no robusto a la especificación"]],
  ];
  recs.forEach(([ic, tit, col, hex, items], i) => {
    const x = 0.6 + i * 4.1;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.6, w: 3.9, h: 3.1, rectRadius: 0.12, fill: { color: C.background2 }, line: { color: HEX.lt2 }, objectName: "Recomendación " + tit });
    circuloIcono(s, ic, x + 0.3, 1.85, 0.75, col, tit);
    T(s, tit, { x: x + 1.2, y: 1.85, w: 2.5, h: 0.75, fontSize: 20, bold: true, color: hex, valign: "middle" });
    T(s, items.map((t, k) => ({ text: t, options: { bullet: true, breakLine: k < items.length - 1 } })),
      { x: x + 0.3, y: 2.85, w: 3.35, h: 1.75, fontSize: 14, color: C.text1, valign: "top", paraSpaceAfter: 8 });
  });
  circuloIcono(s, I.monitor, 0.6, 5.25, 0.7, C.accent2, "Monitoreo");
  T(s, [{ text: "Monitoreo: ", options: { bold: true } },
        { text: "el pipeline se vuelve a ejecutar con cada base anual del SIES en unos 45 segundos. Seguir el % oportuna y la brecha en las carreras intervenidas frente a carreras comparables." }],
    { x: 1.5, y: 5.1, w: 11.2, h: 1.0, fontSize: 15, color: C.text1, valign: "middle" });
  s.addNotes(
`[0:45] Recomendaciones.
Decir: "Las recomendaciones son proporcionales a la evidencia y consideran el costo de equivocarse: intervenir donde el atraso responde al diseño curricular gastaría recursos sin mejorar nada."
"Actuar donde el efecto es grande y robusto: Derecho y carreras profesionales universitarias. Investigar donde es moderado: macrozona Norte. Y no actuar donde no hay evidencia: modalidad y CFT."
"Para monitorear, todo el análisis se regenera con un solo script cuando salga la base del próximo año."`);

  // =============================================================== 10. CIERRE
  s = pres.addSlide({ masterName: "CIERRE", sectionTitle: "Cierre" });
  s.addText("El atraso no es parejo: se concentra en Derecho y en las carreras profesionales universitarias",
    { placeholder: "title" });
  T(s, "La evidencia permite focalizar; el dashboard permite monitorear.", { x: 0.7, y: 3.4, w: 11.9, h: 0.6, fontSize: 20, color: GRIS_CLARO_OSCURO });
  T(s, "¿Preguntas?", { x: 0.7, y: 4.6, w: 6, h: 1.0, fontSize: 44, bold: true, color: C.background1, fontFace: THEME.headFontFace });
  T(s, [{ text: "Dashboard: ", options: { bold: true } }, { text: URL_DASH, options: { breakLine: true } },
        { text: "Código: ", options: { bold: true } }, { text: URL_REPO }],
    { x: 0.7, y: 5.85, w: 9, h: 0.8, fontSize: 14, color: GRIS_CLARO_OSCURO });
  s.addNotes(
`[0:15] Cierre.
Decir la frase del título y abrir preguntas. Para preguntas técnicas, usar las láminas del anexo (bitácora, diagnósticos, sensibilidad).`);

  // =============================================================== ANEXO
  pres.addSection({ title: "Anexo" });
  // A1. Bitácora
  s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Anexo" });
  s.addText("Anexo · Bitácora de limpieza de datos", { placeholder: "title" });
  const cab = ["Paso", "Dimensión", "Regla", "Eliminadas", "Filas después"].map((t) => ({ text: t, options: { bold: true, color: HEX.lt1, fill: { color: HEX.dk1 } } }));
  const cortas = {
    R1: "Solo pregrado (alcance de la pregunta)", R2: "Año de ingreso entre 1950 y 2025 (excluye códigos especiales)",
    R3: "Semestre de ingreso en {1, 2}", R4: "Fecha válida en el año académico 2025 (ene-2025 a feb-2026)",
    R5: "Duración teórica > 0", R6: "Titulación posterior al ingreso",
    R7: "Excluye planes de continuidad", R8: "Elimina MRUN, fecha de nacimiento y títulos en texto",
  };
  s.addTable([cab, ...bit.map((b) => [b.paso, b.dimension, cortas[b.paso], ent(b.eliminadas), ent(b.filas_despues)])], {
    x: 0.6, y: 1.5, w: 12.13, colW: [0.8, 2.1, 5.9, 1.6, 1.73], fontSize: 13, fontFace: THEME.bodyFontFace, color: HEX.dk1,
    border: { type: "solid", pt: 0.5, color: "D9DBDF" }, rowH: 0.42, valign: "middle", margin: [0.03, 0.08, 0.03, 0.08],
  });
  T(s, "Inicio: " + ent(filas.R1.filas_antes) + " filas × 41 columnas   →   Fin: " + ent(kg.n) + " filas × 54 columnas (41 − 4 + 17 derivadas)",
    { x: 0.6, y: 5.55, w: 12.1, h: 0.4, fontSize: 14, bold: true, color: C.text1 });
  T(s, "No eliminados: 11.951 MRUN repetidos (personas con más de un título), 970 filas sin MRUN, 14 edades sin información (→ NA) y casos de duración extrema (se marcan).",
    { x: 0.6, y: 6.0, w: 12.1, h: 0.7, fontSize: 12.5, color: GRIS_TEXTO });
  s.addNotes("Respaldo para preguntas sobre limpieza. R3 a R6 no eliminaron filas: funcionaron como verificaciones.");

  // A2. Diagnósticos
  s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Anexo" });
  s.addText("Anexo · Diagnósticos y validación del modelo", { placeholder: "title" });
  const vifMax = Math.max(...vif.map((v) => Number(v.GVIF_ajustado)));
  const diag = [
    ["Multicolinealidad (GVIF ajustado)", "máx. " + num(vifMax, 2), "Bajo el umbral habitual (≈2,24)"],
    ["Dispersión (Pearson χ² / gl)", num(aj.ratio_dispersion, 2), "Sin sobredispersión"],
    ["Pseudo R² de McFadden", num(aj.pseudo_R2_McFadden, 3), "Esperable en datos individuales"],
    ["AUC en prueba (30 %)", num(met.AUC, 3) + " (" + num(met.AUC_inf, 3) + "–" + num(met.AUC_sup, 3) + ")", "Discriminación moderada"],
    ["Brier en prueba", num(met.Brier, 3) + " vs " + num(met.Brier_referencia, 3), "Mejora de " + num(met.mejora_Brier_pct) + " %"],
  ];
  const cabD = ["Diagnóstico", "Resultado", "Lectura"].map((t) => ({ text: t, options: { bold: true, color: HEX.lt1, fill: { color: HEX.dk1 } } }));
  s.addTable([cabD, ...diag], { x: 0.6, y: 1.5, w: 7.0, colW: [2.7, 1.9, 2.4], fontSize: 13, fontFace: THEME.bodyFontFace, color: HEX.dk1,
    border: { type: "solid", pt: 0.5, color: "D9DBDF" }, rowH: 0.55, valign: "middle", margin: [0.03, 0.08, 0.03, 0.08] });
  s.addImage({ path: FIG("fig_11_calibracion.png"), x: 8.0, y: 1.45, w: 4.7, h: 4.7 * 900 / 1050, objectName: "Calibración", altText: "Gráfico de calibración del modelo por deciles" });
  T(s, "Errores estándar agrupados por institución (sandwich::vcovCL). Partición 70/30 con semilla fija.",
    { x: 0.6, y: 5.0, w: 7.0, h: 0.6, fontSize: 12.5, color: GRIS_TEXTO, italic: true });
  s.addNotes("Respaldo para preguntas sobre supuestos y validez del modelo.");

  // A3. Sensibilidad
  s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Anexo" });
  s.addText("Anexo · Odds ratio y análisis de sensibilidad", { placeholder: "title" });
  s.addImage({ path: FIG("fig_10_odds_ratio.png"), x: 0.6, y: 1.4, w: 4.9, h: 4.9 * 1500 / 1350, objectName: "Odds ratio", altText: "Odds ratio con intervalos de confianza por factor" });
  const cft = sens["grupo_instCFT · técnica"];
  T(s, "¿Qué pasa si se agrega la duración teórica al modelo?", { x: 6.0, y: 1.5, w: 6.7, h: 0.45, fontSize: 18, bold: true, color: C.text1 });
  T(s, [
    { text: "Área, género, edad al ingreso y macrozona: las conclusiones no cambian.", options: { bullet: true, breakLine: true } },
    { text: "CFT · técnica: OR " + num(cft.OR_modelo_principal, 2) + " (no significativo) pasa a " + num(cft.OR_con_duracion, 2) + " (significativo). El resultado depende de la especificación: no se recomienda actuar sobre él.", options: { bullet: true, breakLine: true } },
    { text: "La duración se dejó fuera del modelo principal por su VIF de 8,7 y porque obliga a comparar carreras técnicas y profesionales de igual duración, que no existen en los datos.", options: { bullet: true } },
  ], { x: 6.0, y: 2.1, w: 6.7, h: 3.6, fontSize: 15, color: C.text1, valign: "top", paraSpaceAfter: 10 });
  s.addNotes("Respaldo para preguntas sobre robustez y sobre la decisión de excluir la duración teórica.");

  await pres.writeFile({ fileName: SALIDA });
  console.log("Presentación generada:", SALIDA);
}

module.exports = { THEME, SALIDA };
if (require.main === module) {
  construir().then(async () => {
    const tema = process.env.APPLY_THEME;
    if (tema) {
      const { applyTheme } = require(tema);
      await applyTheme(SALIDA, THEME);
      console.log("Tema aplicado");
    }
  }).catch((e) => { console.error(e); process.exit(1); });
}
